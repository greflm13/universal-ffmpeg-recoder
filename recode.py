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

from ffprobe import Ffprobe

colorama_init()


ADEFAULT = {"aindex": None, "codec": None, "lang": None, "channels": None}
SDEFAULT = {"sindex": None, "type": None, "lang": None}

ASTREAMS = []
SSTREAMS = []

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

FFMPEG_COMMAND = []
FFMPEG_MAPPING = []
FFMPEG_RECODING = []
FFMPEG_DISPOSITIONS = []

vrecoding = False
arecoding = False
changedefault = False


def get_movie_name(file):
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


def get_series_name(series, file):
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


def recode_series(folder):
    series = os.path.basename(folder)
    for dire in os.listdir(folder):
        for file in os.listdir(os.path.realpath(dire)):
            season, name = get_series_name(series, file)
            if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                os.mkdir(os.path.join(os.path.realpath(folder), season))
            recode(os.path.join(os.path.realpath(dire), file), season + "/" + name)


def video(stream):
    global vindex
    global vrecoding
    if stream.codec_name != "hevc":
        FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
        FFMPEG_RECODING.extend([f"-c:v:{vindex}", "libx265"])
        vrecoding = True
        print(
            f"Converting {Color.GREEN}video{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}hevc{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    else:
        FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
        FFMPEG_RECODING.extend([f"-c:v:{vindex}", "copy"])
        print(
            f"Copying    {Color.GREEN}video{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    vindex += 1


def audio(stream):
    global aindex
    global arecoding
    if (
        stream.tags.language == "eng"
        or stream.tags.language == "ger"
        or stream.tags.language == "deu"
        or stream.tags.language == "jpn"
        or stream.tags.language == "und"
    ):
        if stream.codec_name == "ac3" or stream.codec_name == "eac3" or stream.codec_name == "truehd" or stream.codec_name == "dts":
            FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
            FFMPEG_RECODING.extend([f"-c:a:{aindex}", "copy"])
            print(
                f"Copying    {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
            )
        else:
            FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
            FFMPEG_RECODING.extend([f"-c:a:{aindex}", "ac3"])
            arecoding = True
            stream.codec_name = "ac3"
            print(
                f"Converting {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}ac3{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
            )
        obj = stream.to_dict()
        obj["newindex"] = aindex
        ASTREAMS.append(obj)

        match stream.tags.language:
            case "eng":
                if ADEFAULT["lang"] == "eng" or ADEFAULT["lang"] == "und" or ADEFAULT["lang"] is None:
                    if stream.codec_name != ADEFAULT["codec"] or stream.channels > ADEFAULT["channels"]:
                        match ADEFAULT["codec"]:
                            case "aac":
                                if (
                                    stream.codec_name == "ac3"
                                    or stream.codec_name == "eac3"
                                    or stream.codec_name == "truehd"
                                    or stream.codec_name == "dts"
                                    or stream.channels > ADEFAULT["channels"]
                                ):
                                    ADEFAULT["aindex"] = aindex
                                    ADEFAULT["codec"] = stream.codec_name
                                    ADEFAULT["lang"] = stream.tags.language
                                    ADEFAULT["oindex"] = stream.index
                                    ADEFAULT["channels"] = stream.channels
                            case "ac3":
                                if (
                                    stream.codec_name == "eac3"
                                    or stream.codec_name == "truehd"
                                    or stream.codec_name == "dts"
                                    or stream.channels > ADEFAULT["channels"]
                                ):
                                    ADEFAULT["aindex"] = aindex
                                    ADEFAULT["codec"] = stream.codec_name
                                    ADEFAULT["lang"] = stream.tags.language
                                    ADEFAULT["oindex"] = stream.index
                                    ADEFAULT["channels"] = stream.channels
                            case "eac3":
                                if stream.codec_name == "truehd" or stream.codec_name == "dts" or stream.channels > ADEFAULT["channels"]:
                                    ADEFAULT["aindex"] = aindex
                                    ADEFAULT["codec"] = stream.codec_name
                                    ADEFAULT["lang"] = stream.tags.language
                                    ADEFAULT["oindex"] = stream.index
                                    ADEFAULT["channels"] = stream.channels
                            case "dts":
                                if stream.codec_name == "truehd" or stream.channels > ADEFAULT["channels"]:
                                    ADEFAULT["aindex"] = aindex
                                    ADEFAULT["codec"] = stream.codec_name
                                    ADEFAULT["lang"] = stream.tags.language
                                    ADEFAULT["oindex"] = stream.index
                                    ADEFAULT["channels"] = stream.channels
                            case None:
                                ADEFAULT["aindex"] = aindex
                                ADEFAULT["codec"] = stream.codec_name
                                ADEFAULT["lang"] = stream.tags.language
                                ADEFAULT["oindex"] = stream.index
                                ADEFAULT["channels"] = stream.channels
            case "jpn":
                if ADEFAULT["lang"] != "jpn" or stream.codec_name != ADEFAULT["codec"]:
                    match ADEFAULT["codec"]:
                        case "aac":
                            if (
                                stream.codec_name == "ac3"
                                or stream.codec_name == "eac3"
                                or stream.codec_name == "truehd"
                                or stream.codec_name == "dts"
                                or stream.channels > ADEFAULT["channels"]
                            ):
                                ADEFAULT["aindex"] = aindex
                                ADEFAULT["codec"] = stream.codec_name
                                ADEFAULT["lang"] = stream.tags.language
                                ADEFAULT["channels"] = stream.channels
                        case "ac3":
                            if (
                                stream.codec_name == "eac3"
                                or stream.codec_name == "truehd"
                                or stream.codec_name == "dts"
                                or ADEFAULT["lang"] != "jpn"
                                or stream.channels > ADEFAULT["channels"]
                            ):
                                ADEFAULT["aindex"] = aindex
                                ADEFAULT["codec"] = stream.codec_name
                                ADEFAULT["lang"] = stream.tags.language
                                ADEFAULT["channels"] = stream.channels
                        case "eac3":
                            if stream.codec_name == "truehd" or stream.codec_name == "dts" or stream.channels > ADEFAULT["channels"]:
                                ADEFAULT["aindex"] = aindex
                                ADEFAULT["codec"] = stream.codec_name
                                ADEFAULT["lang"] = stream.tags.language
                                ADEFAULT["channels"] = stream.channels
                        case "dts":
                            if stream.codec_name == "truehd" or stream.channels > ADEFAULT["channels"]:
                                ADEFAULT["aindex"] = aindex
                                ADEFAULT["codec"] = stream.codec_name
                                ADEFAULT["lang"] = stream.tags.language
                                ADEFAULT["channels"] = stream.channels
                        case None:
                            ADEFAULT["aindex"] = aindex
                            ADEFAULT["codec"] = stream.codec_name
                            ADEFAULT["lang"] = stream.tags.language
                            ADEFAULT["channels"] = stream.channels
        aindex += 1


def subtitles(stream):
    global sindex
    global changedefault
    if stream.tags.language == "eng" or stream.tags.language == "ger" or stream.tags.language == "deu" or stream.tags.language == "und":
        if stream.codec_name == "subrip" or stream.codec_name == "hdmv_pgs_subtitle":
            FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
            FFMPEG_RECODING.extend([f"-c:s:{sindex}", "copy"])
            print(
                f"Copying    {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.BLUE}{stream.codec_name}{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
        else:
            FFMPEG_MAPPING.extend(["-map", f"0:{stream.index}"])
            FFMPEG_RECODING.extend([f"-c:s:{sindex}", "srt"])
            print(
                f"Converting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.BLUE}srt{Style.RESET_ALL}, language {Color.BLUE}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
            stream.codec_name = "srt"
        obj = stream.to_dict()
        obj["newindex"] = sindex
        SSTREAMS.append(obj)

        match stream.tags.language:
            case "eng":
                if SDEFAULT["lang"] != "eng":
                    if stream.tags.title and "full" in stream.tags.title.lower():
                        if SDEFAULT["type"] != "full":
                            SDEFAULT["sindex"] = sindex
                            SDEFAULT["type"] = "full"
                            SDEFAULT["lang"] = stream.tags.language
                            changedefault = True
                    elif stream.tags.title and "SDH" in stream.tags.title.lower():
                        if SDEFAULT["type"] != "SDH":
                            SDEFAULT["sindex"] = sindex
                            SDEFAULT["type"] = "SDH"
                            SDEFAULT["lang"] = stream.tags.language
            case "ger" | "deu":
                if SDEFAULT["lang"] == "und" or SDEFAULT["lang"] == "ger" or SDEFAULT["lang"] is None:
                    if stream.tags.title and "full" in stream.tags.title.lower():
                        if SDEFAULT["type"] != "full":
                            SDEFAULT["sindex"] = sindex
                            SDEFAULT["type"] = "full"
                            SDEFAULT["lang"] = stream.tags.language
                    elif stream.tags.title and "SDH" in stream.tags.title.lower():
                        if SDEFAULT["type"] != "SDH":
                            SDEFAULT["sindex"] = sindex
                            SDEFAULT["lang"] = stream.tags.language
        sindex += 1


def recode(file, name=None):
    global vindex
    global aindex
    global sindex
    global vrecoding
    global arecoding
    global changedefault
    vindex = 0
    aindex = 0
    sindex = 0

    FFMPEG_COMMAND.extend(["ffmpeg", "-v", "quiet", "-stats", "-hwaccel", "auto", "-i", os.path.realpath(file)])

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
            video(stream)

        if stream.codec_type == "audio":
            audio(stream)

        if stream.codec_type == "subtitle":
            subtitles(stream)

    if aindex > 0 and ADEFAULT["aindex"] is not None:
        for stream in ASTREAMS:
            if ADEFAULT["aindex"] != stream["newindex"]:
                FFMPEG_DISPOSITIONS.extend([f"-disposition:a:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                FFMPEG_DISPOSITIONS.extend([f"-disposition:a:{ADEFAULT['aindex']}", "default"])
                print(
                    f"Setting    {Color.GREEN}audio{Style.RESET_ALL}    stream {Color.BLUE}a:{ADEFAULT['aindex']}{Style.RESET_ALL} to default"
                )
                changedefault = True
    if sindex > 0 and SDEFAULT["sindex"] is not None:
        for stream in SSTREAMS:
            if SDEFAULT["sindex"] != stream["newindex"]:
                FFMPEG_DISPOSITIONS.extend([f"-disposition:s:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                FFMPEG_DISPOSITIONS.extend([f"-disposition:s:{SDEFAULT['sindex']}", "default"])
                print(
                    f"Setting    {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}s:{SDEFAULT['sindex']}{Style.RESET_ALL} to default"
                )
                changedefault = True

    if ffprobe.format.tags.title and ffprobe.format.tags.title != os.path.splitext(output_file)[0]:
        FFMPEG_COMMAND.extend(["-metadata", f"title={os.path.splitext(output_file)[0]}"])

    FFMPEG_COMMAND.extend(FFMPEG_MAPPING)
    FFMPEG_COMMAND.extend(FFMPEG_RECODING)
    if vrecoding:
        FFMPEG_COMMAND.extend(["-crf", "23", "-preset", "veryslow"])
    if arecoding:
        FFMPEG_COMMAND.extend(["-b:a", "192k", "-ar", "48000"])
    if not vrecoding and not arecoding and not changedefault and file == output_file:
        print(f"{Color.RED}No changes to make! Continuing...")
        return
    FFMPEG_COMMAND.extend(FFMPEG_DISPOSITIONS)
    FFMPEG_COMMAND.extend(["-f", "matroska", "-y", "/tmp/" + os.path.basename(output_file)])
    # print(FFMPEG_COMMAND)

    # Run FFMPEG_COMMAND and print live output
    with Popen(FFMPEG_COMMAND, stdout=PIPE, stderr=STDOUT) as process:
        for c in iter(lambda: process.stdout.read(1), b""):
            sys.stdout.buffer.write(c)
            sys.stdout.flush()
        process.wait()

    # Rename old file
    os.rename(os.path.realpath(file), os.path.realpath(file) + ".old")

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
        exit
    else:
        if os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if os.path.isfile(file):
                    notdir += 1
            if notdir == 0:
                recode_series(sys.argv[1])
                exit
            else:
                for file in os.listdir(sys.argv[1]):
                    recode(sys.argv[1] + "/" + file)
                    exit
        for container in VIDEO_CONTAINERS:
            if sys.argv[1].endswith(container):
                recode(sys.argv[1])
                exit


if __name__ == "__main__":
    main()
