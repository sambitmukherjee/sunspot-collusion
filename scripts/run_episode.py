#!/usr/bin/env python3
"""Inspect one frozen manifest episode; --execute explicitly enables model calls."""

import argparse
import os
from pathlib import Path
from typing import Callable

from collusion_experiment.episode import run_episode
from collusion_experiment.v2_manifest import (
    load_confirmatory_config, load_confirmatory_manifest,
    validate_selected_manifest,
)
from collusion_experiment.metrics import load_episode_artifacts
from collusion_experiment.storage import specification_namespace

ROOT = Path(__file__).resolve().parents[1]


def run_selected_episode(*, episode_id: str, config_path: str | Path,
                         manifest_path: str | Path, runs_root: str | Path,
                         execute: bool = False, runner: Callable = run_episode,
                         client_factory: Callable | None = None) -> dict:
    """Plan or execute exactly one manifest row without resuming a prior run."""
    frozen = load_confirmatory_config(config_path)
    manifest = load_confirmatory_manifest(manifest_path)
    config = validate_selected_manifest(manifest, frozen)
    ordered = [row for block in manifest["blocks"] for row in block["episodes"]]
    matches = [index for index, row in enumerate(ordered) if row["episode_id"] == episode_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one frozen manifest episode for ID {episode_id!r}; found {len(matches)}.")
    index = matches[0]
    row = ordered[index]
    runs_root = Path(runs_root)
    target = specification_namespace(runs_root, manifest["specification_version"]) / "runs" / row["run_name"]
    print("Mode:", "EXECUTE" if execute else "DRY RUN — no model calls")
    for key in ("episode_id", "run_name", "block_id", "replicate_id", "sequence_position",
                "treatment_id", "prior_communication", "signal_condition",
                "public_signal_seed", "private_signal_seed_A", "private_signal_seed_B",
                "signal_schedule_hash", "specification_version", "prompt_family", "prompt_version"):
        print(f"{key}: {row[key]}")
    print("target_output_path:", target)
    print("manifest_payload_sha256:", manifest["manifest_payload_sha256"])
    print("response_contract_version:", row["response_contract_version"])
    print("market_response_schema:", row["market_response_schema"], row["market_response_schema_sha256"])
    print("communication_response_schema:", row["communication_response_schema"], row["communication_response_schema_sha256"])
    if not execute:
        return row

    for preceding in ordered[:index]:
        prior_dir = specification_namespace(runs_root, manifest["specification_version"]) / "runs" / preceding["run_name"]
        if not prior_dir.is_dir():
            raise FileNotFoundError(f"Earlier manifest position has no run directory: {prior_dir}")
        prior = load_episode_artifacts(prior_dir)
        if (prior.status not in ("completed", "failed")
                or prior.config["run_name"] != preceding["run_name"]
                or prior.config["specification_version"] != manifest["specification_version"]
                or prior.config["prompt_family"] != manifest["prompt_family"]
                or prior.config["prompt_version"] != manifest["prompt_version"]
                or prior.config["replicate_id"] != preceding["replicate_id"]
                or prior.config["prior_communication"] is not preceding["prior_communication"]
                or prior.config["signal_condition"] != preceding["signal_condition"]
                or prior.config.get("signal_seeds") != {
                    key: preceding[key] for key in
                    ("public_signal_seed", "private_signal_seed_A", "private_signal_seed_B")
                }
                or prior.config["signal_schedule_hash"] != preceding["signal_schedule_hash"]):
            raise ValueError(f"Earlier manifest position is incomplete or mismatched: {prior_dir}")
        if (prior.config.get("response_contract_version") != preceding["response_contract_version"]
                or prior.config.get("prompt_caching_policy") != preceding["prompt_caching_policy"]
                or any(prior.config.get(key) != value
                       for key, value in preceding["scientific_config"].items())
                or any(prior.config.get("structured_response_schemas", {}).get(call_type, {}).get("sha256") != preceding[key]
                       for call_type, key in (("market_decision", "market_response_schema_sha256"),
                                              ("communication", "communication_response_schema_sha256")))):
            raise ValueError(f"Earlier manifest position has mismatched V2 contract provenance: {prior_dir}")
    if target.exists():
        raise FileExistsError(f"Manifest run already exists; never rerun/splice it: {target}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for --execute; no model call was made.")
    if client_factory is None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the OpenAI Python SDK before --execute.") from exc
        client_factory = lambda key: OpenAI(api_key=key)
    client = client_factory(api_key)
    result = runner(
        replicate_id=row["replicate_id"], prior_communication=row["prior_communication"],
        signal_condition=row["signal_condition"], save_dir=runs_root,
        run_name=row["run_name"], public_signal_seed=row["public_signal_seed"],
        private_signal_seed_A=row["private_signal_seed_A"],
        private_signal_seed_B=row["private_signal_seed_B"],
        client=client, config=config, development_mode=False,
        execution_log_dir=ROOT / "execution_logs",
        transcript_metadata={
            "episode_id": row["episode_id"], "block_id": row["block_id"],
            "sequence_position": row["sequence_position"],
            "manifest_payload_sha256": manifest["manifest_payload_sha256"],
        },
    )
    if result.get("status") != "completed":
        raise RuntimeError(f"Episode did not complete; stop at its manifest position: {episode_id}")
    print("Completed:", episode_id, result["run_dir"])
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-id", required=True, help="Exact episode ID from the frozen manifest")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml")
    parser.add_argument("--manifest", type=Path, default=ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "results",
                        help="Base results root; the runner adds <specification_id>/runs")
    parser.add_argument("--execute", action="store_true", help="Explicitly permit paid model calls")
    args = parser.parse_args(argv)
    run_selected_episode(episode_id=args.episode_id, config_path=args.config,
                         manifest_path=args.manifest, runs_root=args.runs_root,
                         execute=args.execute)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
