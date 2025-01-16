#!/usr/bin/env python3

import os
import sys
import json
import re
import shutil
import datetime
import tempfile
import argparse
import configparser
import urllib.parse

from subprocess import Popen, PIPE, STDOUT

import requests
import survey

from colorama import init as colorama_init
from colorama import Fore as Color
from colorama import Style
from rich_argparse import RichHelpFormatter

from ffprobe import Ffprobe, Stream, StreamTags
from FileOperations import File

colorama_init()

# fmt: off
VIDEO_CONTAINERS = [
    ".3g2",".3gp",".amv",".asf",".avi",".drc",".f4a",".f4b",".f4p",".f4v",".flv",".gif",".gifv",".M2TS",
    ".m2v",".m4p",".m4v",".mkv",".mng",".mov",".mp2",".mp4",".mpe",".mpeg",".mpg",".mpv",".MTS",".mxf",
    ".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",".svi",".TS",".viv",".vob",".webm",".wmv",".yuv",
]
# fmt: on

AUDIO_PRIORITY = {"dts": 6, "flac": 5, "opus": 4, "truehd": 3, "eac3": 2, "ac3": 1}
SUBTITLE_PRIORITY = {"full": 3, "sdh": 2, "none": 1}
if os.path.exists("/usr/lib/libamfrt64.so"):
    HWACC = "AMF"
elif os.path.exists("/usr/lib/libcuda.so"):
    HWACC = "CUDA"
else:
    HWACC = None


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


