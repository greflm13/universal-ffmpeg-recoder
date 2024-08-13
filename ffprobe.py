from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, cast, Callable
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class FormatTags:
    empty: Optional[str] = None
    abj: Optional[str] = None
    actor: Optional[str] = None
    artist: Optional[str] = None
    audiodelay: Optional[str] = None
    bitrate: Optional[str] = None
    canseektoend: Optional[str] = None
    com_android_capture_fps: Optional[str] = None
    com_android_version: Optional[str] = None
    com_apple_quicktime_author: Optional[str] = None
    com_apple_quicktime_description: Optional[str] = None
    com_apple_quicktime_displayname: Optional[str] = None
    com_apple_quicktime_keywords: Optional[str] = None
    com_apple_quicktime_title: Optional[str] = None
    comment: Optional[str] = None
    compatible_brands: Optional[str] = None
    composer: Optional[str] = None
    contact: Optional[str] = None
    content_type: Optional[str] = None
    copyright: Optional[str] = None
    creation_time: Optional[str] = None
    creationdate: Optional[str] = None
    date: Optional[str] = None
    date_recorded: Optional[str] = None
    date_release: Optional[str] = None
    date_released: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    encoded_by: Optional[str] = None
    encoder: Optional[str] = None
    encoder_eng: Optional[str] = None
    episode_id: Optional[str] = None
    episode_sort: Optional[str] = None
    file: Optional[str] = None
    filters: Optional[str] = None
    genre: Optional[str] = None
    hd_video: Optional[str] = None
    hw: Optional[str] = None
    imdb: Optional[str] = None
    imdb_eng: Optional[str] = None
    itunmovi: Optional[str] = None
    keywords: Optional[str] = None
    location: Optional[str] = None
    major_brand: Optional[str] = None
    maxrate: Optional[str] = None
    media_type: Optional[str] = None
    minor_version: Optional[str] = None
    modification_time: Optional[datetime] = None
    movie_comment: Optional[str] = None
    movie_encoder: Optional[str] = None
    producer: Optional[str] = None
    production_studio: Optional[str] = None
    publisher: Optional[str] = None
    purl: Optional[str] = None
    released_by: Optional[str] = None
    scene: Optional[str] = None
    screenplay_by: Optional[str] = None
    season_number: Optional[str] = None
    show: Optional[str] = None
    software: Optional[str] = None
    synopsis: Optional[str] = None
    te_is_reencode: Optional[str] = None
    timecode: Optional[str] = None
    title: Optional[str] = None
    tmdb: Optional[str] = None
    tvdb: Optional[str] = None
    tvdb2: Optional[str] = None
    version: Optional[str] = None
    version_eng: Optional[str] = None
    writing_frontend: Optional[str] = None
    written_by: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'FormatTags':
        assert isinstance(obj, dict)
        empty = from_union([from_str, from_none], obj.get(""))
        abj = from_union([from_str, from_none], obj.get("abj"))
        actor = from_union([from_str, from_none], obj.get("actor"))
        artist = from_union([from_str, from_none], obj.get("artist"))
        audiodelay = from_union([from_str, from_none], obj.get("audiodelay"))
        bitrate = from_union([from_str, from_none], obj.get("bitrate"))
        canseektoend = from_union([from_str, from_none], obj.get("canseektoend"))
        com_android_capture_fps = from_union([from_str, from_none], obj.get("com.android.capture.fps"))
        com_android_version = from_union([from_str, from_none], obj.get("com.android.version"))
        com_apple_quicktime_author = from_union([from_str, from_none], obj.get("com.apple.quicktime.author"))
        com_apple_quicktime_description = from_union([from_str, from_none], obj.get("com.apple.quicktime.description"))
        com_apple_quicktime_displayname = from_union([from_str, from_none], obj.get("com.apple.quicktime.displayname"))
        com_apple_quicktime_keywords = from_union([from_str, from_none], obj.get("com.apple.quicktime.keywords"))
        com_apple_quicktime_title = from_union([from_str, from_none], obj.get("com.apple.quicktime.title"))
        comment = from_union([from_str, from_none], obj.get("comment"))
        compatible_brands = from_union([from_str, from_none], obj.get("compatible_brands"))
        composer = from_union([from_str, from_none], obj.get("composer"))
        contact = from_union([from_str, from_none], obj.get("contact"))
        content_type = from_union([from_str, from_none], obj.get("content_type"))
        copyright = from_union([from_str, from_none], obj.get("copyright"))
        creation_time = from_union([from_str, from_none], obj.get("creation_time"))
        creationdate = from_union([from_str, from_none], obj.get("creationdate"))
        date = from_union([from_str, from_none], obj.get("date"))
        date_recorded = from_union([from_str, from_none], obj.get("date_recorded"))
        date_release = from_union([from_str, from_none], obj.get("date_release"))
        date_released = from_union([from_str, from_none], obj.get("date_released"))
        description = from_union([from_str, from_none], obj.get("description"))
        director = from_union([from_str, from_none], obj.get("director"))
        encoded_by = from_union([from_str, from_none], obj.get("encoded_by"))
        encoder = from_union([from_str, from_none], obj.get("encoder"))
        encoder_eng = from_union([from_str, from_none], obj.get("encoder-eng"))
        episode_id = from_union([from_str, from_none], obj.get("episode_id"))
        episode_sort = from_union([from_str, from_none], obj.get("episode_sort"))
        file = from_union([from_str, from_none], obj.get("file"))
        filters = from_union([from_str, from_none], obj.get("filters"))
        genre = from_union([from_str, from_none], obj.get("genre"))
        hd_video = from_union([from_str, from_none], obj.get("hd_video"))
        hw = from_union([from_str, from_none], obj.get("hw"))
        imdb = from_union([from_str, from_none], obj.get("imdb"))
        imdb_eng = from_union([from_str, from_none], obj.get("imdb-eng"))
        itunmovi = from_union([from_str, from_none], obj.get("itunmovi"))
        keywords = from_union([from_str, from_none], obj.get("keywords"))
        location = from_union([from_str, from_none], obj.get("location"))
        major_brand = from_union([from_str, from_none], obj.get("major_brand"))
        maxrate = from_union([from_str, from_none], obj.get("maxrate"))
        media_type = from_union([from_str, from_none], obj.get("media_type"))
        minor_version = from_union([from_str, from_none], obj.get("minor_version"))
        modification_time = from_union([from_datetime, from_none], obj.get("modification_time"))
        movie_comment = from_union([from_str, from_none], obj.get("movie/comment"))
        movie_encoder = from_union([from_str, from_none], obj.get("movie/encoder"))
        producer = from_union([from_str, from_none], obj.get("producer"))
        production_studio = from_union([from_str, from_none], obj.get("production_studio"))
        publisher = from_union([from_str, from_none], obj.get("publisher"))
        purl = from_union([from_str, from_none], obj.get("purl"))
        released_by = from_union([from_str, from_none], obj.get("released by"))
        scene = from_union([from_str, from_none], obj.get("scene"))
        screenplay_by = from_union([from_str, from_none], obj.get("screenplay_by"))
        season_number = from_union([from_str, from_none], obj.get("season_number"))
        show = from_union([from_str, from_none], obj.get("show"))
        software = from_union([from_str, from_none], obj.get("software"))
        synopsis = from_union([from_str, from_none], obj.get("synopsis"))
        te_is_reencode = from_union([from_str, from_none], obj.get("te_is_reencode"))
        timecode = from_union([from_str, from_none], obj.get("timecode"))
        title = from_union([from_str, from_none], obj.get("title"))
        tmdb = from_union([from_str, from_none], obj.get("tmdb"))
        tvdb = from_union([from_str, from_none], obj.get("tvdb"))
        tvdb2 = from_union([from_str, from_none], obj.get("tvdb2"))
        version = from_union([from_str, from_none], obj.get("version"))
        version_eng = from_union([from_str, from_none], obj.get("version-eng"))
        writing_frontend = from_union([from_str, from_none], obj.get("writing frontend"))
        written_by = from_union([from_str, from_none], obj.get("written_by"))
        return FormatTags(empty, abj, actor, artist, audiodelay, bitrate, canseektoend, com_android_capture_fps, com_android_version, com_apple_quicktime_author, com_apple_quicktime_description, com_apple_quicktime_displayname, com_apple_quicktime_keywords, com_apple_quicktime_title, comment, compatible_brands, composer, contact, content_type, copyright, creation_time, creationdate, date, date_recorded, date_release, date_released, description, director, encoded_by, encoder, encoder_eng, episode_id, episode_sort, file, filters, genre, hd_video, hw, imdb, imdb_eng, itunmovi, keywords, location, major_brand, maxrate, media_type, minor_version, modification_time, movie_comment, movie_encoder, producer, production_studio, publisher, purl, released_by, scene, screenplay_by, season_number, show, software, synopsis, te_is_reencode, timecode, title, tmdb, tvdb, tvdb2, version, version_eng, writing_frontend, written_by)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.empty is not None:
            result[""] = from_union([from_str, from_none], self.empty)
        if self.abj is not None:
            result["abj"] = from_union([from_str, from_none], self.abj)
        if self.actor is not None:
            result["actor"] = from_union([from_str, from_none], self.actor)
        if self.artist is not None:
            result["artist"] = from_union([from_str, from_none], self.artist)
        if self.audiodelay is not None:
            result["audiodelay"] = from_union([from_str, from_none], self.audiodelay)
        if self.bitrate is not None:
            result["bitrate"] = from_union([from_str, from_none], self.bitrate)
        if self.canseektoend is not None:
            result["canseektoend"] = from_union([from_str, from_none], self.canseektoend)
        if self.com_android_capture_fps is not None:
            result["com.android.capture.fps"] = from_union([from_str, from_none], self.com_android_capture_fps)
        if self.com_android_version is not None:
            result["com.android.version"] = from_union([from_str, from_none], self.com_android_version)
        if self.com_apple_quicktime_author is not None:
            result["com.apple.quicktime.author"] = from_union([from_str, from_none], self.com_apple_quicktime_author)
        if self.com_apple_quicktime_description is not None:
            result["com.apple.quicktime.description"] = from_union([from_str, from_none], self.com_apple_quicktime_description)
        if self.com_apple_quicktime_displayname is not None:
            result["com.apple.quicktime.displayname"] = from_union([from_str, from_none], self.com_apple_quicktime_displayname)
        if self.com_apple_quicktime_keywords is not None:
            result["com.apple.quicktime.keywords"] = from_union([from_str, from_none], self.com_apple_quicktime_keywords)
        if self.com_apple_quicktime_title is not None:
            result["com.apple.quicktime.title"] = from_union([from_str, from_none], self.com_apple_quicktime_title)
        if self.comment is not None:
            result["comment"] = from_union([from_str, from_none], self.comment)
        if self.compatible_brands is not None:
            result["compatible_brands"] = from_union([from_str, from_none], self.compatible_brands)
        if self.composer is not None:
            result["composer"] = from_union([from_str, from_none], self.composer)
        if self.contact is not None:
            result["contact"] = from_union([from_str, from_none], self.contact)
        if self.content_type is not None:
            result["content_type"] = from_union([from_str, from_none], self.content_type)
        if self.copyright is not None:
            result["copyright"] = from_union([from_str, from_none], self.copyright)
        if self.creation_time is not None:
            result["creation_time"] = from_union([from_str, from_none], self.creation_time)
        if self.creationdate is not None:
            result["creationdate"] = from_union([from_str, from_none], self.creationdate)
        if self.date is not None:
            result["date"] = from_union([from_str, from_none], self.date)
        if self.date_recorded is not None:
            result["date_recorded"] = from_union([from_str, from_none], self.date_recorded)
        if self.date_release is not None:
            result["date_release"] = from_union([from_str, from_none], self.date_release)
        if self.date_released is not None:
            result["date_released"] = from_union([from_str, from_none], self.date_released)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.director is not None:
            result["director"] = from_union([from_str, from_none], self.director)
        if self.encoded_by is not None:
            result["encoded_by"] = from_union([from_str, from_none], self.encoded_by)
        if self.encoder is not None:
            result["encoder"] = from_union([from_str, from_none], self.encoder)
        if self.encoder_eng is not None:
            result["encoder-eng"] = from_union([from_str, from_none], self.encoder_eng)
        if self.episode_id is not None:
            result["episode_id"] = from_union([from_str, from_none], self.episode_id)
        if self.episode_sort is not None:
            result["episode_sort"] = from_union([from_str, from_none], self.episode_sort)
        if self.file is not None:
            result["file"] = from_union([from_str, from_none], self.file)
        if self.filters is not None:
            result["filters"] = from_union([from_str, from_none], self.filters)
        if self.genre is not None:
            result["genre"] = from_union([from_str, from_none], self.genre)
        if self.hd_video is not None:
            result["hd_video"] = from_union([from_str, from_none], self.hd_video)
        if self.hw is not None:
            result["hw"] = from_union([from_str, from_none], self.hw)
        if self.imdb is not None:
            result["imdb"] = from_union([from_str, from_none], self.imdb)
        if self.imdb_eng is not None:
            result["imdb-eng"] = from_union([from_str, from_none], self.imdb_eng)
        if self.itunmovi is not None:
            result["itunmovi"] = from_union([from_str, from_none], self.itunmovi)
        if self.keywords is not None:
            result["keywords"] = from_union([from_str, from_none], self.keywords)
        if self.location is not None:
            result["location"] = from_union([from_str, from_none], self.location)
        if self.major_brand is not None:
            result["major_brand"] = from_union([from_str, from_none], self.major_brand)
        if self.maxrate is not None:
            result["maxrate"] = from_union([from_str, from_none], self.maxrate)
        if self.media_type is not None:
            result["media_type"] = from_union([from_str, from_none], self.media_type)
        if self.minor_version is not None:
            result["minor_version"] = from_union([from_str, from_none], self.minor_version)
        if self.modification_time is not None:
            result["modification_time"] = from_union([lambda x: x.isoformat(), from_none], self.modification_time)
        if self.movie_comment is not None:
            result["movie/comment"] = from_union([from_str, from_none], self.movie_comment)
        if self.movie_encoder is not None:
            result["movie/encoder"] = from_union([from_str, from_none], self.movie_encoder)
        if self.producer is not None:
            result["producer"] = from_union([from_str, from_none], self.producer)
        if self.production_studio is not None:
            result["production_studio"] = from_union([from_str, from_none], self.production_studio)
        if self.publisher is not None:
            result["publisher"] = from_union([from_str, from_none], self.publisher)
        if self.purl is not None:
            result["purl"] = from_union([from_str, from_none], self.purl)
        if self.released_by is not None:
            result["released by"] = from_union([from_str, from_none], self.released_by)
        if self.scene is not None:
            result["scene"] = from_union([from_str, from_none], self.scene)
        if self.screenplay_by is not None:
            result["screenplay_by"] = from_union([from_str, from_none], self.screenplay_by)
        if self.season_number is not None:
            result["season_number"] = from_union([from_str, from_none], self.season_number)
        if self.show is not None:
            result["show"] = from_union([from_str, from_none], self.show)
        if self.software is not None:
            result["software"] = from_union([from_str, from_none], self.software)
        if self.synopsis is not None:
            result["synopsis"] = from_union([from_str, from_none], self.synopsis)
        if self.te_is_reencode is not None:
            result["te_is_reencode"] = from_union([from_str, from_none], self.te_is_reencode)
        if self.timecode is not None:
            result["timecode"] = from_union([from_str, from_none], self.timecode)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.tmdb is not None:
            result["tmdb"] = from_union([from_str, from_none], self.tmdb)
        if self.tvdb is not None:
            result["tvdb"] = from_union([from_str, from_none], self.tvdb)
        if self.tvdb2 is not None:
            result["tvdb2"] = from_union([from_str, from_none], self.tvdb2)
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        if self.version_eng is not None:
            result["version-eng"] = from_union([from_str, from_none], self.version_eng)
        if self.writing_frontend is not None:
            result["writing frontend"] = from_union([from_str, from_none], self.writing_frontend)
        if self.written_by is not None:
            result["written_by"] = from_union([from_str, from_none], self.written_by)
        return result


