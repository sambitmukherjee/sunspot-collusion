"""Known-answer tests for the frozen episode-level inference helpers."""

import pytest

from collusion_experiment.metrics import (
    confirmatory_episode_outcomes, derive_analysis_bootstrap_seed,
    exact_paired_sign_flip_test, load_episode_artifacts,
    paired_block_bootstrap_ci, worst_case_public_pair_sensitivity,
)


def test_confirmatory_outcome_names_reuse_phase7_formulas(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run())
    outcomes = confirmatory_episode_outcomes(episode)
    assert outcomes["public_signal_mapping_score"] == outcomes["public_mapping_score"] == 1.0
    assert outcomes["public_signal_mutual_information_bits"] == outcomes["public_mutual_information_bits"]
    assert outcomes["stage3_unique_participation_rate"] == 1.0
    assert outcomes["stage3_both_rate"] == 0.0
    assert outcomes["stage3_neither_rate"] == 0.0
    assert outcomes["stage3_role_balance_ratio"] == 1.0
    assert outcomes["stage3_regulator_violation_count"] == 1


def test_mapping_denominator_includes_nonunique_rounds(synthetic_analysis_run):
    path = synthetic_analysis_run(states=["A_ONLY", "BOTH", "NEITHER", "B_ONLY",
                                          "A_ONLY", "BOTH", "NEITHER", "B_ONLY"])
    outcomes = confirmatory_episode_outcomes(load_episode_artifacts(path))
    assert outcomes["public_signal_mapping_score"] == 0.5
    assert outcomes["stage3_unique_participation_rate"] == 0.5


def test_exact_sign_flip_known_answers():
    result = exact_paired_sign_flip_test([1.0, 1.0])
    assert result["n_complete_pairs"] == 2
    assert result["block_differences"] == [1.0, 1.0]
    assert result["mean_paired_difference"] == result["median_paired_difference"] == 1.0
    assert result["one_sided_p_value"] == 0.25
    assert result["two_sided_p_value"] == 0.5
    assert exact_paired_sign_flip_test([0.0, 0.0])["one_sided_p_value"] == 1.0
    assert exact_paired_sign_flip_test([-1.0, -1.0])["one_sided_p_value"] == 1.0


def test_bootstrap_is_deterministic_and_resamples_whole_pairs():
    seed = derive_analysis_bootstrap_seed()
    assert seed == 14018003554666323344
    first = paired_block_bootstrap_ci([0.0, 1.0], resamples=10000)
    second = paired_block_bootstrap_ci([0.0, 1.0], resamples=10000)
    assert first == second
    assert first["seed"] == seed and first["resamples"] == 10000
    assert first["lower"] == 0.0 and first["upper"] == 1.0
    assert paired_block_bootstrap_ci([0.25, 0.25], resamples=100)["lower"] == 0.25


def test_adverse_missing_pair_bound_includes_all_planned_blocks():
    pairs = [{"replicate_id": 1, "true_value": 0.8, "false_value": 0.3},
             {"replicate_id": 2, "true_value": None, "false_value": 0.4},
             {"replicate_id": 3, "true_value": 0.7, "false_value": None}]
    result = worst_case_public_pair_sensitivity(pairs, planned_replicate_ids=[1, 2, 3])
    assert result["planned_pairs"] == 3 and result["complete_pairs"] == 1
    assert result["attrition_affected"] is True
    assert [row["worst_case_difference"] for row in result["block_bounds"]] == pytest.approx([0.5, -0.4, -0.3])
    assert result["worst_case_mean_difference"] == pytest.approx(-1 / 15)


def test_inference_rejects_empty_or_nonfinite_input():
    with pytest.raises(ValueError):
        exact_paired_sign_flip_test([])
    with pytest.raises(ValueError):
        paired_block_bootstrap_ci([float("nan")])
