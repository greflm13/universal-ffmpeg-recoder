import json
import datetime
import os

from colorama import Fore as Color, Style
from ffmpeg import FFmpeg, Progress

from modules.ffprobe import Ffprobe


def list_to_dict(lst: list) -> dict:
    """
    Converts a list of strings to a dictionary using every element starting with '-' as a key stripping the '-'
    and the following element as its value.
    If next element also starts with '-', the key will have a value of None.
    """
    result = {}
    for i in range(len(lst)):
        if lst[i].startswith("-"):
            result[lst[i].removeprefix("-")] = lst[i + 1] if i + 1 < len(lst) and not lst[i + 1].startswith("-") else None
    return result


def maplist(lst: list[str]) -> list[str]:
    """
    Converts a list of mapping strings to ffmpeg mapping arguments.

    Args:
        lst (list): A list of mapping strings in the format "-map", "0:a:0", "-map", "0:v:0", etc.
    Returns:
        list: A list of ffmpeg mapping arguments.
    """
    mapping = []
    for item in lst:
        if not item.startswith("-"):
            mapping.append(item)
    return mapping


def format_timedelta(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


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


def human_readable_size(size_bytes):
    """
    Convert a file size in bytes to a human-readable string with autoscaled units.
    """
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"


def probe(file_path: str) -> Ffprobe:
    """
    Probes a media file and returns its metadata.

    Args:
        file_path (str): The path to the media file.

    Returns:
        dict: A dictionary containing the metadata of the media file.
    """
    ffprobe = FFmpeg(executable="ffprobe").input(file_path, print_format="json", show_streams=None, show_format=None, strict="-2", v="error")
    return Ffprobe.from_dict(rename_keys_to_lower(json.loads(ffprobe.execute())))


def ffrecode(input_file: str, output_file: str, ffmpeg_mapping: list, ffmpeg_recoding: list, ffmpeg_dispositions: list, ffmpeg_metadata: list, additional_files: list | None = None) -> None:
    """
    Re-encodes a media file using ffmpeg with the specified arguments.

    Args:
        input_file (str): The path to the input media file.
        output_file (str): The path to the output media file.
        ffmpeg_mapping (list): A list of ffmpeg mapping arguments.
        ffmpeg_recoding (list): A list of ffmpeg recoding arguments.
        ffmpeg_dispositions (list): A list of ffmpeg disposition arguments.
        ffmpeg_metadata (list): A list of ffmpeg metadata arguments.

    Returns:
        None
    """
    ffmpeg_args = list_to_dict(ffmpeg_recoding + ffmpeg_dispositions)
    mapping = maplist(ffmpeg_mapping)
    metadata = maplist(ffmpeg_metadata)
    ffmpeg = FFmpeg(executable="ffmpeg").option("y").option("hwaccel", "auto").option("strict", "-2").option("v", "error").option("stats").input(input_file)
    if additional_files:
        for file in additional_files:
            ffmpeg = ffmpeg.input(file)
    ffmpeg = ffmpeg.output(output_file, ffmpeg_args, f="matroska", map=mapping, metadata=metadata)

    @ffmpeg.on("start")
    def on_start(arguments: list[str]):
        print(f"Recoding started at {Color.GREEN}{timestart.isoformat()}{Style.RESET_ALL}")

    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        termwidth = os.get_terminal_size().columns
        print("\r" + " " * termwidth, end="\r")
        print(f"frame={progress.frame} fps={int(progress.fps)} size={human_readable_size(progress.size)} time={format_timedelta(progress.time)} bitrate={human_readable_size(progress.bitrate)}/s speed={progress.speed}x", end="\r")

    @ffmpeg.on("completed")
    def on_completed():
        timestop = datetime.datetime.now()
        print(f"\nRecoding finished at {Color.GREEN}{timestop.isoformat()}{Style.RESET_ALL}")
        print(f"Recoding took {Color.GREEN}{timestop - timestart}{Style.RESET_ALL}")

    @ffmpeg.on("terminated")
    def on_terminated():
        print("terminated")

    timestart = datetime.datetime.now()
    ffmpeg.execute()
