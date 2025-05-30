#!/usr/bin/env python3

import os
import sys
import json
import re
import shutil
import datetime
import tempfile
import urllib.parse

from subprocess import Popen, PIPE, STDOUT

import requests

from colorama import init as colorama_init
from colorama import Fore as Color
from colorama import Style

from modules.ffprobe import Ffprobe, Stream, StreamTags

colorama_init()

# fmt: off
VIDEO_CONTAINERS = [
    ".3g2",".3gp",".amv",".asf",".avi",".drc",".f4a",".f4b",".f4p",".f4v",".flv",".gif",".gifv",".M2TS",
    ".m2v",".m4p",".m4v",".mkv",".mng",".mov",".mp2",".mp4",".mpe",".mpeg",".mpg",".mpv",".MTS",".mxf",
    ".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",".svi",".TS",".viv",".vob",".webm",".wmv",".yuv",
]
# fmt: on

AUDIO_PRIORITY = {"dts": 4, "truehd": 3, "eac3": 2, "ac3": 1}
SUBTITLE_PRIORITY = {"full": 3, "sdh": 2, "none": 1}
if os.path.exists("/usr/lib/libamfrt64.so"):
    AMF = True
else:
    AMF = False


def rename_keys_to_lower(iterable):
    if isinstance(iterable, dict):
        for key in list(iterable.keys()):
            iterable[key.lower()] = iterable.pop(key)
            if isinstance(iterable[key.lower()], dict) or isinstance(iterable[key.lower()], list):
                iterable[key.lower()] = rename_keys_to_lower(iterable[key.lower()])
    elif isinstance(iterable, list):
        for item in iterable:
            item = rename_keys_to_lower(item)
    return iterable


def get_movie_name(file: str, token: str):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(pattern=r"\d{4}", string=file)
            if match:
                comment = None
                date = None
                year: str = match.group()
                movie_name: str = file[: match.start()].replace("_", " ").replace(".", " ").replace("(", "").replace(")", "")
                output_file = f"{movie_name}({year}).mp4"
                response = requests.get(f"https://api4.thetvdb.com/v4/search?query={movie_name}&type=movie&year={year}", timeout=10, headers={"Authorization": f"Bearer {token}"})
                try:
                    ret = response.json()["data"][0]
                    if "overviews" in ret and "eng" in ret["overviews"]:
                        comment = ret["overviews"]["eng"]
                    if "first_air_time" in ret and ret["first_air_time"] != "":
                        date = ret["first_air_time"]
                    metadata = {"comment": comment, "title": ret["extended_title"], "date": date}
                except IndexError:
                    metadata = {"title": f"{movie_name}({year})"}
            else:
                output_file: str = os.path.splitext(file)[0] + ".mp4"
                metadata = {"title": os.path.splitext(file)[0]}
            return output_file, metadata
    return None, None


def get_series_from_tvdb(series: str, token: str) -> list:
    seriesyear = re.search(r"(\(\d{4}\))", series).groups()[0]
    queryseries = urllib.parse.quote(series.removesuffix(seriesyear).strip())
    response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&year={seriesyear.replace('(', '').replace(')', '')}", timeout=10, headers={"Authorization": f"Bearer {token}"})
    seriesid = response.json()["data"][0]["id"].removeprefix("series-")
    response = requests.get(f"https://api4.thetvdb.com/v4/series/{seriesid}/episodes/default/eng?page=0", timeout=10, headers={"Authorization": f"Bearer {token}"})
    returnlst: list = response.json()["data"]["episodes"]
    while response.json()["links"]["next"] is not None:
        response = requests.get(response.json()["links"]["next"], timeout=10, headers={"Authorization": f"Bearer {token}"})
        returnlst.extend(response.json()["data"]["episodes"])
    return returnlst


