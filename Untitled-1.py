from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union, List, TypeVar, Callable, Type, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
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


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_stringified_bool(x: str) -> bool:
    if x == "true":
        return True
    if x == "false":
        return False
    assert False


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class FormatLongName(Enum):
    AVI_AUDIO_VIDEO_INTERLEAVED = "AVI (Audio Video Interleaved)"
    FLV_FLASH_VIDEO = "FLV (Flash Video)"
    MATROSKA_WEB_M = "Matroska / WebM"
    MPEG_PS_MPEG_2_PROGRAM_STREAM = "MPEG-PS (MPEG-2 Program Stream)"
    QUICK_TIME_MOV = "QuickTime / MOV"


class FormatName(Enum):
    AVI = "avi"
    FLV = "flv"
    MATROSKA_WEBM = "matroska,webm"
    MOV_MP4_M4_A_3_GP_3_G2_MJ2 = "mov,mp4,m4a,3gp,3g2,mj2"
    MPEG = "mpeg"


@dataclass
class Format:
    filename: str
    nb_streams: int
    nb_programs: int
    format_name: FormatName
    format_long_name: FormatLongName
    duration: str
    size: str
    bit_rate: int
    probe_score: int
    start_time: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Format':
        assert isinstance(obj, dict)
        filename = from_str(obj.get("filename"))
        nb_streams = from_int(obj.get("nb_streams"))
        nb_programs = from_int(obj.get("nb_programs"))
        format_name = FormatName(obj.get("format_name"))
        format_long_name = FormatLongName(obj.get("format_long_name"))
        duration = from_str(obj.get("duration"))
        size = from_str(obj.get("size"))
        bit_rate = int(from_str(obj.get("bit_rate")))
        probe_score = from_int(obj.get("probe_score"))
        start_time = from_union([from_str, from_none], obj.get("start_time"))
        tags = from_union([lambda x: from_dict(from_str, x), from_none], obj.get("tags"))
        return Format(filename, nb_streams, nb_programs, format_name, format_long_name, duration, size, bit_rate, probe_score, start_time, tags)

    def to_dict(self) -> dict:
        result: dict = {}
        result["filename"] = from_str(self.filename)
        result["nb_streams"] = from_int(self.nb_streams)
        result["nb_programs"] = from_int(self.nb_programs)
        result["format_name"] = to_enum(FormatName, self.format_name)
        result["format_long_name"] = to_enum(FormatLongName, self.format_long_name)
        result["duration"] = from_str(self.duration)
        result["size"] = from_str(self.size)
        result["bit_rate"] = from_str(str(self.bit_rate))
        result["probe_score"] = from_int(self.probe_score)
        if self.start_time is not None:
            result["start_time"] = from_union([from_str, from_none], self.start_time)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: from_dict(from_str, x), from_none], self.tags)
        return result


class ChannelLayout(Enum):
    MONO = "mono"
    STEREO = "stereo"
    THE_21 = "2.1"
    THE_50_SIDE = "5.0(side)"
    THE_51 = "5.1"
    THE_51_SIDE = "5.1(side)"
    THE_5_CHANNELS_FL_FR_LFE_SL_SR = "5 channels (FL+FR+LFE+SL+SR)"
    THE_61 = "6.1"
    THE_71 = "7.1"


class ChromaLocation(Enum):
    CENTER = "center"
    LEFT = "left"
    TOPLEFT = "topleft"


class CodecLongName(Enum):
    AAC_ADVANCED_AUDIO_CODING = "AAC (Advanced Audio Coding)"
    ADPCM_MICROSOFT = "ADPCM Microsoft"
    ADPCM_SHOCKWAVE_FLASH = "ADPCM Shockwave Flash"
    ALAC_APPLE_LOSSLESS_AUDIO_CODEC = "ALAC (Apple Lossless Audio Codec)"
    ALLIANCE_FOR_OPEN_MEDIA_AV1 = "Alliance for Open Media AV1"
    ASS_ADVANCED_SSA_SUBTITLE = "ASS (Advanced SSA) subtitle"
    ATSC_A_52_A_AC_3 = "ATSC A/52A (AC-3)"
    ATSC_A_52_B_AC_3_E_AC_3 = "ATSC A/52B (AC-3, E-AC-3)"
    BINARY_DATA = "binary data"
    CINEPAK = "Cinepak"
    DCA_DTS_COHERENT_ACOUSTICS = "DCA (DTS Coherent Acoustics)"
    DVD_SUBTITLES = "DVD subtitles"
    FLAC_FREE_LOSSLESS_AUDIO_CODEC = "FLAC (Free Lossless Audio Codec)"
    FLV_SORENSON_SPARK_SORENSON_H_263_FLASH_VIDEO = "FLV / Sorenson Spark / Sorenson H.263 (Flash Video)"
    F_FMPEG_VIDEO_CODEC_1 = "FFmpeg video codec #1"
    GOOGLE_VP9 = "Google VP9"
    HDMV_PRESENTATION_GRAPHIC_STREAM_SUBTITLES = "HDMV Presentation Graphic Stream subtitles"
    H_264_AVC_MPEG_4_AVC_MPEG_4_PART_10 = "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10"
    H_265_HEVC_HIGH_EFFICIENCY_VIDEO_CODING = "H.265 / HEVC (High Efficiency Video Coding)"
    MOTION_JPEG = "Motion JPEG"
    MOV_TEXT = "MOV text"
    MP1_MPEG_AUDIO_LAYER_1 = "MP1 (MPEG audio layer 1)"
    MP3_MPEG_AUDIO_LAYER_3 = "MP3 (MPEG audio layer 3)"
    MPEG_1_VIDEO = "MPEG-1 video"
    MPEG_2_VIDEO = "MPEG-2 video"
    MPEG_4_PART_2 = "MPEG-4 part 2"
    ON2_VP6_FLASH_VERSION = "On2 VP6 (Flash version)"
    ON2_VP8 = "On2 VP8"
    OPEN_TYPE_FONT = "OpenType font"
    OPUS_OPUS_INTERACTIVE_AUDIO_CODEC = "Opus (Opus Interactive Audio Codec)"
    PCM_SIGNED_16_BIT_BIG_ENDIAN = "PCM signed 16-bit big-endian"
    PCM_SIGNED_16_BIT_LITTLE_ENDIAN = "PCM signed 16-bit little-endian"
    PCM_SIGNED_24_BIT_LITTLE_ENDIAN = "PCM signed 24-bit little-endian"
    PCM_UNSIGNED_8_BIT = "PCM unsigned 8-bit"
    PNG_PORTABLE_NETWORK_GRAPHICS_IMAGE = "PNG (Portable Network Graphics) image"
    Q_DESIGN_MUSIC = "QDesign Music"
    RAW_UTF_8_TEXT = "raw UTF-8 text"
    RAW_VIDEO = "raw video"
    SORENSON_VECTOR_QUANTIZER_1_SORENSON_VIDEO_1_SVQ1 = "Sorenson Vector Quantizer 1 / Sorenson Video 1 / SVQ1"
    SUB_RIP_SUBTITLE = "SubRip subtitle"
    TRUE_HD = "TrueHD"
    TRUE_TYPE_FONT = "TrueType font"
    VORBIS = "Vorbis"
    WEB_VTT_SUBTITLE = "WebVTT subtitle"


