#!/usr/bin/env python3

import os
import re
import sys
import shutil
import tempfile
import argparse

from typing import Optional

from colorama import init as colorama_init
from colorama import Fore as Color
from colorama import Style
from rich_argparse import RichHelpFormatter

from modules.ffprobe import StreamTags, Stream
from modules.api import api_login, change_episode_number, change_season_type, get_episode, get_movie_name, get_series_from_tvdb, get_subtitles_from_ost, logout, APITokens
from modules.video import video
from modules.audio import audio, recode_audio
from modules.subs import subtitles
from modules.ffmpeg import probe, ffrecode

colorama_init()

if os.path.exists("/usr/lib/libamfrt64.so"):
    HWACC = "AMF"
elif os.path.exists("/usr/lib/libcuda.so"):
    HWACC = "CUDA"
else:
    HWACC = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recode media to common format", formatter_class=RichHelpFormatter)
    parser.add_argument(
        "-l",
        "--lang",
        help="Language of content, sets audio and subtitle language if undefined and tries to get information in specified language",
        choices=[
            "ara",
            "chi",
            "deu",
            "eng",
            "fin",
            "fre",
            "ger",
            "jpn",
            "kor",
            "rus",
            "spa",
        ],
        default="eng",
        dest="lang",
        metavar="LANG",
    )
    parser.add_argument("-i", "--input", help="File to recode", type=str, required=False, dest="inputfile", metavar="FILE")
    parser.add_argument("-d", "--dir", help="Directory containing files to recode", type=str, required=False, dest="inputdir", metavar="DIR")
    parser.add_argument("-t", "--type", help="Type of content", choices=["film", "series", "rename", "seriesdir", "changeSeasonType"], required=True, dest="contentype", metavar="TYPE")
    parser.add_argument("-a", "--no-api", help="Disable Metadata and Subtitle APIs", default=False, action="store_true", dest="apis")
    parser.add_argument("-s", "--subtitle", help="Directory containing Subtitles", required=False, default="", dest="subdir", metavar="DIR")
    parser.add_argument("-c", "--codec", help="Select codec", required=False, choices=["h264", "h265", "av1"], dest="codec", metavar="CODEC", default="av1")
    parser.add_argument("-b", "--bit", help="Select bit depth", required=False, choices=["8", "10"], dest="bit", metavar="BIT", default="10")
    parser.add_argument("-o", "--output", help="Output folder", required=False, default="", dest="output", metavar="DIR", type=str)
    parser.add_argument("--copy", help="Don't recode video streams, just copy them", required=False, action="store_true", dest="copy")
    parser.add_argument("--hwaccel", help="Enable Hardware Acceleration (faster but larger files)", required=False, action="store_true", dest="hwaccel")
    parser.add_argument("--infolang", help="Language the info shall be retrieved in (defaults to --lang)", required=False, default=None, choices=["eng", "deu"], dest="infolang")
    parser.add_argument("--sublang", help="Language the default subtitle should be (defaults to --lang)", required=False, default=None, choices=["eng", "ger"], dest="sublang")
    parser.add_argument("--searchstring", help="Manual search string for TVDB API", required=False, default=None, dest="searchstring", metavar="SEARCHSTRING")
    return parser.parse_args()


