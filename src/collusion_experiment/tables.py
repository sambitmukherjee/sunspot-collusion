"""Rebuildable, read-only episode and matched-block CSV analysis tables.

All outcomes are obtained from validated durable artifacts through metrics.py.
The manifest supplies identity and treatment position, never outcome values.
"""

import csv
import os
import tempfile
from pathlib import Path

from .metrics import (
    confirmatory_episode_outcomes, episode_summary, load_episode_artifacts,
    paired_prior_communication_difference, stage_summaries,
)
from .storage import specification_namespace

TABLE_SCHEMA_VERSION = "1"

EPISODE_IDENTITY = (
    "table_schema_version", "batch", "block", "replicate_id", "sequence_position",
    "episode_id", "run_name", "treatment_id", "prior_communication",
    "signal_condition", "episode_status", "last_committed_round",
    "specification_version", "prompt_family", "prompt_version", "model",
    "reasoning_effort", "signal_schedule_hash", "failure_type",
)
EPISODE_METRICS = (
    "round_count", "a_only_count", "b_only_count", "both_count", "neither_count",
    "a_only_rate", "b_only_rate", "both_rate", "neither_rate",
    "unique_participation_count", "unique_participation_rate", "role_balance_ratio",
    "seller_a_profit", "seller_b_profit", "joint_profit", "absolute_profit_gap",
    "seller_a_participation_cost", "seller_b_participation_cost", "joint_participation_cost",
    "seller_a_regulator_fines", "seller_b_regulator_fines", "joint_regulator_fines",
    "regulator_violation_count", "screened_unique_active_event_count",
    "public_signal_mapping_score", "public_signal_mutual_information_bits",
    "private_a_mutual_information_bits", "private_b_mutual_information_bits",
)
STAGE_METRICS = (
    "round_count", "a_only_count", "b_only_count", "both_count", "neither_count",
    "a_only_rate", "b_only_rate", "both_rate", "neither_rate",
    "unique_participation_count", "unique_participation_rate", "role_balance_ratio",
    "seller_a_profit", "seller_b_profit", "joint_profit", "absolute_profit_gap",
    "seller_a_participation_cost", "seller_b_participation_cost", "joint_participation_cost",
    "seller_a_regulator_fines", "seller_b_regulator_fines", "joint_regulator_fines",
    "regulator_violation_count", "screened_unique_active_event_count",
)
EPISODE_COLUMNS = EPISODE_IDENTITY + EPISODE_METRICS + tuple(
    f"stage{stage}_{metric}" for stage in (1, 2, 3) for metric in STAGE_METRICS
)

PAIRED_METRICS = (
    "stage3_unique_participation_rate", "stage3_joint_profit",
    "stage3_joint_regulator_fines", "stage3_regulator_violation_count",
)


def _paired_prefix(condition: str, metric: str) -> str:
    if metric == "public_signal_mapping_score":
        return "public_mapping_score"
    name = "stage3_unique_participation" if metric == "stage3_unique_participation_rate" else metric
    return f"{condition}_{name}"


BLOCK_IDENTITY = (
    "table_schema_version", "batch", "block", "replicate_id",
    "attempted_episode_count", "completed_episode_count", "failed_episode_count",
    "incomplete_episode_count", "block_status",
)
BLOCK_POSITIONS = tuple(
    field for position in range(1, 7)
    for field in (f"position_{position}_episode_id", f"position_{position}_episode_status")
)
BLOCK_PUBLIC = (
    "public_mapping_score_no_prior", "public_mapping_score_prior",
    "public_mapping_score_difference",
)
BLOCK_SECONDARY = tuple(
    f"{_paired_prefix(condition, metric)}_{suffix}"
    for condition in ("public", "private", "none")
    for metric in PAIRED_METRICS
    for suffix in ("no_prior", "prior", "difference")
)
BLOCK_COLUMNS = BLOCK_IDENTITY + BLOCK_POSITIONS + BLOCK_PUBLIC + BLOCK_SECONDARY


class TableIntegrityError(ValueError):
    """An existing row or manifest/artifact identity conflicts with source data."""


def _manifest_episode(manifest: dict, episode_id: str) -> tuple[dict, dict]:
    matches = [(block, episode) for block in manifest["blocks"]
               for episode in block["episodes"] if episode["episode_id"] == episode_id]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one manifest position for {episode_id!r}.")
    return matches[0]


