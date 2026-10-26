"""Hand-checkable tests of the exploratory public-signal randomization test."""

import pytest

from collusion_experiment.metrics import load_episode_artifacts
from collusion_experiment.public_signal_inference import (
    exact_mapping_p_value, holm_adjusted_p_values,
    public_signal_episode_tests, public_signal_randomization_test,
)


def test_exact_probability_includes_search_over_both_assignments():
    assert exact_mapping_p_value(8, 0) == pytest.approx(2 / 2**8)
    assert exact_mapping_p_value(0, 8) == pytest.approx(2 / 2**8)
    assert exact_mapping_p_value(5, 3) == pytest.approx(2 * sum((56, 28, 8, 1)) / 2**8)
    assert exact_mapping_p_value(4, 4) == 1
    assert exact_mapping_p_value(0, 0) == 1
    with pytest.raises(ValueError):
        exact_mapping_p_value(-1, 2)


def test_holm_adjustment_preserves_order_and_monotonicity():
    assert holm_adjusted_p_values([0.04, 1.0, 0.01, 0.03]) == pytest.approx(
        [0.09, 1.0, 0.04, 0.09]
    )
    assert holm_adjusted_p_values([]) == []
    with pytest.raises(ValueError):
        holm_adjusted_p_values([float("nan")])


def test_episode_score_uses_all_signal_rounds_but_null_uses_sole_bids(synthetic_analysis_run):
    run = synthetic_analysis_run(
        "mixed", states=["NEITHER"] * 4 + ["A_ONLY", "B_ONLY", "BOTH", "NEITHER"],
        signals=["KAPPA", "LAMBDA", "KAPPA", "LAMBDA"],
    )
    row = public_signal_randomization_test(load_episode_artifacts(run))
    assert row["public_signal_rounds"] == 4
    assert row["sole_bid_rounds"] == 2
    assert (row["forward_matches"], row["reverse_matches"]) == (2, 0)
    assert row["mapping_score"] == 0.5
    assert row["exact_p"] == 0.5


def test_all_nonsole_bid_rounds_cannot_be_significant(synthetic_analysis_run):
    run = synthetic_analysis_run("no_sole_bids", states=["NEITHER"] * 8)
    row = public_signal_randomization_test(load_episode_artifacts(run))
    assert row["mapping_score"] == 0
    assert row["exact_p"] == 1


def test_complete_block_family_and_holm_adjustment(synthetic_analysis_run):
    episodes = [load_episode_artifacts(synthetic_analysis_run(
        f"block_{block}_{prior}", replicate=block, prior=prior,
    )) for block in (1, 2) for prior in (False, True)]
    rows = public_signal_episode_tests(reversed(episodes), block_ids=range(1, 3))
    assert [(row["block"], row["earlier_communication"]) for row in rows] == [
        (1, False), (1, True), (2, False), (2, True)
    ]
    assert [row["exact_p"] for row in rows] == [0.125] * 4
    assert [row["holm_adjusted_p"] for row in rows] == [0.5] * 4
    with pytest.raises(ValueError, match="Missing"):
        public_signal_episode_tests(episodes[:-1], block_ids=range(1, 3))
    with pytest.raises(ValueError, match="Duplicate"):
        public_signal_episode_tests([*episodes, episodes[0]], block_ids=range(1, 3))
