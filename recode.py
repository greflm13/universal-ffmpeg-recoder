#!/usr/bin/env python3

import os
import sys
import json
import re
import shutil
import datetime

from subprocess import Popen, PIPE, STDOUT

from colorama import init as colorama_init
from colorama import Fore as Color
from colorama import Style

from ffprobe import Ffprobe, Stream, StreamTags

colorama_init()

# fmt: off
VIDEO_CONTAINERS = [
    ".3g2",".3gp",".amv",".asf",".avi",".drc",".f4a",".f4b",".f4p",".f4v",".flv",".gif",".gifv",".M2TS",
    ".m2v",".m4p",".m4v",".mkv",".mng",".mov",".mp2",".mp4",".mpe",".mpeg",".mpg",".mpv",".MTS",".mxf",
    ".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",".svi",".TS",".viv",".vob",".webm",".wmv",".yuv",
]
# fmt: on

AUDIO_PRIORITY = {"dts": 4, "truehd": 3, "eac3": 2, "ac3": 1}
SUBTITLE_PRIORITY = {"full": 3, "sdh": 2, None: 1}


def get_movie_name(file: str):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(pattern=r"\d{4}", string=file)
            if match:
                year: str = match.group()
                movie_name: str = file[: match.start()].replace("_", " ").replace(".", " ").replace("(", "").replace(")", "")
                output_file = f"{movie_name}({year}).mkv"
            else:
                output_file: str = os.path.splitext(file)[0] + ".mkv"
    return output_file


def get_series_name(series: str, file: str):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(r"[Ss](\d{1,4})\s?(([Ee]\d{1,4})*)", file)
            if match:
                episodes = match.groups()[1].replace("e", "E").split("E")
                ep = ""
                for episode in episodes:
                    if episode != "":
                        ep = ep + "E" + episode.rjust(2, "0")
                name = series + " - S" + match.groups()[0].rjust(2, "0") + ep + ".mkv"
                season = "Season " + match.groups()[0].rjust(2, "0")
            return season, name
    return None, None


def recode_series(folder: str):
    series = os.path.basename(folder)
    for dire in os.listdir(folder):
        for file in os.listdir(os.path.realpath(os.path.join(folder, dire))):
            season, name = get_series_name(series, file)
            if name is not None:
                if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                    os.mkdir(os.path.join(os.path.realpath(folder), season))
                recode(os.path.join(os.path.realpath(os.path.join(folder, dire)), file), os.path.join(folder, season, name))


def recode_all_series(folder: str):
    for dire in os.listdir(folder):
        recode_series(os.path.join(folder, dire))


def video(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, vrecoding: bool, vindex: int):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.codec_name != "hevc" and stream.disposition.attached_pic == 0:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "libx265"])
        vrecoding = True
        print(f"Converting {Color.GREEN}video{Style.RESET_ALL}      stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}hevc{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file")
    elif stream.disposition.attached_pic == 0:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
        print(f"Copying    {Color.GREEN}video{Style.RESET_ALL}      stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file")
    vindex += 1
    return vrecoding, vindex


def recode_audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list):
    if stream.codec_name in ["ac3", "eac3", "truehd", "dts"]:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "copy"])
        print(f"Copying    {Color.GREEN}audio{Style.RESET_ALL}      stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file")
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "ac3"])
        arecoding = True
        stream.codec_name = "ac3"
        print(f"Converting {Color.GREEN}audio{Style.RESET_ALL}      stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}ac3{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file")
    obj = stream.to_dict()
    obj["newindex"] = aindex
    astreams.append(obj)

    if stream.tags.language in ["eng", "und", "jpn", None]:
        update_audio_default(adefault, stream, aindex)
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


def audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "jpn", "und", None]:
        arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams)
        aindex += 1
    return arecoding, aindex


def subtitles(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, sindex: int, sdefault: dict, sstreams: list):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "und", None]:
        if stream.codec_name in ["subrip", "hdmv_pgs_subtitle", "ass"]:
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "copy"])
            print(f"Copying    {Color.GREEN}subtitle{Style.RESET_ALL}   stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file")
        else:
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "srt"])
            print(f"Converting {Color.GREEN}subtitle{Style.RESET_ALL}   stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}srt{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file")
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