class CodecName(Enum):
    AAC = "aac"
    AC3 = "ac3"
    ADPCM_MS = "adpcm_ms"
    ADPCM_SWF = "adpcm_swf"
    ALAC = "alac"
    ASS = "ass"
    AV1 = "av1"
    BIN_DATA = "bin_data"
    CINEPAK = "cinepak"
    DTS = "dts"
    DVD_SUBTITLE = "dvd_subtitle"
    EAC3 = "eac3"
    FFV1 = "ffv1"
    FLAC = "flac"
    FLV1 = "flv1"
    H264 = "h264"
    HDMV_PGS_SUBTITLE = "hdmv_pgs_subtitle"
    HEVC = "hevc"
    MJPEG = "mjpeg"
    MOV_TEXT = "mov_text"
    MP1 = "mp1"
    MP3 = "mp3"
    MPEG1_VIDEO = "mpeg1video"
    MPEG2_VIDEO = "mpeg2video"
    MPEG4 = "mpeg4"
    OPUS = "opus"
    OTF = "otf"
    PCM_S16_BE = "pcm_s16be"
    PCM_S16_LE = "pcm_s16le"
    PCM_S24_LE = "pcm_s24le"
    PCM_U8 = "pcm_u8"
    PNG = "png"
    QDMC = "qdmc"
    RAWVIDEO = "rawvideo"
    SUBRIP = "subrip"
    SVQ1 = "svq1"
    TEXT = "text"
    TRUEHD = "truehd"
    TTF = "ttf"
    VORBIS = "vorbis"
    VP6_F = "vp6f"
    VP8 = "vp8"
    VP9 = "vp9"
    WEBVTT = "webvtt"


class CodecTag(Enum):
    THE_0_X0000 = "0x0000"
    THE_0_X0001 = "0x0001"
    THE_0_X0002 = "0x0002"
    THE_0_X0055 = "0x0055"
    THE_0_X2000 = "0x2000"
    THE_0_X30323449 = "0x30323449"
    THE_0_X30355844 = "0x30355844"
    THE_0_X31515653 = "0x31515653"
    THE_0_X31564646 = "0x31564646"
    THE_0_X31637661 = "0x31637661"
    THE_0_X31637668 = "0x31637668"
    THE_0_X31766568 = "0x31766568"
    THE_0_X32315659 = "0x32315659"
    THE_0_X332_D6361 = "0x332d6361"
    THE_0_X39307076 = "0x39307076"
    THE_0_X434_D4451 = "0x434d4451"
    THE_0_X44495658 = "0x44495658"
    THE_0_X58564944 = "0x58564944"
    THE_0_X6134706_D = "0x6134706d"
    THE_0_X63616_C61 = "0x63616c61"
    THE_0_X64636_D74 = "0x64636d74"
    THE_0_X64697663 = "0x64697663"
    THE_0_X64697678 = "0x64697678"
    THE_0_X67337874 = "0x67337874"
    THE_0_X6_D63706_C = "0x6d63706c"
    THE_0_X7334706_D = "0x7334706d"
    THE_0_X7375704_F = "0x7375704f"
    THE_0_X74786574 = "0x74786574"
    THE_0_X7634706_D = "0x7634706d"
    THE_0_X7862656_D = "0x7862656d"


class CodecTagString(Enum):
    AC_3 = "ac-3"
    ALAC = "alac"
    AVC1 = "avc1"
    CODEC_TAG_STRING_XVID = "xvid"
    CVID = "cvid"
    DIVX = "DIVX"
    DX50 = "DX50"
    FFV1 = "FFV1"
    HEV1 = "hev1"
    HVC1 = "hvc1"
    I420 = "I420"
    LPCM = "lpcm"
    MEBX = "mebx"
    MP4_A = "mp4a"
    MP4_S = "mp4s"
    MP4_V = "mp4v"
    OPUS = "Opus"
    QDMC = "QDMC"
    SVQ1 = "SVQ1"
    TEXT = "text"
    THE_000 = "[0] [0][0]"
    THE_0000 = "[0][0][0][0]"
    THE_1000 = "[1][0][0][0]"
    THE_2000 = "[2][0][0][0]"
    TMCD = "tmcd"
    TX3_G = "tx3g"
    U_000 = "U[0][0][0]"
    VP09 = "vp09"
    XVID = "XVID"
    YV12 = "YV12"


class CodecType(Enum):
    ATTACHMENT = "attachment"
    AUDIO = "audio"
    DATA = "data"
    SUBTITLE = "subtitle"
    VIDEO = "video"


class Color(Enum):
    BT2020 = "bt2020"
    BT2020_NC = "bt2020nc"
    BT470_BG = "bt470bg"
    BT709 = "bt709"
    GBR = "gbr"
    SMPTE170_M = "smpte170m"
    SMPTE2084 = "smpte2084"


class ColorRange(Enum):
    PC = "pc"
    TV = "tv"


class FieldOrder(Enum):
    BB = "bb"
    PROGRESSIVE = "progressive"
    TB = "tb"
    TT = "tt"


class ID(Enum):
    THE_0_X0 = "0x0"
    THE_0_X1 = "0x1"
    THE_0_X10 = "0x10"
    THE_0_X11 = "0x11"
    THE_0_X12 = "0x12"
    THE_0_X13 = "0x13"
    THE_0_X14 = "0x14"
    THE_0_X15 = "0x15"
    THE_0_X16 = "0x16"
    THE_0_X17 = "0x17"
    THE_0_X18 = "0x18"
    THE_0_X19 = "0x19"
    THE_0_X1_A = "0x1a"
    THE_0_X1_B = "0x1b"
    THE_0_X1_C = "0x1c"
    THE_0_X1_C0 = "0x1c0"
    THE_0_X1_D = "0x1d"
    THE_0_X1_E = "0x1e"
    THE_0_X1_E0 = "0x1e0"
    THE_0_X1_F = "0x1f"
    THE_0_X2 = "0x2"
    THE_0_X20 = "0x20"
    THE_0_X21 = "0x21"
    THE_0_X22 = "0x22"
    THE_0_X23 = "0x23"
    THE_0_X24 = "0x24"
    THE_0_X25 = "0x25"
    THE_0_X26 = "0x26"
    THE_0_X3 = "0x3"
    THE_0_X4 = "0x4"
    THE_0_X5 = "0x5"
    THE_0_X6 = "0x6"
    THE_0_X65 = "0x65"
    THE_0_X7 = "0x7"
    THE_0_X8 = "0x8"
    THE_0_X9 = "0x9"
    THE_0_XA = "0xa"
    THE_0_XB = "0xb"
    THE_0_XC = "0xc"
    THE_0_XC9 = "0xc9"
    THE_0_XD = "0xd"
    THE_0_XE = "0xe"
    THE_0_XF = "0xf"


class PixFmt(Enum):
    BGR0 = "bgr0"
    GBRP16_LE = "gbrp16le"
    PAL8 = "pal8"
    RGB24 = "rgb24"
    RGB555_LE = "rgb555le"
    RGBA = "rgba"
    YUV410_P = "yuv410p"
    YUV420_P = "yuv420p"
    YUV420_P10_LE = "yuv420p10le"
    YUV422_P = "yuv422p"
    YUV422_P10_LE = "yuv422p10le"
    YUV444_P = "yuv444p"
    YUVJ420_P = "yuvj420p"
    YUVJ444_P = "yuvj444p"


class ProfileEnum(Enum):
    ADVANCED_SIMPLE_PROFILE = "Advanced Simple Profile"
    BASELINE = "Baseline"
    CONSTRAINED_BASELINE = "Constrained Baseline"
    DOLBY_DIGITAL_PLUS_DOLBY_ATMOS = "Dolby Digital Plus + Dolby Atmos"
    DOLBY_TRUE_HD_DOLBY_ATMOS = "Dolby TrueHD + Dolby Atmos"
    DTS = "DTS"
    DTS_ES = "DTS-ES"
    DTS_HD_HRA = "DTS-HD HRA"
    DTS_HD_MA = "DTS-HD MA"
    HE_AAC = "HE-AAC"
    HIGH = "High"
    HIGH_10 = "High 10"
    HIGH_422 = "High 4:2:2"
    HIGH_422_INTRA = "High 4:2:2 Intra"
    HIGH_444_PREDICTIVE = "High 4:4:4 Predictive"
    LC = "LC"
    MAIN = "Main"
    MAIN_10 = "Main 10"
    PROFILE_0 = "Profile 0"
    PROFILE_1 = "Profile 1"
    PROGRESSIVE = "Progressive"
    REXT = "Rext"
    SIMPLE_PROFILE = "Simple Profile"


