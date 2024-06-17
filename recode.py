#!/usr/bin/env python3

import os
import sys
import json
import re
import shutil

from subprocess import Popen, PIPE, STDOUT

from colorama import init as colorama_init
from colorama import Fore as Color
from colorama import Style

from ffprobe import Ffprobe, Stream, StreamTags

colorama_init()


VIDEO_CONTAINERS = [
    ".3g2",
    ".3gp",
    ".amv",
    ".asf",
    ".avi",
    ".drc",
    ".f4a",
    ".f4b",
    ".f4p",
    ".f4v",
    ".flv",
    ".gif",
    ".gifv",
    ".M2TS",
    ".m2v",
    ".m4p",
    ".m4v",
    ".mkv",
    ".mng",
    ".mov",
    ".mp2",
    ".mp4",
    ".mpe",
    ".mpeg",
    ".mpg",
    ".mpv",
    ".MTS",
    ".mxf",
    ".nsv",
    ".ogg",
    ".ogv",
    ".qt",
    ".rm",
    ".rmvb",
    ".roq",
    ".svi",
    ".TS",
    ".viv",
    ".vob",
    ".webm",
    ".wmv",
    ".yuv",
]


def get_movie_name(file: str):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(r"\d{4}", file)
            if match:
                year = match.group()
                movie_name = file[: match.start()].replace("_", " ").replace(".", " ").replace("(", "").replace(")", "")
                output_file = f"{movie_name}({year}).mkv"
            else:
                output_file = os.path.splitext(file)[0] + ".mkv"
        else:
            continue
    return output_file


def get_series_name(series: str, file: str):
    match = re.search(r"[Ss](\d{1,4})(([Ee]\d{1,4})*)", file)
    if match:
        episodes = match.groups()[1].replace("e", "E").split("E")
        ep = ""
        for episode in episodes:
            if episode != "":
                ep = ep + "E" + episode.rjust(2, "0")
        name = series + " - S" + match.groups()[0].rjust(2, "0") + ep + ".mkv"
        season = "Season " + match.groups()[0].rjust(2, "0")
    return season, name


def recode_series(folder: str):
    series = os.path.basename(folder)
    for dire in os.listdir(folder):
        for file in os.listdir(os.path.realpath(dire)):
            season, name = get_series_name(series, file)
            if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                os.mkdir(os.path.join(os.path.realpath(folder), season))
            recode(os.path.join(os.path.realpath(dire), file), season + "/" + name)