def get_series_name(series: str, file: str, seriesobj: list):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(r"[Ss](\d{1,4})\s?(([Ee]\d{1,4})*)", file)
            if match:
                seasonnum = match.groups()[0]
                episodes = match.groups()[1].replace("e", "E").split("E")
                episodes.remove("")
                ep = ""
                titles: list[str] = []
                comments: list[str] = [""]
                date = None
                for episode in episodes:
                    ep = ep + "E" + episode.rjust(2, "0")
                    for epi in seriesobj:
                        if epi["seasonNumber"] == int(match.groups()[0]) and epi["number"] == int(episode):
                            if isinstance(epi["name"], str):
                                titles.append(epi["name"])
                            else:
                                titles.append("")
                            if isinstance(epi["overview"], str):
                                comments.append(epi["overview"].replace("\n", "").strip())
                            date = epi["aired"]
                if len(titles) == 2 and re.sub(r"\(\d+\)", "", titles[0]).strip() == re.sub(r"\(\d+\)", "", titles[1]).strip():
                    title = re.sub(r"\(\d+\)", "", titles[0]).strip()
                else:
                    title = " + ".join(titles)
                if title != "":
                    name = f"{series} - S{seasonnum.rjust(2, '0')}{ep} - {title}.mp4"
                else:
                    name = f"{series} - S{seasonnum.rjust(2, '0')}{ep}.mp4"
                season = f"Season {seasonnum.rjust(2, '0')}"
                try:
                    comment = " ".join(comments)
                except TypeError:
                    comment = None
                metadata = {"episode_id": ", ".join(epi.removeprefix("0") for epi in episodes), "season_number": seasonnum.removeprefix("0"), "show": series, "comment": comment, "title": name.removesuffix(".mp4"), "date": date}
                return season, name, metadata
    return None, None, None


def recode_series(folder: str, token: str):
    series = os.path.basename(folder)
    seriesobj = get_series_from_tvdb(series, token)
    for dire in sorted(os.listdir(folder)):
        for file in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
            season, name, metadata = get_series_name(series, file, seriesobj)
            if name is not None:
                if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                    os.mkdir(os.path.join(os.path.realpath(folder), season))
                recode(os.path.join(os.path.realpath(os.path.join(folder, dire)), file), os.path.join(folder, season, name), metadata)


def recode_all_series(folder: str, token: str):
    for dire in sorted(os.listdir(folder)):
        recode_series(os.path.join(folder, dire), token)


def video(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, vrecoding: bool, vindex: int, printlines: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.codec_name != "h264" or stream.pix_fmt != "yuv420p" and not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        if AMF:
            ffmpeg_recoding.extend([f"-c:v:{vindex}", "h264_amf"])
        else:
            ffmpeg_recoding.extend([f"-c:v:{vindex}", "libx264"])
        vrecoding = True
        printlines.append(
            f"Converting {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}h264{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    elif not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    vindex += 1
    return vrecoding, vindex


def recode_audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list, printlines: list):
    if stream.codec_name in ["aac"]:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "aac"])
        arecoding = True
        stream.codec_name = "aac"
        printlines.append(
            f"Converting {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}aac{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    obj = stream.to_dict()
    obj["newindex"] = aindex
    astreams.append(obj)

    # if stream.tags.language in ["eng", "und", "jpn", None]:
    #     update_audio_default(adefault, stream, aindex)
    return arecoding


def update_audio_default(adefault: dict, stream: Stream, aindex: int):
    if (AUDIO_PRIORITY.get(stream.codec_name, 0) > AUDIO_PRIORITY.get(adefault["codec"], 0)) or (AUDIO_PRIORITY.get(stream.codec_name, 0) == AUDIO_PRIORITY.get(adefault["codec"], 0) and stream.channels > adefault["channels"]):
        adefault.update(
            {
                "aindex": aindex,
                "codec": stream.codec_name,
                "lang": stream.tags.language,
                "oindex": stream.index,
                "channels": stream.channels,
            }
        )


def audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list, printlines: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "jpn", "und", None]:
        arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines)
        aindex += 1
    return arecoding, aindex