@dataclass
class Format:
    bit_rate: str
    duration: str
    filename: str
    format_long_name: str
    format_name: str
    nb_programs: int
    nb_streams: int
    probe_score: int
    size: str
    start_time: Optional[str] = None
    tags: Optional[FormatTags] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Format':
        assert isinstance(obj, dict)
        bit_rate = from_str(obj.get("bit_rate"))
        duration = from_str(obj.get("duration"))
        filename = from_str(obj.get("filename"))
        format_long_name = from_str(obj.get("format_long_name"))
        format_name = from_str(obj.get("format_name"))
        nb_programs = from_int(obj.get("nb_programs"))
        nb_streams = from_int(obj.get("nb_streams"))
        probe_score = from_int(obj.get("probe_score"))
        size = from_str(obj.get("size"))
        start_time = from_union([from_str, from_none], obj.get("start_time"))
        tags = from_union([FormatTags.from_dict, from_none], obj.get("tags"))
        return Format(bit_rate, duration, filename, format_long_name, format_name, nb_programs, nb_streams, probe_score, size, start_time, tags)

    def to_dict(self) -> dict:
        result: dict = {}
        result["bit_rate"] = from_str(self.bit_rate)
        result["duration"] = from_str(self.duration)
        result["filename"] = from_str(self.filename)
        result["format_long_name"] = from_str(self.format_long_name)
        result["format_name"] = from_str(self.format_name)
        result["nb_programs"] = from_int(self.nb_programs)
        result["nb_streams"] = from_int(self.nb_streams)
        result["probe_score"] = from_int(self.probe_score)
        result["size"] = from_str(self.size)
        if self.start_time is not None:
            result["start_time"] = from_union([from_str, from_none], self.start_time)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: to_class(FormatTags, x), from_none], self.tags)
        return result


