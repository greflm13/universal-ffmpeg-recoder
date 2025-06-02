import os
import re
import tempfile
import configparser
import urllib.parse

from functools import cache

import requests
import survey

from colorama import Fore as Color
from colorama import Style

from modules.FileOperations import File

# fmt: off
VIDEO_CONTAINERS = [
    ".3g2",".3gp",".amv",".asf",".avi",".drc",".f4a",".f4b",".f4p",".f4v",".flv",".gif",".gifv",".M2TS",
    ".m2v",".m4p",".m4v",".mkv",".mng",".mov",".mp2",".mp4",".mpe",".mpeg",".mpg",".mpv",".MTS",".mxf",
    ".nsv",".ogg",".ogv",".qt",".rm",".rmvb",".roq",".svi",".TS",".viv",".vob",".webm",".wmv",".yuv",
]
# fmt: on


def api_login(config: str) -> dict[str, str | dict[str, str]]:
    if not os.path.exists(config):
        os.mknod(config)

    conf = configparser.ConfigParser()
    conf.read(config)

    if "thetvdb" not in conf:
        conf["thetvdb"] = {}
        conf["thetvdb"]["apikey"] = input('theTVDB api not configured. Please open "https://thetvdb.com/api-information/signup" and paste the api key here: ')
    if "opensubtitles" not in conf:
        conf["opensubtitles"] = {}
        conf["opensubtitles"]["apikey"] = input('OpenSubtitles api not configured. Please open "https://www.opensubtitles.com/consumers" and paste the api key here: ')
        conf["opensubtitles"]["user"] = input("username: ")
        conf["opensubtitles"]["password"] = input("password: ")

    with open(config, "w") as configfile:
        conf.write(configfile)

    response = requests.post("https://api4.thetvdb.com/v4/login", json={"apikey": conf.get("thetvdb", "apikey")}, timeout=10, headers={"Content-Type": "application/json"})
    thetvdbtoken = response.json()["data"]["token"]

    try:
        response = requests.post(
            "https://api.opensubtitles.com/api/v1/login",
            json={"username": conf.get("opensubtitles", "user"), "password": conf.get("opensubtitles", "password")},
            timeout=10,
            headers={"Content-Type": "application/json", "Api-Key": conf.get("opensubtitles", "apikey"), "User-Agent": "recoder v1.0.0"},
        )
        opensubtitlestoken = response.json()["token"]
    except requests.Timeout:
        opensubtitlestoken = None
    except requests.JSONDecodeError:
        opensubtitlestoken = None
    except KeyError:
        opensubtitlestoken = None

    tokens = {"thetvdb": thetvdbtoken, "opensub": {"token": opensubtitlestoken, "api_key": conf.get("opensubtitles", "apikey")}}
    return tokens


def logout(token):
    requests.delete(
        "https://api.opensubtitles.com/api/v1/logout",
        headers={"Content-Type": "application/json", "Api-Key": token["api_key"], "User-Agent": "recoder v1.0.0", "Authorization": f"Bearer {token['token']}"},
    )


def get_movie_name(file: str, token: str, lang: str, stype: str = "single"):
    for container in VIDEO_CONTAINERS:
        if file.endswith(container):
            match = re.search(pattern=r"(.*)(\d{4}(?!p))", string=file)
            if match:
                comment = None
                date = None
                year: str = match.groups()[1]
                movie_name: str = match.groups()[0].replace("_", " ").replace(".", " ").replace("(", "").replace(")", "")
                output_file = f"{movie_name}({year}).mkv"
                if token is None:
                    return output_file, {"title": f"{movie_name}({year})"}
                succ = False
                while not succ:
                    try:
                        response = requests.get(
                            f"https://api4.thetvdb.com/v4/search?query={movie_name}&type=movie&year={year}&language={lang}",
                            timeout=10,
                            headers={"Authorization": f"Bearer {token}"},
                        )
                        succ = True
                    except requests.exceptions.ReadTimeout:
                        succ = False
                if response.status_code != 200:  # type: ignore
                    succ = False
                    while not succ:
                        try:
                            response = requests.get(
                                f"https://api4.thetvdb.com/v4/search?query={movie_name}&type=movie&year={year}", timeout=10, headers={"Authorization": f"Bearer {token}"}
                            )
                            succ = True
                        except requests.exceptions.ReadTimeout:
                            succ = False
                try:
                    ret = response.json()["data"]  # type: ignore
                    if len(ret) > 1 and stype == "single":
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
                        output_file = f"{ret['translations'][lang].replace('/', '-')} ({ret['year']}).mkv"
                    else:
                        metadata = {"comment": comment, "title": ret["extended_title"].replace("/", "-"), "date": date}
                        output_file = f"{ret['extended_title']}.mkv"
                except IndexError:
                    metadata = {"title": f"{movie_name}({year})"}
            else:
                output_file: str = os.path.splitext(file)[0] + ".mkv"
                metadata = {"title": os.path.splitext(file)[0]}
            return output_file, metadata
    return None, None


