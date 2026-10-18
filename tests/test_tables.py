"""Offline known-answer tests for rebuildable, manifest-scoped CSV tables."""

import csv
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from collusion_experiment.config import ExperimentConfig
from collusion_experiment.tables import (
    BLOCK_COLUMNS, EPISODE_COLUMNS, TableIntegrityError,
    build_block_summary_row, build_episode_summary_row, rebuild_summary_tables,
    update_block_summary_table, update_episode_summary_table,
)
from collusion_experiment.structured_outputs import CONTRACT_VERSION, schema_provenance


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def make_block(synthetic_analysis_run, tmp_path, *, spec="TEST_SPEC", block_number=1,
               statuses=None):
    block_id = f"block_{block_number:02d}"
    runs_root = tmp_path / "source"
    positions = []
    for number, (condition, prior) in enumerate(
        (("public", False), ("private", True), ("private", False),
         ("none", False), ("public", True), ("none", True)), 1
    ):
        episode_id = f"{block_id}__{'prior' if prior else 'no_prior'}__{condition}"
        run_name = f"confirmatory_{spec}_{episode_id}"
        status = (statuses or {}).get((condition, prior), "completed")
        states = (["A_ONLY", "BOTH"] if status != "completed" else
                  ["A_ONLY", "BOTH", "NEITHER", "B_ONLY", "BOTH", "BOTH", "BOTH", "BOTH"]
                  if prior else None)
        design = replace(ExperimentConfig(num_rounds=8, communication_end_round=2,
                                          signal_start_round=5, pattern_window=2,
                                          pattern_max_period=2), specification_version=spec)
        original = synthetic_analysis_run(run_name, prior=prior, condition=condition,
                                          replicate=block_number, status=status,
                                          states=states, design=design)
        destination = runs_root / spec / "runs" / run_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(original, destination)
        schemas = schema_provenance()
        saved = json.loads((destination / "config.json").read_text())
        saved["response_contract_version"] = CONTRACT_VERSION
        saved["prompt_caching_policy"] = "provider_default"
        saved["structured_response_schemas"] = schemas
        (destination / "config.json").write_text(json.dumps(saved))
        scientific = asdict(design)
        for key in ("specification_version", "prompt_family", "prompt_version"):
            scientific.pop(key)
        for key in ("public_signal_values", "seller_labels"):
            scientific[key] = list(scientific[key])
        positions.append({
            "episode_id": episode_id, "run_name": run_name,
            "block_id": block_id, "replicate_id": block_number,
            "sequence_position": number,
            "treatment_id": f"{'prior_communication' if prior else 'no_prior_communication'}__{condition}",
            "prior_communication": prior, "signal_condition": condition,
            "signal_schedule_hash": "synthetic-schedule-hash",
            "specification_version": spec, "prompt_family": design.prompt_family,
            "prompt_version": design.prompt_version,
            "response_contract_version": CONTRACT_VERSION,
            "prompt_caching_policy": "provider_default",
            "market_response_schema": schemas["market_decision"]["name"],
            "market_response_schema_sha256": schemas["market_decision"]["sha256"],
            "communication_response_schema": schemas["communication"]["name"],
            "communication_response_schema_sha256": schemas["communication"]["sha256"],
            "scientific_config": scientific,
        })
    return {"specification_version": spec,
            "blocks": [{"block_id": block_id, "replicate_id": block_number,
                        "episodes": positions}]}, runs_root


def run_dir(runs_root, manifest, position):
    return runs_root / manifest["specification_version"] / "runs" / position["run_name"]


def artifact_hashes(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def test_episode_create_append_idempotency_schema_and_source_integrity(synthetic_analysis_run, tmp_path):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path)
    results_root = tmp_path / "derived"
    first, second = manifest["blocks"][0]["episodes"][:2]
    before = artifact_hashes(runs_root)
    path = update_episode_summary_table(run_dir(runs_root, manifest, first), manifest,
                                        first["episode_id"], results_root)
    assert path == results_root / "TEST_SPEC" / "tables" / "episode_summary.csv"
    assert read_csv(path)[0] == list(EPISODE_COLUMNS)
    assert len(read_csv(path)[1]) == 1
    update_episode_summary_table(run_dir(runs_root, manifest, second), manifest,
                                 second["episode_id"], results_root)
    content = path.read_bytes()
    update_episode_summary_table(run_dir(runs_root, manifest, second), manifest,
                                 second["episode_id"], results_root)
    assert path.read_bytes() == content
    rows = read_csv(path)[1]
    assert len(rows) == 2
    assert [(row["batch"], row["block"]) for row in rows] == [("TEST_SPEC", "block_01")] * 2
    assert rows[0]["episode_status"] == "completed"
    assert rows[0]["public_signal_mapping_score"] == "1.0"
    assert rows[1]["public_signal_mapping_score"] == ""
    assert rows[1]["public_signal_mutual_information_bits"] == ""
    assert artifact_hashes(runs_root) == before