def subtitles(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, sindex: int, sdefault: dict, sstreams: list, printlines: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "und", None]:
        if stream.codec_name in ["subrip", "hdmv_pgs_subtitle", "ass", "dvd_subtitle"]:
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "copy"])
            printlines.append(
                f"Copying {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
        else:
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "srt"])
            printlines.append(
                f"Converting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}srt{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
            stream.codec_name = "srt"
        obj = stream.to_dict()
        obj["newindex"] = sindex
        sstreams.append(obj)
        update_subtitle_default(sdefault, stream, sindex)
        sindex += 1
    return sindex


def update_subtitle_default(sdefault: dict, stream: Stream, sindex: int):
    subtitle_type = "none"
    if stream.tags.title:
        title_lower = stream.tags.title.lower()
        if "full" in title_lower:
            subtitle_type = "full"
        elif "sdh" in title_lower:
            subtitle_type = "sdh"
    if SUBTITLE_PRIORITY.get(subtitle_type, 0) > SUBTITLE_PRIORITY.get(sdefault["type"], 0):
        sdefault.update({"lang": stream.tags.language, "oindex": stream.index, "sindex": sindex, "type": subtitle_type})


def recode(file: str, path: str | None = None, metadata: dict | None = None, token: str | None = None):

    printlines = []

    adefault = {"aindex": None, "codec": None, "lang": None, "channels": None}
    sdefault = {"sindex": None, "type": None, "lang": None}

    astreams = []
    sstreams = []

    ffmpeg_command = []
    ffmpeg_mapping = []
    ffmpeg_recoding = []
    ffmpeg_dispositions = []
    ffmpeg_metadata = []

    vindex = 0
    aindex = 0
    sindex = 0
    tindex = 0

    vrecoding = False
    arecoding = False
    changedefault = False
    changemetadata = False

    ffmpeg_command.extend(["ffmpeg", "-v", "error", "-stats", "-hwaccel", "auto", "-strict", "-2", "-i", os.path.realpath(file)])

    if path is None:
        output_file, metadata = get_movie_name(file, token)
        if output_file is None:
            return
    else:
        output_file = path

    if metadata is None:
        metadata = {}
        metadata["title"] = os.path.basename(os.path.splitext(output_file)[0])

    printlines.append(f"{Color.RED}Recoding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(file)}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")

    p = Popen(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-output_format", "json", os.path.realpath(file), "-strict", "-2"],
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    output = json.loads(out.decode("utf-8"))
    ffprobedict = rename_keys_to_lower(output)
    try:
        ffprobe = Ffprobe.from_dict(ffprobedict)
    except Exception as e:
        print(f"Error: {err.decode("utf-8")} {e}")
        raise RuntimeError from e
    if ffprobe.streams is None:
        print(f"Error: {file} has no streams")
        return

    printlines.append(f"{Color.RED}Streams{Style.RESET_ALL}:")
    for stream in ffprobe.streams:
        if stream.tags is None:
            stream.tags = StreamTags.from_dict({"title": None, "language": None})
        if stream.disposition.default:
            disposition = "default"
        else:
            disposition = "none"
        if stream.codec_type != "attachment":
            printlines.append(
                f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
            )
        elif stream.codec_type == "attachment":
            printlines.append(
                f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.filename} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
            )

    for stream in ffprobe.streams:
        if stream.codec_type == "video" and not stream.disposition.attached_pic:
            vrecoding, vindex = video(stream, ffmpeg_mapping, ffmpeg_recoding, vrecoding, vindex, printlines)

    for stream in ffprobe.streams:
        if stream.codec_type == "audio":
            arecoding, aindex = audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines)

    if aindex == 0:
        for stream in ffprobe.streams:
            if stream.codec_type == "audio":
                arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines)
                aindex += 1

    for stream in ffprobe.streams:
        if stream.codec_type == "subtitle":
            sindex = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams, printlines)

    for stream in ffprobe.streams:
        if stream.codec_type == "attachment":
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            printlines.append(
                f"Copying {Color.GREEN}attachment{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.filename}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}t:{tindex}{Style.RESET_ALL} in output file"
            )
            tindex += 1

    # for stream in ffprobe.streams:
    #     if stream.codec_type == "video" and stream.disposition.attached_pic:
    #         ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
    #         ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
    #         ffmpeg_dispositions.extend([f"-disposition:v:{vindex}", "attached_pic"])
    #         printlines.append(
    #             f"Copying {Color.GREEN}attached picture{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
    #         )
    #         vindex += 1

    if aindex > 0 and adefault["aindex"] is not None:
        for stream in astreams:
            if adefault["aindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:a:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:a:{adefault['aindex']}", "default"])
                printlines.append(f"Setting {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}a:{adefault['aindex']}{Style.RESET_ALL} to default")
                changedefault = True
    if sindex > 0 and sdefault["sindex"] is not None:
        for stream in sstreams:
            if sdefault["sindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:s:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:s:{sdefault['sindex']}", "default"])
                printlines.append(f"Setting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}s:{sdefault['sindex']}{Style.RESET_ALL} to default")
                changedefault = True

    try:
        format_tags = ffprobe.format.tags.to_dict()
    except AttributeError:
        format_tags = {}

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
    if os.path.realpath(file) != os.path.realpath(output_file) and not vrecoding and not arecoding and not changedefault and not changemetadata and os.path.splitext(file)[1] == os.path.splitext(output_file)[1]:
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}{file}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
        shutil.move(os.path.realpath(file), os.path.realpath(output_file))
        return

    fd, tmpfile = tempfile.mkstemp(suffix=".mp4")

    ffmpeg_command.extend(ffmpeg_mapping)
    ffmpeg_command.extend(ffmpeg_recoding)
    if vrecoding:
        if AMF:
            ffmpeg_command.extend(["-rc", "cqp", "-qp_i", "23", "-qp_p", "23", "-quality", "quality", "-pixel_format", "yuv420p"])
        else:
            ffmpeg_command.extend(["-crf", "23", "-preset", "veryslow"])
    if arecoding:
        ffmpeg_command.extend(["-b:a", "192k", "-ar", "48000"])
    ffmpeg_command.extend(ffmpeg_dispositions)
    ffmpeg_command.extend(ffmpeg_metadata)
    ffmpeg_command.extend(["-f", "matroska", "-y", tmpfile])
    for line in printlines:
        print(line)
    print(" ".join(ffmpeg_command))

    try:
        timestart = datetime.datetime.now()
        print(f"Recoding started at {Color.GREEN}{timestart.isoformat()}{Style.RESET_ALL}")

        # Run ffmpeg_command and print live output
        with Popen(ffmpeg_command, stdout=PIPE, stderr=STDOUT) as process:
            for c in iter(lambda: process.stdout.read(1), b""):
                sys.stdout.buffer.write(c)
                sys.stdout.flush()
            process.wait()
        timestop = datetime.datetime.now()
        print(f"Recoding finished at {Color.GREEN}{timestop.isoformat()}{Style.RESET_ALL}")
        print(f"Recoding took {Color.GREEN}{timestop - timestart}{Style.RESET_ALL}")

        # Rename old file
        # shutil.move(os.path.realpath(file), os.path.realpath(file) + ".old")

        # Move tempfile to output_file
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}tempfile{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
        shutil.move(tmpfile, os.path.realpath(output_file))
        os.chmod(output_file, 0o644)
    finally:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
    print(f"{Color.GREEN}Done!{Style.RESET_ALL}")


def api_login() -> str:
    with open(os.path.join(os.path.dirname(__file__), "apikey"), "r", encoding="utf-8") as f:
        apikey = f.read()
        f.close()
    response = requests.post("https://api4.thetvdb.com/v4/login", json={"apikey": apikey}, timeout=10, headers={"Content-Type": "application/json"})

    return response.json()["data"]["token"]


def main():
    token = api_login()
    notdir = 0
    if len(sys.argv) < 2:
        for file in sorted(os.listdir(os.getcwd())):
            if os.path.isfile(file):
                notdir += 1
        if notdir == 0:
            for folder in sorted(os.listdir(os.getcwd())):
                for file in sorted(os.listdir(folder)):
                    if os.path.isfile(os.path.join(folder, file)):
                        notdir += 1
            if notdir == 0:
                recode_all_series(os.getcwd(), token)
            else:
                recode_series(os.getcwd(), token)

        else:
            for file in sorted(os.listdir(os.getcwd())):
                try:
                    recode(file, token=token)
                except RuntimeError:
                    continue
    else:
        if os.path.isdir(sys.argv[1]):
            for file in sorted(os.listdir(sys.argv[1])):
                if os.path.isfile(os.path.join(sys.argv[1], file)):
                    notdir += 1
            if notdir == 0:
                recode_series(sys.argv[1], token)
            else:
                for file in sorted(os.listdir(sys.argv[1])):
                    recode(sys.argv[1] + "/" + file, token=token)
        elif sys.argv[1] == "rename":
            folder = os.getcwd()
            series = os.path.basename(folder)
            seriesobj = get_series_from_tvdb(series, token)
            for dire in sorted(os.listdir(folder)):
                if not os.path.isfile(os.path.join(folder, dire)):
                    for file in sorted(os.listdir(os.path.realpath(dire))):
                        try:
                            season, name, metadata = get_series_name(series, file, seriesobj)
                        except RuntimeError:
                            continue
                        if season is not None:
                            old = os.path.join(folder, dire, file)
                            new = os.path.splitext(os.path.join(folder, season, name))[0] + os.path.splitext(file)[1]
                            if old != new:
                                if not os.path.exists(os.path.join(folder, season)):
                                    os.mkdir(os.path.join(folder, season))
                                print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                                shutil.move(old, new)
        for container in VIDEO_CONTAINERS:
            if sys.argv[1].endswith(container):
                recode(sys.argv[1], token=token)


if __name__ == "__main__":
    main()
