"""The CLI writes derived CSV outside source run directories."""

import csv
import hashlib
import os
from pathlib import Path
import subprocess
import sys


def hashes(run_dir):
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in run_dir.iterdir() if path.is_file()}


def test_cli_includes_failures_and_never_rewrites_source_artifacts(synthetic_analysis_run, tmp_path):
    completed = synthetic_analysis_run("completed")
    failed = synthetic_analysis_run("failed", states=["A_ONLY"], status="failed")
    before = {path: hashes(path) for path in (completed, failed)}
    output = tmp_path / "derived" / "episode_summary.csv"
    script = Path(__file__).resolve().parents[1] / "scripts" / "summarize_results.py"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(script.parents[1] / "src")
    command = [sys.executable, str(script), "--runs-root", str(tmp_path), "--output", str(output)]
    process = subprocess.run(command, text=True, capture_output=True, env=environment)
    assert process.returncode == 0, process.stderr
    with output.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {row["status"] for row in rows} == {"completed", "failed"}
    assert next(row for row in rows if row["status"] == "completed")["joint_profit"] == "456.0"
    assert next(row for row in rows if row["status"] == "failed")["joint_profit"] == ""
    assert subprocess.run(command, text=True, capture_output=True, env=environment).returncode != 0
    assert subprocess.run(command + ["--overwrite"], text=True, capture_output=True, env=environment).returncode == 0
    assert {path: hashes(path) for path in (completed, failed)} == before