def test_episode_conflict_and_manifest_mismatch(synthetic_analysis_run, tmp_path):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path)
    position = manifest["blocks"][0]["episodes"][0]
    source = run_dir(runs_root, manifest, position)
    output = update_episode_summary_table(source, manifest, position["episode_id"], tmp_path / "derived")
    text = output.read_text().replace("1.0", "0.0", 1)
    output.write_text(text)
    with pytest.raises(TableIntegrityError, match="Conflicting table row"):
        update_episode_summary_table(source, manifest, position["episode_id"], tmp_path / "derived")
    assert output.read_text() == text
    manifest["blocks"][0]["episodes"][0]["signal_schedule_hash"] = "different"
    with pytest.raises(TableIntegrityError, match="signal_schedule_hash"):
        build_episode_summary_row(source, manifest, position["episode_id"])


@pytest.mark.parametrize("status", ["failed", "incomplete"])
def test_partial_episode_has_identity_and_no_full_outcomes(synthetic_analysis_run, tmp_path, status):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path,
                                     statuses={("public", False): status})
    position = manifest["blocks"][0]["episodes"][0]
    row = build_episode_summary_row(run_dir(runs_root, manifest, position), manifest,
                                    position["episode_id"])
    assert row["episode_status"] == status
    assert row["last_committed_round"] == 2
    assert row["stage1_round_count"] is None
    assert row["stage3_joint_profit"] is None
    assert row["public_signal_mapping_score"] is None
    assert row["failure_type"] == ("SyntheticFailure" if status == "failed" else None)


def test_specifications_write_to_separate_tables(synthetic_analysis_run, tmp_path):
    results = tmp_path / "derived"
    paths = []
    for spec in ("FIRST_SPEC", "SECOND_SPEC"):
        manifest, runs = make_block(synthetic_analysis_run, tmp_path / spec, spec=spec)
        position = manifest["blocks"][0]["episodes"][0]
        paths.append(update_episode_summary_table(run_dir(runs, manifest, position), manifest,
                                                   position["episode_id"], results))
    assert paths[0] != paths[1]
    assert read_csv(paths[0])[1][0]["batch"] == "FIRST_SPEC"
    assert read_csv(paths[1])[1][0]["batch"] == "SECOND_SPEC"


def test_block_create_pairs_status_and_source_integrity(synthetic_analysis_run, tmp_path):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path)
    before = artifact_hashes(runs_root)
    row = build_block_summary_row(manifest, "block_01", runs_root)
    assert row["attempted_episode_count"] == 6
    assert row["completed_episode_count"] == 6
    assert row["block_status"] == "completed"
    assert row["public_mapping_score_no_prior"] == 1.0
    assert row["public_mapping_score_prior"] == 0.0
    assert row["public_mapping_score_difference"] == -1.0
    for condition in ("public", "private", "none"):
        assert row[f"{condition}_stage3_unique_participation_difference"] == -1.0
        assert row[f"{condition}_stage3_joint_profit_difference"] == (
            row[f"{condition}_stage3_joint_profit_prior"]
            - row[f"{condition}_stage3_joint_profit_no_prior"])
    assert row["position_1_episode_id"] == manifest["blocks"][0]["episodes"][0]["episode_id"]
    path = update_block_summary_table(manifest, "block_01", runs_root, tmp_path / "derived")
    assert path == tmp_path / "derived" / "TEST_SPEC" / "tables" / "block_summary.csv"
    assert read_csv(path)[0] == list(BLOCK_COLUMNS)
    assert len(read_csv(path)[1]) == 1
    content = path.read_bytes()
    update_block_summary_table(manifest, "block_01", runs_root, tmp_path / "derived")
    assert path.read_bytes() == content
    assert artifact_hashes(runs_root) == before


