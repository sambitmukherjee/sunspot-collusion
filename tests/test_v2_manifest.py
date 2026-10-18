"""Offline verification of the prospective Structured Outputs V2 plan."""

from collections import Counter
from copy import deepcopy
from dataclasses import asdict, replace
import importlib.util
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

import pytest

from collusion_experiment.config import STRUCTURED_CONFIG
from collusion_experiment.metrics import (
    derive_analysis_bootstrap_seed, exact_paired_sign_flip_test,
    worst_case_public_pair_sensitivity,
)
from collusion_experiment.structured_outputs import (
    COMMUNICATION_RESPONSE_FORMAT, MARKET_KEYS, MARKET_RESPONSE_FORMAT,
    schema_provenance,
)
from collusion_experiment.tables import (
    BLOCK_COLUMNS, EPISODE_COLUMNS, TableIntegrityError, build_episode_summary_row,
)
from collusion_experiment.v2_manifest import (
    PREFIX_SOURCE_PAYLOAD_SHA256, construct_extension_orders, extension_seeds,
    generate_fixed_prefix_blocks, generate_v2_manifest,
    load_confirmatory_config, load_confirmatory_manifest,
    manifest_payload_sha256, validate_selected_manifest,
    validate_v2_manifest,
)
from collusion_experiment import v2_manifest as v2_module

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "configs"
V2_CONFIG = CONFIG_DIR / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml"
V2_MANIFEST = CONFIG_DIR / "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json"
PREFIX_SCIENTIFIC_KEYS = (
    "block_id", "replicate_id", "sequence_position", "episode_id", "run_name",
    "prior_communication", "signal_condition", "treatment_id",
    "public_signal_seed", "private_signal_seed_A", "private_signal_seed_B",
    "signal_schedule_hash",
)


@pytest.fixture(scope="module")
def plans():
    return (generate_fixed_prefix_blocks(),
            load_confirmatory_config(V2_CONFIG), load_confirmatory_manifest(V2_MANIFEST))


def _load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixed_prefix_is_reproduced_in_memory(plans):
    prefix, _, manifest = plans
    assert len(prefix) == 10
    assert manifest["prefix_source_payload_sha256"] == PREFIX_SOURCE_PAYLOAD_SHA256


def test_v2_config_schemas_prompt_contract_and_policy(plans):
    _, frozen, manifest = plans
    assert validate_selected_manifest(manifest, frozen) is STRUCTURED_CONFIG
    assert frozen["prompt_family"] == "fish_p1_adapted"
    assert frozen["prompt_version"] == "PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1"
    assert frozen["response_contract_version"] == "STRUCTURED_OUTPUTS_V1"
    assert frozen["infrastructure"]["prompt_caching_policy"] == "provider_default"
    schemas = schema_provenance()
    assert frozen["schemas"] == {key: {"name": value["name"],
                                      "response_format_sha256": value["sha256"]}
                                 for key, value in schemas.items()}
    assert MARKET_RESPONSE_FORMAT["type"] == COMMUNICATION_RESPONSE_FORMAT["type"] == "json_schema"
    assert MARKET_RESPONSE_FORMAT["json_schema"]["strict"] is True
    assert list(MARKET_RESPONSE_FORMAT["json_schema"]["schema"]["properties"]) == list(MARKET_KEYS)
    assert COMMUNICATION_RESPONSE_FORMAT["json_schema"]["schema"] == {
        "type": "object", "properties": {"message": {"type": "string"}},
        "required": ["message"], "additionalProperties": False}
    assert manifest["prompt_caching_policy"] == "provider_default"