def video(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, vrecoding: bool, vindex: int):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.codec_name != "hevc":
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "libx265"])
        vrecoding = True
        print(
            f"Converting {Color.GREEN}video{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}hevc{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
        print(
            f"Copying    {Color.GREEN}video{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    vindex += 1
    return vrecoding, vindex


def recode_audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list):
    if stream.codec_name == "ac3" or stream.codec_name == "eac3" or stream.codec_name == "truehd" or stream.codec_name == "dts":
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "copy"])
        print(
            f"Copying    {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "ac3"])
        arecoding = True
        stream.codec_name = "ac3"
        print(
            f"Converting {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}ac3{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    obj = stream.to_dict()
    obj["newindex"] = aindex
    astreams.append(obj)

    match stream.tags.language:
        case "eng":
            if adefault["lang"] == "eng" or adefault["lang"] == "und" or adefault["lang"] is None:
                if stream.codec_name != adefault["codec"] or stream.channels > adefault["channels"]:
                    match adefault["codec"]:
                        case "aac":
                            if (
                                stream.codec_name == "ac3"
                                or stream.codec_name == "eac3"
                                or stream.codec_name == "truehd"
                                or stream.codec_name == "dts"
                                or stream.channels > adefault["channels"]
                            ):
                                adefault["aindex"] = aindex
                                adefault["codec"] = stream.codec_name
                                adefault["lang"] = stream.tags.language
                                adefault["oindex"] = stream.index
                                adefault["channels"] = stream.channels
                        case "ac3":
                            if (
                                stream.codec_name == "eac3"
                                or stream.codec_name == "truehd"
                                or stream.codec_name == "dts"
                                or stream.channels > adefault["channels"]
                            ):
                                adefault["aindex"] = aindex
                                adefault["codec"] = stream.codec_name
                                adefault["lang"] = stream.tags.language
                                adefault["oindex"] = stream.index
                                adefault["channels"] = stream.channels
                        case "eac3":
                            if stream.codec_name == "truehd" or stream.codec_name == "dts" or stream.channels > adefault["channels"]:
                                adefault["aindex"] = aindex
                                adefault["codec"] = stream.codec_name
                                adefault["lang"] = stream.tags.language
                                adefault["oindex"] = stream.index
                                adefault["channels"] = stream.channels
                        case "dts":
                            if stream.codec_name == "truehd" or stream.channels > adefault["channels"]:
                                adefault["aindex"] = aindex
                                adefault["codec"] = stream.codec_name
                                adefault["lang"] = stream.tags.language
                                adefault["oindex"] = stream.index
                                adefault["channels"] = stream.channels
                        case None:
                            adefault["aindex"] = aindex
                            adefault["codec"] = stream.codec_name
                            adefault["lang"] = stream.tags.language
                            adefault["oindex"] = stream.index
                            adefault["channels"] = stream.channels
        case "jpn":
            if adefault["lang"] != "jpn" or stream.codec_name != adefault["codec"]:
                match adefault["codec"]:
                    case "aac":
                        if (
                            stream.codec_name == "ac3"
                            or stream.codec_name == "eac3"
                            or stream.codec_name == "truehd"
                            or stream.codec_name == "dts"
                            or stream.channels > adefault["channels"]
                        ):
                            adefault["aindex"] = aindex
                            adefault["codec"] = stream.codec_name
                            adefault["lang"] = stream.tags.language
                            adefault["channels"] = stream.channels
                    case "ac3":
                        if (
                            stream.codec_name == "eac3"
                            or stream.codec_name == "truehd"
                            or stream.codec_name == "dts"
                            or adefault["lang"] != "jpn"
                            or stream.channels > adefault["channels"]
                        ):
                            adefault["aindex"] = aindex
                            adefault["codec"] = stream.codec_name
                            adefault["lang"] = stream.tags.language
                            adefault["channels"] = stream.channels
                    case "eac3":
                        if stream.codec_name == "truehd" or stream.codec_name == "dts" or stream.channels > adefault["channels"]:
                            adefault["aindex"] = aindex
                            adefault["codec"] = stream.codec_name
                            adefault["lang"] = stream.tags.language
                            adefault["channels"] = stream.channels
                    case "dts":
                        if stream.codec_name == "truehd" or stream.channels > adefault["channels"]:
                            adefault["aindex"] = aindex
                            adefault["codec"] = stream.codec_name
                            adefault["lang"] = stream.tags.language
                            adefault["channels"] = stream.channels
                    case None:
                        adefault["aindex"] = aindex
                        adefault["codec"] = stream.codec_name
                        adefault["lang"] = stream.tags.language
                        adefault["channels"] = stream.channels
    return arecoding


def audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if (
        stream.tags.language == "eng"
        or stream.tags.language == "ger"
        or stream.tags.language == "deu"
        or stream.tags.language == "jpn"
        or stream.tags.language == "und"
        or stream.tags.language is None
    ):
        arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams)
        aindex += 1
    return arecoding, aindex


def subtitles(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, sindex: int, sdefault: dict, sstreams: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language == "eng" or stream.tags.language == "ger" or stream.tags.language == "deu" or stream.tags.language == "und":
        if stream.codec_name == "subrip" or stream.codec_name == "hdmv_pgs_subtitle":
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "copy"])
            print(
                f"Copying    {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
        else:
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "srt"])
            print(
                f"Converting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}srt{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
            stream.codec_name = "srt"
        obj = stream.to_dict()
        obj["newindex"] = sindex
        sstreams.append(obj)

        match stream.tags.language:
            case "eng":
                if sdefault["lang"] != "eng":
                    if stream.tags.title and "full" in stream.tags.title.lower():
                        if sdefault["type"] != "full":
                            sdefault["sindex"] = sindex
                            sdefault["type"] = "full"
                            sdefault["lang"] = stream.tags.language
                    elif stream.tags.title and "sdh" in stream.tags.title.lower():
                        if sdefault["type"] != "sdh":
                            sdefault["sindex"] = sindex
                            sdefault["type"] = "sdh"
                            sdefault["lang"] = stream.tags.language
                    elif sdefault["type"] is None:
                        sdefault["sindex"] = sindex
                        sdefault["type"] = "default"
                        sdefault["lang"] = stream.tags.language
            case "ger" | "deu":
                if sdefault["lang"] == "und" or sdefault["lang"] == "ger" or sdefault["lang"] is None:
                    if stream.tags.title and "full" in stream.tags.title.lower():
                        if sdefault["type"] != "full":
                            sdefault["sindex"] = sindex
                            sdefault["type"] = "full"
                            sdefault["lang"] = stream.tags.language
                    elif stream.tags.title and "sdh" in stream.tags.title.lower():
                        if sdefault["type"] != "sdh":
                            sdefault["sindex"] = sindex
                            sdefault["lang"] = stream.tags.language
                    elif sdefault["type"] is None:
                        sdefault["sindex"] = sindex
                        sdefault["type"] = "default"
                        sdefault["lang"] = stream.tags.language
        sindex += 1
    return sindex


def recode(file: str, name: str | None = None):

    adefault = {"aindex": None, "codec": None, "lang": None, "channels": None}
    sdefault = {"sindex": None, "type": None, "lang": None}

    astreams = []
    sstreams = []

    ffmpeg_command = []
    ffmpeg_mapping = []
    ffmpeg_recoding = []
    ffmpeg_dispositions = []

    vindex = 0
    aindex = 0
    sindex = 0

    vrecoding = False
    arecoding = False
    changedefault = False

    # ffmpeg_command.extend(["ffmpeg", "-hwaccel", "auto", "-i", os.path.realpath(file)])
    ffmpeg_command.extend(["ffmpeg", "-v", "quiet", "-stats", "-hwaccel", "auto", "-i", os.path.realpath(file)])

    if name is None:
        output_file = get_movie_name(file)
    else:
        output_file = name

    print(f"{Color.RED}Recoding{Style.RESET_ALL} {Color.YELLOW}{file}{Style.RESET_ALL} to {Color.MAGENTA}{output_file}{Style.RESET_ALL}")

    p = Popen(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-output_format", "json", os.path.realpath(file)],
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    try:
        ffprobe = Ffprobe.from_dict(json.loads(out.decode("utf-8")))
    except:
        print(f"Error: {err}")
        raise
    if ffprobe.streams is None:
        print(f"Error: {file} has no streams")
        return

    for stream in ffprobe.streams:
        if stream.codec_type == "video":
            vrecoding, vindex = video(stream, ffmpeg_mapping, ffmpeg_recoding, vrecoding, vindex)

        if stream.codec_type == "audio":
            arecoding, aindex = audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams)

    if aindex == 0:
        for stream in ffprobe.streams:
            if stream.codec_type == "audio":
                arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams)
                aindex += 1

    for stream in ffprobe.streams:
        if stream.codec_type == "subtitle":
            sindex = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams)

    if aindex > 0 and adefault["aindex"] is not None:
        for stream in astreams:
            if adefault["aindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:a:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:a:{adefault['aindex']}", "default"])
                print(
                    f"Setting    {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}a:{adefault['aindex']}{Style.RESET_ALL} to default"
                )
                changedefault = True
    if sindex > 0 and sdefault["sindex"] is not None:
        for stream in sstreams:
            if sdefault["sindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:s:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:s:{sdefault['sindex']}", "default"])
                print(
                    f"Setting    {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}s:{sdefault['sindex']}{Style.RESET_ALL} to default"
                )
                changedefault = True

    if ffprobe.format.tags.title and ffprobe.format.tags.title != os.path.splitext(output_file)[0] or ffprobe.format.tags.title is None:
        ffmpeg_command.extend(["-metadata", f"title={os.path.splitext(output_file)[0]}"])

    ffmpeg_command.extend(ffmpeg_mapping)
    ffmpeg_command.extend(ffmpeg_recoding)
    if vrecoding:
        ffmpeg_command.extend(["-crf", "23", "-preset", "veryslow"])
    if arecoding:
        ffmpeg_command.extend(["-b:a", "192k", "-ar", "48000"])
    if not vrecoding and not arecoding and not changedefault and file == output_file:
        print(f"{Color.RED}No changes to make! Continuing...")
        return
    ffmpeg_command.extend(ffmpeg_dispositions)
    ffmpeg_command.extend(["-f", "matroska", "-y", "/tmp/" + os.path.basename(output_file)])
    # print(ffmpeg_command)

    # Run ffmpeg_command and print live output
    with Popen(ffmpeg_command, stdout=PIPE, stderr=STDOUT) as process:
        for c in iter(lambda: process.stdout.read(1), b""):
            sys.stdout.buffer.write(c)
            sys.stdout.flush()
        process.wait()

    # Rename old file
    shutil.move(os.path.realpath(file), os.path.realpath(file) + ".old")

    # Move tempfile to output_file
    print(
        f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}tempfile{Style.RESET_ALL} file to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}"
    )
    shutil.move("/tmp/" + os.path.basename(output_file), os.path.realpath(output_file))


def main():
    notdir = 0
    if len(sys.argv) < 2:
        for file in os.listdir(os.getcwd()):
            if os.path.isfile(file):
                notdir += 1
        if notdir == 0:
            recode_series(os.getcwd())
        else:
            for file in os.listdir(os.getcwd()):
                try:
                    recode(file)
                except:
                    continue
    else:
        if os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if os.path.isfile(file):
                    notdir += 1
            if notdir == 0:
                recode_series(sys.argv[1])
            else:
                for file in os.listdir(sys.argv[1]):
                    recode(sys.argv[1] + "/" + file)
        elif sys.argv[1] == "rename":
            folder = os.getcwd()
            series = os.path.basename(folder)
            for dire in os.listdir(folder):
                for file in os.listdir(os.path.realpath(dire)):
                    season, name = get_series_name(series, file)
                    if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                        os.mkdir(os.path.join(os.path.realpath(folder), season))
                    shutil.move(os.path.realpath(file), season + "/" + name)
        for container in VIDEO_CONTAINERS:
            if sys.argv[1].endswith(container):
                recode(sys.argv[1])


if __name__ == "__main__":
    main()
