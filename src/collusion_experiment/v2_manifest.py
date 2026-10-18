"""Offline V2 manifest generation from a fixed schedule prefix."""

from collections import Counter
from dataclasses import asdict, fields
import hashlib
import json
from pathlib import Path
import random

import yaml

from .config import STRUCTURED_CONFIG, ExperimentConfig
from .signals import make_signal_schedule, signal_schedule_hash
from .storage import stable_json
from .structured_outputs import (
    COMMUNICATION_RESPONSE_FORMAT, CONTRACT_VERSION, MARKET_KEYS,
    MARKET_RESPONSE_FORMAT, schema_provenance,
)

ALGORITHM_VERSION = "MANIFEST_V2_30_BLOCKS"
PREFIX_ORDER_AND_SIGNAL_SEED = 4410578998177848469
EXTENSION_DOMAIN = "sunspot-collusion/v2/blocks_11_to_30|"
ORDER_DOMAIN = "sunspot-collusion/v2/treatment_order|"
SIGNAL_DOMAIN = "sunspot-collusion/v2/signal_seeds|"
PREFIX_SOURCE_PAYLOAD_SHA256 = "ebc17aba281f5ea6e6e593aef0ebc453475634f3644ab7b7429548d000500d71"
PREFIX_SCHEDULE_SHA256 = "317198b8ae463cb1e2e2e5ab0ad4138444cf44400db6ee694298fcdc7c996821"
PRIMARY_CONTRAST = "prior_communication=True, public minus prior_communication=False, public"
SECONDARY_OUTCOMES = (
    "public_signal_mutual_information_bits", "stage3_unique_participation_rate",
    "stage3_both_rate", "stage3_neither_rate", "stage3_role_balance_ratio",
    "stage3_joint_profit", "stage3_joint_regulator_fines",
    "stage3_regulator_violation_count",
)
SEED_DERIVATION = (
    "SHA-256 first 8 bytes, big-endian, of 'sunspot-collusion/v2/blocks_11_to_30|' "
    "+ fixed prefix source payload SHA-256; independent treatment_order and "
    "signal_seeds streams use the same derivation with their own domain strings "
    "and the decimal extension seed"
)
V2_BOOTSTRAP_SEED_DESCRIPTION = "fixed paired-block bootstrap seed: 14018003554666323344"


def _derived_seed(domain: str, text: str) -> int:
    return int.from_bytes(hashlib.sha256((domain + text).encode("utf-8")).digest()[:8], "big")


def extension_seeds(prefix_payload_sha256: str) -> dict[str, int]:
    if len(prefix_payload_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in prefix_payload_sha256):
        raise ValueError("A lowercase prefix payload SHA-256 is required.")
    root = _derived_seed(EXTENSION_DOMAIN, prefix_payload_sha256)
    return {"extension_seed": root,
            "treatment_order_seed": _derived_seed(ORDER_DOMAIN, str(root)),
            "signal_seed_stream_seed": _derived_seed(SIGNAL_DOMAIN, str(root))}


def _scientific_config(config: ExperimentConfig) -> dict:
    values = asdict(config)
    for key in ("specification_version", "prompt_family", "prompt_version"):
        values.pop(key)
    for key in ("public_signal_values", "seller_labels"):
        values[key] = list(values[key])
    return values


def treatment_cell_definitions() -> list[dict]:
    return [
        {"prior_communication": prior, "signal_condition": condition,
         "treatment_id": f"{'prior_communication' if prior else 'no_prior_communication'}__{condition}"}
        for prior in (False, True) for condition in ("none", "private", "public")
    ]


def _draw_block_signal_seeds(rng: random.Random) -> dict:
    public = rng.getrandbits(64)
    private_a = rng.getrandbits(64)
    private_b = rng.getrandbits(64)
    while private_b == private_a:
        private_b = rng.getrandbits(64)
    return {"public_signal_seed": public, "private_signal_seed_A": private_a,
            "private_signal_seed_B": private_b}


