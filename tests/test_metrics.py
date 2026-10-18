"""Known-answer, episode-unit analysis tests using synthetic durable runs."""

import json
from math import isclose

import pytest

from collusion_experiment.config import ExperimentConfig
from collusion_experiment.episode import run_episode
from collusion_experiment.metrics import (
    ArtifactConsistencyError, episode_summary, load_episode_artifacts,
    initial_unique_participation_streak, private_signal_mutual_information,
    paired_prior_communication_difference, participation_state,
    public_mapping_adoption_latency, public_mapping_persistence,
    public_mapping_rolling_accuracy, public_signal_mapping_score,
    public_signal_participation_table,
    public_signal_mutual_information, role_balance, stage_for_round,
    stage_summaries, treatment_descriptives,
)
from structured_helpers import market_result


def test_loaded_timing_state_profit_and_stage_known_answers(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run())
    assert episode.status == "completed"
    assert [stage_for_round(i, episode.config) for i in range(1, 9)] == [1, 1, 2, 2, 3, 3, 3, 3]
    assert [participation_state(row, episode.design) for row in episode.rounds[:4]] == [
        "A_ONLY", "BOTH", "NEITHER", "B_ONLY"]
    dual_unequal = dict(episode.rounds[1], actions=[{"action_type": "bid", "price": 2.0},
                                                  {"action_type": "bid", "price": 1.99}])
    assert participation_state(dual_unequal, episode.design) == "BOTH"
    summary = episode_summary(episode)
    assert summary["seller_a_profit"] == summary["seller_b_profit"] == 228
    assert summary["joint_profit"] == 456
    assert summary["absolute_profit_gap"] == 0
    assert summary["joint_participation_cost"] == 128
    assert summary["joint_regulator_fines"] == 16
    assert (summary["a_only_count"], summary["b_only_count"],
            summary["both_count"], summary["neither_count"]) == (3, 3, 1, 1)
    assert summary["unique_participation_rate"] == 0.75
    assert summary["role_balance"] == 1
    assert summary["regulator_violation_count"] == 1
    assert summary["screened_unique_active_event_count"] == 3
    stages = stage_summaries(episode)
    assert [row["round_count"] for row in stages] == [2, 2, 4]
    assert [(row["a_only_count"], row["b_only_count"], row["both_count"], row["neither_count"])
            for row in stages] == [(1, 0, 1, 0), (0, 1, 0, 1), (2, 2, 0, 0)]
    assert [row["joint_profit"] for row in stages] == [52, 84, 320]
    assert stages[2]["unique_participation_rate"] == 1
    assert stages[2]["role_balance"] == 1
    assert [row["screened_unique_active_event_count"] for row in stages] == [0, 0, 3]
    assert [row["regulator_violation_count"] for row in stages] == [0, 0, 1]
    assert [row["joint_regulator_fines"] for row in stages] == [0, 0, 16]
    assert initial_unique_participation_streak(episode, stage=2) == 0
    table = public_signal_participation_table(episode)
    assert table["signal_totals"] == {"KAPPA": 2, "LAMBDA": 2}
    assert table["counts"]["KAPPA"]["A_ONLY"] == 2
    assert public_signal_mapping_score(episode) == 1
    assert isclose(public_signal_mutual_information(episode), 1)
    assert role_balance(0, 0) is None
    assert role_balance(4, 0) == 0


def test_initial_stage_streak_uses_saved_timing(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run(
        "stage2_streak", states=["NEITHER", "NEITHER", "A_ONLY", "B_ONLY",
                                 "NEITHER", "NEITHER", "NEITHER", "NEITHER"]))
    assert initial_unique_participation_streak(episode, stage=2) == 2


def test_public_mapping_denominator_mi_and_controls(synthetic_analysis_run):
    independent = load_episode_artifacts(synthetic_analysis_run(
        "independent", states=["NEITHER"] * 4 + ["A_ONLY", "A_ONLY", "B_ONLY", "B_ONLY"]))
    assert public_signal_mapping_score(independent) == 0.5
    assert isclose(public_signal_mutual_information(independent), 0, abs_tol=1e-12)
    mixed = load_episode_artifacts(synthetic_analysis_run(
        "mixed", states=["NEITHER"] * 4 + ["A_ONLY", "B_ONLY", "BOTH", "NEITHER"]))
    assert public_signal_mapping_score(mixed) == 0.5  # BOTH/NEITHER remain in denominator.
    assert stage_summaries(mixed)[2]["unique_participation_rate"] == 0.5
    assert [row["mapping_accuracy"] for row in public_mapping_rolling_accuracy(mixed, window_size=2)] == [1, 0.5, 0]
    for condition in ("none", "private"):
        episode = load_episode_artifacts(synthetic_analysis_run(condition, condition=condition))
        assert episode_summary(episode)["public_mapping_score"] is None
        assert public_signal_mutual_information(episode) is None
        assert public_mapping_rolling_accuracy(episode, window_size=2) is None
        assert public_signal_participation_table(episode) is None
        if condition == "private":
            assert isclose(private_signal_mutual_information(episode, seller_label="A"), 1)
            assert isclose(private_signal_mutual_information(episode, seller_label="B"), 1)
        else:
            assert private_signal_mutual_information(episode, seller_label="A") is None