@dataclass
class Disposition:
    attached_pic: int
    clean_effects: int
    comment: int
    default: int
    dub: int
    forced: int
    hearing_impaired: int
    karaoke: int
    lyrics: int
    original: int
    timed_thumbnails: int
    visual_impaired: int
    captions: Optional[int] = None
    dependent: Optional[int] = None
    descriptions: Optional[int] = None
    metadata: Optional[int] = None
    non_diegetic: Optional[int] = None
    still_image: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Disposition':
        assert isinstance(obj, dict)
        attached_pic = from_int(obj.get("attached_pic"))
        clean_effects = from_int(obj.get("clean_effects"))
        comment = from_int(obj.get("comment"))
        default = from_int(obj.get("default"))
        dub = from_int(obj.get("dub"))
        forced = from_int(obj.get("forced"))
        hearing_impaired = from_int(obj.get("hearing_impaired"))
        karaoke = from_int(obj.get("karaoke"))
        lyrics = from_int(obj.get("lyrics"))
        original = from_int(obj.get("original"))
        timed_thumbnails = from_int(obj.get("timed_thumbnails"))
        visual_impaired = from_int(obj.get("visual_impaired"))
        captions = from_union([from_int, from_none], obj.get("captions"))
        dependent = from_union([from_int, from_none], obj.get("dependent"))
        descriptions = from_union([from_int, from_none], obj.get("descriptions"))
        metadata = from_union([from_int, from_none], obj.get("metadata"))
        non_diegetic = from_union([from_int, from_none], obj.get("non_diegetic"))
        still_image = from_union([from_int, from_none], obj.get("still_image"))
        return Disposition(attached_pic, clean_effects, comment, default, dub, forced, hearing_impaired, karaoke, lyrics, original, timed_thumbnails, visual_impaired, captions, dependent, descriptions, metadata, non_diegetic, still_image)

    def to_dict(self) -> dict:
        result: dict = {}
        result["attached_pic"] = from_int(self.attached_pic)
        result["clean_effects"] = from_int(self.clean_effects)
        result["comment"] = from_int(self.comment)
        result["default"] = from_int(self.default)
        result["dub"] = from_int(self.dub)
        result["forced"] = from_int(self.forced)
        result["hearing_impaired"] = from_int(self.hearing_impaired)
        result["karaoke"] = from_int(self.karaoke)
        result["lyrics"] = from_int(self.lyrics)
        result["original"] = from_int(self.original)
        result["timed_thumbnails"] = from_int(self.timed_thumbnails)
        result["visual_impaired"] = from_int(self.visual_impaired)
        if self.captions is not None:
            result["captions"] = from_union([from_int, from_none], self.captions)
        if self.dependent is not None:
            result["dependent"] = from_union([from_int, from_none], self.dependent)
        if self.descriptions is not None:
            result["descriptions"] = from_union([from_int, from_none], self.descriptions)
        if self.metadata is not None:
            result["metadata"] = from_union([from_int, from_none], self.metadata)
        if self.non_diegetic is not None:
            result["non_diegetic"] = from_union([from_int, from_none], self.non_diegetic)
        if self.still_image is not None:
            result["still_image"] = from_union([from_int, from_none], self.still_image)
        return result