def get_movie_name(file: str, token: str, lang: str):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(pattern=r"\d{4}", string=file)
            if match:
                comment = None
                date = None
                year: str = match.group()
                movie_name: str = file[: match.start()].replace("_", " ").replace(".", " ").replace("(", "").replace(")", "")
                output_file = f"{movie_name}({year}).mkv"
                response = requests.get(
                    f"https://api4.thetvdb.com/v4/search?query={movie_name}&type=movie&year={year}&language={lang}", timeout=10, headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code != 200:
                    response = requests.get(
                        f"https://api4.thetvdb.com/v4/search?query={movie_name}&type=movie&year={year}", timeout=10, headers={"Authorization": f"Bearer {token}"}
                    )
                try:
                    ret = response.json()["data"]
                    if len(ret) > 1:
                        choices = [f"{movie['slug'].ljust(30)[:30]} {movie.get('year')}: {movie.get('overviews', {}).get(lang, movie.get('overview', ''))[:180]}" for movie in ret]
                        choice = survey.routines.select("Select Movie: ", options=choices)
                    else:
                        choice = 0
                    ret = ret[choice]
                    if "overviews" in ret and lang in ret["overviews"]:
                        comment = ret["overviews"][lang]
                    elif "overviews" in ret and "eng" in ret["overviews"]:
                        comment = ret["overviews"]["eng"]
                    if "first_air_time" in ret and ret["first_air_time"] != "":
                        date = ret["first_air_time"]
                    if "translations" in ret and lang in ret["translations"]:
                        metadata = {"comment": comment, "title": f"{ret['translations'][lang]} ({ret['year']})", "date": date}
                        output_file = f"{ret['translations'][lang]} ({ret['year']}).mkv"
                    else:
                        metadata = {"comment": comment, "title": ret["extended_title"], "date": date}
                        output_file = f"{ret['extended_title']}.mkv"
                except IndexError:
                    metadata = {"title": f"{movie_name}({year})"}
            else:
                output_file: str = os.path.splitext(file)[0] + ".mkv"
                metadata = {"title": os.path.splitext(file)[0]}
            return output_file, metadata
    return None, None


def get_series_from_tvdb(series: str, token: str, lang: str) -> list:
    headers = {"Authorization": f"Bearer {token}"}
    match = re.search(r"\((\d{4})\)", series)
    try:
        seriesyear = match.groups()[0]
        queryseries = urllib.parse.quote(series.removesuffix(f"({seriesyear})").strip())
    except AttributeError:
        seriesyear = ""
        queryseries = urllib.parse.quote(re.search(r"[A-Za-z._-]+", series)[0].replace(".", " ").replace("-", " ").replace("_", " ").upper().removesuffix("S").strip())
    if token is None:
        return [], "", seriesyear
    response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&year={seriesyear}&language={lang}", timeout=10, headers=headers)
    if response.status_code != 200:
        response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&year={seriesyear}", timeout=10, headers=headers)
    res = response.json()["data"]
    choices = [f"{serie['slug'].ljust(30)[:30]} {serie.get('year')}: {serie.get('overviews', {}).get(lang, serie.get('overview', ''))[:180]}" for serie in res]
    choice = survey.routines.select("Select TV Show: ", options=choices)
    seriesid = response.json()["data"][choice]["id"].removeprefix("series-")
    response = requests.get(f"https://api4.thetvdb.com/v4/series/{seriesid}/episodes/default/{lang}?page=0", timeout=10, headers=headers)
    data = response.json()["data"]
    returnlst: list = data["episodes"]
    if lang in data["nameTranslations"]:
        translationres = requests.get(f"https://api4.thetvdb.com/v4/series/{seriesid}/translations/{lang}", timeout=10, headers=headers)
        translation = translationres.json()["data"]
        name = translation["name"]
    else:
        name = data["name"]
    year = data["year"]

    while response.json()["links"]["next"] is not None:
        response = requests.get(response.json()["links"]["next"], timeout=10, headers={"Authorization": f"Bearer {token}"})
        returnlst.extend(response.json()["data"]["episodes"])
    return returnlst, name, year


def get_episode_name(series: str, file: str, seriesobj: list):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(r"[Ss](\d{1,4})\s?(([Ee]\d{1,4})*)", file)
            if match:
                seasonnum = match.groups()[0]
                episodes = match.groups()[1].replace("e", "E").split("E")
                episodes.remove("")
                ep = ""
                titles: list[str] = []
                comments: list[str] = []
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
                            break
                if len(titles) == 2 and re.sub(r"\(\d+\)", "", titles[0]).strip() == re.sub(r"\(\d+\)", "", titles[1]).strip():
                    title = re.sub(r"\(\d+\)", "", titles[0]).strip()
                else:
                    title = " + ".join(titles)
                if title != "":
                    name = f"{series} - S{seasonnum.rjust(2, '0')}{ep} - {title}.mkv"
                else:
                    name = f"{series} - S{seasonnum.rjust(2, '0')}{ep}.mkv"
                season = f"Season {seasonnum.rjust(2, '0')}"
                try:
                    comment = " ".join(comments)
                except TypeError:
                    comment = None
                metadata = {
                    "episode_id": ", ".join(epi.removeprefix("0") for epi in episodes),
                    "season_number": seasonnum.removeprefix("0"),
                    "show": series,
                    "comment": comment,
                    "title": title,
                    "date": date,
                }
                return season, name, metadata
    return None, None, None


def recode_series(folder: str, apitokens: dict | None, lang: str, infolang: str, subdir: str = "", codec: str = "h265", bit: int = 10):
    if apitokens is None:
        apitokens = {"thetvdb": None}
    series = os.path.basename(folder)
    parentfolder = os.path.realpath(folder).removesuffix(f"/{series}")
    seriesobj, seriesname, year = get_series_from_tvdb(series, apitokens["thetvdb"], lang=infolang)
    if year != "":
        series = f"{seriesname} ({year})"
    for dire in sorted(os.listdir(folder)):
        if os.path.isdir(os.path.join(folder, dire)):
            for file in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
                season, name, metadata = get_episode_name(series, file, seriesobj)
                if name is not None:
                    if not os.path.exists(os.path.join(parentfolder, series, season)):
                        os.makedirs(os.path.join(parentfolder, series, season))
                    recode(
                        file=os.path.join(folder, dire, file),
                        path=os.path.join(parentfolder, series, season, name),
                        metadata=metadata,
                        lang=lang,
                        apitokens=apitokens,
                        subdir=subdir,
                        codec=codec,
                        bit=bit,
                    )
        else:
            season, name, metadata = get_episode_name(series, dire, seriesobj)
            if name is not None:
                if not os.path.exists(os.path.join(parentfolder, series, season)):
                    os.makedirs(os.path.join(parentfolder, series, season))
                recode(
                    file=os.path.join(os.path.realpath(folder), dire),
                    path=os.path.join(parentfolder, series, season, name),
                    metadata=metadata,
                    lang=lang,
                    apitokens=apitokens,
                    subdir=subdir,
                    codec=codec,
                    bit=bit,
                )


def video(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, vrecoding: bool, vindex: int, printlines: list, codec="h265", bit=10):
    if codec == "av1":
        codec = {"name": "av1", "swenc": "libsvtav1", "amdenc": "av1_amf", "nvdenc": "av1_nvenc"}
    elif codec == "h265":
        codec = {"name": "hevc", "swenc": "libx265", "amdenc": "hevc_amf", "nvdenc": "hevc_nvenc"}
    elif codec == "h264":
        codec = {"name": "h264", "swenc": "libx264", "amdenc": "h264_amf", "nvdenc": "h264_nvenc"}
    if stream.tags is None:
        stream.tags = StreamTags(title=None)
    if (stream.codec_name != codec["name"] or (bit == 8 and stream.pix_fmt != "yuv420p")) and not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        if HWACC == "AMF":
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codec["amdenc"]])
        elif HWACC == "CUDA":
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codec["nvdenc"]])
        else:
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codec["swenc"]])
        vrecoding = True
        printlines.append(
            f"Converting {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}{codec['name']} {Color.YELLOW}{stream.pix_fmt}{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    elif not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name} {Color.YELLOW}{stream.pix_fmt}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    vindex += 1
    return vrecoding, vindex, stream.pix_fmt


def recode_audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list, printlines: list, lang: str = "eng"):
    if stream.codec_name in AUDIO_PRIORITY.keys():
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "ac3"])
        arecoding = True
        stream.codec_name = "ac3"
        printlines.append(
            f"Converting {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}ac3{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    obj = stream.to_dict()
    obj["newindex"] = aindex
    astreams.append(obj)

    if stream.tags.language in ["eng", "und", "jpn", None, lang]:
        update_audio_default(adefault, stream, aindex, lang)
    return arecoding


def update_audio_default(adefault: dict, stream: Stream, aindex: int, lang: str = "eng"):
    if (
        (AUDIO_PRIORITY.get(stream.codec_name, 0) > AUDIO_PRIORITY.get(adefault["codec"], 0))
        or (AUDIO_PRIORITY.get(stream.codec_name, 0) == AUDIO_PRIORITY.get(adefault["codec"], 0) and stream.channels > adefault["channels"])
        or (adefault["lang"] != lang and stream.tags.language == lang)
    ):
        adefault.update(
            {
                "aindex": aindex,
                "codec": stream.codec_name,
                "lang": stream.tags.language,
                "oindex": stream.index,
                "channels": stream.channels,
            }
        )


def audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list, printlines: list, lang: str = "eng"):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "jpn", "und", None, lang]:
        arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines, lang)
        aindex += 1
    return arecoding, aindex


