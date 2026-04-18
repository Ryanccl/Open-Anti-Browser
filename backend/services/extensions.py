from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path
import re


CHROME_UPLOAD_SUFFIXES = {".zip", ".crx"}
FIREFOX_UPLOAD_SUFFIXES = {".xpi", ".zip"}


def prepare_extension_paths(root_dir: Path, engine: str, extension_id: str, filename: str) -> tuple[Path, Path]:
    engine_dir = root_dir / engine / extension_id
    source_name = Path(filename or "extension").name or "extension"
    source_path = engine_dir / source_name
    unpack_dir = engine_dir / "unpacked"
    engine_dir.mkdir(parents=True, exist_ok=True)
    return source_path, unpack_dir


def persist_uploaded_extension(root_dir: Path, engine: str, extension_id: str, filename: str, content: bytes) -> tuple[str, str]:
    source_path, unpack_dir = prepare_extension_paths(root_dir, engine, extension_id, filename)
    source_path.write_bytes(content)

    if engine == "chrome":
        extension_root = extract_chrome_extension(source_path, unpack_dir)
        return str(source_path), str(extension_root)

    firefox_source = normalize_firefox_extension_file(source_path)
    return str(firefox_source), ""


def persist_extension_folder(root_dir: Path, engine: str, extension_id: str, folder_path: str | Path) -> tuple[str, str, str]:
    source_dir = Path(folder_path).expanduser().resolve()
    if not source_dir.exists():
        raise FileNotFoundError(f"扩展文件夹不存在：{source_dir}")
    if not source_dir.is_dir():
        raise ValueError("请选择扩展文件夹，不是文件")

    extension_root = discover_extension_directory_root(source_dir)
    if not (extension_root / "manifest.json").exists():
        raise ValueError("扩展文件夹里没有找到 manifest.json")

    engine_dir = root_dir / engine / extension_id
    if engine_dir.exists():
        shutil.rmtree(engine_dir, ignore_errors=True)
    engine_dir.mkdir(parents=True, exist_ok=True)

    if engine == "chrome":
        unpack_dir = engine_dir / "unpacked"
        shutil.copytree(extension_root, unpack_dir)
        chrome_root = discover_chrome_extension_root(unpack_dir)
        if not (chrome_root / "manifest.json").exists():
            raise ValueError("Chrome 扩展文件夹里没有找到 manifest.json")
        return str(unpack_dir), str(chrome_root), extension_root.name

    target_name = f"{safe_folder_name(extension_root.name)}.xpi"
    target_path = engine_dir / target_name
    zip_directory(extension_root, target_path)
    return str(target_path), "", extension_root.name


def normalize_firefox_extension_file(source_path: Path) -> Path:
    if source_path.suffix.lower() == ".xpi":
        return source_path
    target = source_path.with_suffix(".xpi")
    if target != source_path:
        target.write_bytes(source_path.read_bytes())
        source_path.unlink(missing_ok=True)
    return target


def discover_extension_directory_root(source_dir: Path) -> Path:
    manifest_at_root = source_dir / "manifest.json"
    if manifest_at_root.exists():
        return source_dir

    manifest_candidates = sorted(source_dir.rglob("manifest.json"))
    if len(manifest_candidates) == 1:
        return manifest_candidates[0].parent
    if not manifest_candidates:
        return source_dir
    raise ValueError("所选文件夹里找到多个 manifest.json，请选择具体的扩展根目录")


def zip_directory(source_dir: Path, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for path in sorted(source_dir.rglob("*")):
            if path.is_dir():
                continue
            zip_file.write(path, path.relative_to(source_dir).as_posix())


def safe_folder_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or "extension"


def extract_chrome_extension(source_path: Path, unpack_dir: Path) -> Path:
    suffix = source_path.suffix.lower()
    if suffix not in CHROME_UPLOAD_SUFFIXES:
        raise ValueError("Chrome 扩展只支持 zip 或 crx 文件")

    if unpack_dir.exists():
        shutil.rmtree(unpack_dir, ignore_errors=True)
    unpack_dir.mkdir(parents=True, exist_ok=True)

    if suffix == ".zip":
        zip_bytes = source_path.read_bytes()
    else:
        zip_bytes = extract_zip_payload_from_crx(source_path.read_bytes())

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        safe_extract_zip(zip_file, unpack_dir)

    extension_root = discover_chrome_extension_root(unpack_dir)
    if not (extension_root / "manifest.json").exists():
        raise ValueError("Chrome 扩展里没有找到 manifest.json")
    return extension_root


def extract_zip_payload_from_crx(raw: bytes) -> bytes:
    zip_magic = b"PK\x03\x04"
    zip_index = raw.find(zip_magic)
    if zip_index < 0:
        raise ValueError("CRX 文件解析失败，未找到扩展内容")
    return raw[zip_index:]


def safe_extract_zip(zip_file: zipfile.ZipFile, target_dir: Path) -> None:
    target_dir = target_dir.resolve()
    for member in zip_file.infolist():
        member_path = target_dir / member.filename
        resolved = member_path.resolve()
        if target_dir not in resolved.parents and resolved != target_dir:
            raise ValueError("扩展文件路径非法")
        if member.is_dir():
            resolved.mkdir(parents=True, exist_ok=True)
            continue
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with zip_file.open(member) as source, open(resolved, "wb") as target:
            shutil.copyfileobj(source, target)


def discover_chrome_extension_root(unpack_dir: Path) -> Path:
    manifest_at_root = unpack_dir / "manifest.json"
    if manifest_at_root.exists():
        return unpack_dir

    manifest_candidates = sorted(unpack_dir.rglob("manifest.json"))
    if not manifest_candidates:
        return unpack_dir

    top_level_candidates = []
    for manifest_path in manifest_candidates:
        parent = manifest_path.parent
        try:
            parent.relative_to(unpack_dir)
        except ValueError:
            continue
        top_level_candidates.append(parent)

    unique_candidates = []
    seen = set()
    for item in top_level_candidates:
        key = str(item.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        unique_candidates.append(item)

    if len(unique_candidates) == 1:
        return unique_candidates[0]
    return unpack_dir


def remove_extension_storage(root_dir: Path, engine: str, extension_id: str) -> None:
    shutil.rmtree(root_dir / engine / extension_id, ignore_errors=True)