@dataclass
class SideDataList:
    side_data_type: str
    avg_bitrate: Optional[int] = None
    blue_x: Optional[str] = None
    blue_y: Optional[str] = None
    buffer_size: Optional[int] = None
    displaymatrix: Optional[str] = None
    green_x: Optional[str] = None
    green_y: Optional[str] = None
    inverted: Optional[int] = None
    max_average: Optional[int] = None
    max_bitrate: Optional[int] = None
    max_content: Optional[int] = None
    max_luminance: Optional[str] = None
    min_bitrate: Optional[int] = None
    min_luminance: Optional[str] = None
    pitch: Optional[int] = None
    projection: Optional[str] = None
    red_x: Optional[str] = None
    red_y: Optional[str] = None
    roll: Optional[int] = None
    rotation: Optional[int] = None
    service_type: Optional[int] = None
    type: Optional[str] = None
    vbv_delay: Optional[int] = None
    white_point_x: Optional[str] = None
    white_point_y: Optional[str] = None
    yaw: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SideDataList':
        assert isinstance(obj, dict)
        side_data_type = from_str(obj.get("side_data_type"))
        avg_bitrate = from_union([from_int, from_none], obj.get("avg_bitrate"))
        blue_x = from_union([from_str, from_none], obj.get("blue_x"))
        blue_y = from_union([from_str, from_none], obj.get("blue_y"))
        buffer_size = from_union([from_int, from_none], obj.get("buffer_size"))
        displaymatrix = from_union([from_str, from_none], obj.get("displaymatrix"))
        green_x = from_union([from_str, from_none], obj.get("green_x"))
        green_y = from_union([from_str, from_none], obj.get("green_y"))
        inverted = from_union([from_int, from_none], obj.get("inverted"))
        max_average = from_union([from_int, from_none], obj.get("max_average"))
        max_bitrate = from_union([from_int, from_none], obj.get("max_bitrate"))
        max_content = from_union([from_int, from_none], obj.get("max_content"))
        max_luminance = from_union([from_str, from_none], obj.get("max_luminance"))
        min_bitrate = from_union([from_int, from_none], obj.get("min_bitrate"))
        min_luminance = from_union([from_str, from_none], obj.get("min_luminance"))
        pitch = from_union([from_int, from_none], obj.get("pitch"))
        projection = from_union([from_str, from_none], obj.get("projection"))
        red_x = from_union([from_str, from_none], obj.get("red_x"))
        red_y = from_union([from_str, from_none], obj.get("red_y"))
        roll = from_union([from_int, from_none], obj.get("roll"))
        rotation = from_union([from_int, from_none], obj.get("rotation"))
        service_type = from_union([from_int, from_none], obj.get("service_type"))
        type = from_union([from_str, from_none], obj.get("type"))
        vbv_delay = from_union([from_int, from_none], obj.get("vbv_delay"))
        white_point_x = from_union([from_str, from_none], obj.get("white_point_x"))
        white_point_y = from_union([from_str, from_none], obj.get("white_point_y"))
        yaw = from_union([from_int, from_none], obj.get("yaw"))
        return SideDataList(side_data_type, avg_bitrate, blue_x, blue_y, buffer_size, displaymatrix, green_x, green_y, inverted, max_average, max_bitrate, max_content, max_luminance, min_bitrate, min_luminance, pitch, projection, red_x, red_y, roll, rotation, service_type, type, vbv_delay, white_point_x, white_point_y, yaw)

    def to_dict(self) -> dict:
        result: dict = {}
        result["side_data_type"] = from_str(self.side_data_type)
        if self.avg_bitrate is not None:
            result["avg_bitrate"] = from_union([from_int, from_none], self.avg_bitrate)
        if self.blue_x is not None:
            result["blue_x"] = from_union([from_str, from_none], self.blue_x)
        if self.blue_y is not None:
            result["blue_y"] = from_union([from_str, from_none], self.blue_y)
        if self.buffer_size is not None:
            result["buffer_size"] = from_union([from_int, from_none], self.buffer_size)
        if self.displaymatrix is not None:
            result["displaymatrix"] = from_union([from_str, from_none], self.displaymatrix)
        if self.green_x is not None:
            result["green_x"] = from_union([from_str, from_none], self.green_x)
        if self.green_y is not None:
            result["green_y"] = from_union([from_str, from_none], self.green_y)
        if self.inverted is not None:
            result["inverted"] = from_union([from_int, from_none], self.inverted)
        if self.max_average is not None:
            result["max_average"] = from_union([from_int, from_none], self.max_average)
        if self.max_bitrate is not None:
            result["max_bitrate"] = from_union([from_int, from_none], self.max_bitrate)
        if self.max_content is not None:
            result["max_content"] = from_union([from_int, from_none], self.max_content)
        if self.max_luminance is not None:
            result["max_luminance"] = from_union([from_str, from_none], self.max_luminance)
        if self.min_bitrate is not None:
            result["min_bitrate"] = from_union([from_int, from_none], self.min_bitrate)
        if self.min_luminance is not None:
            result["min_luminance"] = from_union([from_str, from_none], self.min_luminance)
        if self.pitch is not None:
            result["pitch"] = from_union([from_int, from_none], self.pitch)
        if self.projection is not None:
            result["projection"] = from_union([from_str, from_none], self.projection)
        if self.red_x is not None:
            result["red_x"] = from_union([from_str, from_none], self.red_x)
        if self.red_y is not None:
            result["red_y"] = from_union([from_str, from_none], self.red_y)
        if self.roll is not None:
            result["roll"] = from_union([from_int, from_none], self.roll)
        if self.rotation is not None:
            result["rotation"] = from_union([from_int, from_none], self.rotation)
        if self.service_type is not None:
            result["service_type"] = from_union([from_int, from_none], self.service_type)
        if self.type is not None:
            result["type"] = from_union([from_str, from_none], self.type)
        if self.vbv_delay is not None:
            result["vbv_delay"] = from_union([from_int, from_none], self.vbv_delay)
        if self.white_point_x is not None:
            result["white_point_x"] = from_union([from_str, from_none], self.white_point_x)
        if self.white_point_y is not None:
            result["white_point_y"] = from_union([from_str, from_none], self.white_point_y)
        if self.yaw is not None:
            result["yaw"] = from_union([from_int, from_none], self.yaw)
        return result