def recode(file: str, path: str | None = None):

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
    tindex = 0

    vrecoding = False
    arecoding = False
    changedefault = False

    ffmpeg_command.extend(["ffmpeg", "-v", "quiet", "-stats", "-hwaccel", "auto", "-i", os.path.realpath(file)])

    if path is None:
        output_file = get_movie_name(file)
    else:
        output_file = path

    print(f"{Color.RED}Recoding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(file)}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")

    p = Popen(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-output_format", "json", os.path.realpath(file)],
        stdout=PIPE,
        stderr=PIPE,
    )
    out, err = p.communicate()
    try:
        ffprobe = Ffprobe.from_dict(json.loads(out.decode("utf-8")))
    except Exception as err:
        print(f"Error: {err}")
        raise RuntimeError from err
    if ffprobe.streams is None:
        print(f"Error: {file} has no streams")
        return

    print(f"{Color.RED}Streams{Style.RESET_ALL}:")
    for stream in ffprobe.streams:
        if stream.tags is None:
            stream.tags = StreamTags.from_dict({"title": None, "language": None})
        if stream.disposition.default:
            disposition = "default"
        else:
            disposition = "none"
        print(f"{Color.BLUE}0:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}")

    for stream in ffprobe.streams:
        if stream.codec_type == "video":
            vrecoding, vindex = video(stream, ffmpeg_mapping, ffmpeg_recoding, vrecoding, vindex)

    for stream in ffprobe.streams:
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

    for stream in ffprobe.streams:
        if stream.codec_type == "attachment":
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            print(f"Copying    {Color.GREEN}attachment{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.filename}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}t:{tindex}{Style.RESET_ALL} in output file")
            tindex += 1

    if aindex > 0 and adefault["aindex"] is not None:
        for stream in astreams:
            if adefault["aindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:a:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:a:{adefault['aindex']}", "default"])
                print(f"Setting    {Color.GREEN}audio{Style.RESET_ALL}      stream {Color.BLUE}a:{adefault['aindex']}{Style.RESET_ALL} to default")
                changedefault = True
    if sindex > 0 and sdefault["sindex"] is not None:
        for stream in sstreams:
            if sdefault["sindex"] != stream["newindex"]:
                ffmpeg_dispositions.extend([f"-disposition:s:{stream['newindex']}", "none"])
            elif stream["disposition"]["default"] == 0:
                ffmpeg_dispositions.extend([f"-disposition:s:{sdefault['sindex']}", "default"])
                print(f"Setting    {Color.GREEN}subtitle{Style.RESET_ALL}   stream {Color.BLUE}s:{sdefault['sindex']}{Style.RESET_ALL} to default")
                changedefault = True

    if ffprobe.format.tags.title and ffprobe.format.tags.title != os.path.basename(os.path.splitext(output_file)[0]) or ffprobe.format.tags.title is None:
        ffmpeg_command.extend(["-metadata", f"title={os.path.basename(os.path.splitext(output_file)[0])}"])
        print(f"{Color.RED}Changing {Color.BLUE} title{Style.RESET_ALL} from {Color.CYAN}{ffprobe.format.tags.title}{Style.RESET_ALL} to {Color.CYAN}{os.path.basename(os.path.splitext(output_file)[0])}{Style.RESET_ALL}")
        changedefault = True

    ffmpeg_command.extend(ffmpeg_mapping)
    ffmpeg_command.extend(ffmpeg_recoding)
    if vrecoding:
        ffmpeg_command.extend(["-crf", "23", "-preset", "veryslow"])
    if arecoding:
        ffmpeg_command.extend(["-b:a", "192k", "-ar", "48000"])
    if not vrecoding and not arecoding and not changedefault and os.path.realpath(file) == os.path.realpath(output_file):
        print(f"{Color.RED}No changes to make! Continuing...{Style.RESET_ALL}")
        return
    ffmpeg_command.extend(ffmpeg_dispositions)
    ffmpeg_command.extend(["-f", "matroska", "-y", "/tmp/" + os.path.basename(output_file)])
    # print(ffmpeg_command)

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
    print(f"{Color.RED}Recoding took {Style.RESET_ALL}{timestop - timestart}{Style.RESET_ALL}")

    # Rename old file
    shutil.move(os.path.realpath(file), os.path.realpath(file) + ".old")

    # Move tempfile to output_file
    print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}tempfile{Style.RESET_ALL} file to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
    shutil.move("/tmp/" + os.path.basename(output_file), os.path.realpath(output_file))


def main():
    notdir = 0
    if len(sys.argv) < 2:
        for file in os.listdir(os.getcwd()):
            if os.path.isfile(file):
                notdir += 1
        if notdir == 0:
            for folder in os.listdir(os.getcwd()):
                for file in os.listdir(folder):
                    if os.path.isfile(os.path.join(folder, file)):
                        notdir += 1
            if notdir == 0:
                recode_all_series(os.getcwd())
            else:
                recode_series(os.getcwd())

        else:
            for file in os.listdir(os.getcwd()):
                try:
                    recode(file)
                except RuntimeError:
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
                    try:
                        season, name = get_series_name(series, file)
                    except RuntimeError:
                        continue
                    if not os.path.exists(os.path.join(os.path.realpath(folder), season)):
                        os.mkdir(os.path.join(os.path.realpath(folder), season))
                    shutil.move(
                        os.path.join(os.path.realpath(dire), file),
                        os.path.splitext(os.path.join(folder, season, name))[0] + os.path.splitext(file)[1],
                    )
        for container in VIDEO_CONTAINERS:
            if sys.argv[1].endswith(container):
                recode(sys.argv[1])


if __name__ == "__main__":
    main()
