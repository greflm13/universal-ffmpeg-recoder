from colorama import Fore as Color
from colorama import Style

from modules.ffprobe import Stream, StreamTags


def video(stream: Stream, ffmpeg_mapping: list, ffmpeg_recoding: list, vrecoding: bool, vindex: int, printlines: list, hwacc: str | None, codec="av1", bit=10):
    codecd = {"name": "av1", "swenc": "libsvtav1", "amdenc": "av1_amf", "nvdenc": "av1_nvenc"}
    if codec == "av1":
        codecd = {"name": "av1", "swenc": "libsvtav1", "amdenc": "av1_amf", "nvdenc": "av1_nvenc"}
    elif codec == "h265":
        codecd = {"name": "hevc", "swenc": "libx265", "amdenc": "hevc_amf", "nvdenc": "hevc_nvenc"}
    elif codec == "h264":
        codecd = {"name": "h264", "swenc": "libx264", "amdenc": "h264_amf", "nvdenc": "h264_nvenc"}
    if stream.tags is None:
        stream.tags = StreamTags(title=None)
    if (stream.codec_name != codecd["name"] or (bit == 8 and stream.pix_fmt != "yuv420p")) and not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        if hwacc == "AMF":
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codecd["amdenc"]])
        elif hwacc == "CUDA":
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codecd["nvdenc"]])
        else:
            ffmpeg_recoding.extend([f"-c:v:{vindex}", codecd["swenc"]])
        vrecoding = True
        printlines.append(
            f"Converting {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} to codec {Color.RED}{codecd['name']} {Color.YELLOW}{stream.pix_fmt}{Style.RESET_ALL} with index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    elif not stream.disposition.attached_pic:
        ffmpeg_mapping.extend(["-map", f"0:{stream.index}"])
        ffmpeg_recoding.extend([f"-c:v:{vindex}", "copy"])
        printlines.append(
            f"Copying {Color.GREEN}video{Style.RESET_ALL} stream {Color.BLUE}0:{stream.index}{Style.RESET_ALL} titled {Color.CYAN}{stream.tags.title}{Style.RESET_ALL} with codec {Color.RED}{stream.codec_name} {Color.YELLOW}{stream.pix_fmt}{Style.RESET_ALL} and index {Color.BLUE}v:{vindex}{Style.RESET_ALL} in output file"
        )
    vindex += 1
    return vrecoding, vindex, stream.pix_fmt
