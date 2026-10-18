#!/usr/bin/env python3
"""Write one read-only, episode-level CSV row per durable run."""

import argparse
import csv
from pathlib import Path

from collusion_experiment.metrics import discover_run_directories, episode_summary, load_episode_artifacts
from collusion_experiment.storage import (
    CHECKPOINT_FILENAME, CONFIG_FILENAME, FAILURE_FILENAME, FINAL_FILENAME, ROUNDS_FILENAME,
)


ARTIFACT_NAMES = {CHECKPOINT_FILENAME, CONFIG_FILENAME, FAILURE_FILENAME, FINAL_FILENAME, ROUNDS_FILENAME}


def write_summary(paths: list[str | Path], output: str | Path, *, overwrite: bool = False) -> int:
    run_dirs = discover_run_directories(paths)
    if not run_dirs:
        raise ValueError("No run directories found.")
    output = Path(output)
    resolved_output = output.resolve()
    if output.name in ARTIFACT_NAMES or any(resolved_output.is_relative_to(run.resolve()) for run in run_dirs):
        raise ValueError("Summary output must be separate from scientific run artifacts.")
    rows = [episode_summary(load_episode_artifacts(run)) for run in run_dirs]
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w" if overwrite else "x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Run directories or parents of run directories")
    parser.add_argument("--runs-root", action="append", default=[], help="Another parent results directory")
    parser.add_argument("--output", required=True, type=Path, help="New episode-summary CSV path")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing derived CSV")
    args = parser.parse_args(argv)
    if not (args.paths or args.runs_root):
        parser.error("Provide at least one run directory or --runs-root.")
    count = write_summary(args.paths + args.runs_root, args.output, overwrite=args.overwrite)
    print(f"Wrote {count} episode rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
