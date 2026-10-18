"""Durable, explicit JSON artifacts for one clean episode.

JSONL is the scientific commit log. A failed append attempts to restore the
previous file length; the runner does not advance its checkpoint until an
append has flushed and fsynced successfully. Automatic resume is deferred.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "config.json"
ROUNDS_FILENAME = "rounds.jsonl"
CHECKPOINT_FILENAME = "state_checkpoint.json"
FAILURE_FILENAME = "failure.json"
FINAL_FILENAME = "final_episode.json"


def specification_namespace(base_dir: str | Path, specification_version: str) -> Path:
    """Keep generated artifacts from different specifications under separate roots."""
    if (not isinstance(specification_version, str) or not specification_version
            or specification_version in (".", "..")
            or Path(specification_version).name != specification_version
            or "/" in specification_version or "\\" in specification_version):
        raise ValueError("specification_version must be one safe directory name.")
    return Path(base_dir) / specification_version


def stable_json(value: Any) -> str:
    """Serialize without NaN, with stable keys and Unicode preserved."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _fsync_directory(directory: Path) -> None:
    """Best-effort directory fsync; some filesystems reject directory fds."""
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        try:
            os.fsync(fd)
        except OSError:
            pass
    finally:
        os.close(fd)


def create_run_directory(base_dir: str | Path, run_name: str) -> Path:
    if not isinstance(run_name, str) or not run_name or run_name in (".", ".."):
        raise ValueError("run_name must be a nonempty directory name.")
    if Path(run_name).name != run_name or "/" in run_name or "\\" in run_name:
        raise ValueError("run_name must not contain path separators.")
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / run_name
    run_dir.mkdir(exist_ok=False)
    _fsync_directory(base)
    return run_dir


def write_json_atomic(path: str | Path, value: Any) -> None:
    """Write, fsync, atomically replace, then best-effort fsync the directory."""
    path = Path(path)
    payload = stable_json(value) + "\n"
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
        _fsync_directory(path.parent)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def initialize_rounds_jsonl(path: str | Path) -> None:
    path = Path(path)
    with path.open("xb") as handle:
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(path.parent)


def append_jsonl(path: str | Path, value: Any) -> None:
    """Append one complete line and fsync; roll back a failed partial write."""
    path = Path(path)
    line = (stable_json(value) + "\n").encode("utf-8")
    with path.open("r+b") as handle:
        handle.seek(0, os.SEEK_END)
        start = handle.tell()
        try:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        except Exception:
            handle.truncate(start)
            handle.flush()
            os.fsync(handle.fileno())
            raise