def test_v2_structure_prefix_matching_balance_and_hash(plans):
    prefix, frozen, manifest = plans
    assert validate_v2_manifest(manifest, frozen)["episodes"] == 180
    assert len(manifest["blocks"]) == 30
    ids, names = [], []
    positions = Counter()
    for block in manifest["blocks"]:
        assert len(block["episodes"]) == 6
        assert {row["treatment_id"] for row in block["episodes"]} == {
            "no_prior_communication__none", "no_prior_communication__private",
            "no_prior_communication__public", "prior_communication__none",
            "prior_communication__private", "prior_communication__public"}
        for position, row in enumerate(block["episodes"], 1):
            assert row["sequence_position"] == position
            assert row["response_contract_version"] == "STRUCTURED_OUTPUTS_V1"
            assert row["prompt_caching_policy"] == "provider_default"
            assert row["scientific_config"] == manifest["scientific_config"]
            ids.append(row["episode_id"])
            names.append(row["run_name"])
            positions[row["treatment_id"], position] += 1
        for condition, keys in (("public", ("public_signal_seed",)),
                                ("private", ("private_signal_seed_A", "private_signal_seed_B"))):
            pair = [row for row in block["episodes"] if row["signal_condition"] == condition]
            assert len(pair) == 2
            assert all(pair[0][key] == pair[1][key] for key in keys)
            assert pair[0]["signal_schedule_hash"] == pair[1]["signal_schedule_hash"]
    assert len(set(ids)) == len(set(names)) == 180
    assert set(positions.values()) == {5}
    for old_block, new_block in zip(prefix, manifest["blocks"][:10]):
        for old, new in zip(old_block["episodes"], new_block["episodes"]):
            assert {key: new[key] for key in PREFIX_SCIENTIFIC_KEYS} == {
                key: old[key] for key in PREFIX_SCIENTIFIC_KEYS}
    assert manifest["prefix_source_payload_sha256"] == PREFIX_SOURCE_PAYLOAD_SHA256
    assert manifest_payload_sha256(manifest) == manifest["manifest_payload_sha256"]
    broken = deepcopy(manifest)
    broken["blocks"][10]["episodes"][0]["signal_schedule_hash"] = "0" * 64
    broken["manifest_payload_sha256"] = manifest_payload_sha256(broken)
    with pytest.raises(ValueError, match="schedule hash"):
        validate_v2_manifest(broken, frozen)


def test_extension_is_fresh_process_reproducible_and_not_screened(plans, monkeypatch):
    prefix, frozen, manifest = plans
    assert manifest["extension_seed"] == extension_seeds(PREFIX_SOURCE_PAYLOAD_SHA256)["extension_seed"]
    assert len(construct_extension_orders(prefix, manifest["treatment_order_seed"])) == 20
    calls = []
    real = v2_module.make_signal_schedule

    def counted(condition, **kwargs):
        calls.append(condition)
        return real(condition, **kwargs)

    monkeypatch.setattr(v2_module, "make_signal_schedule", counted)
    generated = generate_v2_manifest(frozen)
    assert generated["manifest_payload_sha256"] == manifest["manifest_payload_sha256"]
    assert Counter(calls) == {"none": 60, "private": 60, "public": 60}
    code = (
        "from collusion_experiment.v2_manifest import load_confirmatory_config,generate_v2_manifest;"
        f"f=load_confirmatory_config({str(V2_CONFIG)!r});"
        "print(generate_v2_manifest(f)['manifest_payload_sha256'])"
    )
    result = subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)
    assert result.stdout.strip() == manifest["manifest_payload_sha256"]


def test_v2_dry_runs_and_namespaces_do_not_call_models(plans, tmp_path, capsys):
    _, _, v2 = plans
    one = _load_script("run_episode")
    block = _load_script("run_block")

    def forbidden(*args, **kwargs):
        raise AssertionError("Dry run must not create a client or execute an episode")

    samples = (v2["blocks"][0]["episodes"][0],
               v2["blocks"][10]["episodes"][2],
               v2["blocks"][29]["episodes"][5])
    for row in samples:
        assert one.run_selected_episode(
            episode_id=row["episode_id"], config_path=V2_CONFIG,
            manifest_path=V2_MANIFEST, runs_root=tmp_path,
            runner=forbidden, client_factory=forbidden) == row
    assert len(block.run_selected_block(
        block_id="block_11", config_path=V2_CONFIG, manifest_path=V2_MANIFEST,
        runs_root=tmp_path, runner=forbidden, client_factory=forbidden)) == 6
    output = capsys.readouterr().out
    assert "DRY RUN" in output and v2["specification_version"] in output
    assert all(str(tmp_path / v2["specification_version"] / "runs" / row["run_name"]) in output
               for row in samples)
    assert list(tmp_path.iterdir()) == []
    tampered = deepcopy(v2)
    tampered["specification_version"] = "WRONG_SPECIFICATION"
    tampered["manifest_payload_sha256"] = manifest_payload_sha256(tampered)
    tampered_path = tmp_path / "tampered_manifest.json"
    tampered_path.write_text(json.dumps(tampered))
    with pytest.raises(ValueError, match="version"):
        one.run_selected_episode(episode_id=samples[0]["episode_id"],
                                 config_path=V2_CONFIG, manifest_path=tampered_path,
                                 runs_root=tmp_path)


