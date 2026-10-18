#!/usr/bin/env python3
"""Inspect a frozen block by default; --execute explicitly enables model calls."""

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


def run_selected_block(*, block_id: str, config_path: str | Path,
                       manifest_path: str | Path, runs_root: str | Path,
                       execute: bool = False, start_position: int = 1,
                       runner: Callable = run_episode, client_factory: Callable | None = None) -> list[dict]:
    """Plan or execute in immutable manifest order; never resume within a run."""
    frozen = load_confirmatory_config(config_path)
    manifest = load_confirmatory_manifest(manifest_path)
    config = validate_selected_manifest(manifest, frozen)
    block = next((item for item in manifest["blocks"] if item["block_id"] == block_id), None)
    if block is None:
        raise ValueError(f"Unknown block: {block_id}.")
    if isinstance(start_position, bool) or not isinstance(start_position, int) or not 1 <= start_position <= 6:
        raise ValueError("start_position must be 1..6.")
    runs_root = Path(runs_root)
    batch_runs = specification_namespace(runs_root, manifest["specification_version"]) / "runs"
    episodes = block["episodes"]
    print("Mode:", "EXECUTE" if execute else "DRY RUN — no model calls")
    print("Specification:", manifest["specification_version"])
    print("Prompt family/version:", manifest["prompt_family"], manifest["prompt_version"])
    print("Response contract:", manifest["response_contract_version"])
    print("Market schema:", manifest["market_response_schema"], manifest["market_response_schema_sha256"])
    print("Communication schema:", manifest["communication_response_schema"], manifest["communication_response_schema_sha256"])
    for episode in episodes:
        print(" | ".join((
            block_id, f"position={episode['sequence_position']}", episode["episode_id"],
            episode["treatment_id"],
            f"seeds={episode['public_signal_seed']},{episode['private_signal_seed_A']},{episode['private_signal_seed_B']}",
            f"schedule_hash={episode['signal_schedule_hash']}",
            f"target={batch_runs / episode['run_name']}",
        )))
    if not execute:
        return episodes

    # Global order includes all earlier blocks, including recorded failures.
    preceding = [earlier for item in manifest["blocks"]
                 if item["replicate_id"] < block["replicate_id"]
                 for earlier in item["episodes"]] + episodes[:start_position - 1]
    for episode in preceding:
        prior_dir = batch_runs / episode["run_name"]
        if not prior_dir.is_dir():
            raise FileNotFoundError(f"Earlier manifest position has no run directory: {prior_dir}")
        prior = load_episode_artifacts(prior_dir)
        if (prior.status not in ("completed", "failed")
                or prior.config["run_name"] != episode["run_name"]
                or prior.config["specification_version"] != manifest["specification_version"]
                or prior.config["prompt_family"] != manifest["prompt_family"]
                or prior.config["prompt_version"] != manifest["prompt_version"]
                or prior.config["replicate_id"] != episode["replicate_id"]
                or prior.config["prior_communication"] is not episode["prior_communication"]
                or prior.config["signal_condition"] != episode["signal_condition"]
                or prior.config["signal_schedule_hash"] != episode["signal_schedule_hash"]):
            raise ValueError(f"Earlier manifest position is incomplete or mismatched: {prior_dir}")
        if (prior.config.get("response_contract_version") != episode["response_contract_version"]
                or prior.config.get("prompt_caching_policy") != episode["prompt_caching_policy"]
                or prior.config.get("signal_seeds") != {
                    key: episode[key] for key in
                    ("public_signal_seed", "private_signal_seed_A", "private_signal_seed_B")
                }
                or any(prior.config.get(key) != value
                       for key, value in episode["scientific_config"].items())
                or any(prior.config.get("structured_response_schemas", {}).get(call_type, {}).get("sha256") != episode[key]
                       for call_type, key in (("market_decision", "market_response_schema_sha256"),
                                              ("communication", "communication_response_schema_sha256")))):
            raise ValueError(f"Earlier manifest position has mismatched V2 contract provenance: {prior_dir}")
    remaining = episodes[start_position - 1:]
    for episode in remaining:
        target = batch_runs / episode["run_name"]
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
    for episode in remaining:
        result = runner(
            replicate_id=episode["replicate_id"],
            prior_communication=episode["prior_communication"],
            signal_condition=episode["signal_condition"],
            save_dir=runs_root, run_name=episode["run_name"],
            public_signal_seed=episode["public_signal_seed"],
            private_signal_seed_A=episode["private_signal_seed_A"],
            private_signal_seed_B=episode["private_signal_seed_B"],
            client=client, config=config, development_mode=False,
            execution_log_dir=ROOT / "execution_logs",
            transcript_metadata={
                "episode_id": episode["episode_id"], "block_id": episode["block_id"],
                "sequence_position": episode["sequence_position"],
                "manifest_payload_sha256": manifest["manifest_payload_sha256"],
            },
        )
        if result.get("status") != "completed":
            raise RuntimeError(f"Episode did not complete; stop at its manifest position: {episode['episode_id']}")
        print("Completed:", episode["episode_id"], result["status"], result["run_dir"])
    return remaining


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", required=True, help="Frozen block ID, e.g. block_01")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml")
    parser.add_argument("--manifest", type=Path, default=ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json")
    parser.add_argument("--runs-root", type=Path, default=ROOT / "results",
                        help="Base results root; the runner adds <specification_id>/runs")
    parser.add_argument("--start-position", type=int, default=1,
                        help="For later continuation, require earlier positions to be durable")
    parser.add_argument("--execute", action="store_true", help="Explicitly permit paid model calls")
    args = parser.parse_args(argv)
    run_selected_block(block_id=args.block, config_path=args.config,
                       manifest_path=args.manifest, runs_root=args.runs_root,
                       execute=args.execute, start_position=args.start_position)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
