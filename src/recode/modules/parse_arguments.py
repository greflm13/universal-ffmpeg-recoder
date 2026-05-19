import argparse
import json
import sys
from importlib.metadata import version
from pathlib import Path

from rich_argparse import RichHelpFormatter

__version__ = version("universal-ffmpeg-recoder")


def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore
    else:
        base = Path(__file__).resolve().parents[1]
    return base.joinpath(*parts)


def parse_args() -> argparse.Namespace:
    languages = json.loads(resource_path("languages.json").read_text())
    parser = argparse.ArgumentParser(description="Recode media to common format", formatter_class=RichHelpFormatter)
    parser.add_argument(
        "-l",
        "--lang",
        help="Language of content, sets audio and subtitle language if undefined and tries to get information in specified language",
        choices=languages,
        default="eng",
        dest="lang",
        metavar="LANG",
    )
    parser.add_argument("-i", "--input", help="File to recode", type=str, required=False, dest="inputfile", metavar="FILE")
    parser.add_argument(
        "-d", "--dir", help="Directory containing files to recode", type=str, required=False, dest="inputdir", metavar="DIR"
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Type of content",
        choices=["film", "series", "rename", "seriesdir", "changeSeasonType"],
        required=True,
        dest="contentype",
        metavar="TYPE",
    )
    parser.add_argument("-a", "--no-api", help="Disable Metadata and Subtitle APIs", default=False, action="store_true", dest="apis")
    parser.add_argument("-s", "--subtitle", help="Directory containing Subtitles", required=False, default="", dest="subdir", metavar="DIR")
    parser.add_argument(
        "-c", "--codec", help="Select codec", required=False, choices=["h264", "h265", "av1"], dest="codec", metavar="CODEC", default="av1"
    )
    parser.add_argument(
        "-b", "--bit", help="Select bit depth", required=False, choices=["8", "10"], dest="bit", metavar="BIT", default="10"
    )
    parser.add_argument("-o", "--output", help="Output folder", required=False, default="", dest="output", metavar="DIR", type=str)
    parser.add_argument("-V", "--version", action="version", version="%(prog)s-" + __version__)
    parser.add_argument("--copy", help="Don't recode video streams, just copy them", required=False, action="store_true", dest="copy")
    parser.add_argument(
        "--hwaccel", help="Enable Hardware Acceleration (faster but larger files)", required=False, action="store_true", dest="hwaccel"
    )
    parser.add_argument(
        "--infolang",
        help="Language the info shall be retrieved in (defaults to --lang)",
        required=False,
        default=None,
        choices=languages,
        dest="infolang",
        metavar="LANG",
    )
    parser.add_argument(
        "--sublang",
        help="Language the default subtitle should be (defaults to --lang)",
        required=False,
        default=None,
        choices=languages,
        dest="sublang",
        metavar="LANG",
    )
    parser.add_argument(
        "--searchstring",
        help="Manual search string for TVDB API",
        required=False,
        default=None,
        dest="searchstring",
        metavar="SEARCHSTRING",
    )
    parser.add_argument("--omit-cover", help="Don't include cover in output file", required=False, action="store_true", dest="omitcover")
    parser.add_argument(
        "--sub-selector",
        help="Regex to select subtitle stream based on title",
        required=False,
        default=None,
        dest="subselector",
        metavar="REGEX",
    )
    parser.add_argument(
        "--metadata-only", help="Only change metadata, copy streams", required=False, action="store_true", dest="onlymetadata"
    )
    return parser.parse_args()