class SampleAspectRatio(Enum):
    THE_1011 = "10:11"
    THE_10788 = "107:88"
    THE_11 = "1:1"
    THE_1211 = "12:11"
    THE_12801281 = "1280:1281"
    THE_135127 = "135:127"
    THE_14841485 = "1484:1485"
    THE_149144 = "149:144"
    THE_157144 = "157:144"
    THE_159179 = "159:179"
    THE_1615 = "16:15"
    THE_181166 = "181:166"
    THE_191179 = "191:179"
    THE_192185 = "192:185"
    THE_200201 = "200:201"
    THE_2116 = "21:16"
    THE_225224 = "225:224"
    THE_277206 = "277:206"
    THE_28001971 = "2800:1971"
    THE_289900 = "289:900"
    THE_374351 = "374:351"
    THE_3932 = "39:32"
    THE_4033 = "40:33"
    THE_40954096 = "4095:4096"
    THE_43114316 = "4311:4316"
    THE_4345 = "43:45"
    THE_4748 = "47:48"
    THE_478537 = "478:537"
    THE_481480 = "481:480"
    THE_51215120 = "5121:5120"
    THE_5954 = "59:54"
    THE_639640 = "639:640"
    THE_6445 = "64:45"
    THE_6567 = "65:67"
    THE_667640 = "667:640"
    THE_7180 = "71:80"
    THE_720677 = "720:677"
    THE_757720 = "757:720"
    THE_769720 = "769:720"
    THE_799659 = "799:659"
    THE_816817 = "816:817"
    THE_8380 = "83:80"
    THE_853720 = "853:720"
    THE_853854 = "853:854"
    THE_863704 = "863:704"
    THE_871704 = "871:704"
    THE_872873 = "872:873"
    THE_873704 = "873:704"
    THE_881704 = "881:704"
    THE_883704 = "883:704"
    THE_89 = "8:9"
    THE_916 = "9:16"
    THE_959960 = "959:960"
    THE_983676 = "983:676"


class SampleFmt(Enum):
    FLTP = "fltp"
    S16 = "s16"
    S16_P = "s16p"
    S32 = "s32"
    S32_P = "s32p"
    U8 = "u8"


class SideDataType(Enum):
    AUDIO_SERVICE_TYPE = "Audio Service Type"
    CONTENT_LIGHT_LEVEL_METADATA = "Content light level metadata"
    CPB_PROPERTIES = "CPB properties"
    DISPLAY_MATRIX = "Display Matrix"
    MASTERING_DISPLAY_METADATA = "Mastering display metadata"
    SPHERICAL_MAPPING = "Spherical Mapping"
    STEREO_3_D = "Stereo 3D"


@dataclass
class SideDataList:
    side_data_type: SideDataType
    service_type: Optional[int] = None
    displaymatrix: Optional[str] = None
    rotation: Optional[int] = None
    max_bitrate: Optional[int] = None
    min_bitrate: Optional[int] = None
    avg_bitrate: Optional[int] = None
    buffer_size: Optional[int] = None
    vbv_delay: Optional[int] = None
    type: Optional[str] = None
    inverted: Optional[int] = None
    projection: Optional[str] = None
    yaw: Optional[int] = None
    pitch: Optional[int] = None
    roll: Optional[int] = None
    max_content: Optional[int] = None
    max_average: Optional[int] = None
    red_x: Optional[str] = None
    red_y: Optional[str] = None
    green_x: Optional[str] = None
    green_y: Optional[str] = None
    blue_x: Optional[str] = None
    blue_y: Optional[str] = None
    white_point_x: Optional[str] = None
    white_point_y: Optional[str] = None
    min_luminance: Optional[str] = None
    max_luminance: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SideDataList':
        assert isinstance(obj, dict)
        side_data_type = SideDataType(obj.get("side_data_type"))
        service_type = from_union([from_int, from_none], obj.get("service_type"))
        displaymatrix = from_union([from_str, from_none], obj.get("displaymatrix"))
        rotation = from_union([from_int, from_none], obj.get("rotation"))
        max_bitrate = from_union([from_int, from_none], obj.get("max_bitrate"))
        min_bitrate = from_union([from_int, from_none], obj.get("min_bitrate"))
        avg_bitrate = from_union([from_int, from_none], obj.get("avg_bitrate"))
        buffer_size = from_union([from_int, from_none], obj.get("buffer_size"))
        vbv_delay = from_union([from_int, from_none], obj.get("vbv_delay"))
        type = from_union([from_str, from_none], obj.get("type"))
        inverted = from_union([from_int, from_none], obj.get("inverted"))
        projection = from_union([from_str, from_none], obj.get("projection"))
        yaw = from_union([from_int, from_none], obj.get("yaw"))
        pitch = from_union([from_int, from_none], obj.get("pitch"))
        roll = from_union([from_int, from_none], obj.get("roll"))
        max_content = from_union([from_int, from_none], obj.get("max_content"))
        max_average = from_union([from_int, from_none], obj.get("max_average"))
        red_x = from_union([from_str, from_none], obj.get("red_x"))
        red_y = from_union([from_str, from_none], obj.get("red_y"))
        green_x = from_union([from_str, from_none], obj.get("green_x"))
        green_y = from_union([from_str, from_none], obj.get("green_y"))
        blue_x = from_union([from_str, from_none], obj.get("blue_x"))
        blue_y = from_union([from_str, from_none], obj.get("blue_y"))
        white_point_x = from_union([from_str, from_none], obj.get("white_point_x"))
        white_point_y = from_union([from_str, from_none], obj.get("white_point_y"))
        min_luminance = from_union([from_str, from_none], obj.get("min_luminance"))
        max_luminance = from_union([from_str, from_none], obj.get("max_luminance"))
        return SideDataList(side_data_type, service_type, displaymatrix, rotation, max_bitrate, min_bitrate, avg_bitrate, buffer_size, vbv_delay, type, inverted, projection, yaw, pitch, roll, max_content, max_average, red_x, red_y, green_x, green_y, blue_x, blue_y, white_point_x, white_point_y, min_luminance, max_luminance)

    def to_dict(self) -> dict:
        result: dict = {}
        result["side_data_type"] = to_enum(SideDataType, self.side_data_type)
        if self.service_type is not None:
            result["service_type"] = from_union([from_int, from_none], self.service_type)
        if self.displaymatrix is not None:
            result["displaymatrix"] = from_union([from_str, from_none], self.displaymatrix)
        if self.rotation is not None:
            result["rotation"] = from_union([from_int, from_none], self.rotation)
        if self.max_bitrate is not None:
            result["max_bitrate"] = from_union([from_int, from_none], self.max_bitrate)
        if self.min_bitrate is not None:
            result["min_bitrate"] = from_union([from_int, from_none], self.min_bitrate)
        if self.avg_bitrate is not None:
            result["avg_bitrate"] = from_union([from_int, from_none], self.avg_bitrate)
        if self.buffer_size is not None:
            result["buffer_size"] = from_union([from_int, from_none], self.buffer_size)
        if self.vbv_delay is not None:
            result["vbv_delay"] = from_union([from_int, from_none], self.vbv_delay)
        if self.type is not None:
            result["type"] = from_union([from_str, from_none], self.type)
        if self.inverted is not None:
            result["inverted"] = from_union([from_int, from_none], self.inverted)
        if self.projection is not None:
            result["projection"] = from_union([from_str, from_none], self.projection)
        if self.yaw is not None:
            result["yaw"] = from_union([from_int, from_none], self.yaw)
        if self.pitch is not None:
            result["pitch"] = from_union([from_int, from_none], self.pitch)
        if self.roll is not None:
            result["roll"] = from_union([from_int, from_none], self.roll)
        if self.max_content is not None:
            result["max_content"] = from_union([from_int, from_none], self.max_content)
        if self.max_average is not None:
            result["max_average"] = from_union([from_int, from_none], self.max_average)
        if self.red_x is not None:
            result["red_x"] = from_union([from_str, from_none], self.red_x)
        if self.red_y is not None:
            result["red_y"] = from_union([from_str, from_none], self.red_y)
        if self.green_x is not None:
            result["green_x"] = from_union([from_str, from_none], self.green_x)
        if self.green_y is not None:
            result["green_y"] = from_union([from_str, from_none], self.green_y)
        if self.blue_x is not None:
            result["blue_x"] = from_union([from_str, from_none], self.blue_x)
        if self.blue_y is not None:
            result["blue_y"] = from_union([from_str, from_none], self.blue_y)
        if self.white_point_x is not None:
            result["white_point_x"] = from_union([from_str, from_none], self.white_point_x)
        if self.white_point_y is not None:
            result["white_point_y"] = from_union([from_str, from_none], self.white_point_y)
        if self.min_luminance is not None:
            result["min_luminance"] = from_union([from_str, from_none], self.min_luminance)
        if self.max_luminance is not None:
            result["max_luminance"] = from_union([from_str, from_none], self.max_luminance)
        return result


