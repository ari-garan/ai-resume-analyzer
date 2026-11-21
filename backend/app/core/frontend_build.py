import hashlib

from app.core.constants import FRONTEND_PATH, FRONTEND_BUILD_PATH


def frontend_source_fingerprint() -> str:
    files = [path for path in (FRONTEND_PATH / "src").rglob("*") if path.is_file()]
    files.extend(
        FRONTEND_PATH / name
        for name in ("index.html", "package.json", "vite.config.ts")
    )
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(FRONTEND_PATH).as_posix()):
        digest.update(path.relative_to(FRONTEND_PATH).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def frontend_build_is_current() -> bool:
    marker = FRONTEND_BUILD_PATH / ".build-source-hash"
    try:
        return marker.read_text(encoding="utf-8").strip() == frontend_source_fingerprint()
    except OSError:
        return False
