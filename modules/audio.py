from colorama import Fore as Color
from colorama import Style

from modules.ffprobe import Stream, StreamTags

AUDIO_PRIORITY = {"dts": 6, "flac": 5, "opus": 4, "truehd": 3, "eac3": 2, "ac3": 1}


def recode_audio(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, arecoding: bool, aindex: int, adefault: dict, astreams: list, printlines: list, lang: str = "eng"):
    if stream.codec_name in AUDIO_PRIORITY.keys():
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name}{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    else:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:a:{aindex}", "libopus"])
        arecoding = True
        stream.codec_name = "opus"
        printlines.append(
            f"Converting {Color.GREEN}audio{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}opus{Style.RESET_ALL}, language {Color.MAGENTA}{stream.tags.language}{Style.RESET_ALL} and index {Color.BLUE}a:{aindex}{Style.RESET_ALL} in output file"
        )
    obj = stream.to_dict()
    obj["newindex"] = aindex
    astreams.append(obj)

    if stream.tags.language in ["eng", "und", "jpn", None, lang]:
        update_audio_default(adefault, stream, aindex, lang)

    return arecoding


def update_audio_default(adefault: dict, stream: Stream, aindex: int, lang: str = "eng"):
    if (
        (stream.channels > adefault["channels"] and stream.tags.language == lang)
        or (AUDIO_PRIORITY.get(stream.codec_name, 0) > AUDIO_PRIORITY.get(adefault["codec"], 0) and stream.channels == adefault["channels"] and stream.tags.language == lang)
        or (adefault["lang"] != lang and stream.tags.language == lang)
    ):
        adefault.update(
            {
                "aindex": aindex,
                "codec": stream.codec_name,
                "lang": stream.tags.language,
                "oindex": stream.index,
                "channels": stream.channels,
                "title": stream.tags.title,
            }
        )


def audio(
    stream: Stream,
    ffmpeg_mapping: list,
    ffmpeg_recoding: list,
    arecoding: bool,
    aindex: int,
    adefault: dict,
    astreams: list,
    printlines: list,
    dispositions: dict[str, dict[str, str | list[str]]],
    changealang: list,
    lang: str = "eng",
):
    if stream.tags is None:
        stream.tags = StreamTags.from_dict({"title": None})
    if stream.tags.language in ["und", None, "ger"]:
        if stream.tags.language == "ger":
            changealang.append({"index": aindex, "lang": "deu"})
            stream.tags.language = "deu"
        else:
            changealang.append({"index": aindex, "lang": lang})
            stream.tags.language = lang
    if stream.tags.language in ["eng", "ger", "deu", "jpn", "und", None, lang]:
        arecoding = recode_audio(stream, ffmpeg_mapping, ffmpeg_recoding, arecoding, aindex, adefault, astreams, printlines, lang)
        dispositiontypes = [dispo[0] for dispo in stream.disposition.to_dict().items() if dispo[1]]
        dispositions["a" + str(aindex)] = {
            "stype": "a",
            "index": aindex,
            "title": stream.tags.title,
            "lang": stream.tags.language,
            "types": dispositiontypes,
        }
        aindex += 1
    return arecoding, aindex, changealang