def subtitles(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, sindex: int, sdefault: dict, sstreams: list, printlines: list, file=0):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["eng", "ger", "deu", "und", None]:
        if stream.codec_name in ["subrip", "hdmv_pgs_subtitle", "ass", "dvd_subtitle"]:
            ffmpeg_mapping.extend(["-map", f"{file}:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "copy"])
            printlines.append(
                f"Copying {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}{file}:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
            )
        else:
            ffmpeg_mapping.extend(["-map", f"{file}:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:s:{sindex}", "srt"])
            printlines.append(
                f"Converting {Color.GREEN}subtitle{Style.RESET_ALL} stream {Color.BLUE}{file}:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}srt{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}s:{sindex}{Style.RESET_ALL} in output file"
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


def get_subtitles_from_ost(token: str, metadata: dict, lang: str, file: str):
    headers = {"Content-Type": "application/json", "Api-Key": token["api_key"], "User-Agent": "recoder v1.0.1", "Authorization": f"Bearer {token['token']}"}
    if metadata.get("show", False):
        match = re.findall(r"([\w\s]+)\s\((\d{4})\)", metadata["show"])[0]
        name = f"{match[0]} ({match[1]}) - {metadata['title']}"
    else:
        name = metadata["title"]
    response = requests.get(f"https://api.opensubtitles.com/api/v1/utilities/guessit?filename={name}", headers=headers)
    params = response.json()
    params["language"] = lang[:2]
    params["page"] = 0
    params["moviehash"] = File(file).get_hash()
    params["order_by"] = "ratings"

    response = requests.get("https://api.opensubtitles.com/api/v1/subtitles", params=urllib.parse.urlencode(params), headers=headers)
    try:
        subtitle = response.json()["data"][0]["attributes"]
    except IndexError:
        return None
    response = requests.post("https://api.opensubtitles.com/api/v1/download", headers=headers, json={"file_id": subtitle["files"][0]["file_id"]})
    link = response.json()["link"]
    filename = response.json()["file_name"]
    response = requests.get(link, headers=headers)
    content = response.content
    fd, tmpfile = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    with open(tmpfile, "wb") as f:
        f.write(content)
    return tmpfile


def recode(
    file: str, lang: str, infolang: str, path: str | None = None, metadata: dict | None = None, apitokens: dict | None = None, subdir: str = "", codec: str = "h265", bit: int = 10
):
    prelines = []
    midlines = []
    printlines = []

    adefault = {"aindex": None, "codec": None, "lang": None, "channels": None}
    sdefault = {"sindex": None, "type": None, "lang": None}

    videostreams = []
    audiostreams = []
    subtitlestreams = []
    attachmentstreams = []

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

    subfile = ""

    ffmpeg_command.extend(["ffmpeg", "-v", "error", "-stats", "-hwaccel", "auto", "-strict", "-2", "-i", os.path.realpath(file)])

    if path is None:
        output_file, metadata = get_movie_name(file, apitokens["thetvdb"], lang=infolang)
        if output_file is None:
            return
    else:
        output_file = path

    if metadata is None:
        metadata = {}
        metadata["title"] = os.path.basename(os.path.splitext(output_file)[0])

    prelines.append(
        f"{Color.RED}Recoding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(file)}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}"
    )

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
        print(f"Error: {err.decode('utf-8')} {e}")
        return
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

    for stream in videostreams:
        vrecoding, vindex, pix_fmt = video(stream, ffmpeg_mapping, ffmpeg_recoding, vrecoding, vindex, printlines, codec, bit)

    for stream in audiostreams:
        arecoding, aindex = audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines, lang)

    if aindex == 0:
        for stream in audiostreams:
            arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines)
            aindex += 1

    for stream in subtitlestreams:
        sindex = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams, printlines)

    if sindex == 0:
        if subdir != "" and os.path.isdir(subdir):
            episode = re.findall(r"[Ss]\d{2,4}[Ee]\d{2,4}", path)[0]
            files = os.listdir(subdir)
            subfile = [fil for fil in files if episode in fil]
            if len(subfile) == 1:
                subfile = os.path.join(subdir, subfile[0])
                if os.path.isdir(subfile):
                    subfil = os.listdir(subfile)
                    subfile = [os.path.join(subfile, fil) for fil in subfil]
                else:
                    subfile = [subfile]
        else:
            subfile = [get_subtitles_from_ost(token=apitokens["opensub"], metadata=metadata, lang=lang, file=file)]
        try:
            for fil in subfile:
                p = Popen(
                    ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-output_format", "json", fil, "-strict", "-2"],
                    stdout=PIPE,
                    stderr=PIPE,
                )
                out, err = p.communicate()
                output = json.loads(out.decode("utf-8"))
                ffprobedict = rename_keys_to_lower(output)
                try:
                    sub = Ffprobe.from_dict(ffprobedict)
                except Exception:
                    ...
                prelines.append(f"{Color.RED}Adding{Style.RESET_ALL} {Color.YELLOW}{os.path.realpath(fil)}{Style.RESET_ALL}")
                ffmpeg_command.extend(["-i", fil])
                for stream in sub.streams:
                    if stream.tags is None:
                        stream.tags = StreamTags.from_dict({"title": None, "language": lang})
                    midlines.append(
                        f"{Color.BLUE}1:{stream.index} {Color.GREEN}{stream.codec_type} {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.MAGENTA}{stream.tags.language} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
                    )
                    sindex = subtitles(stream, ffmpeg_mapping, ffmpeg_recoding, sindex, sdefault, sstreams, printlines, file=1)
        except Exception:
            ...

    for stream in attachmentstreams:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        printlines.append(
            f"Copying {Color.GREEN}attachment{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.filename}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}t:{tindex}{Style.RESET_ALL} in output file"
        )
        tindex += 1

    for stream in ffprobe.streams:
        disposition = " ".join([dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]])
        if stream.codec_type == "video" and stream.codec_name == "mjpeg" and stream.tags.filename == "cover.jpg":
            midlines.append(
                f"{Color.BLUE}0:{stream.index} {Color.GREEN}attached picture {Color.CYAN}{stream.tags.title} {Color.RED}{stream.codec_name} {Color.YELLOW}{disposition}{Style.RESET_ALL}"
            )
            ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
            ffmpeg_recoding.extend([f"-c:v:{vindex}", "mjpeg", f"-filter:v:{vindex}", "scale=-1:600"])
            ffmpeg_dispositions.extend([f"-disposition:v:{vindex}", "attached_pic"])
            printlines.append(
                f"Copying {Color.GREEN}attached picture{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
            )
            vindex += 1

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
                printlines.append(
                    f"Changing {Color.GREEN}{tag}{Style.RESET_ALL} from {Color.CYAN}{format_tags[tag]}{Style.RESET_ALL} to {Color.CYAN}{metadata[tag].strip()}{Style.RESET_ALL}"
                )
            ffmpeg_metadata.extend(["-metadata", f"{tag}={metadata[tag].strip()}"])
            changemetadata = True

    if not vrecoding and not arecoding and not changedefault and not changemetadata and os.path.realpath(file) == os.path.realpath(output_file):
        print(f"{Color.RED}No changes to make: {Color.GREEN}{file} {Color.BLUE}Continuing...{Style.RESET_ALL}")
        return
    if os.path.realpath(file) != os.path.realpath(output_file) and not vrecoding and not arecoding and not changedefault and not changemetadata:
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}{file}{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
        shutil.move(os.path.realpath(file), os.path.realpath(output_file))
        return

    fd, tmpfile = tempfile.mkstemp(suffix=".mkv")

    ffmpeg_command.extend(ffmpeg_mapping)
    ffmpeg_command.extend(ffmpeg_recoding)
    if vrecoding:
        if HWACC == "AMF":
            ffmpeg_command.extend(["-rc", "hqvbr", "-qvbr_quality_level", "23", "-quality", "quality"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_command.extend(["-pixel_format", "p010le"])
            else:
                ffmpeg_command.extend(["-pixel_format", "yuv420p"])
        elif HWACC == "CUDA":
            if codec != "av1":
                ffmpeg_command.extend(["-preset", "p7", "-rc", "vbr_hq", "-cq", "23"])
            else:
                ffmpeg_command.extend(["-preset", "p7", "-rc", "vbr", "-cq", "23"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_command.extend(["-pixel_format", "p010le"])
            else:
                ffmpeg_command.extend(["-pixel_format", "yuv420p"])
        else:
            if codec != "av1":
                ffmpeg_command.extend(["-crf", "23", "-preset", "veryslow"])
            else:
                ffmpeg_command.extend(["-crf", "23"])
            if bit == 10 and pix_fmt == "yuv420p10le":
                ffmpeg_command.extend(["-pixel_format", "yuv420p10le"])
            else:
                ffmpeg_command.extend(["-pixel_format", "yuv420p"])
    if arecoding:
        ffmpeg_command.extend(["-b:a", "192k", "-ar", "48000"])
    ffmpeg_command.extend(ffmpeg_dispositions)
    ffmpeg_command.extend(ffmpeg_metadata)
    ffmpeg_command.extend(["-f", "matroska", "-y", tmpfile])
    for line in prelines:
        print(line)
    for line in midlines:
        print(line)
    for line in printlines:
        print(line)
    # print(" ".join(ffmpeg_command))

    timestart = datetime.datetime.now()
    print(f"Recoding started at {Color.GREEN}{timestart.isoformat()}{Style.RESET_ALL}")

    # Run ffmpeg_command and print live output
    try:
        with Popen(ffmpeg_command, stdout=PIPE, stderr=STDOUT) as process:
            for c in iter(lambda: process.stdout.read(1), b""):
                sys.stdout.buffer.write(c)
                sys.stdout.flush()
            process.wait()
        timestop = datetime.datetime.now()
        print(f"Recoding finished at {Color.GREEN}{timestop.isoformat()}{Style.RESET_ALL}")
        print(f"Recoding took {Color.GREEN}{timestop - timestart}{Style.RESET_ALL}")

        # Rename old file
        shutil.move(os.path.realpath(file), os.path.realpath(file) + ".old")

        # Move tempfile to output_file
        print(f"{Color.RED}Moving{Style.RESET_ALL} {Color.YELLOW}tempfile{Style.RESET_ALL} to {Color.MAGENTA}{os.path.realpath(output_file)}{Style.RESET_ALL}")
        try:
            shutil.move(tmpfile, os.path.realpath(output_file))
            os.chmod(output_file, 0o644)
        finally:
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
    finally:
        if isinstance(subfile, str):
            if os.path.exists(subfile):
                os.remove(subfile)
    print(f"{Color.GREEN}Done!{Style.RESET_ALL}")


def api_login(config: str) -> str:
    if not os.path.exists(config):
        os.mknod(config)

    conf = configparser.ConfigParser()
    conf.read(config)

    if not "thetvdb" in conf:
        conf["thetvdb"] = {}
        conf["thetvdb"]["apikey"] = input('theTVDB api not configured. Please open "https://thetvdb.com/api-information/signup" and paste the api key here: ')
    if not "opensubtitles" in conf:
        conf["opensubtitles"] = {}
        conf["opensubtitles"]["apikey"] = input('OpenSubtitles api not configured. Please open "https://www.opensubtitles.com/consumers" and paste the api key here: ')
        conf["opensubtitles"]["user"] = input("username: ")
        conf["opensubtitles"]["password"] = input("password: ")

    with open(config, "w") as configfile:
        conf.write(configfile)

    response = requests.post("https://api4.thetvdb.com/v4/login", json={"apikey": conf.get("thetvdb", "apikey")}, timeout=10, headers={"Content-Type": "application/json"})
    thetvdbtoken = response.json()["data"]["token"]

    response = requests.post(
        "https://api.opensubtitles.com/api/v1/login",
        json={"username": conf.get("opensubtitles", "user"), "password": conf.get("opensubtitles", "password")},
        timeout=10,
        headers={"Content-Type": "application/json", "Api-Key": conf.get("opensubtitles", "apikey"), "User-Agent": "recoder v1.0.0"},
    )
    opensubtitlestoken = response.json()["token"]

    tokens = {"thetvdb": thetvdbtoken, "opensub": {"token": opensubtitlestoken, "api_key": conf.get("opensubtitles", "apikey")}}
    return tokens


def logout(token):
    requests.delete(
        "https://api.opensubtitles.com/api/v1/logout",
        headers={"Content-Type": "application/json", "Api-Key": token["api_key"], "User-Agent": "recoder v1.0.0", "Authorization": f"Bearer {token['token']}"},
    )


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

    parser = argparse.ArgumentParser(description="Recode media to common format", formatter_class=RichHelpFormatter)
    parser.add_argument(
        "-l",
        "--lang",
        help="Language of content, sets audio and subtitle language if undefined and tries to get information in specified language",
        choices=["eng", "deu", "spa", "jpn"],
        default="eng",
        dest="lang",
        metavar="LANG",
    )
    parser.add_argument("-i", "--input", help="File to recode", type=str, required=False, dest="inputfile", metavar="FILE")
    parser.add_argument("-d", "--dir", help="Directory containing files to recode", type=str, required=False, dest="inputdir", metavar="DIR")
    parser.add_argument("-t", "--type", help="Type of content", choices=["film", "series", "rename", "seriesdir"], required=True, dest="contentype", metavar="TYPE")
    parser.add_argument("-a", "--no-api", help="Disable Metadata and Subtitle APIs", default=False, action="store_true", dest="apis")
    parser.add_argument("-s", "--subtitle", help="Directory containing Subtitles", required=False, default="", dest="subdir", metavar="DIR")
    parser.add_argument("-c", "--codec", help="Select codec", required=False, choices=["h264", "h265", "av1"], dest="codec", metavar="CODEC", default="av1")
    parser.add_argument("-b", "--bit", help="Select bit depth", required=False, choices=["8", "10"], dest="bit", metavar="BIT", default="10")
    parser.add_argument("--hwaccel", help="Enable Hardware Acceleration (faster but larger files)", required=False, action="store_true", dest="hwaccel")
    parser.add_argument("--infolang", help="Language the info shall be retrieved in (defaults to --lang)", required=False, default=None, choices=["eng", "deu"], dest="infolang")
    args = parser.parse_args()

    if args.hwaccel is False:
        global HWACC
        HWACC = None

    if not args.apis:
        apitokens = api_login(configpath)
    else:
        apitokens = None

    if not args.infolang:
        infolang = args.lang
    else:
        infolang = args.infolang

    if args.contentype == "film":
        if args.inputfile:
            if os.path.isfile(args.inputfile):
                recode(file=args.inputfile, apitokens=apitokens, lang=args.lang, infolang=infolang, subdir=args.subdir, codec=args.codec, bit=int(args.bit))
            else:
                error = f'File "{args.inputfile}" does not exist or is a directory.'
                raise FileNotFoundError(error)
        elif args.inputdir:
            if os.path.isdir(args.inputdir):
                for subdir in os.listdir(args.inputdir):
                    recode(file=subdir, apitokens=apitokens, lang=args.lang, infolang=infolang, subdir=args.subdir, codec=args.codec, bit=int(args.bit))
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
                        subdir=args.subdir,
                        codec=args.codec,
                        bit=int(args.bit),
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
                recode_series(args.inputdir, apitokens=apitokens, lang=args.lang, infolang=infolang, subdir=args.subdir, codec=args.codec, bit=int(args.bit))
            else:
                error = f'Directory "{args.inputdir}" does not exist'
                raise FileNotFoundError(error)
        else:
            recode_series(os.getcwd(), apitokens=apitokens, lang=args.lang, infolang=infolang, subdir=args.subdir, codec=args.codec, bit=int(args.bit))
    elif args.contentype == "rename":
        folder = os.getcwd()
        series = os.path.basename(folder)
        parentfolder = os.path.realpath(folder).removesuffix(f"/{series}")
        seriesobj, seriesname, year = get_series_from_tvdb(series, apitokens["thetvdb"], lang=infolang)
        if year != "":
            series = f"{seriesname} ({year})"
        for dire in sorted(os.listdir(folder)):
            if os.path.isdir(dire):
                for subdir in sorted(os.listdir(os.path.realpath(os.path.join(folder, dire)))):
                    season, name, metadata = get_episode_name(series, subdir, seriesobj)
                    if name is not None:
                        if not os.path.exists(os.path.join(parentfolder, series, season)):
                            os.makedirs(os.path.join(parentfolder, series, season))
                        old = os.path.join(folder, dire, subdir)
                        new = os.path.splitext(os.path.join(parentfolder, series, season, name))[0] + os.path.splitext(subdir)[1]
                        if old != new:
                            print(f"Moving {Color.YELLOW}{old}{Style.RESET_ALL} to {Color.MAGENTA}{new}{Style.RESET_ALL}")
                            shutil.move(old, new)
            else:
                season, name, metadata = get_episode_name(series, dire, seriesobj)
                if name is not None:
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
