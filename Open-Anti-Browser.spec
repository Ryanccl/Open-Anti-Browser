from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


project_root = Path(SPEC).resolve().parent


datas = [
    (str(project_root / "frontend" / "dist"), "frontend/dist"),
    (str(project_root / "assets"), "assets"),
    (str(project_root / "engines"), "engines"),
]
datas += collect_data_files("babel")
datas += collect_data_files("pycountry")
datas += collect_data_files("pytz")
datas += collect_data_files("curl_cffi")

binaries = []
binaries += collect_dynamic_libs("curl_cffi")

hiddenimports = []
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("curl_cffi")


a = Analysis(
    ["launch_app.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="Open-Anti-Browser",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "app.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Open-Anti-Browser",
)