def manifest_payload_sha256(manifest: dict) -> str:
    payload = {key: value for key, value in manifest.items() if key != "manifest_payload_sha256"}
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def load_confirmatory_config(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError("Confirmatory YAML must be a mapping.")
    return value


def load_confirmatory_manifest(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Confirmatory manifest must be a JSON object.")
    return value


def generate_fixed_prefix_blocks(config: ExperimentConfig = STRUCTURED_CONFIG) -> list[dict]:
    """Reconstruct and fingerprint the fixed first ten blocks of the V2 plan."""
    rng = random.Random(PREFIX_ORDER_AND_SIGNAL_SEED)
    cells = treatment_cell_definitions()
    rng.shuffle(cells)
    shifts = list(range(len(cells)))
    rng.shuffle(shifts)
    orders = [[cells[(position + shift) % len(cells)].copy() for position in range(len(cells))]
              for shift in shifts + shifts[:4]]
    rng.shuffle(orders)
    blocks = []
    scientific_rows = []
    for replicate_id, order in enumerate(orders, 1):
        block_id = f"block_{replicate_id:02d}"
        seeds = _draw_block_signal_seeds(rng)
        episodes = []
        for position, cell in enumerate(order, 1):
            condition = cell["signal_condition"]
            active = {"public_signal_seed": seeds["public_signal_seed"] if condition == "public" else None,
                      "private_signal_seed_A": seeds["private_signal_seed_A"] if condition == "private" else None,
                      "private_signal_seed_B": seeds["private_signal_seed_B"] if condition == "private" else None}
            schedule = make_signal_schedule(condition, **active, config=config)
            episode_id = f"{block_id}__{cell['treatment_id']}"
            row = {"episode_id": episode_id, "run_name": f"confirmatory_{episode_id}",
                   "block_id": block_id, "replicate_id": replicate_id,
                   "sequence_position": position, **cell, **active,
                   "signal_schedule_hash": signal_schedule_hash(schedule)}
            scientific_rows.append(row)
            episodes.append(_v2_row(row, config))
        blocks.append({"block_id": block_id, "replicate_id": replicate_id, "episodes": episodes})
    fingerprint = hashlib.sha256(stable_json(scientific_rows).encode("utf-8")).hexdigest()
    if fingerprint != PREFIX_SCHEDULE_SHA256:
        raise ValueError("Fixed prefix schedule fingerprint mismatch.")
    return blocks


def validate_v2_config(frozen: dict, config: ExperimentConfig = STRUCTURED_CONFIG) -> None:
    if config != STRUCTURED_CONFIG or config.response_contract_version != CONTRACT_VERSION:
        raise ValueError("V2 requires the canonical implemented Structured Outputs config.")
    if (frozen.get("specification_version") != config.specification_version
            or frozen.get("prompt_family") != config.prompt_family
            or frozen.get("prompt_version") != config.prompt_version
            or frozen.get("response_contract_version") != CONTRACT_VERSION
            or frozen.get("design_status") != "confirmatory"):
        raise ValueError("V2 specification, prompt, response contract, or status mismatch.")
    scientific = frozen.get("scientific_config")
    expected = _scientific_config(config)
    if not isinstance(scientific, dict) or set(scientific) != set(expected):
        raise ValueError("V2 scientific_config fields differ from ExperimentConfig.")
    for field in fields(ExperimentConfig):
        if field.name not in expected:
            continue
        actual = scientific[field.name]
        expected_value = expected[field.name]
        if field.name in ("public_signal_values", "seller_labels"):
            actual = tuple(actual)
            expected_value = tuple(expected_value)
        if actual != expected_value or type(actual) is not type(expected_value):
            raise ValueError(f"V2 scientific_config mismatch: {field.name}.")
    schemas = schema_provenance()
    for call_type in ("communication", "market_decision"):
        actual = frozen.get("schemas", {}).get(call_type)
        if actual != {"name": schemas[call_type]["name"],
                      "response_format_sha256": schemas[call_type]["sha256"]}:
            raise ValueError(f"V2 {call_type} schema name/hash mismatch.")
    market = MARKET_RESPONSE_FORMAT["json_schema"]["schema"]
    communication = COMMUNICATION_RESPONSE_FORMAT["json_schema"]["schema"]
    if (list(market["properties"]) != list(MARKET_KEYS)
            or market["required"] != list(MARKET_KEYS)
            or market["additionalProperties"] is not False
            or list(communication["properties"]) != ["message"]
            or communication["required"] != ["message"]
            or communication["additionalProperties"] is not False):
        raise ValueError("Implemented Structured Outputs semantics differ from V2 plan.")
    policy = frozen.get("infrastructure", {})
    if policy.get("prompt_caching_policy") != "provider_default":
        raise ValueError("V2 prompt caching must retain the provider default.")
    if frozen.get("sample_size") != {
        "num_blocks": 30, "episodes_per_block": 6, "planned_episodes": 180,
        "stopping_rule": "complete_all_planned_episodes",
    }:
        raise ValueError("V2 sample size or stopping rule mismatch.")
    if (frozen.get("manifest_algorithm_version") != ALGORITHM_VERSION
            or frozen.get("manifest_generation_seed_derivation") != SEED_DERIVATION):
        raise ValueError("V2 manifest algorithm provenance mismatch.")
    if frozen.get("primary_analysis") != {
        "outcome": "public_signal_mapping_score", "contrast": PRIMARY_CONTRAST,
        "test": "exact_one_sided_paired_sign_flip_mean", "direction": "greater_than_zero",
        "alpha": 0.05, "bootstrap_resamples": 10000,
        "bootstrap_confidence_level": 0.95,
            "bootstrap_seed_derivation": V2_BOOTSTRAP_SEED_DESCRIPTION,
    }:
        raise ValueError("V2 primary analysis differs from the frozen design.")
    if tuple(frozen.get("secondary_outcomes", ())) != SECONDARY_OUTCOMES:
        raise ValueError("V2 secondary outcomes mismatch.")
    if frozen.get("failure_policy") != {
        "failed_episode_occupies_position": True, "replace_in_primary_manifest": False,
        "splice_partial_episode": False,
        "missing_public_pair_analysis": "complete_pairs_with_worst_case_sensitivity",
    }:
        raise ValueError("V2 failure policy mismatch.")


def construct_extension_orders(prefix_blocks: list[dict], order_seed: int) -> list[list[dict]]:
    """Decompose the residual 6×6 count matrix into 20 perfect matchings.

    Python random.Random (MT19937) shuffles fixed-order treatment and candidate
    position lists. Depth-first augmenting paths resolve ties. A regular
    bipartite residual always has a perfect matching after each removal.
    """
    cells = treatment_cell_definitions()
    by_id = {cell["treatment_id"]: cell for cell in cells}
    treatment_ids = list(by_id)
    prefix_counts = Counter((row["treatment_id"], row["sequence_position"])
                            for block in prefix_blocks for row in block["episodes"])
    residual = {(treatment_id, position): 5 - prefix_counts[treatment_id, position]
                for treatment_id in treatment_ids for position in range(1, 7)}
    if (any(value < 0 for value in residual.values())
            or any(sum(residual[t, p] for p in range(1, 7)) != 20 for t in treatment_ids)
            or any(sum(residual[t, p] for t in treatment_ids) != 20 for p in range(1, 7))):
        raise ValueError("Exact V2 position balance is impossible with this prefix.")
    rng = random.Random(order_seed)
    orders = []
    for _ in range(20):
        treatment_order = treatment_ids.copy()
        rng.shuffle(treatment_order)
        matched: dict[int, str] = {}

        def augment(treatment_id: str, seen: set[int]) -> bool:
            candidates = [p for p in range(1, 7) if residual[treatment_id, p] > 0]
            rng.shuffle(candidates)
            for position in candidates:
                if position in seen:
                    continue
                seen.add(position)
                if position not in matched or augment(matched[position], seen):
                    matched[position] = treatment_id
                    return True
            return False

        for treatment_id in treatment_order:
            if not augment(treatment_id, set()):
                raise ValueError("Residual position matching failed.")
        if len(matched) != 6:
            raise ValueError("Incomplete residual position matching.")
        orders.append([by_id[matched[position]].copy() for position in range(1, 7)])
        for position, treatment_id in matched.items():
            residual[treatment_id, position] -= 1
    if any(residual.values()):
        raise ValueError("Residual position counts did not reach zero.")
    return orders


def _v2_row(row: dict, config: ExperimentConfig) -> dict:
    schemas = schema_provenance()
    return {**row, "specification_version": config.specification_version,
            "prompt_family": config.prompt_family, "prompt_version": config.prompt_version,
            "response_contract_version": CONTRACT_VERSION,
            "market_response_schema": schemas["market_decision"]["name"],
            "market_response_schema_sha256": schemas["market_decision"]["sha256"],
            "communication_response_schema": schemas["communication"]["name"],
            "communication_response_schema_sha256": schemas["communication"]["sha256"],
            "prompt_caching_policy": "provider_default",
            "scientific_config": _scientific_config(config)}


def generate_v2_manifest(frozen: dict, config: ExperimentConfig = STRUCTURED_CONFIG) -> dict:
    validate_v2_config(frozen, config)
    blocks = generate_fixed_prefix_blocks(config)
    seeds = extension_seeds(PREFIX_SOURCE_PAYLOAD_SHA256)
    orders = construct_extension_orders(blocks, seeds["treatment_order_seed"])
    signal_rng = random.Random(seeds["signal_seed_stream_seed"])
    for replicate_id, order in enumerate(orders, 11):
        block_id = f"block_{replicate_id:02d}"
        block_seeds = _draw_block_signal_seeds(signal_rng)
        episodes = []
        for position, cell in enumerate(order, 1):
            condition = cell["signal_condition"]
            active = {"public_signal_seed": block_seeds["public_signal_seed"] if condition == "public" else None,
                      "private_signal_seed_A": block_seeds["private_signal_seed_A"] if condition == "private" else None,
                      "private_signal_seed_B": block_seeds["private_signal_seed_B"] if condition == "private" else None}
            schedule = make_signal_schedule(condition, **active, config=config)
            episode_id = f"{block_id}__{cell['treatment_id']}"
            row = {"episode_id": episode_id, "run_name": f"confirmatory_{episode_id}",
                   "block_id": block_id, "replicate_id": replicate_id,
                   "sequence_position": position, **cell, **active,
                   "signal_schedule_hash": signal_schedule_hash(schedule)}
            episodes.append(_v2_row(row, config))
        blocks.append({"block_id": block_id, "replicate_id": replicate_id, "episodes": episodes})
    schemas = schema_provenance()
    manifest = {"manifest_algorithm_version": ALGORITHM_VERSION,
                "specification_version": config.specification_version,
                "prompt_family": config.prompt_family, "prompt_version": config.prompt_version,
                "response_contract_version": CONTRACT_VERSION,
                "market_response_schema": schemas["market_decision"]["name"],
                "market_response_schema_sha256": schemas["market_decision"]["sha256"],
                "communication_response_schema": schemas["communication"]["name"],
                "communication_response_schema_sha256": schemas["communication"]["sha256"],
                "prompt_caching_policy": "provider_default",
                "scientific_config": _scientific_config(config),
                "scientific_config_sha256": hashlib.sha256(stable_json(_scientific_config(config)).encode()).hexdigest(),
                "prefix_source_payload_sha256": PREFIX_SOURCE_PAYLOAD_SHA256, **seeds,
                "extension_seed_derivation": SEED_DERIVATION,
                "num_blocks": 30, "episodes_per_block": 6, "planned_episodes": 180,
                "blocks": blocks}
    manifest["manifest_payload_sha256"] = manifest_payload_sha256(manifest)
    return manifest


def validate_v2_manifest(manifest: dict, frozen: dict) -> dict:
    validate_v2_config(frozen)
    if not isinstance(manifest, dict) or manifest.get("manifest_payload_sha256") != manifest_payload_sha256(manifest):
        raise ValueError("V2 manifest payload hash mismatch.")
    blocks = manifest.get("blocks")
    if not isinstance(blocks, list) or len(blocks) != 30:
        raise ValueError("V2 manifest must contain 30 blocks.")
    counts = Counter()
    ids, names = set(), set()
    cells = {cell["treatment_id"] for cell in treatment_cell_definitions()}
    for index, block in enumerate(blocks, 1):
        block_id = f"block_{index:02d}"
        if block.get("block_id") != block_id or block.get("replicate_id") != index:
            raise ValueError("V2 block identity/order mismatch.")
        rows = block.get("episodes")
        if not isinstance(rows, list) or len(rows) != 6 or {row.get("treatment_id") for row in rows} != cells:
            raise ValueError("V2 block must contain all six treatment cells.")
        for position, row in enumerate(rows, 1):
            if (row.get("sequence_position") != position or row.get("block_id") != block_id
                    or row.get("replicate_id") != index):
                raise ValueError("V2 sequence position mismatch.")
            ids.add(row.get("episode_id"))
            names.add(row.get("run_name"))
            counts[row["treatment_id"], position] += 1
            active = {key: row.get(key) for key in
                      ("public_signal_seed", "private_signal_seed_A", "private_signal_seed_B")}
            schedule = make_signal_schedule(row["signal_condition"], **active, config=STRUCTURED_CONFIG)
            if row.get("signal_schedule_hash") != signal_schedule_hash(schedule):
                raise ValueError("V2 signal schedule hash mismatch.")
        for condition, keys in (("public", ("public_signal_seed",)),
                                ("private", ("private_signal_seed_A", "private_signal_seed_B"))):
            pair = [row for row in rows if row["signal_condition"] == condition]
            if any(pair[0][key] != pair[1][key] for key in keys) or pair[0]["signal_schedule_hash"] != pair[1]["signal_schedule_hash"]:
                raise ValueError("V2 matched signal schedules disagree.")
    if len(ids) != 180 or len(names) != 180 or any(counts[cell, position] != 5
            for cell in cells for position in range(1, 7)):
        raise ValueError("V2 uniqueness or exact treatment-position balance failed.")
    expected = generate_v2_manifest(frozen)
    if manifest != expected:
        raise ValueError("V2 manifest differs from deterministic validated extension.")
    return {"blocks": 30, "episodes": 180, "counterbalanced": True,
            "matched_schedules": True,
            "prefix_source_payload_sha256": PREFIX_SOURCE_PAYLOAD_SHA256,
            "manifest_payload_sha256": manifest["manifest_payload_sha256"]}


def validate_selected_manifest(manifest: dict, frozen: dict) -> ExperimentConfig:
    """Validate the active V2 plan and return its runtime config."""
    if frozen.get("specification_version") != manifest.get("specification_version"):
        raise ValueError("Config and manifest specification versions differ.")
    validate_v2_manifest(manifest, frozen)
    return STRUCTURED_CONFIG