class Mimetype(Enum):
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    APPLICATION_VND_MS_OPENTYPE = "application/vnd.ms-opentype"
    APPLICATION_XML = "application/xml"
    APPLICATION_X_TRUETYPE_FONT = "application/x-truetype-font"
    FONT_OTF = "font/otf"
    FONT_SFNT = "font/sfnt"
    FONT_TTF = "font/ttf"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_WEBP = "image/webp"
    TEXT_PLAIN = "text/plain"
    TEXT_X_NFO = "text/x-nfo"


class StatisticsTags(Enum):
    BPS_DURATION_NUMBER_OF_FRAMES_NUMBER_OF_BYTES = "BPS DURATION NUMBER_OF_FRAMES NUMBER_OF_BYTES"
    BPS_DURATION_NUMBER_OF_FRAMES_NUMBER_OF_BYTES_SOURCE_ID = "BPS DURATION NUMBER_OF_FRAMES NUMBER_OF_BYTES SOURCE_ID"


class Encoder(Enum):
    AVC_CODING = "AVC Coding"
    EMPTY = "                               "
    H264 = "h264"
    H_264 = "H.264"
    JVT_AVC_CODING = "JVT/AVC Coding"
    LAVC57_83101_LIBX264 = "Lavc57.83.101 libx264"
    LAVC58_134100_LIBX264 = "Lavc58.134.100 libx264"
    LAVC59_18100_LIBX264 = "Lavc59.18.100 libx264"
    LAVC59_37100_LIBX264 = "Lavc59.37.100 libx264"
    LAVC60_3100_LIBX264 = "Lavc60.3.100 libx264"
    LAVC60_31102_H264_VAAPI = "Lavc60.31.102 h264_vaapi"
    LAVC60_31102_LIBX264 = "Lavc60.31.102 libx264"
    LAVC60_32102_LIBVPX_VP9 = "Lavc60.32.102 libvpx-vp9"
    SORENSON_VIDEO = "Sorenson Video"
    VIDEO_HANDLER = "VideoHandler"


class HandlerName(Enum):
    AC_351 = "AC-3 5.1"
    APPLE_SOUND_MEDIA_HANDLER = "Apple Sound Media Handler"
    APPLE_VIDEO_MEDIA_HANDLER = "Apple Video Media Handler"
    BRASIL = "Brasil"
    CORE_MEDIA_AUDIO = "Core Media Audio"
    CORE_MEDIA_METADATA = "Core Media Metadata"
    CORE_MEDIA_TIME_CODE = "Core Media Time Code"
    CORE_MEDIA_VIDEO = "Core Media Video"
    ESPAÑA = "España"
    GPAC_ISO_AUDIO_HANDLER = "GPAC ISO Audio Handler"
    GPAC_ISO_VIDEO_HANDLER = "GPAC ISO Video Handler"
    GPAC_MPEG_4_BIFS_HANDLER = "GPAC MPEG-4 BIFS Handler"
    GPAC_MPEG_4_OD_HANDLER = "GPAC MPEG-4 OD Handler"
    GPAC_MPEG_4_SCENE_DESCRIPTION_HANDLER = "GPAC MPEG-4 Scene Description Handler"
    HANDLER_NAME_MAINCONCEPT_MP4_SOUND_MEDIA_HANDLER = "Mainconcept MP4 Sound Media Handler"
    HANDLER_NAME_SOUND_HANDLER = "\u000cSoundHandler"
    HANDLER_NAME_VIDEO_HANDLER = "\u000cVideoHandler"
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_5112011 = "IsoMedia File Produced by Google, 5-11-2011"
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC = "ISO Media file produced by Google Inc."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_02252019 = "ISO Media file produced by Google Inc. Created on: 02/25/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03022019 = "ISO Media file produced by Google Inc. Created on: 03/02/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03032019 = "ISO Media file produced by Google Inc. Created on: 03/03/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03062019 = "ISO Media file produced by Google Inc. Created on: 03/06/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03072019 = "ISO Media file produced by Google Inc. Created on: 03/07/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03092019 = "ISO Media file produced by Google Inc. Created on: 03/09/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_03132019 = "ISO Media file produced by Google Inc. Created on: 03/13/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_04222019 = "ISO Media file produced by Google Inc. Created on: 04/22/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_04242019 = "ISO Media file produced by Google Inc. Created on: 04/24/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_05012019 = "ISO Media file produced by Google Inc. Created on: 05/01/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_05182019 = "ISO Media file produced by Google Inc. Created on: 05/18/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_05262019 = "ISO Media file produced by Google Inc. Created on: 05/26/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_06062019 = "ISO Media file produced by Google Inc. Created on: 06/06/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_06132019 = "ISO Media file produced by Google Inc. Created on: 06/13/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_07062019 = "ISO Media file produced by Google Inc. Created on: 07/06/2019."
    ISO_MEDIA_FILE_PRODUCED_BY_GOOGLE_INC_CREATED_ON_09022023 = "ISO Media file produced by Google Inc. Created on: 09/02/2023."
    LATINOAMÉRICA = "Latinoamérica"
    L_SMASH_VIDEO_MEDIA_HANDLER = "L-SMASH Video Media Handler"
    MAINCONCEPT_MP4_SOUND_MEDIA_HANDLER = "#Mainconcept MP4 Sound Media Handler"
    MAINCONCEPT_MP4_VIDEO_MEDIA_HANDLER = "Mainconcept MP4 Video Media Handler"
    MAINCONCEPT_VIDEO_MEDIA_HANDLER = "\u001fMainconcept Video Media Handler"
    MODULE_DE_GESTION_SON = "Module de gestion Son"
    MODULE_DE_GESTION_VID_O = "Module de gestion vid�o"
    PORTUGAL = "Portugal"
    SDH = "SDH"
    SOUND_HANDLE = "SoundHandle"
    SOUND_HANDLER = "SoundHandler"
    SOUND_MEDIA_HANDLER = "Sound Media Handler"
    STEREO = "Stereo"
    SUBTITLE_HANDLER = "SubtitleHandler"
    SURROUND = "Surround"
    TIME_CODE_HANDLER = "TimeCodeHandler"
    TWITTER_VORK_MUXER = "Twitter-vork muxer"
    VIDEO = "video"
    VIDEO_HANDLE = "VideoHandle"
    VIDEO_HANDLER = "VideoHandler"
    VIDEO_MEDIA_HANDLER = "Video Media Handler"
    Ý_崦 = "ʱ����ý�崦������"
    ƻ_ƵÝ_崦 = "ƻ����Ƶý�崦������"
    简体 = "简体"
    繁體 = "繁體"