def _validated_episode(run_dir: str | Path, manifest: dict, position: dict):
    episode = load_episode_artifacts(run_dir)
    config = episode.config
    for field in ("run_name", "replicate_id", "prior_communication", "signal_condition",
                  "signal_schedule_hash", "specification_version", "prompt_family", "prompt_version"):
        if config.get(field) != position.get(field) or type(config.get(field)) is not type(position.get(field)):
            raise TableIntegrityError(f"Saved episode and manifest disagree on {field}: {run_dir}")
    for field in ("response_contract_version", "prompt_caching_policy"):
        if config.get(field) != position[field]:
            raise TableIntegrityError(f"Saved V2 episode and manifest disagree on {field}: {run_dir}")
    for call_type, prefix in (("market_decision", "market"), ("communication", "communication")):
        schema = config.get("structured_response_schemas", {}).get(call_type, {})
        if (schema.get("name") != position[f"{prefix}_response_schema"]
                or schema.get("sha256") != position[f"{prefix}_response_schema_sha256"]):
            raise TableIntegrityError(f"Saved V2 schema and manifest disagree for {call_type}: {run_dir}")
    for field, expected in position["scientific_config"].items():
        if config.get(field) != expected:
            raise TableIntegrityError(f"Saved V2 scientific config disagrees on {field}: {run_dir}")
    if position["specification_version"] != manifest["specification_version"]:
        raise TableIntegrityError("Manifest and position specification IDs disagree.")
    return episode


def build_episode_summary_row(run_dir: str | Path, manifest: dict, episode_id: str) -> dict:
    """Build one manifest-identified row without changing source artifacts."""
    block, position = _manifest_episode(manifest, episode_id)
    episode = _validated_episode(run_dir, manifest, position)
    summary = episode_summary(episode)
    outcomes = confirmatory_episode_outcomes(episode)
    row = dict.fromkeys(EPISODE_COLUMNS)
    row.update({
        "table_schema_version": TABLE_SCHEMA_VERSION,
        "batch": manifest["specification_version"], "block": block["block_id"],
        "replicate_id": position["replicate_id"],
        "sequence_position": position["sequence_position"],
        "episode_id": episode_id, "run_name": position["run_name"],
        "treatment_id": position["treatment_id"],
        "prior_communication": position["prior_communication"],
        "signal_condition": position["signal_condition"],
        "episode_status": episode.status, "last_committed_round": episode.last_completed_round,
        "specification_version": episode.config["specification_version"],
        "prompt_family": episode.config["prompt_family"],
        "prompt_version": episode.config["prompt_version"],
        "model": episode.config["model"],
        "reasoning_effort": episode.config["reasoning_effort"],
        "signal_schedule_hash": episode.config["signal_schedule_hash"],
        "failure_type": summary["failure_type"],
    })
    if episode.status == "completed":
        for metric in EPISODE_METRICS:
            source = "role_balance" if metric == "role_balance_ratio" else metric
            row[metric] = outcomes[source] if source in outcomes else summary[source]
        for stage_number, stage in enumerate(stage_summaries(episode), 1):
            for metric in STAGE_METRICS:
                source = "role_balance" if metric == "role_balance_ratio" else metric
                row[f"stage{stage_number}_{metric}"] = stage[source]
    return row


def _csv_value(value) -> str:
    return "" if value is None else str(value)


def _read_table(path: Path, columns: tuple[str, ...]) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(columns):
            raise TableIntegrityError(f"Unexpected CSV schema in {path}.")
        return list(reader)


