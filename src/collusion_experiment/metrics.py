"""Read-only descriptive analysis of durable episode artifacts.

Episodes, not rounds, are the independent units for treatment comparisons.
Stage and round summaries are descriptive diagnostics. Phase 8 freezes named
confirmatory outcomes and episode-level inferential helpers below.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, fields
from itertools import product
import json
from math import isclose, isfinite, log2
from pathlib import Path
import random
from statistics import mean, median, stdev
from typing import Any, Iterable

from .config import DEFAULT_CONFIG, ExperimentConfig
from .market import validate_action_pair
from .storage import CONFIG_FILENAME, FAILURE_FILENAME, FINAL_FILENAME, ROUNDS_FILENAME

STATES = ("A_ONLY", "B_ONLY", "BOTH", "NEITHER")


class ArtifactConsistencyError(ValueError):
    """A run artifact is missing, malformed, or scientifically inconsistent."""


@dataclass(frozen=True)
class EpisodeArtifacts:
    run_dir: Path
    config: dict
    design: ExperimentConfig
    rounds: tuple[dict, ...]
    status: str  # completed, failed, or incomplete; corrupt data raises.
    final: dict | None
    failure: dict | None
    last_completed_round: int


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ArtifactConsistencyError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArtifactConsistencyError(f"Expected a JSON object in {path}.")
    return value


def _read_jsonl(path: Path) -> tuple[dict, ...]:
    try:
        with path.open(encoding="utf-8") as handle:
            records = []
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    raise ArtifactConsistencyError(f"Blank JSONL line {line_number} in {path}.")
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ArtifactConsistencyError(f"JSONL line {line_number} is not an object in {path}.")
                records.append(record)
    except (OSError, ValueError) as exc:
        if isinstance(exc, ArtifactConsistencyError):
            raise
        raise ArtifactConsistencyError(f"Cannot read valid JSONL from {path}: {exc}") from exc
    return tuple(records)


def _loaded_design(config: dict) -> ExperimentConfig:
    try:
        values = {field.name: config[field.name] for field in fields(ExperimentConfig)}
        values["public_signal_values"] = tuple(values["public_signal_values"])
        values["seller_labels"] = tuple(values["seller_labels"])
        return ExperimentConfig(**values)
    except (KeyError, TypeError, ValueError) as exc:
        raise ArtifactConsistencyError(f"Invalid saved experiment configuration: {exc}") from exc


def stage_for_round(round_number: int, episode_config: dict | ExperimentConfig) -> int:
    """Derive stage only from this episode's saved timing, never local defaults."""
    try:
        horizon = episode_config["num_rounds"] if isinstance(episode_config, dict) else episode_config.num_rounds
        communication_end = (episode_config["communication_end_round"] if isinstance(episode_config, dict)
                             else episode_config.communication_end_round)
        signal_start = (episode_config["signal_start_round"] if isinstance(episode_config, dict)
                        else episode_config.signal_start_round)
    except KeyError as exc:
        raise ArtifactConsistencyError(f"Missing saved timing: {exc}") from exc
    if isinstance(round_number, bool) or not isinstance(round_number, int) or not 1 <= round_number <= horizon:
        raise ArtifactConsistencyError(f"Round {round_number!r} lies outside saved horizon 1..{horizon}.")
    return 1 if round_number <= communication_end else (2 if round_number < signal_start else 3)


def participation_state(round_record: dict, design: ExperimentConfig) -> str:
    """Classify numerical bids, not sales or profits, in fixed A/B order."""
    a, b = validate_action_pair(round_record["actions"], design)
    active = (a["action_type"] == "bid", b["action_type"] == "bid")
    return {(True, False): "A_ONLY", (False, True): "B_ONLY",
            (True, True): "BOTH", (False, False): "NEITHER"}[active]


