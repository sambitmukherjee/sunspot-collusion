#!/usr/bin/env python3
"""Update or rebuild derived episode and block tables from durable artifacts."""

import argparse
from pathlib import Path

from collusion_experiment.v2_manifest import load_confirmatory_manifest
from collusion_experiment.tables import (
    rebuild_summary_tables, update_block_summary_table, update_episode_summary_table,
)

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "configs" /
                        "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "results",
                        help="Base directory containing <specification_id>/runs")
    parser.add_argument("--results-root", type=Path, default=ROOT / "results",
                        help="Base directory for <specification_id>/tables")
    commands = parser.add_subparsers(dest="command", required=True)
    episode = commands.add_parser("episode", help="Insert one attempted episode row")
    episode.add_argument("--episode-id", required=True)
    block = commands.add_parser("block", help="Insert a fully attempted block row")
    block.add_argument("--block-id", required=True)
    rebuild = commands.add_parser("rebuild", help="Recompute tables in manifest order")
    rebuild.add_argument("--overwrite", action="store_true",
                         help="Replace existing derived tables when they differ")
    args = parser.parse_args(argv)
    manifest = load_confirmatory_manifest(args.manifest)
    if args.command == "episode":
        positions = [item for group in manifest["blocks"] for item in group["episodes"]
                     if item["episode_id"] == args.episode_id]
        if len(positions) != 1:
            parser.error("Episode ID must identify exactly one manifest position.")
        run_dir = args.runs_root / manifest["specification_version"] / "runs" / positions[0]["run_name"]
        output = update_episode_summary_table(run_dir, manifest, args.episode_id, args.results_root)
    elif args.command == "block":
        output = update_block_summary_table(manifest, args.block_id, args.runs_root, args.results_root)
    else:
        output = rebuild_summary_tables(manifest, args.runs_root, args.results_root,
                                        overwrite=args.overwrite)
    print("Updated:", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