def _write_table_atomic(path: Path, columns: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=path.parent, prefix=f".{path.name}.",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _update(path: Path, columns: tuple[str, ...], key: tuple[str, ...], row: dict) -> Path:
    rows = _read_table(path, columns)
    new = {column: _csv_value(row[column]) for column in columns}
    identity = tuple(new[column] for column in key)
    existing = [item for item in rows if tuple(item[column] for column in key) == identity]
    if len(existing) > 1:
        raise TableIntegrityError(f"Duplicate table key {identity} in {path}.")
    if existing:
        if existing[0] != new:
            raise TableIntegrityError(f"Conflicting table row {identity} in {path}.")
        return path
    _write_table_atomic(path, columns, rows + [new])
    return path


def _table_path(results_root: str | Path, specification_id: str, filename: str) -> Path:
    return specification_namespace(results_root, specification_id) / "tables" / filename


def update_episode_summary_table(run_dir: str | Path, manifest: dict, episode_id: str,
                                 results_root: str | Path) -> Path:
    row = build_episode_summary_row(run_dir, manifest, episode_id)
    path = _table_path(results_root, row["batch"], "episode_summary.csv")
    return _update(path, EPISODE_COLUMNS, ("batch", "episode_id"), row)


def build_block_summary_row(manifest: dict, block_id: str, runs_root: str | Path) -> dict:
    """Build a block row only after all six planned positions have run directories."""
    blocks = [block for block in manifest["blocks"] if block["block_id"] == block_id]
    if len(blocks) != 1:
        raise ValueError(f"Expected exactly one block {block_id!r}.")
    block = blocks[0]
    positions = sorted(block["episodes"], key=lambda item: item["sequence_position"])
    if len(positions) != 6 or [item["sequence_position"] for item in positions] != list(range(1, 7)):
        raise TableIntegrityError("Block must contain six distinct manifest positions.")
    rows = []
    for position in positions:
        run_dir = (specification_namespace(runs_root, manifest["specification_version"])
                   / "runs" / position["run_name"])
        if not run_dir.is_dir():
            raise ValueError(f"Manifest position has not been attempted: {run_dir}")
        rows.append(build_episode_summary_row(run_dir, manifest, position["episode_id"]))
    counts = {status: sum(item["episode_status"] == status for item in rows)
              for status in ("completed", "failed", "incomplete")}
    row = dict.fromkeys(BLOCK_COLUMNS)
    row.update({
        "table_schema_version": TABLE_SCHEMA_VERSION,
        "batch": manifest["specification_version"], "block": block_id,
        "replicate_id": block["replicate_id"], "attempted_episode_count": len(rows),
        "completed_episode_count": counts["completed"],
        "failed_episode_count": counts["failed"],
        "incomplete_episode_count": counts["incomplete"],
        "block_status": ("incomplete" if counts["incomplete"] else
                         "completed_with_failures" if counts["failed"] else "completed"),
    })
    for position, episode in zip(positions, rows):
        number = position["sequence_position"]
        row[f"position_{number}_episode_id"] = episode["episode_id"]
        row[f"position_{number}_episode_status"] = episode["episode_status"]
    for condition in ("public", "private", "none"):
        for metric in (("public_signal_mapping_score",) + PAIRED_METRICS
                       if condition == "public" else PAIRED_METRICS):
            paired = paired_prior_communication_difference(
                [{**episode, "status": episode["episode_status"]} for episode in rows],
                signal_condition=condition, metric=metric,
            )
            if len(paired) != 1:
                raise TableIntegrityError(f"Missing matched {condition} pair in {block_id}.")
            values = paired[0]
            prefix = _paired_prefix(condition, metric)
            row[f"{prefix}_no_prior"] = values["false_value"]
            row[f"{prefix}_prior"] = values["true_value"]
            row[f"{prefix}_difference"] = values["difference"]
    return row


def update_block_summary_table(manifest: dict, block_id: str, runs_root: str | Path,
                               results_root: str | Path) -> Path:
    row = build_block_summary_row(manifest, block_id, runs_root)
    path = _table_path(results_root, row["batch"], "block_summary.csv")
    return _update(path, BLOCK_COLUMNS, ("batch", "block"), row)


def rebuild_summary_tables(manifest: dict, runs_root: str | Path, results_root: str | Path,
                           *, overwrite: bool = False) -> tuple[Path, Path]:
    """Recompute available episode rows and fully attempted blocks from artifacts."""
    batch = manifest["specification_version"]
    runs = specification_namespace(runs_root, batch) / "runs"
    episode_rows, block_rows = [], []
    for block in manifest["blocks"]:
        all_attempted = True
        for position in sorted(block["episodes"], key=lambda item: item["sequence_position"]):
            run_dir = runs / position["run_name"]
            if run_dir.is_dir():
                episode_rows.append(build_episode_summary_row(run_dir, manifest, position["episode_id"]))
            else:
                all_attempted = False
        if all_attempted:
            block_rows.append(build_block_summary_row(manifest, block["block_id"], runs_root))
    targets = (
        (_table_path(results_root, batch, "episode_summary.csv"), EPISODE_COLUMNS, episode_rows),
        (_table_path(results_root, batch, "block_summary.csv"), BLOCK_COLUMNS, block_rows),
    )
    for path, columns, rows in targets:
        normalized = [{column: _csv_value(row[column]) for column in columns} for row in rows]
        if path.exists() and not overwrite:
            if _read_table(path, columns) != normalized:
                raise TableIntegrityError(f"Rebuilt table differs from {path}; use overwrite explicitly.")
        else:
            _write_table_atomic(path, columns, normalized)
    return targets[0][0], targets[1][0]