def test_exact_thirty_pair_test_and_missing_pair_sensitivity():
    small = [0.125, -0.025, 0.0, 0.125]
    observed = sum(small)
    null = [sum(sign * value for sign, value in zip(signs, small))
            for signs in product((-1, 1), repeat=len(small))]
    result = exact_paired_sign_flip_test(small)
    assert result["one_sided_p_value"] == sum(value >= observed - 1e-12 for value in null) / 16
    assert result["two_sided_p_value"] == sum(abs(value) >= abs(observed) - 1e-12 for value in null) / 16
    thirty = exact_paired_sign_flip_test([1 / 80] * 29 + [0.0])
    assert thirty["n_complete_pairs"] == 30
    assert thirty["one_sided_p_value"] == 2 ** -29
    assert derive_analysis_bootstrap_seed(STRUCTURED_CONFIG.specification_version) == 14018003554666323344
    sensitivity = worst_case_public_pair_sensitivity(
        [{"replicate_id": 1, "true_value": 0.75, "false_value": None}],
        planned_replicate_ids=range(1, 31))
    assert sensitivity["planned_pairs"] == 30 and sensitivity["complete_pairs"] == 0


def test_v2_tables_keep_status_and_block_fields_without_fixed_ten_block_limit(plans, synthetic_analysis_run):
    assert {"batch", "block", "episode_status"} <= set(EPISODE_COLUMNS)
    assert {"batch", "block", "block_status", "public_mapping_score_difference"} <= set(BLOCK_COLUMNS)
    source = (ROOT / "src" / "collusion_experiment" / "tables.py").read_text()
    assert 'for block in manifest["blocks"]' in source
    assert 'episode_rows.append(build_episode_summary_row' in source
    assert 'block_rows.append(build_block_summary_row' in source
    position = deepcopy(plans[2]["blocks"][10]["episodes"][0])
    design = replace(STRUCTURED_CONFIG, num_rounds=8, communication_end_round=2,
                     signal_start_round=5, pattern_window=2, pattern_max_period=2)
    path = synthetic_analysis_run(position["run_name"], prior=position["prior_communication"],
                                  condition=position["signal_condition"], replicate=11,
                                  status="failed", design=design)
    saved = json.loads((path / "config.json").read_text())
    saved["signal_schedule_hash"] = position["signal_schedule_hash"]
    saved["response_contract_version"] = "STRUCTURED_OUTPUTS_V1"
    saved["prompt_caching_policy"] = "provider_default"
    saved["structured_response_schemas"] = schema_provenance()
    (path / "config.json").write_text(json.dumps(saved))
    failure = json.loads((path / "failure.json").read_text())
    (path / "failure.json").write_text(json.dumps(failure))
    scientific = asdict(design)
    for key in ("specification_version", "prompt_family", "prompt_version"):
        scientific.pop(key)
    for key in ("public_signal_values", "seller_labels"):
        scientific[key] = list(scientific[key])
    position["scientific_config"] = scientific
    manifest = {"specification_version": design.specification_version,
                "blocks": [{"block_id": position["block_id"], "replicate_id": 11,
                            "episodes": [position]}]}
    row = build_episode_summary_row(path, manifest, position["episode_id"])
    assert row["batch"] == design.specification_version and row["block"] == "block_11"
    assert row["episode_status"] == "failed" and row["public_signal_mapping_score"] is None
    saved["structured_response_schemas"]["communication"]["sha256"] = "0" * 64
    (path / "config.json").write_text(json.dumps(saved))
    with pytest.raises(TableIntegrityError, match="schema"):
        build_episode_summary_row(path, manifest, position["episode_id"])