def recode_series(folder: str, apitokens: APITokens | None, lang: str, infolang: str, sublang: str, subdir: str = "", codec: str = "h265", bit: int = 10, output: str = "", copy: bool = False, searchstring: str | None = None):
    if apitokens is None:
        apitokens = APITokens(thetvdb=None, opensub={"api_key": None, "token": None})
    series = os.path.basename(folder)
    parentfolder = output if output != "" else os.path.realpath(folder).removesuffix(f"/{series}")
    seriesobj, seriesname, year = get_series_from_tvdb(series, apitokens["thetvdb"], lang=infolang, searchstring=searchstring)
    if seriesobj is None:
        return
    if year != "":
        series = f"{seriesname} ({year})"
    for dire in sorted(os.listdir(folder)):
        if os.path.isdir(os.path.join(folder, dire)):
            for file in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
                season, name, metadata = get_episode(series, file, seriesobj)
                if name is not None and season is not None:
                    if not os.path.exists(os.path.join(parentfolder, series, season)):
                        os.makedirs(os.path.join(parentfolder, series, season))
                    recode(
                        file=os.path.join(folder, dire, file),
                        path=os.path.join(parentfolder, series, season, name),
                        metadata=metadata,
                        lang=lang,
                        infolang=infolang,
                        sublang=sublang,
                        apitokens=apitokens,
                        subdir=subdir,
                        codec=codec,
                        bit=bit,
                        output=output,
                        copy=copy,
                    )
        else:
            season, name, metadata = get_episode(series, dire, seriesobj)
            if name is not None and season is not None:
                if not os.path.exists(os.path.join(parentfolder, series, season)):
                    os.makedirs(os.path.join(parentfolder, series, season))
                recode(
                    file=os.path.join(os.path.realpath(folder), dire),
                    path=os.path.join(parentfolder, series, season, name),
                    metadata=metadata,
                    lang=lang,
                    infolang=infolang,
                    sublang=sublang,
                    apitokens=apitokens,
                    subdir=subdir,
                    codec=codec,
                    bit=bit,
                    output=output,
                    copy=copy,
                )