def split_string_at_whitespace(text: str, n: int) -> list[str]:
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= n - 4:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def build_choice_list(series_list: list[dict[str, str | dict[str, str]]], lang: str) -> list[str]:
    filtered_list = []
    choice_list = []
    termwidth = os.get_terminal_size().columns

    for series in series_list:
        if series.get("translations", False):
            name = series["translations"].get("eng", series["name"])  # type: ignore
        else:
            name = series["name"]
        if series.get("overviews", False):
            overview = series["overviews"].get(lang, series["overviews"].get(series["primary_language"])) # type: ignore
        else:
            overview = ""
        if overview is None:
            overview = ""
        filtered_list.append(
            {
                "slug": series["slug"],
                "name": name,
                "year": series.get("year", "    "),
                "overview": overview,
            }
        )

    slug_max_len = max([len(series["slug"]) for series in filtered_list])
    name_max_len = max([len(series["name"]) for series in filtered_list])

    constants = slug_max_len + name_max_len + 13
    free_space = termwidth - constants
    spacer = " " * slug_max_len + " | " + " " * name_max_len + " |      | "
    overview = ""

    for series in filtered_list:
        if constants + len(series["overview"]) > termwidth:
            lines = split_string_at_whitespace(series["overview"], free_space)
            for i, line in enumerate(lines):
                if i == 0:
                    overview = line
                else:
                    overview += "\n" + spacer + line
        else:
            overview = series["overview"]
        choice_list.append(f"{series['slug'].ljust(slug_max_len)} | {series['name'].ljust(name_max_len)} | {series['year']} | {overview}")

    return choice_list


@cache
def find_series_id(series: str, token: str, lang: str) -> str | None:
    headers = {"Authorization": f"Bearer {token}"}
    match = re.search(r"\((\d{4})\)", series)
    try:
        seriesyear = match.groups()[0]  # type: ignore
        queryseries = urllib.parse.quote(series.removesuffix(f"({seriesyear})").strip())
    except AttributeError:
        seriesyear = ""
        queryseries = urllib.parse.quote(re.search(r"[A-Za-z._-]+", series)[0].replace(".", " ").replace("-", " ").replace("_", " ").upper().removesuffix("S").strip())  # type: ignore
    response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&year={seriesyear}&language={lang}", timeout=10, headers=headers)
    if response.status_code != 200:
        response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&year={seriesyear}", timeout=10, headers=headers)
    res = response.json()["data"]
    if res == []:
        response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series&language={lang}", timeout=10, headers=headers)
        if response.status_code != 200:
            response = requests.get(f"https://api4.thetvdb.com/v4/search?query={queryseries}&type=series", timeout=10, headers=headers)
        res = response.json()["data"]
    # choices = [f"{serie['slug'].ljust(30)[:30]} {serie.get('year')}: {serie.get('overviews', {}).get(lang, serie.get('overview', ''))[:180]}" for serie in res]
    choices = build_choice_list(res, lang)
    if choices == []:
        print(f"{Color.RED}err: {Style.RESET_ALL}Series not found! {Color.BLUE}{series}{Style.RESET_ALL}")
        return None
    choice = survey.routines.select("Select TV Show: ", options=choices)
    return response.json()["data"][choice]["id"].removeprefix("series-")