def _pair(record: dict, key: str, round_number: int) -> tuple[float, float]:
    value = record.get(key)
    if not isinstance(value, list) or len(value) != 2:
        raise ArtifactConsistencyError(f"Round {round_number}: {key} must contain A and B values.")
    try:
        pair = float(value[0]), float(value[1])
    except (TypeError, ValueError) as exc:
        raise ArtifactConsistencyError(f"Round {round_number}: invalid {key} values.") from exc
    if not all(isfinite(number) for number in pair):
        raise ArtifactConsistencyError(f"Round {round_number}: nonfinite {key} values.")
    return pair


def _amount(record: dict, key: str, context: str) -> float:
    try:
        value = float(record[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ArtifactConsistencyError(f"{context}: invalid or missing {key}.") from exc
    if not isfinite(value):
        raise ArtifactConsistencyError(f"{context}: nonfinite {key}.")
    return value


def _same_amount(actual: float, expected: float) -> bool:
    return isclose(actual, expected, rel_tol=0, abs_tol=1e-6)


def load_episode_artifacts(run_dir: str | Path) -> EpisodeArtifacts:
    """Load and validate one run without writing to its directory.

    A failed run may have a committed prefix. A missing final/failure artifact is
    incomplete. Corrupt or inconsistent artifacts raise ArtifactConsistencyError.
    """
    run_dir = Path(run_dir)
    config = _read_json(run_dir / CONFIG_FILENAME)
    design = _loaded_design(config)
    rounds = _read_jsonl(run_dir / ROUNDS_FILENAME)
    final_path, failure_path = run_dir / FINAL_FILENAME, run_dir / FAILURE_FILENAME
    final = _read_json(final_path) if final_path.is_file() else None
    failure = _read_json(failure_path) if failure_path.is_file() else None
    if final is not None and failure is not None:
        raise ArtifactConsistencyError(f"Both final and failure artifacts exist in {run_dir}.")
    status = "completed" if final is not None else ("failed" if failure is not None else "incomplete")
    if config.get("run_name") != run_dir.name:
        raise ArtifactConsistencyError("Saved run_name disagrees with run directory.")
    if type(config.get("prior_communication")) is not bool:
        raise ArtifactConsistencyError("Saved prior_communication must be Boolean.")
    if config.get("signal_condition") not in ("none", "private", "public"):
        raise ArtifactConsistencyError("Saved signal_condition is invalid.")
    if type(config.get("replicate_id")) is not int or config["replicate_id"] < 1:
        raise ArtifactConsistencyError("Saved replicate_id must be a positive integer.")
    if len(rounds) > design.num_rounds:
        raise ArtifactConsistencyError("More round records than the saved horizon.")
    cumulative = [0.0, 0.0]
    for expected_round, record in enumerate(rounds, 1):
        if (type(record.get("round_number")) is not int or record["round_number"] != expected_round
                or type(record.get("round")) is not int or record["round"] != expected_round):
            raise ArtifactConsistencyError(f"Round sequence has a gap/duplicate at position {expected_round}.")
        expected_stage = stage_for_round(expected_round, design)
        if type(record.get("analytical_stage")) is not int or record["analytical_stage"] != expected_stage:
            raise ArtifactConsistencyError(f"Round {expected_round}: stored stage disagrees with saved timing.")
        treatment = record.get("treatment", {})
        if (type(treatment.get("prior_communication")) is not bool
                or treatment.get("prior_communication") != config["prior_communication"]
                or treatment.get("signal_condition") != config["signal_condition"]
                or type(treatment.get("replicate_id")) is not int
                or treatment.get("replicate_id") != config["replicate_id"]):
            raise ArtifactConsistencyError(f"Round {expected_round}: treatment metadata disagrees with config.")
        try:
            participation_state(record, design)
        except (KeyError, TypeError, ValueError) as exc:
            raise ArtifactConsistencyError(f"Round {expected_round}: invalid market actions: {exc}") from exc
        profits = _pair(record, "net_profits", expected_round)
        _pair(record, "participation_costs", expected_round)
        _pair(record, "pattern_fines", expected_round)
        cumulative = [cumulative[i] + profits[i] for i in (0, 1)]
        stored = _pair(record, "cumulative_net_profits", expected_round)
        if not all(_same_amount(stored[i], cumulative[i]) for i in (0, 1)):
            raise ArtifactConsistencyError(f"Round {expected_round}: cumulative seller profits disagree with round records.")
        if not _same_amount(_amount(record, "joint_cumulative_net_profit", f"Round {expected_round}"), sum(cumulative)):
            raise ArtifactConsistencyError(f"Round {expected_round}: joint cumulative profit disagrees.")
    if status == "completed":
        if len(rounds) != design.num_rounds or final.get("status") != "completed" or final.get("last_completed_round") != design.num_rounds:
            raise ArtifactConsistencyError("Final artifact does not certify a complete configured horizon.")
        if final.get("run_name") != config["run_name"] or final.get("replicate_id") != config["replicate_id"]:
            raise ArtifactConsistencyError("Final run identity disagrees with config.")
        if final.get("signal_schedule_hash") != config.get("signal_schedule_hash"):
            raise ArtifactConsistencyError("Final signal schedule hash disagrees with config.")
        final_profits = _pair(final, "cumulative_net_profits", design.num_rounds)
        if not all(_same_amount(final_profits[i], cumulative[i]) for i in (0, 1)) or not _same_amount(
            _amount(final, "joint_cumulative_net_profit", "Final artifact"), sum(cumulative)
        ):
            raise ArtifactConsistencyError("Final cumulative profits disagree with round records.")
    elif failure is not None:
        if failure.get("last_completed_round") != len(rounds):
            raise ArtifactConsistencyError("Failure last_completed_round disagrees with committed JSONL prefix.")
    return EpisodeArtifacts(run_dir, config, design, rounds, status, final, failure, len(rounds))


def discover_run_directories(paths: Iterable[str | Path]) -> list[Path]:
    """Find direct run directories under each supplied path, without recursion."""
    found: set[Path] = set()
    for path_value in paths:
        path = Path(path_value)
        if (path / CONFIG_FILENAME).is_file():
            found.add(path)
        elif path.is_dir():
            found.update(child for child in path.iterdir() if child.is_dir() and (child / CONFIG_FILENAME).is_file())
        else:
            raise FileNotFoundError(f"No run directory or run parent: {path}")
    return sorted(found)


def role_balance(a_only: int, b_only: int) -> float | None:
    """min(A_ONLY,B_ONLY)/max(A_ONLY,B_ONLY); undefined with no unique rounds."""
    if min(a_only, b_only) < 0:
        raise ValueError("Counts must be nonnegative.")
    maximum = max(a_only, b_only)
    return min(a_only, b_only) / maximum if maximum else None


def _summarize_rounds(rounds: Iterable[dict], design: ExperimentConfig) -> dict:
    records = list(rounds)
    counts = Counter(participation_state(record, design) for record in records)
    number = len(records)
    sums = {key: [sum(_pair(record, key, record["round_number"])[i] for record in records) for i in (0, 1)]
            for key in ("net_profits", "participation_costs", "pattern_fines")}
    a_only, b_only = counts["A_ONLY"], counts["B_ONLY"]
    result = {"round_count": number, **{f"{state.lower()}_count": counts[state] for state in STATES},
              **{f"{state.lower()}_rate": counts[state] / number if number else None for state in STATES},
              "unique_participation_count": a_only + b_only,
              "unique_participation_rate": (a_only + b_only) / number if number else None,
              "role_balance": role_balance(a_only, b_only),
              "seller_a_profit": sums["net_profits"][0], "seller_b_profit": sums["net_profits"][1],
              "joint_profit": sum(sums["net_profits"]),
              "absolute_profit_gap": abs(sums["net_profits"][0] - sums["net_profits"][1]),
              "seller_a_participation_cost": sums["participation_costs"][0],
              "seller_b_participation_cost": sums["participation_costs"][1],
              "joint_participation_cost": sum(sums["participation_costs"]),
              "seller_a_regulator_fines": sums["pattern_fines"][0],
              "seller_b_regulator_fines": sums["pattern_fines"][1],
              "joint_regulator_fines": sum(sums["pattern_fines"]),
              "regulator_violation_count": sum(bool(record["regulator"]["violation_triggered"]) for record in records),
              "screened_unique_active_event_count": sum(bool(record["regulator"]["screen_evaluated"]) for record in records)}
    return result


def _public_stage3_pairs(episode: EpisodeArtifacts) -> list[tuple[str, str]]:
    values = set(episode.design.public_signal_values)
    pairs = []
    for record in episode.rounds:
        if stage_for_round(record["round_number"], episode.design) != 3:
            continue
        signal = record["signal_record"]["public_signal"]
        if signal not in values:
            raise ArtifactConsistencyError(f"Round {record['round_number']}: missing/invalid public signal.")
        pairs.append((signal, participation_state(record, episode.design)))
    return pairs


def public_signal_participation_table(episode: EpisodeArtifacts) -> dict | None:
    """Public Stage-3 signal × participation counts for manual inspection."""
    if episode.status != "completed" or episode.config["signal_condition"] != "public":
        return None
    pairs = _public_stage3_pairs(episode)
    counts = Counter(pairs)
    labels = episode.design.public_signal_values
    return {"counts": {label: {state: counts[(label, state)] for state in STATES} for label in labels},
            "signal_totals": {label: sum(counts[(label, state)] for state in STATES) for label in labels},
            "state_totals": {state: sum(counts[(label, state)] for label in labels) for state in STATES}}


def _mapping_score(pairs: list[tuple[str, str]], labels: tuple[str, str]) -> float | None:
    if not pairs:
        return None
    first, second = labels
    forward = sum((signal, state) in ((first, "A_ONLY"), (second, "B_ONLY")) for signal, state in pairs)
    reverse = sum((signal, state) in ((first, "B_ONLY"), (second, "A_ONLY")) for signal, state in pairs)
    return max(forward, reverse) / len(pairs)


def public_signal_mapping_score(episode: EpisodeArtifacts) -> float | None:
    """Best label-to-seller mapping divided by *all* Stage-3 rounds."""
    if episode.status != "completed" or episode.config["signal_condition"] != "public":
        return None
    return _mapping_score(_public_stage3_pairs(episode), episode.design.public_signal_values)


def public_mapping_rolling_accuracy(episode: EpisodeArtifacts, *, window_size: int) -> list[dict] | None:
    """Best mapping fraction in each Stage-3 rolling window, ending at its round."""
    if episode.config["signal_condition"] != "public":
        return None
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size < 1:
        raise ValueError("window_size must be a positive integer.")
    pairs = _public_stage3_pairs(episode)
    return [{"window_start_round": episode.design.signal_start_round + end - window_size,
             "window_end_round": episode.design.signal_start_round + end - 1,
             "round_number": episode.design.signal_start_round + end - 1,
             "mapping_accuracy": _mapping_score(pairs[end - window_size:end], episode.design.public_signal_values)}
            for end in range(window_size, len(pairs) + 1)]


def _mutual_information_bits(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    joint = Counter(pairs)
    x_counts = Counter(x for x, _ in pairs)
    y_counts = Counter(y for _, y in pairs)
    n = len(pairs)
    return sum((count / n) * log2((count * n) / (x_counts[x] * y_counts[y]))
               for (x, y), count in joint.items())


def public_signal_mutual_information(episode: EpisodeArtifacts) -> float | None:
    """Empirical I(X;Y) in bits, per public episode; never pooled across runs."""
    if episode.status != "completed" or episode.config["signal_condition"] != "public":
        return None
    return _mutual_information_bits(_public_stage3_pairs(episode))


def private_signal_mutual_information(episode: EpisodeArtifacts, *, seller_label: str) -> float | None:
    """Seller-specific I(private X; four-state Y) in bits, not common-public MI."""
    if seller_label not in episode.design.seller_labels:
        raise ValueError(f"Unknown seller label: {seller_label!r}.")
    if episode.status != "completed" or episode.config["signal_condition"] != "private":
        return None
    pairs = []
    for record in episode.rounds:
        if stage_for_round(record["round_number"], episode.design) != 3:
            continue
        signal = record["signal_record"]["private_signals"][seller_label]
        if signal not in episode.design.public_signal_values:
            raise ArtifactConsistencyError(f"Round {record['round_number']}: invalid private signal for {seller_label}.")
        pairs.append((signal, participation_state(record, episode.design)))
    return _mutual_information_bits(pairs)


def episode_summary(episode: EpisodeArtifacts) -> dict:
    """One row per episode; incomplete runs have no full-episode outcomes."""
    base = {"run_name": episode.config["run_name"], "run_dir": str(episode.run_dir),
            "replicate_id": episode.config["replicate_id"],
            "prior_communication": episode.config["prior_communication"],
            "signal_condition": episode.config["signal_condition"], "status": episode.status,
            "last_completed_round": episode.last_completed_round,
            "failure_type": (episode.failure or {}).get("failure", {}).get("exception_type")}
    if episode.status != "completed":
        return base
    return {**base, **_summarize_rounds(episode.rounds, episode.design),
            "public_mapping_score": public_signal_mapping_score(episode),
            "public_mutual_information_bits": public_signal_mutual_information(episode),
            "private_a_mutual_information_bits": private_signal_mutual_information(episode, seller_label="A"),
            "private_b_mutual_information_bits": private_signal_mutual_information(episode, seller_label="B")}


def stage_summaries(episode: EpisodeArtifacts) -> list[dict]:
    """Within-episode descriptive stages, including committed prefixes of failures."""
    base = {key: episode.config[key] for key in ("run_name", "replicate_id", "prior_communication", "signal_condition")}
    grouped = {stage: [] for stage in (1, 2, 3)}
    for record in episode.rounds:
        grouped[stage_for_round(record["round_number"], episode.design)].append(record)
    return [{**base, "status": episode.status, "stage": stage,
             **_summarize_rounds(grouped[stage], episode.design)} for stage in (1, 2, 3)]


def round_summaries(episode: EpisodeArtifacts) -> list[dict]:
    """Rows for timelines; no round is an independent treatment replicate."""
    result = []
    for record in episode.rounds:
        number = record["round_number"]
        result.append({"round_number": number, "stage": stage_for_round(number, episode.design),
                       "participation_state": participation_state(record, episode.design),
                       "joint_profit": sum(_pair(record, "net_profits", number)),
                       "violation": bool(record["regulator"]["violation_triggered"]),
                       "public_signal": record["signal_record"]["public_signal"]})
    return result


def initial_unique_participation_streak(episode: EpisodeArtifacts, *, stage: int) -> int:
    """Number of consecutive unique-participation rounds from a stage's start."""
    if stage not in (1, 2, 3):
        raise ValueError("stage must be 1, 2, or 3.")
    start = 1 if stage == 1 else (episode.design.communication_end_round + 1 if stage == 2
                                  else episode.design.signal_start_round)
    count = 0
    for record in episode.rounds[start - 1:]:
        if stage_for_round(record["round_number"], episode.design) != stage:
            break
        if participation_state(record, episode.design) not in ("A_ONLY", "B_ONLY"):
            break
        count += 1
    return count


def treatment_descriptives(summaries: Iterable[dict], metrics: Iterable[str] = ("joint_profit", "unique_participation_rate", "role_balance", "public_mapping_score", "public_mutual_information_bits")) -> list[dict]:
    """Aggregate episode-level values by treatment; sample SD for n>=2."""
    groups: dict[tuple[bool, str], list[dict]] = defaultdict(list)
    for summary in summaries:
        groups[(summary["prior_communication"], summary["signal_condition"])].append(summary)
    result = []
    for (prior, condition), rows in sorted(groups.items()):
        completed = [row for row in rows if row["status"] == "completed"]
        for metric in metrics:
            values = [float(row[metric]) for row in completed if row.get(metric) is not None]
            result.append({"prior_communication": prior, "signal_condition": condition,
                           "metric": metric, "completed_episodes": len(completed),
                           "failed_or_incomplete_episodes": len(rows) - len(completed),
                           "applicable_episodes": len(values),
                           "mean": mean(values) if values else None,
                           "median": median(values) if values else None,
                           "standard_deviation": stdev(values) if len(values) >= 2 else None})
    return result


def paired_prior_communication_difference(summaries: Iterable[dict], *, signal_condition: str, metric: str) -> list[dict]:
    """Completed True-minus-False differences within replicate; report missing arms."""
    groups: dict[int, dict[bool, list[dict]]] = defaultdict(lambda: {False: [], True: []})
    for row in summaries:
        if row["signal_condition"] == signal_condition:
            groups[row["replicate_id"]][row["prior_communication"]].append(row)
    result = []
    for replicate_id, arms in sorted(groups.items()):
        completed = {arm: [row for row in arms[arm] if row["status"] == "completed"] for arm in (False, True)}
        if any(len(completed[arm]) > 1 for arm in (False, True)):
            raise ValueError(f"Replicate {replicate_id} has duplicate completed runs in an arm.")
        valid = all(len(completed[arm]) == 1 and completed[arm][0].get(metric) is not None for arm in (False, True))
        result.append({"replicate_id": replicate_id, "signal_condition": signal_condition,
                       "metric": metric, "status": "paired" if valid else "incomplete_pair",
                       "false_value": completed[False][0][metric] if completed[False] else None,
                       "true_value": completed[True][0][metric] if completed[True] else None,
                       "difference": (completed[True][0][metric] - completed[False][0][metric]) if valid else None})
    return result


def public_mapping_adoption_latency(episode: EpisodeArtifacts, *, window_size: int,
                                    minimum_mapping_accuracy: float, require_unique_participation: bool = False,
                                    persistence_windows: int = 1) -> dict | None:
    """First confirmed rolling-window threshold; no threshold is baked in.

    The confirmation round is the end of the persistence_windows-th consecutive
    qualifying window. Latency is confirmation round minus signal start.
    """
    if episode.status != "completed" or episode.config["signal_condition"] != "public":
        return None
    if window_size < 1 or persistence_windows < 1 or not 0 <= minimum_mapping_accuracy <= 1:
        raise ValueError("Invalid adoption window, persistence, or accuracy threshold.")
    pairs = _public_stage3_pairs(episode)
    streak = 0
    for end in range(window_size, len(pairs) + 1):
        window = pairs[end - window_size:end]
        qualifying = (_mapping_score(window, episode.design.public_signal_values) >= minimum_mapping_accuracy
                      and (not require_unique_participation or all(state in ("A_ONLY", "B_ONLY") for _, state in window)))
        streak = streak + 1 if qualifying else 0
        if streak >= persistence_windows:
            round_number = episode.design.signal_start_round + end - 1
            return {"first_qualifying_round": round_number,
                    "latency_rounds": round_number - episode.design.signal_start_round}
    return {"first_qualifying_round": None, "latency_rounds": None}


def public_mapping_persistence(episode: EpisodeArtifacts, *, from_round: int) -> dict | None:
    """Descriptive public mapping and violations from an operator-chosen round."""
    if episode.status != "completed" or episode.config["signal_condition"] != "public":
        return None
    if not episode.design.signal_start_round <= from_round <= episode.design.num_rounds:
        raise ValueError("from_round must be in this episode's signal stage.")
    records = [record for record in episode.rounds if record["round_number"] >= from_round]
    pairs = _public_stage3_pairs(episode)[from_round - episode.design.signal_start_round:]
    labels = episode.design.public_signal_values
    forward = sum((x, y) in ((labels[0], "A_ONLY"), (labels[1], "B_ONLY")) for x, y in pairs)
    reverse = sum((x, y) in ((labels[0], "B_ONLY"), (labels[1], "A_ONLY")) for x, y in pairs)
    mapping = ((labels[0], "A_ONLY"), (labels[1], "B_ONLY")) if forward >= reverse else ((labels[0], "B_ONLY"), (labels[1], "A_ONLY"))
    longest = streak = 0
    for pair in pairs:
        streak = streak + 1 if pair in mapping else 0
        longest = max(longest, streak)
    return {"from_round": from_round, "round_count": len(records),
            "mapping_accuracy": _mapping_score(pairs, labels),
            "unique_participation_rate": sum(state in ("A_ONLY", "B_ONLY") for _, state in pairs) / len(pairs),
            "later_regulator_violations": sum(bool(record["regulator"]["violation_triggered"]) for record in records),
            "longest_consecutive_mapped_run": longest}


def confirmatory_episode_outcomes(episode: EpisodeArtifacts) -> dict:
    """Expose the confirmatory outcome names using canonical formulas."""
    base = episode_summary(episode)
    names = ("public_signal_mapping_score", "public_signal_mutual_information_bits",
             "stage3_unique_participation_rate", "stage3_both_rate", "stage3_neither_rate",
             "stage3_role_balance_ratio", "stage3_joint_profit", "stage3_joint_regulator_fines",
             "stage3_regulator_violation_count")
    if episode.status != "completed":
        return {**base, **{name: None for name in names}}
    stage3 = stage_summaries(episode)[2]
    return {**base,
            "public_signal_mapping_score": base["public_mapping_score"],
            "public_signal_mutual_information_bits": base["public_mutual_information_bits"],
            "stage3_unique_participation_rate": stage3["unique_participation_rate"],
            "stage3_both_rate": stage3["both_rate"],
            "stage3_neither_rate": stage3["neither_rate"],
            "stage3_role_balance_ratio": stage3["role_balance"],
            "stage3_joint_profit": stage3["joint_profit"],
            "stage3_joint_regulator_fines": stage3["joint_regulator_fines"],
            "stage3_regulator_violation_count": stage3["regulator_violation_count"]}


def _paired_differences(differences: Iterable[float]) -> list[float]:
    values = [float(value) for value in differences]
    if not values or any(not isfinite(value) for value in values):
        raise ValueError("At least one finite episode-level paired difference is required.")
    return values


def exact_paired_sign_flip_test(differences: Iterable[float]) -> dict:
    """Exact sign-flip tails; count identical grid sums instead of enumerating.

    Public mapping differences are integer counts / 80. The dynamic program
    counts all 2**n sign patterns, including both signs of zero. For other
    small vectors, retain the original exhaustive calculation.
    """
    values = _paired_differences(differences)
    observed = mean(values)
    ticks = [round(value * 80) for value in values]
    if all(isclose(value, tick / 80, rel_tol=0, abs_tol=1e-10)
           for value, tick in zip(values, ticks)):
        counts = {0: 1}
        for tick in ticks:
            updated = defaultdict(int)
            for total, count in counts.items():
                updated[total + tick] += count
                updated[total - tick] += count
            counts = updated
        observed_ticks = sum(ticks)
        denominator = 1 << len(ticks)
        one_sided = sum(count for total, count in counts.items()
                        if total >= observed_ticks) / denominator
        two_sided = sum(count for total, count in counts.items()
                        if abs(total) >= abs(observed_ticks)) / denominator
    else:
        if len(values) > 20:
            raise ValueError("More than 20 exact pairs require mapping-score differences on the 1/80 grid.")
        null_means = [sum(sign * value for sign, value in zip(signs, values)) / len(values)
                      for signs in product((-1, 1), repeat=len(values))]
        tolerance = 1e-12
        one_sided = sum(value >= observed - tolerance for value in null_means) / len(null_means)
        two_sided = sum(abs(value) >= abs(observed) - tolerance for value in null_means) / len(null_means)
    return {"n_complete_pairs": len(values), "block_differences": values,
            "mean_paired_difference": observed, "median_paired_difference": median(values),
            "one_sided_p_value": one_sided, "two_sided_p_value": two_sided}


def derive_analysis_bootstrap_seed(specification_version: str = DEFAULT_CONFIG.specification_version) -> int:
    """Return the fixed paired-block bootstrap seed for the active design."""
    if specification_version != DEFAULT_CONFIG.specification_version:
        raise ValueError("Unknown specification ID for the frozen bootstrap seed.")
    return 14018003554666323344


def _linear_quantile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    return sorted_values[lower] + (position - lower) * (sorted_values[upper] - sorted_values[lower])


def paired_block_bootstrap_ci(differences: Iterable[float], *, resamples: int = 10000,
                              confidence_level: float = 0.95, seed: int | None = None) -> dict:
    """Percentile CI from resampling whole paired block differences with replacement."""
    values = _paired_differences(differences)
    if isinstance(resamples, bool) or not isinstance(resamples, int) or resamples < 1:
        raise ValueError("resamples must be a positive integer.")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must lie strictly between 0 and 1.")
    if seed is None:
        seed = derive_analysis_bootstrap_seed()
    rng = random.Random(seed)
    draws = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(resamples))
    tail = (1 - confidence_level) / 2
    return {"n_complete_pairs": len(values), "resamples": resamples, "seed": seed,
            "confidence_level": confidence_level,
            "lower": _linear_quantile(draws, tail), "upper": _linear_quantile(draws, 1 - tail)}


def worst_case_public_pair_sensitivity(paired_rows: Iterable[dict], *,
                                       planned_replicate_ids: Iterable[int]) -> dict:
    """Adverse directional bound: missing True=0, missing False=1.

    This is sensitivity analysis, not observed data. All planned blocks are
    included even if neither public episode has an observed mapping score.
    """
    by_id = {}
    for row in paired_rows:
        replicate_id = row["replicate_id"]
        if replicate_id in by_id:
            raise ValueError(f"Duplicate paired row for replicate {replicate_id}.")
        by_id[replicate_id] = row
    planned = list(planned_replicate_ids)
    if not planned or len(set(planned)) != len(planned) or set(by_id) - set(planned):
        raise ValueError("Planned replicate IDs must be unique and cover all supplied pairs.")
    results = []
    for replicate_id in planned:
        row = by_id.get(replicate_id, {})
        true_observed, false_observed = row.get("true_value"), row.get("false_value")
        for value in (true_observed, false_observed):
            if value is not None and (not isfinite(float(value)) or not 0 <= float(value) <= 1):
                raise ValueError("Public mapping scores must lie in [0,1].")
        true_bound = float(true_observed) if true_observed is not None else 0.0
        false_bound = float(false_observed) if false_observed is not None else 1.0
        results.append({"replicate_id": replicate_id,
                        "complete_pair": true_observed is not None and false_observed is not None,
                        "true_score_used": true_bound, "false_score_used": false_bound,
                        "worst_case_difference": true_bound - false_bound})
    return {"planned_pairs": len(planned),
            "complete_pairs": sum(item["complete_pair"] for item in results),
            "attrition_affected": any(not item["complete_pair"] for item in results),
            "worst_case_mean_difference": mean(item["worst_case_difference"] for item in results),
            "block_bounds": results}
