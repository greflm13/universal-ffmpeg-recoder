from colorama import Fore as Color
from colorama import Style

from modules.ffprobe import Stream, StreamTags

SUBTITLE_PRIORITY = {"forced": 4, "full": 3, "none": 1}


def subtitles(
    stream: Stream,
    ffmpeg_mapping: list,
    ffmpeg_recoding: list,
    sindex: int,
    sdefault: dict,
    sstreams: list,
    printlines: list,
    dispositions: dict[str, dict[str, str | list[str]]],
    changeslang: list,
    lang: str,
    file=0,
):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["und", None, "ger"]:
        if lang == "ger":
            lang = "deu"
        changeslang.append({"index": sindex, "lang": lang})
        stream.tags.language = lang
    if stream.tags.language in ["eng", "ger", "deu", "und", None]:
        stream.tags.language = "deu" if stream.tags.language == "ger" else stream.tags.language
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
        dispositiontypes = [dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]]
        dispositions["s" + str(sindex)] = {
            "stype": "s",
            "index": sindex,
            "title": stream.tags.title,
            "lang": stream.tags.language,
            "types": dispositiontypes,
        }
        update_subtitle_default(sdefault, stream, sindex, dispositions, lang)
        sindex += 1
    return sindex, changeslang


def update_subtitle_default(sdefault: dict, stream: Stream, sindex: int, dispositions: dict[str, dict[str, str | list[str]]], lang: str):
    subtitle_type = "none"
    if stream.tags.title:
        title_lower = stream.tags.title.lower()
        if "full" in title_lower:
            subtitle_type = "full"
        elif "sdh" in title_lower:
            subtitle_type = "sdh"
        elif "forced" in title_lower:
            subtitle_type = "forced"
    if (stream.tags.language == lang or stream.tags.language is None) and (SUBTITLE_PRIORITY.get(subtitle_type, 0) > SUBTITLE_PRIORITY.get(sdefault["type"], 0)):
        sdefault.update(
            {
                "lang": stream.tags.language,
                "oindex": stream.index,
                "sindex": sindex,
                "type": subtitle_type if not stream.disposition.forced else "forced",
                "title": stream.tags.title,
            }
        )

    if subtitle_type == "forced" or stream.disposition.forced:
        stype = "s"
        if dispositions.get(stype + str(sindex), False):
            if "forced" not in dispositions.get(stype + str(sindex))["types"]:
                dispositions.get(stype + str(sindex))["types"].append("forced")
        else:
            dispositions[stype + str(sindex)] = {"stype": stype, "index": str(sindex), "title": stream.tags.title, "lang": stream.tags.language, "types": ["forced"]}
        stream.disposition.forced = True
    if subtitle_type == "sdh" or stream.disposition.hearing_impaired:
        stype = "s"
        if dispositions.get(stype + str(sindex), False):
            if "hearing_impaired" not in dispositions.get(stype + str(sindex))["types"]:
                dispositions.get(stype + str(sindex))["types"].append("hearing_impaired")
        else:
            dispositions[stype + str(sindex)] = {"stype": stype, "index": str(sindex), "title": stream.tags.title, "lang": stream.tags.language, "types": ["hearing_impaired"]}