@dataclass
class StreamTags:
    statistics_tags: Optional[str] = None
    statistics_tags_eng: Optional[str] = None
    statistics_writing_app: Optional[str] = None
    statistics_writing_app_eng: Optional[str] = None
    statistics_writing_date_utc: Optional[str] = None
    statistics_writing_date_utc_eng: Optional[str] = None
    alpha_mode: Optional[str] = None
    bps: Optional[str] = None
    bps_eng: Optional[str] = None
    creation_time: Optional[datetime] = None
    duration: Optional[str] = None
    duration_eng: Optional[str] = None
    encoder: Optional[str] = None
    encoder_options: Optional[str] = None
    filename: Optional[str] = None
    handler_name: Optional[str] = None
    language: Optional[str] = None
    mimetype: Optional[str] = None
    number_of_bytes: Optional[str] = None
    number_of_bytes_eng: Optional[str] = None
    number_of_frames: Optional[str] = None
    number_of_frames_eng: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    source_id_eng: Optional[str] = None
    timecode: Optional[str] = None
    title: Optional[str] = None
    track: Optional[str] = None
    vendor_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'StreamTags':
        assert isinstance(obj, dict)
        statistics_tags = from_union([from_str, from_none], obj.get("_statistics_tags"))
        statistics_tags_eng = from_union([from_str, from_none], obj.get("_statistics_tags-eng"))
        statistics_writing_app = from_union([from_str, from_none], obj.get("_statistics_writing_app"))
        statistics_writing_app_eng = from_union([from_str, from_none], obj.get("_statistics_writing_app-eng"))
        statistics_writing_date_utc = from_union([from_str, from_none], obj.get("_statistics_writing_date_utc"))
        statistics_writing_date_utc_eng = from_union([from_str, from_none], obj.get("_statistics_writing_date_utc-eng"))
        alpha_mode = from_union([from_str, from_none], obj.get("alpha_mode"))
        bps = from_union([from_str, from_none], obj.get("bps"))
        bps_eng = from_union([from_str, from_none], obj.get("bps-eng"))
        creation_time = from_union([from_datetime, from_none], obj.get("creation_time"))
        duration = from_union([from_str, from_none], obj.get("duration"))
        duration_eng = from_union([from_str, from_none], obj.get("duration-eng"))
        encoder = from_union([from_str, from_none], obj.get("encoder"))
        encoder_options = from_union([from_str, from_none], obj.get("encoder_options"))
        filename = from_union([from_str, from_none], obj.get("filename"))
        handler_name = from_union([from_str, from_none], obj.get("handler_name"))
        language = from_union([from_str, from_none], obj.get("language"))
        mimetype = from_union([from_str, from_none], obj.get("mimetype"))
        number_of_bytes = from_union([from_str, from_none], obj.get("number_of_bytes"))
        number_of_bytes_eng = from_union([from_str, from_none], obj.get("number_of_bytes-eng"))
        number_of_frames = from_union([from_str, from_none], obj.get("number_of_frames"))
        number_of_frames_eng = from_union([from_str, from_none], obj.get("number_of_frames-eng"))
        source = from_union([from_str, from_none], obj.get("source"))
        source_id = from_union([from_str, from_none], obj.get("source_id"))
        source_id_eng = from_union([from_str, from_none], obj.get("source_id-eng"))
        timecode = from_union([from_str, from_none], obj.get("timecode"))
        title = from_union([from_str, from_none], obj.get("title"))
        track = from_union([from_str, from_none], obj.get("track"))
        vendor_id = from_union([from_str, from_none], obj.get("vendor_id"))
        return StreamTags(statistics_tags, statistics_tags_eng, statistics_writing_app, statistics_writing_app_eng, statistics_writing_date_utc, statistics_writing_date_utc_eng, alpha_mode, bps, bps_eng, creation_time, duration, duration_eng, encoder, encoder_options, filename, handler_name, language, mimetype, number_of_bytes, number_of_bytes_eng, number_of_frames, number_of_frames_eng, source, source_id, source_id_eng, timecode, title, track, vendor_id)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.statistics_tags is not None:
            result["_statistics_tags"] = from_union([from_str, from_none], self.statistics_tags)
        if self.statistics_tags_eng is not None:
            result["_statistics_tags-eng"] = from_union([from_str, from_none], self.statistics_tags_eng)
        if self.statistics_writing_app is not None:
            result["_statistics_writing_app"] = from_union([from_str, from_none], self.statistics_writing_app)
        if self.statistics_writing_app_eng is not None:
            result["_statistics_writing_app-eng"] = from_union([from_str, from_none], self.statistics_writing_app_eng)
        if self.statistics_writing_date_utc is not None:
            result["_statistics_writing_date_utc"] = from_union([from_str, from_none], self.statistics_writing_date_utc)
        if self.statistics_writing_date_utc_eng is not None:
            result["_statistics_writing_date_utc-eng"] = from_union([from_str, from_none], self.statistics_writing_date_utc_eng)
        if self.alpha_mode is not None:
            result["alpha_mode"] = from_union([from_str, from_none], self.alpha_mode)
        if self.bps is not None:
            result["bps"] = from_union([from_str, from_none], self.bps)
        if self.bps_eng is not None:
            result["bps-eng"] = from_union([from_str, from_none], self.bps_eng)
        if self.creation_time is not None:
            result["creation_time"] = from_union([lambda x: x.isoformat(), from_none], self.creation_time)
        if self.duration is not None:
            result["duration"] = from_union([from_str, from_none], self.duration)
        if self.duration_eng is not None:
            result["duration-eng"] = from_union([from_str, from_none], self.duration_eng)
        if self.encoder is not None:
            result["encoder"] = from_union([from_str, from_none], self.encoder)
        if self.encoder_options is not None:
            result["encoder_options"] = from_union([from_str, from_none], self.encoder_options)
        if self.filename is not None:
            result["filename"] = from_union([from_str, from_none], self.filename)
        if self.handler_name is not None:
            result["handler_name"] = from_union([from_str, from_none], self.handler_name)
        if self.language is not None:
            result["language"] = from_union([from_str, from_none], self.language)
        if self.mimetype is not None:
            result["mimetype"] = from_union([from_str, from_none], self.mimetype)
        if self.number_of_bytes is not None:
            result["number_of_bytes"] = from_union([from_str, from_none], self.number_of_bytes)
        if self.number_of_bytes_eng is not None:
            result["number_of_bytes-eng"] = from_union([from_str, from_none], self.number_of_bytes_eng)
        if self.number_of_frames is not None:
            result["number_of_frames"] = from_union([from_str, from_none], self.number_of_frames)
        if self.number_of_frames_eng is not None:
            result["number_of_frames-eng"] = from_union([from_str, from_none], self.number_of_frames_eng)
        if self.source is not None:
            result["source"] = from_union([from_str, from_none], self.source)
        if self.source_id is not None:
            result["source_id"] = from_union([from_str, from_none], self.source_id)
        if self.source_id_eng is not None:
            result["source_id-eng"] = from_union([from_str, from_none], self.source_id_eng)
        if self.timecode is not None:
            result["timecode"] = from_union([from_str, from_none], self.timecode)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.track is not None:
            result["track"] = from_union([from_str, from_none], self.track)
        if self.vendor_id is not None:
            result["vendor_id"] = from_union([from_str, from_none], self.vendor_id)
        return result