@cache
def get_extended_series(seriesid: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api4.thetvdb.com/v4/series/{seriesid}/extended", timeout=10, headers=headers)
    return response.json()["data"]


def get_season_type(seriesid: str, token: str, specifier: str = "") -> str:
    data = get_extended_series(seriesid, token)
    data = data["seasonTypes"]
    if len(data) > 1:
        types = [typ["alternateName"] if typ["alternateName"] is not None else typ["name"] for typ in data]
        choice = survey.routines.select(f"Select{specifier} Season Type: ", options=types)
        return data[choice]["type"]
    else:
        return "default"


@cache
def get_episodelist(seriesid: str, seasonType: str, lang: str, token: str) -> tuple[list[dict[str, str | dict[str, str]]], str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api4.thetvdb.com/v4/series/{seriesid}/episodes/{seasonType}/{lang}?page=0", timeout=10, headers=headers)
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
        response = requests.get(response.json()["links"]["next"], timeout=10, headers=headers)
        returnlst.extend(response.json()["data"]["episodes"])
    return returnlst, name, year


@cache
def get_series_from_tvdb(series: str, token: str, lang: str) -> tuple[list[dict[str, str | dict[str, str]]] | None, str, str]:
    if token is None:
        return None, "", ""
    seriesid = find_series_id(series, token, lang)
    if seriesid is not None:
        seasonType = get_season_type(seriesid, token)
        return get_episodelist(seriesid, seasonType, lang, token)
    return None, "", ""


def change_season_type(series: str, token: str, lang: str) -> tuple[list[dict[str, str | dict[str, str]]] | None, list[dict[str, str | dict[str, str]]] | None, str, str]:
    if token is None:
        return None, "", ""
    seriesid = find_series_id(series, token, lang)
    if seriesid is None:
        return None, None, "", ""
    currSeasonType = get_season_type(seriesid, token, "Current")
    destSeasonType = get_season_type(seriesid, token, "Desired")
    currlist, name, year = get_episodelist(seriesid, currSeasonType, lang, token)
    destlist, name, year = get_episodelist(seriesid, destSeasonType, lang, token)
    return currlist, destlist, name, year


def change_episode_number(series: str, file: str, seriesobj: list, destobj: list) -> tuple[str | None, str | None]:
    if os.path.splitext(file)[1] in VIDEO_CONTAINERS:
        match = re.search(r"[Ss](\d{1,4})\s?(([Ee]\d{1,4})*)", file)
        if match:
            seasonnum = match.groups()[0]
            episodes = match.groups()[1].replace("e", "E").split("E")
            episodes.remove("")
            episodeIDs: list[str] = []
            titles: list[str] = []
            for episode in episodes:
                for epi in seriesobj:
                    if epi["seasonNumber"] == int(seasonnum) and epi["number"] == int(episode):
                        episodeIDs.append(epi["id"])
                        break

            seasonnum = ""
            ep = ""

            for eid in episodeIDs:
                for epi in destobj:
                    if epi["id"] == eid:
                        if isinstance(epi["name"], str):
                            titles.append(epi["name"])
                        else:
                            titles.append("")
                        seasonnum = epi["seasonNumber"]
                        ep = ep + f"E{epi['number']:02d}"
                        break

            if seasonnum == "":
                return "Uncategorized", file

            if len(titles) == 2 and re.sub(r"\(\d+\)", "", titles[0]).strip() == re.sub(r"\(\d+\)", "", titles[1]).strip():
                title = re.sub(r"\(\d+\)", "", titles[0]).strip()
            else:
                title = " + ".join(titles)
            if title != "":
                name = f"{series} - S{seasonnum:02d}{ep} - {title.replace('/', '-')}.mkv"
            else:
                name = f"{series} - S{seasonnum:02d}{ep}.mkv"
            season = f"Season {seasonnum:02d}"
            return season, name

    return None, None


def get_episode(series: str, file: str, seriesobj: list) -> tuple[str | None, str | None, dict[str, str] | None]:
    if os.path.splitext(file)[1] in VIDEO_CONTAINERS:
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
                    if epi["seasonNumber"] == int(seasonnum) and epi["number"] == int(episode):
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
                name = f"{series} - S{seasonnum.rjust(2, '0')}{ep} - {title.replace('/', '-')}.mkv"
            else:
                name = f"{series} - S{seasonnum.rjust(2, '0')}{ep}.mkv"
            season = f"Season {seasonnum.rjust(2, '0')}"
            try:
                comment = " ".join(comments)
            except TypeError:
                comment = None
            metadata: dict[str, str] = {
                "episode_id": ", ".join(epi.removeprefix("0") for epi in episodes),
                "season_number": seasonnum.removeprefix("0"),
                "show": series,
                "comment": comment,
                "title": title,
                "date": date,
            }  # type: ignore
            return season, name, metadata
    return None, None, None


def get_subtitles_from_ost(token: dict[str, str], metadata: dict, lang: str, file: str):
    if token.get("token", None) is None:
        return None
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
    except requests.JSONDecodeError:
        return None
    response = requests.post("https://api.opensubtitles.com/api/v1/download", headers=headers, json={"file_id": subtitle["files"][0]["file_id"]})
    link = response.json()["link"]
    filename = response.json()["file_name"]
    response = requests.get(link, headers=headers)
    content = response.text
    if content == "":
        return None
    _, tmpfile = tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
    with open(tmpfile, "w") as f:
        f.write(content)
    return tmpfile