class Language(Enum):
    ARA = "ara"
    BAQ = "baq"
    BRE = "bre"
    BUL = "bul"
    CAT = "cat"
    CES = "ces"
    CHI = "chi"
    CZE = "cze"
    DAN = "dan"
    DEU = "deu"
    DUT = "dut"
    ELL = "ell"
    ENG = "eng"
    EST = "est"
    FIL = "fil"
    FIN = "fin"
    FRA = "fra"
    FRE = "fre"
    GER = "ger"
    GLG = "glg"
    GRE = "gre"
    HEB = "heb"
    HIN = "hin"
    HRV = "hrv"
    HUN = "hun"
    ICE = "ice"
    IND = "ind"
    ITA = "ita"
    JPN = "jpn"
    KAN = "kan"
    KOR = "kor"
    LAV = "lav"
    LIT = "lit"
    MAC = "mac"
    MAL = "mal"
    MAY = "may"
    MSA = "msa"
    MUL = "mul"
    NLD = "nld"
    NOB = "nob"
    NOR = "nor"
    PAN = "pan"
    PER = "per"
    POL = "pol"
    POR = "por"
    RON = "ron"
    RUM = "rum"
    RUS = "rus"
    SCR = "scr"
    SLO = "slo"
    SLV = "slv"
    SPA = "spa"
    SQI = "sqi"
    SRP = "srp"
    SWE = "swe"
    TAM = "tam"
    TEL = "tel"
    TGL = "tgl"
    THA = "tha"
    TUR = "tur"
    UKR = "ukr"
    UND = "und"
    VIE = "vie"
    WOL = "wol"
    ZHO = "zho"


class VendorID(Enum):
    APPL = "appl"
    FFMP = "FFMP"
    S_VIS = "SVis"
    THE_0000 = "[0][0][0][0]"


class Timecode(Enum):
    THE_00000000 = "00:00:00:00"
    THE_00000200 = "00:00:02:00"


@dataclass
class Tags:
    duration: Optional[datetime] = None
    tags_language: Optional[Language] = None
    title: Optional[str] = None
    encoder: Optional[str] = None
    bps_eng: Optional[int] = None
    duration_eng: Optional[datetime] = None
    number_of_frames_eng: Optional[int] = None
    number_of_bytes_eng: Optional[str] = None
    statistics_writing_app_eng: Optional[str] = None
    statistics_writing_date_utc_eng: Optional[datetime] = None
    statistics_tags_eng: Optional[StatisticsTags] = None
    handler_name: Optional[str] = None
    vendor_id: Optional[VendorID] = None
    bps: Optional[int] = None
    number_of_frames: Optional[int] = None
    number_of_bytes: Optional[str] = None
    statistics_writing_app: Optional[str] = None
    statistics_writing_date_utc: Optional[datetime] = None
    statistics_tags: Optional[StatisticsTags] = None
    creation_time: Optional[datetime] = None
    tags_handler_name: Optional[HandlerName] = None
    tags_vendor_id: Optional[VendorID] = None
    tags_encoder: Optional[Encoder] = None
    tags_timecode: Optional[str] = None
    alpha_mode: Optional[int] = None
    filename: Optional[str] = None
    mimetype: Optional[Mimetype] = None
    source_id_eng: Optional[str] = None
    source_id: Optional[str] = None
    timecode: Optional[Timecode] = None
    language: Optional[str] = None
    source: Optional[str] = None
    track: Optional[int] = None
    encoder_options: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Tags':
        assert isinstance(obj, dict)
        duration = from_union([from_datetime, from_none], obj.get("DURATION"))
        tags_language = from_union([Language, from_none], obj.get("language"))
        title = from_union([from_str, from_none], obj.get("title"))
        encoder = from_union([from_str, from_none], obj.get("ENCODER"))
        bps_eng = from_union([from_none, lambda x: int(from_str(x))], obj.get("BPS-eng"))
        duration_eng = from_union([from_datetime, from_none], obj.get("DURATION-eng"))
        number_of_frames_eng = from_union([from_none, lambda x: int(from_str(x))], obj.get("NUMBER_OF_FRAMES-eng"))
        number_of_bytes_eng = from_union([from_str, from_none], obj.get("NUMBER_OF_BYTES-eng"))
        statistics_writing_app_eng = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_APP-eng"))
        statistics_writing_date_utc_eng = from_union([from_datetime, from_none], obj.get("_STATISTICS_WRITING_DATE_UTC-eng"))
        statistics_tags_eng = from_union([StatisticsTags, from_none], obj.get("_STATISTICS_TAGS-eng"))
        handler_name = from_union([from_str, from_none], obj.get("HANDLER_NAME"))
        vendor_id = from_union([VendorID, from_none], obj.get("VENDOR_ID"))
        bps = from_union([from_none, lambda x: int(from_str(x))], obj.get("BPS"))
        number_of_frames = from_union([from_none, lambda x: int(from_str(x))], obj.get("NUMBER_OF_FRAMES"))
        number_of_bytes = from_union([from_str, from_none], obj.get("NUMBER_OF_BYTES"))
        statistics_writing_app = from_union([from_str, from_none], obj.get("_STATISTICS_WRITING_APP"))
        statistics_writing_date_utc = from_union([from_datetime, from_none], obj.get("_STATISTICS_WRITING_DATE_UTC"))
        statistics_tags = from_union([StatisticsTags, from_none], obj.get("_STATISTICS_TAGS"))
        creation_time = from_union([from_datetime, from_none], obj.get("creation_time"))
        tags_handler_name = from_union([HandlerName, from_none], obj.get("handler_name"))
        tags_vendor_id = from_union([VendorID, from_none], obj.get("vendor_id"))
        tags_encoder = from_union([Encoder, from_none], obj.get("encoder"))
        tags_timecode = from_union([from_str, from_none], obj.get("timecode"))
        alpha_mode = from_union([from_none, lambda x: int(from_str(x))], obj.get("alpha_mode"))
        filename = from_union([from_str, from_none], obj.get("filename"))
        mimetype = from_union([Mimetype, from_none], obj.get("mimetype"))
        source_id_eng = from_union([from_str, from_none], obj.get("SOURCE_ID-eng"))
        source_id = from_union([from_str, from_none], obj.get("SOURCE_ID"))
        timecode = from_union([Timecode, from_none], obj.get("TIMECODE"))
        language = from_union([from_str, from_none], obj.get("LANGUAGE"))
        source = from_union([from_str, from_none], obj.get("Source"))
        track = from_union([from_none, lambda x: int(from_str(x))], obj.get("track"))
        encoder_options = from_union([from_str, from_none], obj.get("ENCODER_OPTIONS"))
        return Tags(duration, tags_language, title, encoder, bps_eng, duration_eng, number_of_frames_eng, number_of_bytes_eng, statistics_writing_app_eng, statistics_writing_date_utc_eng, statistics_tags_eng, handler_name, vendor_id, bps, number_of_frames, number_of_bytes, statistics_writing_app, statistics_writing_date_utc, statistics_tags, creation_time, tags_handler_name, tags_vendor_id, tags_encoder, tags_timecode, alpha_mode, filename, mimetype, source_id_eng, source_id, timecode, language, source, track, encoder_options)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.duration is not None:
            result["DURATION"] = from_union([lambda x: x.isoformat(), from_none], self.duration)
        if self.tags_language is not None:
            result["language"] = from_union([lambda x: to_enum(Language, x), from_none], self.tags_language)
        if self.title is not None:
            result["title"] = from_union([from_str, from_none], self.title)
        if self.encoder is not None:
            result["ENCODER"] = from_union([from_str, from_none], self.encoder)
        if self.bps_eng is not None:
            result["BPS-eng"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.bps_eng)
        if self.duration_eng is not None:
            result["DURATION-eng"] = from_union([lambda x: x.isoformat(), from_none], self.duration_eng)
        if self.number_of_frames_eng is not None:
            result["NUMBER_OF_FRAMES-eng"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.number_of_frames_eng)
        if self.number_of_bytes_eng is not None:
            result["NUMBER_OF_BYTES-eng"] = from_union([from_str, from_none], self.number_of_bytes_eng)
        if self.statistics_writing_app_eng is not None:
            result["_STATISTICS_WRITING_APP-eng"] = from_union([from_str, from_none], self.statistics_writing_app_eng)
        if self.statistics_writing_date_utc_eng is not None:
            result["_STATISTICS_WRITING_DATE_UTC-eng"] = from_union([lambda x: x.isoformat(), from_none], self.statistics_writing_date_utc_eng)
        if self.statistics_tags_eng is not None:
            result["_STATISTICS_TAGS-eng"] = from_union([lambda x: to_enum(StatisticsTags, x), from_none], self.statistics_tags_eng)
        if self.handler_name is not None:
            result["HANDLER_NAME"] = from_union([from_str, from_none], self.handler_name)
        if self.vendor_id is not None:
            result["VENDOR_ID"] = from_union([lambda x: to_enum(VendorID, x), from_none], self.vendor_id)
        if self.bps is not None:
            result["BPS"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.bps)
        if self.number_of_frames is not None:
            result["NUMBER_OF_FRAMES"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.number_of_frames)
        if self.number_of_bytes is not None:
            result["NUMBER_OF_BYTES"] = from_union([from_str, from_none], self.number_of_bytes)
        if self.statistics_writing_app is not None:
            result["_STATISTICS_WRITING_APP"] = from_union([from_str, from_none], self.statistics_writing_app)
        if self.statistics_writing_date_utc is not None:
            result["_STATISTICS_WRITING_DATE_UTC"] = from_union([lambda x: x.isoformat(), from_none], self.statistics_writing_date_utc)
        if self.statistics_tags is not None:
            result["_STATISTICS_TAGS"] = from_union([lambda x: to_enum(StatisticsTags, x), from_none], self.statistics_tags)
        if self.creation_time is not None:
            result["creation_time"] = from_union([lambda x: x.isoformat(), from_none], self.creation_time)
        if self.tags_handler_name is not None:
            result["handler_name"] = from_union([lambda x: to_enum(HandlerName, x), from_none], self.tags_handler_name)
        if self.tags_vendor_id is not None:
            result["vendor_id"] = from_union([lambda x: to_enum(VendorID, x), from_none], self.tags_vendor_id)
        if self.tags_encoder is not None:
            result["encoder"] = from_union([lambda x: to_enum(Encoder, x), from_none], self.tags_encoder)
        if self.tags_timecode is not None:
            result["timecode"] = from_union([from_str, from_none], self.tags_timecode)
        if self.alpha_mode is not None:
            result["alpha_mode"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.alpha_mode)
        if self.filename is not None:
            result["filename"] = from_union([from_str, from_none], self.filename)
        if self.mimetype is not None:
            result["mimetype"] = from_union([lambda x: to_enum(Mimetype, x), from_none], self.mimetype)
        if self.source_id_eng is not None:
            result["SOURCE_ID-eng"] = from_union([from_str, from_none], self.source_id_eng)
        if self.source_id is not None:
            result["SOURCE_ID"] = from_union([from_str, from_none], self.source_id)
        if self.timecode is not None:
            result["TIMECODE"] = from_union([lambda x: to_enum(Timecode, x), from_none], self.timecode)
        if self.language is not None:
            result["LANGUAGE"] = from_union([from_str, from_none], self.language)
        if self.source is not None:
            result["Source"] = from_union([from_str, from_none], self.source)
        if self.track is not None:
            result["track"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.track)
        if self.encoder_options is not None:
            result["ENCODER_OPTIONS"] = from_union([from_str, from_none], self.encoder_options)
        return result


