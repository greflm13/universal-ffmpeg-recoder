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
    artist: Optional[str] = None
    tags_artist: Optional[str] = None
    audiodelay: Optional[str] = None
    bitrate: Optional[str] = None
    can_seek_to_end: Optional[str] = None
    com_android_capture_fps: Optional[str] = None
    com_android_version: Optional[str] = None
    tags_com_apple_quicktime_author: Optional[str] = None
    com_apple_quicktime_author: Optional[str] = None
    tags_com_apple_quicktime_description: Optional[str] = None
    com_apple_quicktime_description: Optional[str] = None
    tags_com_apple_quicktime_displayname: Optional[str] = None
    com_apple_quicktime_displayname: Optional[str] = None
    tags_com_apple_quicktime_keywords: Optional[str] = None
    com_apple_quicktime_keywords: Optional[str] = None
    tags_com_apple_quicktime_title: Optional[str] = None
    com_apple_quicktime_title: Optional[str] = None
    tags_comment: Optional[str] = None
    comment: Optional[str] = None
    tags_compatible_brands: Optional[str] = None
    compatible_brands: Optional[str] = None
    composer: Optional[str] = None
    creation_time: Optional[str] = None
    creationdate: Optional[str] = None
    date: Optional[str] = None
    tags_date: Optional[str] = None
    description: Optional[str] = None
    tags_description: Optional[str] = None
    tags_encoder: Optional[str] = None
    encoder: Optional[str] = None
    encoder_eng: Optional[str] = None
    episode_sort: Optional[str] = None
    file: Optional[str] = None
    hd_video: Optional[str] = None
    hw: Optional[str] = None
    i_tun_movi: Optional[str] = None
    keywords: Optional[str] = None
    location: Optional[str] = None
    tags_major_brand: Optional[str] = None
    major_brand: Optional[str] = None
    maxrate: Optional[str] = None
    media_type: Optional[str] = None
    tags_minor_version: Optional[str] = None
    minor_version: Optional[str] = None
    modification_time: Optional[datetime] = None
    purl: Optional[str] = None
    scene: Optional[str] = None
    season_number: Optional[str] = None
    software: Optional[str] = None
    summary: Optional[str] = None
    synopsis: Optional[str] = None
    tags_synopsis: Optional[str] = None
    te_is_reencode: Optional[str] = None
    timecode: Optional[str] = None
    title: Optional[str] = None
    writing_frontend: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "FormatTags":
        assert isinstance(obj, dict)
        artist = from_union([from_str, from_none], obj.get("ARTIST"))
        tags_artist = from_union([from_str, from_none], obj.get("artist"))
        audiodelay = from_union([from_str, from_none], obj.get("audiodelay"))
        bitrate = from_union([from_str, from_none], obj.get("bitrate"))
        can_seek_to_end = from_union([from_str, from_none], obj.get("canSeekToEnd"))
        com_android_capture_fps = from_union([from_str, from_none], obj.get("com.android.capture.fps"))
        com_android_version = from_union([from_str, from_none], obj.get("com.android.version"))
        tags_com_apple_quicktime_author = from_union([from_str, from_none], obj.get("com.apple.quicktime.author"))
        com_apple_quicktime_author = from_union([from_str, from_none], obj.get("COM.APPLE.QUICKTIME.AUTHOR"))
        tags_com_apple_quicktime_description = from_union([from_str, from_none], obj.get("com.apple.quicktime.description"))
        com_apple_quicktime_description = from_union([from_str, from_none], obj.get("COM.APPLE.QUICKTIME.DESCRIPTION"))
        tags_com_apple_quicktime_displayname = from_union([from_str, from_none], obj.get("com.apple.quicktime.displayname"))
        com_apple_quicktime_displayname = from_union([from_str, from_none], obj.get("COM.APPLE.QUICKTIME.DISPLAYNAME"))
        tags_com_apple_quicktime_keywords = from_union([from_str, from_none], obj.get("com.apple.quicktime.keywords"))
        com_apple_quicktime_keywords = from_union([from_str, from_none], obj.get("COM.APPLE.QUICKTIME.KEYWORDS"))
        tags_com_apple_quicktime_title = from_union([from_str, from_none], obj.get("com.apple.quicktime.title"))
        com_apple_quicktime_title = from_union([from_str, from_none], obj.get("COM.APPLE.QUICKTIME.TITLE"))
        tags_comment = from_union([from_str, from_none], obj.get("comment"))
        comment = from_union([from_str, from_none], obj.get("COMMENT"))
        tags_compatible_brands = from_union([from_str, from_none], obj.get("compatible_brands"))
        compatible_brands = from_union([from_str, from_none], obj.get("COMPATIBLE_BRANDS"))
        composer = from_union([from_str, from_none], obj.get("composer"))
        creation_time = from_union([from_str, from_none], obj.get("creation_time"))
        creationdate = from_union([from_str, from_none], obj.get("creationdate"))
        date = from_union([from_str, from_none], obj.get("DATE"))
        tags_date = from_union([from_str, from_none], obj.get("date"))
        description = from_union([from_str, from_none], obj.get("DESCRIPTION"))
        tags_description = from_union([from_str, from_none], obj.get("description"))
        tags_encoder = from_union([from_str, from_none], obj.get("encoder"))
        encoder = from_union([from_str, from_none], obj.get("ENCODER"))
        encoder_eng = from_union([from_str, from_none], obj.get("encoder-eng"))
        episode_sort = from_union([from_str, from_none], obj.get("episode_sort"))
        file = from_union([from_str, from_none], obj.get("FILE"))
        hd_video = from_union([from_str, from_none], obj.get("hd_video"))
        hw = from_union([from_str, from_none], obj.get("Hw"))
        i_tun_movi = from_union([from_str, from_none], obj.get("iTunMOVI"))
        keywords = from_union([from_str, from_none], obj.get("KEYWORDS"))
        location = from_union([from_str, from_none], obj.get("location"))
        tags_major_brand = from_union([from_str, from_none], obj.get("major_brand"))
        major_brand = from_union([from_str, from_none], obj.get("MAJOR_BRAND"))
        maxrate = from_union([from_str, from_none], obj.get("maxrate"))
        media_type = from_union([from_str, from_none], obj.get("media_type"))
        tags_minor_version = from_union([from_str, from_none], obj.get("minor_version"))
        minor_version = from_union([from_str, from_none], obj.get("MINOR_VERSION"))
        modification_time = from_union([from_datetime, from_none], obj.get("modification_time"))
        purl = from_union([from_str, from_none], obj.get("PURL"))
        scene = from_union([from_str, from_none], obj.get("SCENE"))
        season_number = from_union([from_str, from_none], obj.get("season_number"))
        software = from_union([from_str, from_none], obj.get("software"))
        summary = from_union([from_str, from_none], obj.get("SUMMARY"))
        synopsis = from_union([from_str, from_none], obj.get("SYNOPSIS"))
        tags_synopsis = from_union([from_str, from_none], obj.get("synopsis"))
        te_is_reencode = from_union([from_str, from_none], obj.get("te_is_reencode"))
        timecode = from_union([from_str, from_none], obj.get("TIMECODE"))
        title = from_union([from_str, from_none], obj.get("title"))
        writing_frontend = from_union([from_str, from_none], obj.get("Writing frontend"))
        return FormatTags(
            artist,
            tags_artist,
            audiodelay,
            bitrate,
            can_seek_to_end,
            com_android_capture_fps,
            com_android_version,
            tags_com_apple_quicktime_author,
            com_apple_quicktime_author,
            tags_com_apple_quicktime_description,
            com_apple_quicktime_description,
            tags_com_apple_quicktime_displayname,
            com_apple_quicktime_displayname,
            tags_com_apple_quicktime_keywords,
            com_apple_quicktime_keywords,
            tags_com_apple_quicktime_title,
            com_apple_quicktime_title,
            tags_comment,
            comment,
            tags_compatible_brands,
            compatible_brands,
            composer,
            creation_time,
            creationdate,
            date,
            tags_date,
            description,
            tags_description,
            tags_encoder,
            encoder,
            encoder_eng,
            episode_sort,
            file,
            hd_video,
            hw,
            i_tun_movi,
            keywords,
            location,
            tags_major_brand,
            major_brand,
            maxrate,
            media_type,
            tags_minor_version,
            minor_version,
            modification_time,
            purl,
            scene,
            season_number,
            software,
            summary,
            synopsis,
            tags_synopsis,
            te_is_reencode,
            timecode,
            title,
            writing_frontend,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        if self.artist is not None:
            result["ARTIST"] = from_union([from_str, from_none], self.artist)
        if self.tags_artist is not None:
            result["artist"] = from_union([from_str, from_none], self.tags_artist)
        if self.audiodelay is not None:
            result["audiodelay"] = from_union([from_str, from_none], self.audiodelay)
        if self.bitrate is not None:
            result["bitrate"] = from_union([from_str, from_none], self.bitrate)
        if self.can_seek_to_end is not None:
            result["canSeekToEnd"] = from_union([from_str, from_none], self.can_seek_to_end)
        if self.com_android_capture_fps is not None:
            result["com.android.capture.fps"] = from_union([from_str, from_none], self.com_android_capture_fps)
        if self.com_android_version is not None:
            result["com.android.version"] = from_union([from_str, from_none], self.com_android_version)
        if self.tags_com_apple_quicktime_author is not None:
            result["com.apple.quicktime.author"] = from_union([from_str, from_none], self.tags_com_apple_quicktime_author)
        if self.com_apple_quicktime_author is not None:
            result["COM.APPLE.QUICKTIME.AUTHOR"] = from_union([from_str, from_none], self.com_apple_quicktime_author)
        if self.tags_com_apple_quicktime_description is not None:
            result["com.apple.quicktime.description"] = from_union([from_str, from_none], self.tags_com_apple_quicktime_description)
        if self.com_apple_quicktime_description is not None:
            result["COM.APPLE.QUICKTIME.DESCRIPTION"] = from_union([from_str, from_none], self.com_apple_quicktime_description)
        if self.tags_com_apple_quicktime_displayname is not None:
            result["com.apple.quicktime.displayname"] = from_union([from_str, from_none], self.tags_com_apple_quicktime_displayname)
        if self.com_apple_quicktime_displayname is not None:
            result["COM.APPLE.QUICKTIME.DISPLAYNAME"] = from_union([from_str, from_none], self.com_apple_quicktime_displayname)
        if self.tags_com_apple_quicktime_keywords is not None:
            result["com.apple.quicktime.keywords"] = from_union([from_str, from_none], self.tags_com_apple_quicktime_keywords)
        if self.com_apple_quicktime_keywords is not None:
            result["COM.APPLE.QUICKTIME.KEYWORDS"] = from_union([from_str, from_none], self.com_apple_quicktime_keywords)
        if self.tags_com_apple_quicktime_title is not None:
            result["com.apple.quicktime.title"] = from_union([from_str, from_none], self.tags_com_apple_quicktime_title)
        if self.com_apple_quicktime_title is not None:
            result["COM.APPLE.QUICKTIME.TITLE"] = from_union([from_str, from_none], self.com_apple_quicktime_title)
        if self.tags_comment is not None:
            result["comment"] = from_union([from_str, from_none], self.tags_comment)
        if self.comment is not None:
            result["COMMENT"] = from_union([from_str, from_none], self.comment)
        if self.tags_compatible_brands is not None:
            result["compatible_brands"] = from_union([from_str, from_none], self.tags_compatible_brands)
        if self.compatible_brands is not None:
            result["COMPATIBLE_BRANDS"] = from_union([from_str, from_none], self.compatible_brands)
        if self.composer is not None:
            result["composer"] = from_union([from_str, from_none], self.composer)
        if self.creation_time is not None:
            result["creation_time"] = from_union([from_str, from_none], self.creation_time)
        if self.creationdate is not None:
            result["creationdate"] = from_union([from_str, from_none], self.creationdate)
        if self.date is not None:
            result["DATE"] = from_union([from_str, from_none], self.date)
        if self.tags_date is not None:
            result["date"] = from_union([from_str, from_none], self.tags_date)
        if self.description is not None:
            result["DESCRIPTION"] = from_union([from_str, from_none], self.description)
        if self.tags_description is not None:
            result["description"] = from_union([from_str, from_none], self.tags_description)
        if self.tags_encoder is not None:
            result["encoder"] = from_union([from_str, from_none], self.tags_encoder)
        if self.encoder is not None:
            result["ENCODER"] = from_union([from_str, from_none], self.encoder)
        if self.encoder_eng is not None:
            result["encoder-eng"] = from_union([from_str, from_none], self.encoder_eng)
        if self.episode_sort is not None:
            result["episode_sort"] = from_union([from_str, from_none], self.episode_sort)
        if self.file is not None:
            result["FILE"] = from_union([from_str, from_none], self.file)
        if self.hd_video is not None:
            result["hd_video"] = from_union([from_str, from_none], self.hd_video)
        if self.hw is not None:
            result["Hw"] = from_union([from_str, from_none], self.hw)
        if self.i_tun_movi is not None:
            result["iTunMOVI"] = from_union([from_str, from_none], self.i_tun_movi)
        if self.keywords is not None:
            result["KEYWORDS"] = from_union([from_str, from_none], self.keywords)
        if self.location is not None:
            result["location"] = from_union([from_str, from_none], self.location)
        if self.tags_major_brand is not None:
            result["major_brand"] = from_union([from_str, from_none], self.tags_major_brand)
        if self.major_brand is not None:
            result["MAJOR_BRAND"] = from_union([from_str, from_none], self.major_brand)
        if self.maxrate is not None:
            result["maxrate"] = from_union([from_str, from_none], self.maxrate)
        if self.media_type is not None:
            result["media_type"] = from_union([from_str, from_none], self.media_type)
        if self.tags_minor_version is not None:
            result["minor_version"] = from_union([from_str, from_none], self.tags_minor_version)
        if self.minor_version is not None:
            result["MINOR_VERSION"] = from_union([from_str, from_none], self.minor_version)
        if self.modification_time is not None:
            result["modification_time"] = from_union([lambda x: x.isoformat(), from_none], self.modification_time)
        if self.purl is not None:
            result["PURL"] = from_union([from_str, from_none], self.purl)
        if self.scene is not None:
            result["SCENE"] = from_union([from_str, from_none], self.scene)
        if self.season_number is not None:
            result["season_number"] = from_union([from_str, from_none], self.season_number)
        if self.software is not None:
            result["software"] = from_union([from_str, from_none], self.software)
        if self.summary is not None:
            result["SUMMARY"] = from_union([from_str, from_none], self.summary)
        if self.synopsis is not None:
            result["SYNOPSIS"] = from_union([from_str, from_none], self.synopsis)
        if self.tags_synopsis is not None:
            result["synopsis"] = from_union([from_str, from_none], self.tags_synopsis)
        if self.te_is_reencode is not None:
            result["te_is_reencode"] = from_union([from_str, from_none], self.te_is_reencode)
        if self.timecode is not None:
            result["TIMECODE"] = from_union([from_str, from_none], self.timecode)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.writing_frontend is not None:
            result["Writing frontend"] = from_union([from_str, from_none], self.writing_frontend)
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
    def from_dict(obj: Any) -> "Format":
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
        return Format(
            bit_rate, duration, filename, format_long_name, format_name, nb_programs, nb_streams, probe_score, size, start_time, tags
        )

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
    captions: int
    clean_effects: int
    comment: int
    default: int
    dependent: int
    descriptions: int
    dub: int
    forced: int
    hearing_impaired: int
    karaoke: int
    lyrics: int
    metadata: int
    non_diegetic: int
    original: int
    still_image: int
    timed_thumbnails: int
    visual_impaired: int

    @staticmethod
    def from_dict(obj: Any) -> "Disposition":
        assert isinstance(obj, dict)
        attached_pic = from_int(obj.get("attached_pic"))
        captions = from_int(obj.get("captions"))
        clean_effects = from_int(obj.get("clean_effects"))
        comment = from_int(obj.get("comment"))
        default = from_int(obj.get("default"))
        dependent = from_int(obj.get("dependent"))
        descriptions = from_int(obj.get("descriptions"))
        dub = from_int(obj.get("dub"))
        forced = from_int(obj.get("forced"))
        hearing_impaired = from_int(obj.get("hearing_impaired"))
        karaoke = from_int(obj.get("karaoke"))
        lyrics = from_int(obj.get("lyrics"))
        metadata = from_int(obj.get("metadata"))
        non_diegetic = from_int(obj.get("non_diegetic"))
        original = from_int(obj.get("original"))
        still_image = from_int(obj.get("still_image"))
        timed_thumbnails = from_int(obj.get("timed_thumbnails"))
        visual_impaired = from_int(obj.get("visual_impaired"))
        return Disposition(
            attached_pic,
            captions,
            clean_effects,
            comment,
            default,
            dependent,
            descriptions,
            dub,
            forced,
            hearing_impaired,
            karaoke,
            lyrics,
            metadata,
            non_diegetic,
            original,
            still_image,
            timed_thumbnails,
            visual_impaired,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["attached_pic"] = from_int(self.attached_pic)
        result["captions"] = from_int(self.captions)
        result["clean_effects"] = from_int(self.clean_effects)
        result["comment"] = from_int(self.comment)
        result["default"] = from_int(self.default)
        result["dependent"] = from_int(self.dependent)
        result["descriptions"] = from_int(self.descriptions)
        result["dub"] = from_int(self.dub)
        result["forced"] = from_int(self.forced)
        result["hearing_impaired"] = from_int(self.hearing_impaired)
        result["karaoke"] = from_int(self.karaoke)
        result["lyrics"] = from_int(self.lyrics)
        result["metadata"] = from_int(self.metadata)
        result["non_diegetic"] = from_int(self.non_diegetic)
        result["original"] = from_int(self.original)
        result["still_image"] = from_int(self.still_image)
        result["timed_thumbnails"] = from_int(self.timed_thumbnails)
        result["visual_impaired"] = from_int(self.visual_impaired)
        return result


@dataclass
class SideDataList:
    side_data_type: str
    avg_bitrate: Optional[int] = None
    buffer_size: Optional[int] = None
    displaymatrix: Optional[str] = None
    inverted: Optional[int] = None
    max_bitrate: Optional[int] = None
    min_bitrate: Optional[int] = None
    pitch: Optional[int] = None
    projection: Optional[str] = None
    roll: Optional[int] = None
    rotation: Optional[int] = None
    service_type: Optional[int] = None
    type: Optional[str] = None
    vbv_delay: Optional[int] = None
    yaw: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> "SideDataList":
        assert isinstance(obj, dict)
        side_data_type = from_str(obj.get("side_data_type"))
        avg_bitrate = from_union([from_int, from_none], obj.get("avg_bitrate"))
        buffer_size = from_union([from_int, from_none], obj.get("buffer_size"))
        displaymatrix = from_union([from_str, from_none], obj.get("displaymatrix"))
        inverted = from_union([from_int, from_none], obj.get("inverted"))
        max_bitrate = from_union([from_int, from_none], obj.get("max_bitrate"))
        min_bitrate = from_union([from_int, from_none], obj.get("min_bitrate"))
        pitch = from_union([from_int, from_none], obj.get("pitch"))
        projection = from_union([from_str, from_none], obj.get("projection"))
        roll = from_union([from_int, from_none], obj.get("roll"))
        rotation = from_union([from_int, from_none], obj.get("rotation"))
        service_type = from_union([from_int, from_none], obj.get("service_type"))
        _type = from_union([from_str, from_none], obj.get("type"))
        vbv_delay = from_union([from_int, from_none], obj.get("vbv_delay"))
        yaw = from_union([from_int, from_none], obj.get("yaw"))
        return SideDataList(
            side_data_type,
            avg_bitrate,
            buffer_size,
            displaymatrix,
            inverted,
            max_bitrate,
            min_bitrate,
            pitch,
            projection,
            roll,
            rotation,
            service_type,
            _type,
            vbv_delay,
            yaw,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["side_data_type"] = from_str(self.side_data_type)
        if self.avg_bitrate is not None:
            result["avg_bitrate"] = from_union([from_int, from_none], self.avg_bitrate)
        if self.buffer_size is not None:
            result["buffer_size"] = from_union([from_int, from_none], self.buffer_size)
        if self.displaymatrix is not None:
            result["displaymatrix"] = from_union([from_str, from_none], self.displaymatrix)
        if self.inverted is not None:
            result["inverted"] = from_union([from_int, from_none], self.inverted)
        if self.max_bitrate is not None:
            result["max_bitrate"] = from_union([from_int, from_none], self.max_bitrate)
        if self.min_bitrate is not None:
            result["min_bitrate"] = from_union([from_int, from_none], self.min_bitrate)
        if self.pitch is not None:
            result["pitch"] = from_union([from_int, from_none], self.pitch)
        if self.projection is not None:
            result["projection"] = from_union([from_str, from_none], self.projection)
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
    tags_encoder: Optional[str] = None
    encoder: Optional[str] = None
    filename: Optional[str] = None
    tags_handler_name: Optional[str] = None
    handler_name: Optional[str] = None
    language: Optional[str] = None
    mimetype: Optional[str] = None
    number_of_bytes: Optional[str] = None
    number_of_bytes_eng: Optional[str] = None
    number_of_frames: Optional[str] = None
    number_of_frames_eng: Optional[str] = None
    source_id: Optional[str] = None
    source_id_eng: Optional[str] = None
    tags_timecode: Optional[str] = None
    timecode: Optional[str] = None
    title: Optional[str] = None
    tags_vendor_id: Optional[str] = None
    vendor_id: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> "StreamTags":
        assert isinstance(obj, dict)
        statistics_tags = from_union([from_str, from_none], obj.get("_STATISTICS_TAGS"))
        statistics_tags_eng = from_union([from_str, from_none], obj.get("_STATISTICS_TAGS-eng"))
        statistics_writing_app = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_APP"))
        statistics_writing_app_eng = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_APP-eng"))
        statistics_writing_date_utc = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_DATE_UTC"))
        statistics_writing_date_utc_eng = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_DATE_UTC-eng"))
        alpha_mode = from_union([from_str, from_none], obj.get("alpha_mode"))
        bps = from_union([from_str, from_none], obj.get("BPS"))
        bps_eng = from_union([from_str, from_none], obj.get("BPS-eng"))
        creation_time = from_union([from_datetime, from_none], obj.get("creation_time"))
        duration = from_union([from_str, from_none], obj.get("DURATION"))
        duration_eng = from_union([from_str, from_none], obj.get("DURATION-eng"))
        tags_encoder = from_union([from_str, from_none], obj.get("encoder"))
        encoder = from_union([from_str, from_none], obj.get("ENCODER"))
        filename = from_union([from_str, from_none], obj.get("filename"))
        tags_handler_name = from_union([from_str, from_none], obj.get("handler_name"))
        handler_name = from_union([from_str, from_none], obj.get("HANDLER_NAME"))
        language = from_union([from_str, from_none], obj.get("language"))
        mimetype = from_union([from_str, from_none], obj.get("mimetype"))
        number_of_bytes = from_union([from_str, from_none], obj.get("NUMBER_OF_BYTES"))
        number_of_bytes_eng = from_union([from_str, from_none], obj.get("NUMBER_OF_BYTES-eng"))
        number_of_frames = from_union([from_str, from_none], obj.get("NUMBER_OF_FRAMES"))
        number_of_frames_eng = from_union([from_str, from_none], obj.get("NUMBER_OF_FRAMES-eng"))
        source_id = from_union([from_str, from_none], obj.get("SOURCE_ID"))
        source_id_eng = from_union([from_str, from_none], obj.get("SOURCE_ID-eng"))
        tags_timecode = from_union([from_str, from_none], obj.get("timecode"))
        timecode = from_union([from_str, from_none], obj.get("TIMECODE"))
        title = from_union([from_str, from_none], obj.get("title"))
        tags_vendor_id = from_union([from_str, from_none], obj.get("vendor_id"))
        vendor_id = from_union([from_str, from_none], obj.get("VENDOR_ID"))
        return StreamTags(
            statistics_tags,
            statistics_tags_eng,
            statistics_writing_app,
            statistics_writing_app_eng,
            statistics_writing_date_utc,
            statistics_writing_date_utc_eng,
            alpha_mode,
            bps,
            bps_eng,
            creation_time,
            duration,
            duration_eng,
            tags_encoder,
            encoder,
            filename,
            tags_handler_name,
            handler_name,
            language,
            mimetype,
            number_of_bytes,
            number_of_bytes_eng,
            number_of_frames,
            number_of_frames_eng,
            source_id,
            source_id_eng,
            tags_timecode,
            timecode,
            title,
            tags_vendor_id,
            vendor_id,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        if self.statistics_tags is not None:
            result["_STATISTICS_TAGS"] = from_union([from_str, from_none], self.statistics_tags)
        if self.statistics_tags_eng is not None:
            result["_STATISTICS_TAGS-eng"] = from_union([from_str, from_none], self.statistics_tags_eng)
        if self.statistics_writing_app is not None:
            result["_STATISTICS_WRITING_APP"] = from_union([from_str, from_none], self.statistics_writing_app)
        if self.statistics_writing_app_eng is not None:
            result["_STATISTICS_WRITING_APP-eng"] = from_union([from_str, from_none], self.statistics_writing_app_eng)
        if self.statistics_writing_date_utc is not None:
            result["_STATISTICS_WRITING_DATE_UTC"] = from_union([from_str, from_none], self.statistics_writing_date_utc)
        if self.statistics_writing_date_utc_eng is not None:
            result["_STATISTICS_WRITING_DATE_UTC-eng"] = from_union([from_str, from_none], self.statistics_writing_date_utc_eng)
        if self.alpha_mode is not None:
            result["alpha_mode"] = from_union([from_str, from_none], self.alpha_mode)
        if self.bps is not None:
            result["BPS"] = from_union([from_str, from_none], self.bps)
        if self.bps_eng is not None:
            result["BPS-eng"] = from_union([from_str, from_none], self.bps_eng)
        if self.creation_time is not None:
            result["creation_time"] = from_union([lambda x: x.isoformat(), from_none], self.creation_time)
        if self.duration is not None:
            result["DURATION"] = from_union([from_str, from_none], self.duration)
        if self.duration_eng is not None:
            result["DURATION-eng"] = from_union([from_str, from_none], self.duration_eng)
        if self.tags_encoder is not None:
            result["encoder"] = from_union([from_str, from_none], self.tags_encoder)
        if self.encoder is not None:
            result["ENCODER"] = from_union([from_str, from_none], self.encoder)
        if self.filename is not None:
            result["filename"] = from_union([from_str, from_none], self.filename)
        if self.tags_handler_name is not None:
            result["handler_name"] = from_union([from_str, from_none], self.tags_handler_name)
        if self.handler_name is not None:
            result["HANDLER_NAME"] = from_union([from_str, from_none], self.handler_name)
        if self.language is not None:
            result["language"] = from_union([from_str, from_none], self.language)
        if self.mimetype is not None:
            result["mimetype"] = from_union([from_str, from_none], self.mimetype)
        if self.number_of_bytes is not None:
            result["NUMBER_OF_BYTES"] = from_union([from_str, from_none], self.number_of_bytes)
        if self.number_of_bytes_eng is not None:
            result["NUMBER_OF_BYTES-eng"] = from_union([from_str, from_none], self.number_of_bytes_eng)
        if self.number_of_frames is not None:
            result["NUMBER_OF_FRAMES"] = from_union([from_str, from_none], self.number_of_frames)
        if self.number_of_frames_eng is not None:
            result["NUMBER_OF_FRAMES-eng"] = from_union([from_str, from_none], self.number_of_frames_eng)
        if self.source_id is not None:
            result["SOURCE_ID"] = from_union([from_str, from_none], self.source_id)
        if self.source_id_eng is not None:
            result["SOURCE_ID-eng"] = from_union([from_str, from_none], self.source_id_eng)
        if self.tags_timecode is not None:
            result["timecode"] = from_union([from_str, from_none], self.tags_timecode)
        if self.timecode is not None:
            result["TIMECODE"] = from_union([from_str, from_none], self.timecode)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.tags_vendor_id is not None:
            result["vendor_id"] = from_union([from_str, from_none], self.tags_vendor_id)
        if self.vendor_id is not None:
            result["VENDOR_ID"] = from_union([from_str, from_none], self.vendor_id)
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
    def from_dict(obj: Any) -> "Stream":
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
        duration = from_union([from_str, from_none], obj.get("duration"))
        duration_ts = from_union([from_int, from_none], obj.get("duration_ts"))
        extradata_size = from_union([from_int, from_none], obj.get("extradata_size"))
        field_order = from_union([from_str, from_none], obj.get("field_order"))
        film_grain = from_union([from_int, from_none], obj.get("film_grain"))
        has_b_frames = from_union([from_int, from_none], obj.get("has_b_frames"))
        height = from_union([from_int, from_none], obj.get("height"))
        _id = from_union([from_str, from_none], obj.get("id"))
        initial_padding = from_union([from_int, from_none], obj.get("initial_padding"))
        is_avc = from_union([from_str, from_none], obj.get("is_avc"))
        level = from_union([from_int, from_none], obj.get("level"))
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
        return Stream(
            avg_frame_rate,
            codec_tag,
            codec_tag_string,
            codec_type,
            disposition,
            index,
            r_frame_rate,
            time_base,
            bit_rate,
            bits_per_raw_sample,
            bits_per_sample,
            channel_layout,
            channels,
            chroma_location,
            closed_captions,
            codec_long_name,
            codec_name,
            coded_height,
            coded_width,
            color_primaries,
            color_range,
            color_space,
            color_transfer,
            display_aspect_ratio,
            divx_packed,
            duration,
            duration_ts,
            extradata_size,
            field_order,
            film_grain,
            has_b_frames,
            height,
            _id,
            initial_padding,
            is_avc,
            level,
            missing_streams,
            nal_length_size,
            nb_frames,
            pix_fmt,
            profile,
            quarter_sample,
            refs,
            sample_aspect_ratio,
            sample_fmt,
            sample_rate,
            side_data_list,
            start_pts,
            start_time,
            tags,
            width,
        )

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
            result["side_data_list"] = from_union(
                [lambda x: from_list(lambda x: to_class(SideDataList, x), x), from_none], self.side_data_list
            )
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
    format: Optional[Format] = None
    streams: Optional[List[Stream]] = None

    @staticmethod
    def from_dict(obj: Any) -> "Ffprobe":
        assert isinstance(obj, dict)
        _format = from_union([Format.from_dict, from_none], obj.get("format"))
        streams = from_union([lambda x: from_list(Stream.from_dict, x), from_none], obj.get("streams"))
        return Ffprobe(_format, streams)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.format is not None:
            result["format"] = from_union([lambda x: to_class(Format, x), from_none], self.format)
        if self.streams is not None:
            result["streams"] = from_union([lambda x: from_list(lambda x: to_class(Stream, x), x), from_none], self.streams)
        return result


def ffprobe_from_dict(s: Any) -> Ffprobe:
    return Ffprobe.from_dict(s)


def ffprobe_to_dict(x: Ffprobe) -> Any:
    return to_class(Ffprobe, x)
