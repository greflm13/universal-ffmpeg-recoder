import os
import platform

app_name = os.environ.get("APP_NAME", "recode")
build_os = os.environ.get("BUILD_OS", platform.system().lower())
build_arch = os.environ.get("BUILD_ARCH", platform.machine())

name = f"{app_name}-{build_os}-{build_arch}"

datas = [("src/recode/languages.json", ".")]

a = Analysis(
    [
        "src/recode/main.py",
        "src/recode/modules/api.py",
        "src/recode/modules/audio.py",
        "src/recode/modules/datatypes.py",
        "src/recode/modules/ffmpeg_utils.py",
        "src/recode/modules/FileOperations.py",
        "src/recode/modules/__init__.py",
        "src/recode/modules/logger.py",
        "src/recode/modules/parse_arguments.py",
        "src/recode/modules/subs.py",
        "src/recode/modules/video.py",
    ],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