class TimeBase(Enum):
    THE_100124000 = "1001/24000"
    THE_100130000 = "1001/30000"
    THE_1002997 = "100/2997"
    THE_102422181 = "1024/22181"
    THE_11 = "1/1"
    THE_110 = "1/10"
    THE_11000 = "1/1000"
    THE_11000000 = "1/1000000"
    THE_110009 = "1/10009"
    THE_110014 = "1/10014"
    THE_110240 = "1/10240"
    THE_110624 = "1/10624"
    THE_111025 = "1/11025"
    THE_111127 = "1/11127"
    THE_111458 = "1/11458"
    THE_111494 = "1/11494"
    THE_111554 = "1/11554"
    THE_111574 = "1/11574"
    THE_111848 = "1/11848"
    THE_111964 = "1/11964"
    THE_111982 = "1/11982"
    THE_111988 = "1/11988"
    THE_112169 = "1/12169"
    THE_112288 = "1/12288"
    THE_112303 = "1/12303"
    THE_112351 = "1/12351"
    THE_112732 = "1/12732"
    THE_112800 = "1/12800"
    THE_113182 = "1/13182"
    THE_114296 = "1/14296"
    THE_114306 = "1/14306"
    THE_114336 = "1/14336"
    THE_114352 = "1/14352"
    THE_114568 = "1/14568"
    THE_114656 = "1/14656"
    THE_114848 = "1/14848"
    THE_114911 = "1/14911"
    THE_114947 = "1/14947"
    THE_114977 = "1/14977"
    THE_115360 = "1/15360"
    THE_116000 = "1/16000"
    THE_118348 = "1/18348"
    THE_118608 = "1/18608"
    THE_118992 = "1/18992"
    THE_119088 = "1/19088"
    THE_119168 = "1/19168"
    THE_119184 = "1/19184"
    THE_119575 = "1/19575"
    THE_12 = "1/2"
    THE_124000 = "1/24000"
    THE_124097 = "1/24097"
    THE_124703 = "1/24703"
    THE_124911 = "1/24911"
    THE_125 = "1/25"
    THE_125000 = "1/25000"
    THE_125083 = "1/25083"
    THE_1251998 = "125/1998"
    THE_1252997 = "125/2997"
    THE_125613 = "1/25613"
    THE_126383 = "1/26383"
    THE_126573 = "1/26573"
    THE_126784 = "1/26784"
    THE_127839 = "1/27839"
    THE_127939 = "1/27939"
    THE_12857 = "1/2857"
    THE_128651 = "1/28651"
    THE_128653 = "1/28653"
    THE_128779 = "1/28779"
    THE_128923 = "1/28923"
    THE_129000 = "1/29000"
    THE_129421 = "1/29421"
    THE_129517 = "1/29517"
    THE_129571 = "1/29571"
    THE_129657 = "1/29657"
    THE_129793 = "1/29793"
    THE_129809 = "1/29809"
    THE_129881 = "1/29881"
    THE_129891 = "1/29891"
    THE_129933 = "1/29933"
    THE_129937 = "1/29937"
    THE_12997 = "1/2997"
    THE_130 = "1/30"
    THE_13000 = "1/3000"
    THE_130000 = "1/30000"
    THE_13079 = "1/3079"
    THE_13088 = "1/3088"
    THE_132000 = "1/32000"
    THE_13437 = "1/3437"
    THE_13738 = "1/3738"
    THE_13741 = "1/3741"
    THE_13743 = "1/3743"
    THE_144100 = "1/44100"
    THE_1441000 = "1/441000"
    THE_1466096000 = "1/466096000"
    THE_148000 = "1/48000"
    THE_14871 = "1/4871"
    THE_15003 = "1/5003"
    THE_1519 = "1/519"
    THE_15847 = "1/5847"
    THE_15887 = "1/5887"
    THE_1600 = "1/600"
    THE_16000 = "1/6000"
    THE_160000 = "1/60000"
    THE_1666 = "1/666"
    THE_17367 = "1/7367"
    THE_18000 = "1/8000"
    THE_190000 = "1/90000"
    THE_19000000 = "1/9000000"
    THE_196000 = "1/96000"
    THE_3125 = "3/125"
    THE_321225 = "32/1225"
    THE_400011000000 = "40001/1000000"
    THE_9250 = "9/250"