def test_parameterized_adoption_and_persistence(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run())
    assert public_mapping_adoption_latency(episode, window_size=2, minimum_mapping_accuracy=1) == {
        "first_qualifying_round": 6, "latency_rounds": 1}
    assert public_mapping_adoption_latency(episode, window_size=2, minimum_mapping_accuracy=1,
                                           persistence_windows=2)["first_qualifying_round"] == 7
    persistence = public_mapping_persistence(episode, from_round=6)
    assert persistence["mapping_accuracy"] == persistence["unique_participation_rate"] == 1
    assert persistence["later_regulator_violations"] == 1
    assert persistence["longest_consecutive_mapped_run"] == 3
    with pytest.raises(ValueError):
        public_mapping_adoption_latency(episode, window_size=0, minimum_mapping_accuracy=1)


def test_current_horizon_rolling_boundaries_replace_obsolete_notebook_dates(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run(
        "canonical_timing", design=ExperimentConfig(),
        states=["A_ONLY", "B_ONLY"] * 75, signals=["KAPPA", "LAMBDA"] * 40))
    windows = public_mapping_rolling_accuracy(episode, window_size=20)
    assert len(windows) == 61
    assert windows[0]["window_start_round"] == 71
    assert windows[-1]["window_end_round"] == 150


def test_failed_prefix_reported_without_full_episode_metrics(synthetic_analysis_run):
    failed = load_episode_artifacts(synthetic_analysis_run("failed", states=["A_ONLY", "BOTH"], status="failed"))
    assert failed.status == "failed" and failed.last_completed_round == 2
    row = episode_summary(failed)
    assert row["failure_type"] == "SyntheticFailure"
    assert "joint_profit" not in row
    assert [stage["round_count"] for stage in stage_summaries(failed)] == [2, 0, 0]
    descriptives = treatment_descriptives([row])
    assert descriptives[0]["completed_episodes"] == 0
    assert descriptives[0]["failed_or_incomplete_episodes"] == 1
    assert descriptives[0]["mean"] is None


def test_corrupt_artifacts_rejected_not_normalized(synthetic_analysis_run):
    path = synthetic_analysis_run()
    records = [json.loads(line) for line in (path / "rounds.jsonl").read_text().splitlines()]
    records[4]["analytical_stage"] = 1  # Current defaults would also say 1; saved config says 3.
    (path / "rounds.jsonl").write_text("".join(json.dumps(row) + "\n" for row in records))
    with pytest.raises(ArtifactConsistencyError, match="stored stage"):
        load_episode_artifacts(path)


@pytest.mark.parametrize("mutation,diagnostic", [
    ("round_gap", "gap/duplicate"),
    ("treatment", "treatment metadata"),
    ("cumulative_profit", "cumulative seller profits"),
    ("schedule_hash", "signal schedule hash"),
])
def test_loader_rejects_durable_cross_artifact_disagreement(synthetic_analysis_run, mutation, diagnostic):
    path = synthetic_analysis_run(mutation)
    if mutation == "schedule_hash":
        final_path = path / "final_episode.json"
        final = json.loads(final_path.read_text())
        final["signal_schedule_hash"] = "wrong"
        final_path.write_text(json.dumps(final) + "\n")
    else:
        rounds_path = path / "rounds.jsonl"
        records = [json.loads(line) for line in rounds_path.read_text().splitlines()]
        if mutation == "round_gap":
            records[1]["round"] = records[1]["round_number"] = 3
        elif mutation == "treatment":
            records[0]["treatment"]["signal_condition"] = "none"
        else:
            records[0]["cumulative_net_profits"][0] += 1
        rounds_path.write_text("".join(json.dumps(record) + "\n" for record in records))
    with pytest.raises(ArtifactConsistencyError, match=diagnostic):
        load_episode_artifacts(path)


def test_episode_level_treatment_and_paired_contrasts():
    rows = [
        {"replicate_id": 1, "prior_communication": False, "signal_condition": "public", "status": "completed", "joint_profit": 10},
        {"replicate_id": 1, "prior_communication": True, "signal_condition": "public", "status": "completed", "joint_profit": 15},
        {"replicate_id": 2, "prior_communication": False, "signal_condition": "public", "status": "completed", "joint_profit": 20},
        {"replicate_id": 2, "prior_communication": True, "signal_condition": "public", "status": "failed"},
    ]
    pairs = paired_prior_communication_difference(rows, signal_condition="public", metric="joint_profit")
    assert [(row["status"], row["difference"]) for row in pairs] == [("paired", 5), ("incomplete_pair", None)]
    descriptions = treatment_descriptives(rows, metrics=["joint_profit"])
    false_arm = next(row for row in descriptions if row["prior_communication"] is False)
    assert false_arm["completed_episodes"] == 2
    assert false_arm["mean"] == false_arm["median"] == 15
    assert isclose(false_arm["standard_deviation"], 2 ** 0.5 * 5)
    with pytest.raises(ValueError, match="duplicate"):
        paired_prior_communication_difference(rows + [rows[0]], signal_condition="public", metric="joint_profit")


def test_loader_accepts_actual_offline_runner_artifacts(tmp_path):
    config = ExperimentConfig(num_rounds=4, communication_end_round=1,
                              signal_start_round=3, pattern_window=2,
                              pattern_max_period=2)
    def fake_market(*, prompt, seller_label):
        return market_result(prompt=prompt, action="NO BID", observations="synthetic",
                             plans="plan", insights="insight", config=config)
    result = run_episode(replicate_id=3, prior_communication=False,
                         signal_condition="none", save_dir=tmp_path,
                         run_name="actual_runner", market_decision_caller=fake_market,
                         config=config, development_mode=True)
    episode = load_episode_artifacts(result["run_dir"])
    summary = episode_summary(episode)
    assert episode.status == "completed"
    assert summary["neither_count"] == 4
    assert summary["joint_profit"] == 0
    assert [row["round_count"] for row in stage_summaries(episode)] == [1, 1, 2]