@dataclass
class Stream:
    avg_frame_rate: str
    codec_tag: str
    codec_tag_string: str
    codec_type: str
    disposition: Disposition
    index: int
    r_frame_rate: str
    time_base: str
    bit_rate: Optional[str] = None
    bits_per_raw_sample: Optional[str] = None
    bits_per_sample: Optional[int] = None
    channel_layout: Optional[str] = None
    channels: Optional[int] = None
    chroma_location: Optional[str] = None
    closed_captions: Optional[int] = None
    codec_long_name: Optional[str] = None
    codec_name: Optional[str] = None
    coded_height: Optional[int] = None
    coded_width: Optional[int] = None
    color_primaries: Optional[str] = None
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    divx_packed: Optional[str] = None
    dmix_mode: Optional[str] = None
    duration: Optional[str] = None
    duration_ts: Optional[int] = None
    extradata_size: Optional[int] = None
    field_order: Optional[str] = None
    film_grain: Optional[int] = None
    has_b_frames: Optional[int] = None
    height: Optional[int] = None
    id: Optional[str] = None
    initial_padding: Optional[int] = None
    is_avc: Optional[str] = None
    level: Optional[int] = None
    loro_cmixlev: Optional[str] = None
    loro_surmixlev: Optional[str] = None
    ltrt_cmixlev: Optional[str] = None
    ltrt_surmixlev: Optional[str] = None
    missing_streams: Optional[str] = None
    nal_length_size: Optional[str] = None
    nb_frames: Optional[str] = None
    pix_fmt: Optional[str] = None
    profile: Optional[str] = None
    quarter_sample: Optional[str] = None
    refs: Optional[int] = None
    sample_aspect_ratio: Optional[str] = None
    sample_fmt: Optional[str] = None
    sample_rate: Optional[str] = None
    side_data_list: Optional[List[SideDataList]] = None
    start_pts: Optional[int] = None
    start_time: Optional[str] = None
    tags: Optional[StreamTags] = None
    width: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Stream':
        assert isinstance(obj, dict)
        avg_frame_rate = from_str(obj.get("avg_frame_rate"))
        codec_tag = from_str(obj.get("codec_tag"))
        codec_tag_string = from_str(obj.get("codec_tag_string"))
        codec_type = from_str(obj.get("codec_type"))
        disposition = Disposition.from_dict(obj.get("disposition"))
        index = from_int(obj.get("index"))
        r_frame_rate = from_str(obj.get("r_frame_rate"))
        time_base = from_str(obj.get("time_base"))
        bit_rate = from_union([from_str, from_none], obj.get("bit_rate"))
        bits_per_raw_sample = from_union([from_str, from_none], obj.get("bits_per_raw_sample"))
        bits_per_sample = from_union([from_int, from_none], obj.get("bits_per_sample"))
        channel_layout = from_union([from_str, from_none], obj.get("channel_layout"))
        channels = from_union([from_int, from_none], obj.get("channels"))
        chroma_location = from_union([from_str, from_none], obj.get("chroma_location"))
        closed_captions = from_union([from_int, from_none], obj.get("closed_captions"))
        codec_long_name = from_union([from_str, from_none], obj.get("codec_long_name"))
        codec_name = from_union([from_str, from_none], obj.get("codec_name"))
        coded_height = from_union([from_int, from_none], obj.get("coded_height"))
        coded_width = from_union([from_int, from_none], obj.get("coded_width"))
        color_primaries = from_union([from_str, from_none], obj.get("color_primaries"))
        color_range = from_union([from_str, from_none], obj.get("color_range"))
        color_space = from_union([from_str, from_none], obj.get("color_space"))
        color_transfer = from_union([from_str, from_none], obj.get("color_transfer"))
        display_aspect_ratio = from_union([from_str, from_none], obj.get("display_aspect_ratio"))
        divx_packed = from_union([from_str, from_none], obj.get("divx_packed"))
        dmix_mode = from_union([from_str, from_none], obj.get("dmix_mode"))
        duration = from_union([from_str, from_none], obj.get("duration"))
        duration_ts = from_union([from_int, from_none], obj.get("duration_ts"))
        extradata_size = from_union([from_int, from_none], obj.get("extradata_size"))
        field_order = from_union([from_str, from_none], obj.get("field_order"))
        film_grain = from_union([from_int, from_none], obj.get("film_grain"))
        has_b_frames = from_union([from_int, from_none], obj.get("has_b_frames"))
        height = from_union([from_int, from_none], obj.get("height"))
        id = from_union([from_str, from_none], obj.get("id"))
        initial_padding = from_union([from_int, from_none], obj.get("initial_padding"))
        is_avc = from_union([from_str, from_none], obj.get("is_avc"))
        level = from_union([from_int, from_none], obj.get("level"))
        loro_cmixlev = from_union([from_str, from_none], obj.get("loro_cmixlev"))
        loro_surmixlev = from_union([from_str, from_none], obj.get("loro_surmixlev"))
        ltrt_cmixlev = from_union([from_str, from_none], obj.get("ltrt_cmixlev"))
        ltrt_surmixlev = from_union([from_str, from_none], obj.get("ltrt_surmixlev"))
        missing_streams = from_union([from_str, from_none], obj.get("missing_streams"))
        nal_length_size = from_union([from_str, from_none], obj.get("nal_length_size"))
        nb_frames = from_union([from_str, from_none], obj.get("nb_frames"))
        pix_fmt = from_union([from_str, from_none], obj.get("pix_fmt"))
        profile = from_union([from_str, from_none], obj.get("profile"))
        quarter_sample = from_union([from_str, from_none], obj.get("quarter_sample"))
        refs = from_union([from_int, from_none], obj.get("refs"))
        sample_aspect_ratio = from_union([from_str, from_none], obj.get("sample_aspect_ratio"))
        sample_fmt = from_union([from_str, from_none], obj.get("sample_fmt"))
        sample_rate = from_union([from_str, from_none], obj.get("sample_rate"))
        side_data_list = from_union([lambda x: from_list(SideDataList.from_dict, x), from_none], obj.get("side_data_list"))
        start_pts = from_union([from_int, from_none], obj.get("start_pts"))
        start_time = from_union([from_str, from_none], obj.get("start_time"))
        tags = from_union([StreamTags.from_dict, from_none], obj.get("tags"))
        width = from_union([from_int, from_none], obj.get("width"))
        return Stream(avg_frame_rate, codec_tag, codec_tag_string, codec_type, disposition, index, r_frame_rate, time_base, bit_rate, bits_per_raw_sample, bits_per_sample, channel_layout, channels, chroma_location, closed_captions, codec_long_name, codec_name, coded_height, coded_width, color_primaries, color_range, color_space, color_transfer, display_aspect_ratio, divx_packed, dmix_mode, duration, duration_ts, extradata_size, field_order, film_grain, has_b_frames, height, id, initial_padding, is_avc, level, loro_cmixlev, loro_surmixlev, ltrt_cmixlev, ltrt_surmixlev, missing_streams, nal_length_size, nb_frames, pix_fmt, profile, quarter_sample, refs, sample_aspect_ratio, sample_fmt, sample_rate, side_data_list, start_pts, start_time, tags, width)

    def to_dict(self) -> dict:
        result: dict = {}
        result["avg_frame_rate"] = from_str(self.avg_frame_rate)
        result["codec_tag"] = from_str(self.codec_tag)
        result["codec_tag_string"] = from_str(self.codec_tag_string)
        result["codec_type"] = from_str(self.codec_type)
        result["disposition"] = to_class(Disposition, self.disposition)
        result["index"] = from_int(self.index)
        result["r_frame_rate"] = from_str(self.r_frame_rate)
        result["time_base"] = from_str(self.time_base)
        if self.bit_rate is not None:
            result["bit_rate"] = from_union([from_str, from_none], self.bit_rate)
        if self.bits_per_raw_sample is not None:
            result["bits_per_raw_sample"] = from_union([from_str, from_none], self.bits_per_raw_sample)
        if self.bits_per_sample is not None:
            result["bits_per_sample"] = from_union([from_int, from_none], self.bits_per_sample)
        if self.channel_layout is not None:
            result["channel_layout"] = from_union([from_str, from_none], self.channel_layout)
        if self.channels is not None:
            result["channels"] = from_union([from_int, from_none], self.channels)
        if self.chroma_location is not None:
            result["chroma_location"] = from_union([from_str, from_none], self.chroma_location)
        if self.closed_captions is not None:
            result["closed_captions"] = from_union([from_int, from_none], self.closed_captions)
        if self.codec_long_name is not None:
            result["codec_long_name"] = from_union([from_str, from_none], self.codec_long_name)
        if self.codec_name is not None:
            result["codec_name"] = from_union([from_str, from_none], self.codec_name)
        if self.coded_height is not None:
            result["coded_height"] = from_union([from_int, from_none], self.coded_height)
        if self.coded_width is not None:
            result["coded_width"] = from_union([from_int, from_none], self.coded_width)
        if self.color_primaries is not None:
            result["color_primaries"] = from_union([from_str, from_none], self.color_primaries)
        if self.color_range is not None:
            result["color_range"] = from_union([from_str, from_none], self.color_range)
        if self.color_space is not None:
            result["color_space"] = from_union([from_str, from_none], self.color_space)
        if self.color_transfer is not None:
            result["color_transfer"] = from_union([from_str, from_none], self.color_transfer)
        if self.display_aspect_ratio is not None:
            result["display_aspect_ratio"] = from_union([from_str, from_none], self.display_aspect_ratio)
        if self.divx_packed is not None:
            result["divx_packed"] = from_union([from_str, from_none], self.divx_packed)
        if self.dmix_mode is not None:
            result["dmix_mode"] = from_union([from_str, from_none], self.dmix_mode)
        if self.duration is not None:
            result["duration"] = from_union([from_str, from_none], self.duration)
        if self.duration_ts is not None:
            result["duration_ts"] = from_union([from_int, from_none], self.duration_ts)
        if self.extradata_size is not None:
            result["extradata_size"] = from_union([from_int, from_none], self.extradata_size)
        if self.field_order is not None:
            result["field_order"] = from_union([from_str, from_none], self.field_order)
        if self.film_grain is not None:
            result["film_grain"] = from_union([from_int, from_none], self.film_grain)
        if self.has_b_frames is not None:
            result["has_b_frames"] = from_union([from_int, from_none], self.has_b_frames)
        if self.height is not None:
            result["height"] = from_union([from_int, from_none], self.height)
        if self.id is not None:
            result["id"] = from_union([from_str, from_none], self.id)
        if self.initial_padding is not None:
            result["initial_padding"] = from_union([from_int, from_none], self.initial_padding)
        if self.is_avc is not None:
            result["is_avc"] = from_union([from_str, from_none], self.is_avc)
        if self.level is not None:
            result["level"] = from_union([from_int, from_none], self.level)
        if self.loro_cmixlev is not None:
            result["loro_cmixlev"] = from_union([from_str, from_none], self.loro_cmixlev)
        if self.loro_surmixlev is not None:
            result["loro_surmixlev"] = from_union([from_str, from_none], self.loro_surmixlev)
        if self.ltrt_cmixlev is not None:
            result["ltrt_cmixlev"] = from_union([from_str, from_none], self.ltrt_cmixlev)
        if self.ltrt_surmixlev is not None:
            result["ltrt_surmixlev"] = from_union([from_str, from_none], self.ltrt_surmixlev)
        if self.missing_streams is not None:
            result["missing_streams"] = from_union([from_str, from_none], self.missing_streams)
        if self.nal_length_size is not None:
            result["nal_length_size"] = from_union([from_str, from_none], self.nal_length_size)
        if self.nb_frames is not None:
            result["nb_frames"] = from_union([from_str, from_none], self.nb_frames)
        if self.pix_fmt is not None:
            result["pix_fmt"] = from_union([from_str, from_none], self.pix_fmt)
        if self.profile is not None:
            result["profile"] = from_union([from_str, from_none], self.profile)
        if self.quarter_sample is not None:
            result["quarter_sample"] = from_union([from_str, from_none], self.quarter_sample)
        if self.refs is not None:
            result["refs"] = from_union([from_int, from_none], self.refs)
        if self.sample_aspect_ratio is not None:
            result["sample_aspect_ratio"] = from_union([from_str, from_none], self.sample_aspect_ratio)
        if self.sample_fmt is not None:
            result["sample_fmt"] = from_union([from_str, from_none], self.sample_fmt)
        if self.sample_rate is not None:
            result["sample_rate"] = from_union([from_str, from_none], self.sample_rate)
        if self.side_data_list is not None:
            result["side_data_list"] = from_union([lambda x: from_list(lambda x: to_class(SideDataList, x), x), from_none], self.side_data_list)
        if self.start_pts is not None:
            result["start_pts"] = from_union([from_int, from_none], self.start_pts)
        if self.start_time is not None:
            result["start_time"] = from_union([from_str, from_none], self.start_time)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: to_class(StreamTags, x), from_none], self.tags)
        if self.width is not None:
            result["width"] = from_union([from_int, from_none], self.width)
        return result


@dataclass
class Ffprobe:
    format: Format
    streams: List[Stream]

    @staticmethod
    def from_dict(obj: Any) -> 'Ffprobe':
        assert isinstance(obj, dict)
        format = Format.from_dict(obj.get("format"))
        streams = from_list(Stream.from_dict, obj.get("streams"))
        return Ffprobe(format, streams)

    def to_dict(self) -> dict:
        result: dict = {}
        result["format"] = to_class(Format, self.format)
        result["streams"] = from_list(lambda x: to_class(Stream, x), self.streams)
        return result


def f_fprobe_from_dict(s: Any) -> Ffprobe:
    return Ffprobe.from_dict(s)


def f_fprobe_to_dict(x: Ffprobe) -> Any:
    return to_class(Ffprobe, x)