@dataclass
class Stream:
    index: int
    codec_type: CodecType
    codec_tag_string: CodecTagString
    codec_tag: CodecTag
    r_frame_rate: str
    avg_frame_rate: str
    time_base: TimeBase
    disposition: Dict[str, int]
    codec_name: Optional[CodecName] = None
    codec_long_name: Optional[CodecLongName] = None
    profile: Optional[Union[ProfileEnum, int]] = None
    width: Optional[int] = None
    height: Optional[int] = None
    coded_width: Optional[int] = None
    coded_height: Optional[int] = None
    closed_captions: Optional[int] = None
    film_grain: Optional[int] = None
    has_b_frames: Optional[int] = None
    sample_aspect_ratio: Optional[SampleAspectRatio] = None
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[PixFmt] = None
    level: Optional[int] = None
    color_range: Optional[ColorRange] = None
    color_space: Optional[Color] = None
    color_transfer: Optional[Color] = None
    color_primaries: Optional[Color] = None
    chroma_location: Optional[ChromaLocation] = None
    refs: Optional[int] = None
    start_pts: Optional[int] = None
    start_time: Optional[str] = None
    extradata_size: Optional[int] = None
    tags: Optional[Tags] = None
    sample_fmt: Optional[SampleFmt] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    channel_layout: Optional[ChannelLayout] = None
    bits_per_sample: Optional[int] = None
    initial_padding: Optional[int] = None
    bit_rate: Optional[int] = None
    duration_ts: Optional[int] = None
    duration: Optional[str] = None
    field_order: Optional[FieldOrder] = None
    is_avc: Optional[bool] = None
    nal_length_size: Optional[int] = None
    id: Optional[ID] = None
    bits_per_raw_sample: Optional[int] = None
    nb_frames: Optional[int] = None
    side_data_list: Optional[List[SideDataList]] = None
    quarter_sample: Optional[bool] = None
    divx_packed: Optional[bool] = None
    missing_streams: Optional[int] = None
    dmix_mode: Optional[int] = None
    ltrt_cmixlev: Optional[str] = None
    ltrt_surmixlev: Optional[str] = None
    loro_cmixlev: Optional[str] = None
    loro_surmixlev: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Stream':
        assert isinstance(obj, dict)
        index = from_int(obj.get("index"))
        codec_type = CodecType(obj.get("codec_type"))
        codec_tag_string = CodecTagString(obj.get("codec_tag_string"))
        codec_tag = CodecTag(obj.get("codec_tag"))
        r_frame_rate = from_str(obj.get("r_frame_rate"))
        avg_frame_rate = from_str(obj.get("avg_frame_rate"))
        time_base = TimeBase(obj.get("time_base"))
        disposition = from_dict(from_int, obj.get("disposition"))
        codec_name = from_union([CodecName, from_none], obj.get("codec_name"))
        codec_long_name = from_union([CodecLongName, from_none], obj.get("codec_long_name"))
        profile = from_union([from_none, lambda x: from_union([ProfileEnum, lambda x: int(x)], from_str(x))], obj.get("profile"))
        width = from_union([from_int, from_none], obj.get("width"))
        height = from_union([from_int, from_none], obj.get("height"))
        coded_width = from_union([from_int, from_none], obj.get("coded_width"))
        coded_height = from_union([from_int, from_none], obj.get("coded_height"))
        closed_captions = from_union([from_int, from_none], obj.get("closed_captions"))
        film_grain = from_union([from_int, from_none], obj.get("film_grain"))
        has_b_frames = from_union([from_int, from_none], obj.get("has_b_frames"))
        sample_aspect_ratio = from_union([SampleAspectRatio, from_none], obj.get("sample_aspect_ratio"))
        display_aspect_ratio = from_union([from_str, from_none], obj.get("display_aspect_ratio"))
        pix_fmt = from_union([PixFmt, from_none], obj.get("pix_fmt"))
        level = from_union([from_int, from_none], obj.get("level"))
        color_range = from_union([ColorRange, from_none], obj.get("color_range"))
        color_space = from_union([Color, from_none], obj.get("color_space"))
        color_transfer = from_union([Color, from_none], obj.get("color_transfer"))
        color_primaries = from_union([Color, from_none], obj.get("color_primaries"))
        chroma_location = from_union([ChromaLocation, from_none], obj.get("chroma_location"))
        refs = from_union([from_int, from_none], obj.get("refs"))
        start_pts = from_union([from_int, from_none], obj.get("start_pts"))
        start_time = from_union([from_str, from_none], obj.get("start_time"))
        extradata_size = from_union([from_int, from_none], obj.get("extradata_size"))
        tags = from_union([Tags.from_dict, from_none], obj.get("tags"))
        sample_fmt = from_union([SampleFmt, from_none], obj.get("sample_fmt"))
        sample_rate = from_union([from_none, lambda x: int(from_str(x))], obj.get("sample_rate"))
        channels = from_union([from_int, from_none], obj.get("channels"))
        channel_layout = from_union([ChannelLayout, from_none], obj.get("channel_layout"))
        bits_per_sample = from_union([from_int, from_none], obj.get("bits_per_sample"))
        initial_padding = from_union([from_int, from_none], obj.get("initial_padding"))
        bit_rate = from_union([from_none, lambda x: int(from_str(x))], obj.get("bit_rate"))
        duration_ts = from_union([from_int, from_none], obj.get("duration_ts"))
        duration = from_union([from_str, from_none], obj.get("duration"))
        field_order = from_union([FieldOrder, from_none], obj.get("field_order"))
        is_avc = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("is_avc"))
        nal_length_size = from_union([from_none, lambda x: int(from_str(x))], obj.get("nal_length_size"))
        id = from_union([ID, from_none], obj.get("id"))
        bits_per_raw_sample = from_union([from_none, lambda x: int(from_str(x))], obj.get("bits_per_raw_sample"))
        nb_frames = from_union([from_none, lambda x: int(from_str(x))], obj.get("nb_frames"))
        side_data_list = from_union([lambda x: from_list(SideDataList.from_dict, x), from_none], obj.get("side_data_list"))
        quarter_sample = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("quarter_sample"))
        divx_packed = from_union([from_none, lambda x: from_stringified_bool(from_str(x))], obj.get("divx_packed"))
        missing_streams = from_union([from_none, lambda x: int(from_str(x))], obj.get("missing_streams"))
        dmix_mode = from_union([from_none, lambda x: int(from_str(x))], obj.get("dmix_mode"))
        ltrt_cmixlev = from_union([from_str, from_none], obj.get("ltrt_cmixlev"))
        ltrt_surmixlev = from_union([from_str, from_none], obj.get("ltrt_surmixlev"))
        loro_cmixlev = from_union([from_str, from_none], obj.get("loro_cmixlev"))
        loro_surmixlev = from_union([from_str, from_none], obj.get("loro_surmixlev"))
        return Stream(index, codec_type, codec_tag_string, codec_tag, r_frame_rate, avg_frame_rate, time_base, disposition, codec_name, codec_long_name, profile, width, height, coded_width, coded_height, closed_captions, film_grain, has_b_frames, sample_aspect_ratio, display_aspect_ratio, pix_fmt, level, color_range, color_space, color_transfer, color_primaries, chroma_location, refs, start_pts, start_time, extradata_size, tags, sample_fmt, sample_rate, channels, channel_layout, bits_per_sample, initial_padding, bit_rate, duration_ts, duration, field_order, is_avc, nal_length_size, id, bits_per_raw_sample, nb_frames, side_data_list, quarter_sample, divx_packed, missing_streams, dmix_mode, ltrt_cmixlev, ltrt_surmixlev, loro_cmixlev, loro_surmixlev)

    def to_dict(self) -> dict:
        result: dict = {}
        result["index"] = from_int(self.index)
        result["codec_type"] = to_enum(CodecType, self.codec_type)
        result["codec_tag_string"] = to_enum(CodecTagString, self.codec_tag_string)
        result["codec_tag"] = to_enum(CodecTag, self.codec_tag)
        result["r_frame_rate"] = from_str(self.r_frame_rate)
        result["avg_frame_rate"] = from_str(self.avg_frame_rate)
        result["time_base"] = to_enum(TimeBase, self.time_base)
        result["disposition"] = from_dict(from_int, self.disposition)
        if self.codec_name is not None:
            result["codec_name"] = from_union([lambda x: to_enum(CodecName, x), from_none], self.codec_name)
        if self.codec_long_name is not None:
            result["codec_long_name"] = from_union([lambda x: to_enum(CodecLongName, x), from_none], self.codec_long_name)
        if self.profile is not None:
            result["profile"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: to_enum(ProfileEnum, (lambda x: is_type(ProfileEnum, x))(x)))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.profile)
        if self.width is not None:
            result["width"] = from_union([from_int, from_none], self.width)
        if self.height is not None:
            result["height"] = from_union([from_int, from_none], self.height)
        if self.coded_width is not None:
            result["coded_width"] = from_union([from_int, from_none], self.coded_width)
        if self.coded_height is not None:
            result["coded_height"] = from_union([from_int, from_none], self.coded_height)
        if self.closed_captions is not None:
            result["closed_captions"] = from_union([from_int, from_none], self.closed_captions)
        if self.film_grain is not None:
            result["film_grain"] = from_union([from_int, from_none], self.film_grain)
        if self.has_b_frames is not None:
            result["has_b_frames"] = from_union([from_int, from_none], self.has_b_frames)
        if self.sample_aspect_ratio is not None:
            result["sample_aspect_ratio"] = from_union([lambda x: to_enum(SampleAspectRatio, x), from_none], self.sample_aspect_ratio)
        if self.display_aspect_ratio is not None:
            result["display_aspect_ratio"] = from_union([from_str, from_none], self.display_aspect_ratio)
        if self.pix_fmt is not None:
            result["pix_fmt"] = from_union([lambda x: to_enum(PixFmt, x), from_none], self.pix_fmt)
        if self.level is not None:
            result["level"] = from_union([from_int, from_none], self.level)
        if self.color_range is not None:
            result["color_range"] = from_union([lambda x: to_enum(ColorRange, x), from_none], self.color_range)
        if self.color_space is not None:
            result["color_space"] = from_union([lambda x: to_enum(Color, x), from_none], self.color_space)
        if self.color_transfer is not None:
            result["color_transfer"] = from_union([lambda x: to_enum(Color, x), from_none], self.color_transfer)
        if self.color_primaries is not None:
            result["color_primaries"] = from_union([lambda x: to_enum(Color, x), from_none], self.color_primaries)
        if self.chroma_location is not None:
            result["chroma_location"] = from_union([lambda x: to_enum(ChromaLocation, x), from_none], self.chroma_location)
        if self.refs is not None:
            result["refs"] = from_union([from_int, from_none], self.refs)
        if self.start_pts is not None:
            result["start_pts"] = from_union([from_int, from_none], self.start_pts)
        if self.start_time is not None:
            result["start_time"] = from_union([from_str, from_none], self.start_time)
        if self.extradata_size is not None:
            result["extradata_size"] = from_union([from_int, from_none], self.extradata_size)
        if self.tags is not None:
            result["tags"] = from_union([lambda x: to_class(Tags, x), from_none], self.tags)
        if self.sample_fmt is not None:
            result["sample_fmt"] = from_union([lambda x: to_enum(SampleFmt, x), from_none], self.sample_fmt)
        if self.sample_rate is not None:
            result["sample_rate"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.sample_rate)
        if self.channels is not None:
            result["channels"] = from_union([from_int, from_none], self.channels)
        if self.channel_layout is not None:
            result["channel_layout"] = from_union([lambda x: to_enum(ChannelLayout, x), from_none], self.channel_layout)
        if self.bits_per_sample is not None:
            result["bits_per_sample"] = from_union([from_int, from_none], self.bits_per_sample)
        if self.initial_padding is not None:
            result["initial_padding"] = from_union([from_int, from_none], self.initial_padding)
        if self.bit_rate is not None:
            result["bit_rate"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.bit_rate)
        if self.duration_ts is not None:
            result["duration_ts"] = from_union([from_int, from_none], self.duration_ts)
        if self.duration is not None:
            result["duration"] = from_union([from_str, from_none], self.duration)
        if self.field_order is not None:
            result["field_order"] = from_union([lambda x: to_enum(FieldOrder, x), from_none], self.field_order)
        if self.is_avc is not None:
            result["is_avc"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.is_avc)
        if self.nal_length_size is not None:
            result["nal_length_size"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.nal_length_size)
        if self.id is not None:
            result["id"] = from_union([lambda x: to_enum(ID, x), from_none], self.id)
        if self.bits_per_raw_sample is not None:
            result["bits_per_raw_sample"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.bits_per_raw_sample)
        if self.nb_frames is not None:
            result["nb_frames"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.nb_frames)
        if self.side_data_list is not None:
            result["side_data_list"] = from_union([lambda x: from_list(lambda x: to_class(SideDataList, x), x), from_none], self.side_data_list)
        if self.quarter_sample is not None:
            result["quarter_sample"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.quarter_sample)
        if self.divx_packed is not None:
            result["divx_packed"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(bool, x))(x)).lower())(x))], self.divx_packed)
        if self.missing_streams is not None:
            result["missing_streams"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.missing_streams)
        if self.dmix_mode is not None:
            result["dmix_mode"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.dmix_mode)
        if self.ltrt_cmixlev is not None:
            result["ltrt_cmixlev"] = from_union([from_str, from_none], self.ltrt_cmixlev)
        if self.ltrt_surmixlev is not None:
            result["ltrt_surmixlev"] = from_union([from_str, from_none], self.ltrt_surmixlev)
        if self.loro_cmixlev is not None:
            result["loro_cmixlev"] = from_union([from_str, from_none], self.loro_cmixlev)
        if self.loro_surmixlev is not None:
            result["loro_surmixlev"] = from_union([from_str, from_none], self.loro_surmixlev)
        return result


@dataclass
class FfprobeElement:
    streams: List[Stream]
    format: Format

    @staticmethod
    def from_dict(obj: Any) -> 'FfprobeElement':
        assert isinstance(obj, dict)
        streams = from_list(Stream.from_dict, obj.get("streams"))
        format = Format.from_dict(obj.get("format"))
        return FfprobeElement(streams, format)

    def to_dict(self) -> dict:
        result: dict = {}
        result["streams"] = from_list(lambda x: to_class(Stream, x), self.streams)
        result["format"] = to_class(Format, self.format)
        return result


def ffprobe_from_dict(s: Any) -> List[FfprobeElement]:
    return from_list(FfprobeElement.from_dict, s)


def ffprobe_to_dict(x: List[FfprobeElement]) -> Any:
    return from_list(lambda x: to_class(FfprobeElement, x), x)