def recode(
    file: str,
    lang: str,
    infolang: str,
    sublang: str,
    path: Optional[str] = None,
    metadata: Optional[dict] = None,
    apitokens: Optional[APITokens] = None,
    subdir: str = "",
    codec: str = "h265",
    bit: int = 10,
    stype: str = "single",
    output: str = "",
    copy: bool = False,
    searchstring: str | None = None,
):
    prelines = []
    midlines = []
    printlines = []

    adefault = {"aindex": None, "codec": None, "lang": None, "channels": 0, "title": None, "oindex": None}
    sdefault = {"sindex": None, "type": None, "lang": None, "title": None, "oindex": None}

    videostreams: list[Stream] = []
    audiostreams: list[Stream] = []
    subtitlestreams: list[Stream] = []
    attachmentstreams: list[Stream] = []

    changealang: list[dict[str, str]] = []
    changeslang: list[dict[str, str]] = []
    dispositions: dict[str, dict[str, str | list[str]]] = {}

    astreams = []
    sstreams = []

    ffmpeg_mapping = []
    ffmpeg_recoding = []
    ffmpeg_dispositions = []
    ffmpeg_metadata = []
    additional_files = []

    vindex = 0
    aindex = 0
    sindex = 0
    tindex = 0

    vrecoding = False
    arecoding = False
    changedefault = False
    changemetadata = False

    subfile = ""

    if apitokens is None:
        apitokens = APITokens(thetvdb=None, opensub={"api_key": None, "token": None})

    if path is None:
        output_file, metadata = get_movie_name(file, apitokens["thetvdb"], lang=infolang, stype=stype, searchstring=searchstring)
        if output_file is None:
            return
        output_dir = output if output != "" else os.path.realpath(file).removesuffix(file)
        output_file = os.path.join(output_dir, output_file)
    else:
        output_file = path

    if metadata is None:
        metadata = {}
        metadata["title"] = os.path.basename(os.path.splitext(output_file)[0])

    output_file = output_file.replace("?", "")

    prelines.append(f"{Color.RED}Recoding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(file)}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")

    ffprobe = probe(os.path.realpath(file))

    if ffprobe.streams is None:
        print(f"Error: {file} has no streams")
        return

    midlines.append(f"{Color.RED}Streams{Style.RESET_ALL}:")
    for stream in ffprobe.streams:
        if stream.tags is None:
            stream.tags = StreamTags(title=None, language=None)
        disposition = " ".join([dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]])
        if stream.codec_type != "attachment":
            if stream.codec_type == "video" and not (stream.disposition.attached_pic or stream.codec_name == "mjpeg"):
                midlines.append(
                    f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.WHITE}{stream.pix_fmt} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
                )
                videostreams.append(stream)
            elif stream.codec_type == "audio":
                midlines.append(
                    f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
                )
                audiostreams.append(stream)
            elif stream.codec_type == "subtitle":
                midlines.append(
                    f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
                )
                subtitlestreams.append(stream)
        elif stream.codec_type == "attachment":
            midlines.append(
                f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.filename} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
            )
            attachmentstreams.append(stream)

    printlines.append(f"{Color.LIGHTBLACK_EX}|------------------------------------------------------------------{Style.RESET_ALL}")

    for stream in videostreams:
        vrecoding, vindex, pix_fmt = video(stream, ffmpeg_mapping, ffmpeg_recoding, vrecoding, vindex, printlines, dispositions, HWACC, codec, bit, copy)

    for stream in audiostreams:
        arecoding, aindex, changealang = audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines, dispositions, changealang, lang)

    if aindex == 0:
        for stream in audiostreams:
            arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines)
            aindex += 1

    for stream in subtitlestreams:
        sindex, changeslang = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams, printlines, dispositions, changeslang, sublang)

    if sindex == 0:
        if subdir != "" and os.path.isdir(subdir):
            episode = re.findall(r"[Ss]\d{2,4}[Ee]\d{2,4}", str(path))[0]
            files = os.listdir(subdir)
            subfile = [fil for fil in files if episode.lower() in fil.lower()]
            if len(subfile) == 1:
                subfile = os.path.join(subdir, subfile[0])
                if os.path.isdir(subfile):
                    subfil = os.listdir(subfile)
                    subfile = [os.path.join(subfile, fil) for fil in subfil]
                else:
                    subfile = [subfile]
        elif subdir != "" and os.path.isfile(subdir):
            subfile = [subdir]
        else:
            subfile = [get_subtitles_from_ost(token=apitokens["opensub"], metadata=metadata, lang=sublang, file=file)]
        try:
            for fil in subfile:
                sub = probe(os.path.realpath(fil))
                prelines.append(f"{Color.RED}Adding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(fil)}{Style.RESET_ALL}")
                additional_files.append(os.path.realpath(fil))
                for stream in sub.streams:
                    if stream.tags is None:
                        stream.tags = StreamTags.from_dict({"title": None, "language": sublang})
                    disposition = " ".join([dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]])
                    midlines.append(
                        f"{Color.BLUE}1:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
                    )
                    sindex, changeslang = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams, printlines, dispositions, changeslang, sublang, file=1)
        except Exception:
            ...

    for stream in attachmentstreams:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        printlines.append(
            f"Copying {Color.GREEN}attachment{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.filename}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}t:{tindex}{Style.RESET_ALL} in output file"
        )
        tindex += 1

    for stream in ffprobe.streams:
        if stream.codec_type == "video" and stream.codec_name == "mjpeg" and stream.tags.filename == "cover.jpg":
            disposition = " ".join([dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]])
            midlines.append(f"{Color.BLUE}0:{stream.index} {Color.GREEN}attached picture {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.YELLOW}{disposition}{Style.RESET_ALL}")
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:v:{vindex}", "mjpeg", f"-filter:v:{vindex}", "scale=-1:600"])
            ffmpeg_dispositions.extend([f"-disposition:v:{vindex}", "attached_pic"])
            printlines.append(
                f"Copying {Color.GREEN}attached picture{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
            )
            vindex += 1

    printlines.append(f"{Color.LIGHTBLACK_EX}|------------------------------------------------------------------{Style.RESET_ALL}")

    if aindex > 0 and adefault["aindex"] is not None:
        for stream in astreams:
            if adefault["aindex"] != stream["newindex"] and not dispositions.get("a" + str(stream["newindex"]), False):
                if "default" in dispositions["a" + str(stream["newindex"])]["types"]:
                    dispositions["a" + str(stream["newindex"])]["types"].remove("default")
            elif adefault["aindex"] == stream["newindex"] and dispositions.get("a" + str(stream["newindex"]), False):
                if "default" not in dispositions["a" + str(stream["newindex"])]["types"]:
                    dispositions["a" + str(stream["newindex"])]["types"].append("default")
            elif adefault["aindex"] == stream["newindex"] and not dispositions.get("a" + str(stream["newindex"]), False) and not stream["disposition"].get("default", False):
                dispositions["a" + str(stream["newindex"])] = {
                    "stype": "a",
                    "index": stream["newindex"],
                    "title": stream["tags"].get("title", "None"),
                    "lang": stream["tags"]["language"],
                    "types": ["default"],
                }
    if sindex > 0 and sdefault["sindex"] is not None:
        for stream in sstreams:
            if sdefault["sindex"] != stream["newindex"] and not dispositions.get("s" + str(stream["newindex"]), False):
                if "default" in dispositions["s" + str(stream["newindex"])]["types"]:
                    dispositions["s" + str(stream["newindex"])]["types"].remove("default")
            elif sdefault["sindex"] == stream["newindex"] and dispositions.get("s" + str(stream["newindex"]), False):
                if "default" not in dispositions["s" + str(stream["newindex"])]["types"]:
                    dispositions["s" + str(stream["newindex"])]["types"].append("default")
            elif sdefault["sindex"] == stream["newindex"] and not dispositions.get("s" + str(stream["newindex"]), False):
                dispositions["s" + str(stream["newindex"])] = {
                    "stype": "s",
                    "index": stream["newindex"],
                    "title": stream["tags"].get("title", "None"),
                    "lang": stream["tags"].get("language", "und"),
                    "types": ["default"],
                }

    if len(changealang) > 0:
        for change in changealang:
            ffmpeg_dispositions.extend([f"-metadata:s:a:{change['index']}", f"language={change['lang']}"])
            printlines.append(f"Setting {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}a:{change['index']}{Style.RESET_ALL} language to {Color.MAGENTA}{change['lang']}{Style.RESET_ALL}")
            changedefault = True

    if len(changeslang) > 0:
        for change in changeslang:
            ffmpeg_dispositions.extend([f"-metadata:s:s:{change['index']}", f"language={change['lang']}"])
            printlines.append(f"Setting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}s:{change['index']}{Style.RESET_ALL} language to {Color.MAGENTA}{change['lang']}{Style.RESET_ALL}")
            changedefault = True

    for disposition in dispositions.values():
        if disposition["stype"] == "s":
            typ = "subtitle"
        elif disposition["stype"] == "a":
            typ = "audio"
        elif disposition["stype"] == "v":
            typ = "video"
        if disposition["types"] == []:
            disposition["types"] = ["none"]
        ffmpeg_dispositions.extend([f"-disposition:{disposition['stype']}:{disposition['index']}", "+".join(disposition["types"])])
        if typ == "subtitle":
            before = " ".join(sorted([k for k, v in sstreams[int(disposition["index"])]["disposition"].items() if v]))
            if before == "":
                before = "none"
            after = " ".join(sorted(disposition["types"]))
            if before != after:
                printlines.append(
                    f"Setting {Color.GREEN}{typ}{Style.RESET_ALL} stream {Color.BLUE}{disposition['stype']}:{disposition['index']}{Style.RESET_ALL} titled {Color.CYAN}{disposition['title']}{Style.RESET_ALL} language {Color.MAGENTA}{disposition['lang']}{Style.RESET_ALL} to {Color.YELLOW}{after}{Style.RESET_ALL}"
                )
                changedefault = True
        elif typ == "audio":
            before = " ".join(sorted([k for k, v in astreams[int(disposition["index"])]["disposition"].items() if v]))
            if before == "":
                before = "none"
            after = " ".join(sorted(disposition["types"]))
            if before != after:
                printlines.append(
                    f"Setting {Color.GREEN}{typ}{Style.RESET_ALL} stream {Color.BLUE}{disposition['stype']}:{disposition['index']}{Style.RESET_ALL} titled {Color.CYAN}{disposition['title']}{Style.RESET_ALL} language {Color.MAGENTA}{disposition['lang']}{Style.RESET_ALL} to {Color.YELLOW}{after}{Style.RESET_ALL}"
                )
                changedefault = True

    try:
        format_tags = ffprobe.format.tags.to_dict()
    except AttributeError:
        format_tags = {}

    if changedefault:
        printlines.append(f"{Color.LIGHTBLACK_EX}|------------------------------------------------------------------{Style.RESET_ALL}")

    for tag in metadata.keys():
        if metadata[tag] != "" and metadata[tag] is not None:
            if tag in format_tags and metadata[tag].strip() == format_tags[tag]:
                continue
            if tag not in format_tags:
                printlines.append(f"Changing {Color.GREEN}{tag}{Style.RESET_ALL} from {Color.CYAN}None{Style.RESET_ALL} to {Color.CYAN}{metadata[tag].strip()}{Style.RESET_ALL}")
            else:
                printlines.append(f"Changing {Color.GREEN}{tag}{Style.RESET_ALL} from {Color.CYAN}{format_tags[tag]}{Style.RESET_ALL} to {Color.CYAN}{metadata[tag].strip()}{Style.RESET_ALL}")
            ffmpeg_metadata.extend(["-metadata", f"{tag}={metadata[tag].strip()}"])
            changemetadata = True

    if not vrecoding and not arecoding and not changedefault and not changemetadata and os.path.realpath(file) == os.path.realpath(output_file):
        print(f"{Color.RED}No changes to make: {Color.GREEN}{file} {Color.BLUE}Continuing...{Style.RESET_ALL}")
        return
    if os.path.realpath(file) != os.path.realpath(output_file) and not vrecoding and not arecoding and not changedefault and not changemetadata:
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}{file}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
        shutil.move(os.path.realpath(file), os.path.realpath(output_file))
        return

    if changemetadata:
        printlines.append(f"{Color.LIGHTBLACK_EX}|------------------------------------------------------------------{Style.RESET_ALL}")

    _, tmpfile = tempfile.mkstemp(suffix=".mkv")

    if vrecoding:
        if HWACC == "AMF":
            ffmpeg_recoding.extend(["-rc", "hqvbr", "-qvbr_quality_level", "23", "-quality", "quality"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_recoding.extend(["-pixel_format", "p010le"])
            else:
                ffmpeg_recoding.extend(["-pixel_format", "yuv420p"])
        elif HWACC == "CUDA":
            if codec != "av1":
                ffmpeg_recoding.extend(["-preset", "p7", "-rc", "vbr_hq", "-cq", "23"])
            else:
                ffmpeg_recoding.extend(["-preset", "p7", "-rc", "vbr", "-cq", "23"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_recoding.extend(["-pixel_format", "p010le"])
            else:
                ffmpeg_recoding.extend(["-pixel_format", "yuv420p"])
        else:
            if codec != "av1":
                ffmpeg_recoding.extend(["-crf", "23", "-preset", "veryslow"])
            else:
                ffmpeg_recoding.extend(["-crf", "23"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_recoding.extend(["-pixel_format", "yuv420p10le"])
            else:
                ffmpeg_recoding.extend(["-pixel_format", "yuv420p"])
    if arecoding:
        ffmpeg_recoding.extend(["-b:a", "192k", "-ar", "48000"])
    for line in prelines:
        print(line)
    for line in midlines:
        print(line)
    for line in printlines:
        print(line)

    try:
        completed = ffrecode(os.path.realpath(file), tmpfile, ffmpeg_mapping, ffmpeg_recoding, ffmpeg_dispositions, ffmpeg_metadata, additional_files)
        if not completed:
            print(f"{Color.RED}Recoding failed, skipping moving file.{Style.RESET_ALL}")
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
            return

        if output == "":
            # Rename old file
            shutil.move(os.path.realpath(file), os.path.realpath(file) + ".old")

        # Move tempfile to output_file
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}tempfile{Style.RESET_ALL} to {Color.MAGENTA}{output_file}{Style.RESET_ALL}")
        try:
            shutil.move(tmpfile, output_file)
            os.chmod(output_file, 0o644)
        finally:
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
    finally:
        if isinstance(subfile, str):
            if os.path.exists(subfile):
                os.remove(subfile)
    print(f"{Color.GREEN}Done!{Style.RESET_ALL}")


def main():
    if "APPDATA" in os.environ:
        confighome = os.environ["APPDATA"]
    elif "XDG_CONFIG_HOME" in os.environ:
        confighome = os.environ["XDG_CONFIG_HOME"]
    else:
        confighome = os.path.join(os.environ["HOME"], ".config")
    configpath = os.path.join(confighome, "universal-ffmpeg-recoder")
    if not os.path.exists:
        os.makedirs(configpath)

    args = parse_args()

    if args.hwaccel is False:
        global HWACC
        HWACC = None

    if not args.apis:
        apitokens = api_login(configpath)
    else:
        apitokens = None

    if not args.infolang:
        infolang = args.lang
        if infolang == "ger":
            infolang = "deu"
    else:
        infolang = args.infolang

    if not args.sublang:
        sublang = args.lang
    else:
        sublang = args.sublang

    if args.contentype == "film":
        if args.inputfile:
            if os.path.isfile(args.inputfile):
                recode(
                    file=args.inputfile,
                    apitokens=apitokens,
                    lang=args.lang,
                    infolang=infolang,
                    sublang=sublang,
                    subdir=args.subdir,
                    codec=args.codec,
                    bit=int(args.bit),
                    stype="single",
                    output=args.output,
                    copy=args.copy,
                    searchstring=args.searchstring,
                )
            else:
                error = f'File "{args.inputfile}" does not exist or is a directory.'
                raise FileNotFoundError(error)
        elif args.inputdir:
            if os.path.isdir(args.inputdir):
                for subdir in os.listdir(args.inputdir):
                    recode(
                        file=subdir,
                        apitokens=apitokens,
                        lang=args.lang,
                        infolang=infolang,
                        sublang=sublang,
                        subdir=args.subdir,
                        codec=args.codec,
                        bit=int(args.bit),
                        stype="multi",
                        output=args.output,
                        copy=args.copy,
                        searchstring=args.searchstring,
                    )
            else:
                error = f'Directory "{args.inputdir}" does not exist'
                raise FileNotFoundError(error)
        else:
            print("error: inputfile or directory required if type is film")
            sys.exit()
    elif args.contentype == "seriesdir":
        if args.inputdir:
            if os.path.isdir(args.inputdir):
                for subdir in sorted(os.listdir(args.inputdir)):
                    recode_series(
                        os.path.join(os.path.realpath(args.inputdir), subdir),
                        apitokens=apitokens,
                        lang=args.lang,
                        infolang=infolang,
                        sublang=sublang,
                        subdir=args.subdir,
                        codec=args.codec,
                        bit=int(args.bit),
                        output=args.output,
                        copy=args.copy,
                        searchstring=args.searchstring,
                    )
            else:
                error = f'Directory "{args.inputdir}" does not exist'
                raise FileNotFoundError(error)
        else:
            print("error: inputdirectory required if type is seriesdir")
            sys.exit()
    elif args.contentype == "series":
        if args.inputdir:
            if os.path.isdir(args.inputdir):
                recode_series(
                    args.inputdir,
                    apitokens=apitokens,
                    lang=args.lang,
                    infolang=infolang,
                    sublang=sublang,
                    subdir=args.subdir,
                    codec=args.codec,
                    bit=int(args.bit),
                    output=args.output,
                    copy=args.copy,
                    searchstring=args.searchstring,
                )
            else:
                error = f'Directory "{args.inputdir}" does not exist'
                raise FileNotFoundError(error)
        else:
            recode_series(
                os.getcwd(),
                apitokens=apitokens,
                lang=args.lang,
                infolang=infolang,
                sublang=sublang,
                subdir=args.subdir,
                codec=args.codec,
                bit=int(args.bit),
                output=args.output,
                copy=args.copy,
                searchstring=args.searchstring,
            )
    elif args.contentype == "rename":
        folder = os.getcwd()
        series = os.path.basename(folder)
        parentfolder = os.path.realpath(folder).removesuffix(f"/{series}")
        seriesobj, seriesname, year = get_series_from_tvdb(series, apitokens["thetvdb"], lang=infolang, searchstring=args.searchstring)
        if year != "":
            series = f"{seriesname} ({year})"
        for dire in sorted(os.listdir(folder)):
            if os.path.isdir(dire):
                for subdir in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
                    season, name, _ = get_episode(series, subdir, seriesobj)
                    if name is not None:
                        if not os.path.exists(os.path.join(parentfolder, series, season)):
                            os.makedirs(os.path.join(parentfolder, series, season))
                        old = os.path.join(folder, dire, subdir)
                        new = os.path.splitext(os.path.join(parentfolder, series, season, name))[0] + os.path.splitext(subdir)[1].replace("?", "")
                        if old != new:
                            print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                            shutil.move(old, new)
            else:
                season, name, _ = get_episode(series, dire, seriesobj)
                if name is not None:
                    if not os.path.exists(os.path.join(parentfolder, series, season)):
                        os.makedirs(os.path.join(parentfolder, series, season))
                    old = os.path.join(folder, dire)
                    new = os.path.splitext(os.path.join(parentfolder, series, season, name))[0] + os.path.splitext(dire)[1].replace("?", "")
                    if old != new:
                        print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                        shutil.move(old, new)
    elif args.contentype == "changeSeasonType":
        folder = os.getcwd()
        series = os.path.basename(folder)
        parentfolder = os.path.realpath(folder).removesuffix(f"/{series}")
        currseriesobj, destseriesobj, seriesname, year = change_season_type(series, apitokens["thetvdb"], lang=infolang)
        if year != "":
            series = f"{seriesname} ({year})"
        for dire in sorted(os.listdir(folder)):
            if os.path.isdir(dire):
                for subdir in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
                    season, name = change_episode_number(series, subdir, currseriesobj, destseriesobj)
                    if name is not None:
                        if not os.path.exists(os.path.join(parentfolder, series, season)):
                            os.makedirs(os.path.join(parentfolder, series, season))
                        old = os.path.join(folder, dire, subdir)
                        new = os.path.splitext(os.path.join(parentfolder, series, season, name))[0] + os.path.splitext(subdir)[1]
                        if old != new:
                            print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                            shutil.move(old, new)
            else:
                season, name = change_episode_number(series, subdir, currseriesobj, destseriesobj)
                if name is not None and season is not None:
                    if not os.path.exists(os.path.join(parentfolder, series, season)):
                        os.makedirs(os.path.join(parentfolder, series, season))
                    old = os.path.join(folder, dire)
                    new = os.path.splitext(os.path.join(parentfolder, series, season, name))[0] + os.path.splitext(dire)[1]
                    if old != new:
                        print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                        shutil.move(old, new)

    if not args.apis:
        logout(apitokens["opensub"])


if __name__ == "__main__":
    main()