def test_block_append_conflict_and_missing_public_pair(synthetic_analysis_run, tmp_path):
    manifest1, runs_root = make_block(synthetic_analysis_run, tmp_path,
                                      statuses={("public", True): "failed"})
    first = build_block_summary_row(manifest1, "block_01", runs_root)
    assert first["failed_episode_count"] == 1
    assert first["block_status"] == "completed_with_failures"
    assert first["public_mapping_score_prior"] is None
    assert first["public_mapping_score_difference"] is None
    assert first["public_stage3_joint_profit_difference"] is None
    assert first["private_stage3_joint_profit_difference"] is not None
    results = tmp_path / "derived"
    path = update_block_summary_table(manifest1, "block_01", runs_root, results)
    manifest2, _ = make_block(synthetic_analysis_run, tmp_path, block_number=2)
    manifest = {**manifest1, "blocks": manifest1["blocks"] + manifest2["blocks"]}
    update_block_summary_table(manifest, "block_02", runs_root, results)
    assert len(read_csv(path)[1]) == 2
    rows = read_csv(path)[1]
    assert [(row["batch"], row["block"]) for row in rows] == [
        ("TEST_SPEC", "block_01"), ("TEST_SPEC", "block_02")]
    changed = path.read_text().replace("completed_with_failures", "completed", 1)
    path.write_text(changed)
    with pytest.raises(TableIntegrityError, match="Conflicting table row"):
        update_block_summary_table(manifest, "block_01", runs_root, results)
    assert path.read_text() == changed


def test_block_waits_for_all_six_and_counts_incomplete(synthetic_analysis_run, tmp_path):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path,
                                     statuses={("none", True): "incomplete"})
    row = build_block_summary_row(manifest, "block_01", runs_root)
    assert row["attempted_episode_count"] == 6
    assert row["incomplete_episode_count"] == 1
    assert row["block_status"] == "incomplete"
    assert row["position_6_episode_status"] == "incomplete"
    assert row["none_stage3_unique_participation_difference"] is None
    position = manifest["blocks"][0]["episodes"][-1]
    shutil.rmtree(run_dir(runs_root, manifest, position))
    with pytest.raises(ValueError, match="not been attempted"):
        build_block_summary_row(manifest, "block_01", runs_root)


def test_incremental_and_rebuild_agree_without_network(synthetic_analysis_run, tmp_path):
    manifest1, runs_root = make_block(synthetic_analysis_run, tmp_path)
    manifest2, _ = make_block(synthetic_analysis_run, tmp_path, block_number=2)
    manifest = {**manifest1, "blocks": manifest1["blocks"] + manifest2["blocks"]}
    incremental = tmp_path / "incremental"
    rebuilt = tmp_path / "rebuilt"
    before = artifact_hashes(runs_root)
    for block in manifest["blocks"]:
        for position in block["episodes"]:
            update_episode_summary_table(run_dir(runs_root, manifest, position), manifest,
                                         position["episode_id"], incremental)
        update_block_summary_table(manifest, block["block_id"], runs_root, incremental)
    rebuilt_paths = rebuild_summary_tables(manifest, runs_root, rebuilt)
    for filename, path in zip(("episode_summary.csv", "block_summary.csv"), rebuilt_paths):
        assert path.read_bytes() == (incremental / "TEST_SPEC" / "tables" / filename).read_bytes()
    assert artifact_hashes(runs_root) == before
    assert len(read_csv(rebuilt_paths[0])[1]) == 12
    assert len(read_csv(rebuilt_paths[1])[1]) == 2
    assert not any("mutual_information" in column for column in BLOCK_COLUMNS)


def test_cli_episode_block_and_rebuild_are_offline(synthetic_analysis_run, tmp_path):
    manifest, runs_root = make_block(synthetic_analysis_run, tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    results = tmp_path / "cli_results"
    script = Path(__file__).resolve().parents[1] / "scripts" / "update_summary_tables.py"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(script.parents[1] / "src")
    base = [sys.executable, str(script), "--manifest", str(manifest_path),
            "--runs-root", str(runs_root), "--results-root", str(results)]
    first = manifest["blocks"][0]["episodes"][0]
    for command in (("episode", "--episode-id", first["episode_id"]),
                    ("block", "--block-id", "block_01"), ("rebuild", "--overwrite")):
        process = subprocess.run(base + list(command), capture_output=True, text=True,
                                 env=environment, check=False)
        assert process.returncode == 0, process.stderr
    assert len(read_csv(results / "TEST_SPEC" / "tables" / "episode_summary.csv")[1]) == 6
    assert len(read_csv(results / "TEST_SPEC" / "tables" / "block_summary.csv")[1]) == 1
