"""Unique-active pattern regulation and exhaustive period classification."""

import pytest

from collusion_experiment.market import deterministic_market_outcome, make_bid_action, make_no_bid_action
from collusion_experiment.regulator import (
    apply_pattern_regulator,
    detect_repeating_period,
    make_initial_regulator_state,
    summarize_regulator_state,
    unique_active_seller,
    validate_regulator_state,
)


A_ONLY = [make_bid_action(2.0), make_no_bid_action()]
B_ONLY = [make_no_bid_action(), make_bid_action(2.0)]
BOTH_TIE = [make_bid_action(2.0), make_bid_action(2.0)]
BOTH_UNEQUAL = [make_bid_action(1.99), make_bid_action(2.0)]
NEITHER = [make_no_bid_action(), make_no_bid_action()]


def apply(actions: list, state: dict) -> dict:
    pre_profits = deterministic_market_outcome(actions)["pre_regulator_net_profits"]
    return apply_pattern_regulator(actions, pre_profits, state)


def test_no_screen_before_twentieth_event() -> None:
    state = make_initial_regulator_state()
    for number in range(1, 20):
        result = apply(A_ONLY, state)
        assert result["unique_active_event"]
        assert not result["screen_evaluated"]
        assert not result["violation_triggered"]
        assert len(result["regulator_state"]["unique_active_history"]) == number
        state = result["regulator_state"]


@pytest.mark.parametrize("period", range(1, 9))
def test_periods_one_through_eight_trigger(period: int) -> None:
    block = "A" + "B" * (period - 1)
    window = (block * 20)[:20]
    assert detect_repeating_period(window) == period
    state = {"unique_active_history": list(window[:-1])}
    actions = A_ONLY if window[-1] == "A" else B_ONLY
    result = apply(actions, state)
    assert result["screen_evaluated"]
    assert result["detected_period"] == period
    assert result["pattern_fines"] == [8.0, 8.0]


def test_irregular_window_does_not_trigger() -> None:
    window = "AABABBBAABBAABABBBAB"
    assert len(window) == 20
    assert detect_repeating_period(window) is None
    actions = A_ONLY if window[-1] == "A" else B_ONLY
    result = apply(actions, {"unique_active_history": list(window[:-1])})
    assert result["screen_evaluated"]
    assert not result["violation_triggered"]


@pytest.mark.parametrize("actions", [BOTH_TIE, BOTH_UNEQUAL, NEITHER])
def test_non_unique_round_neither_appends_nor_screens(actions: list) -> None:
    state = {"unique_active_history": ["A"] * 20}
    result = apply(actions, state)
    assert not result["unique_active_event"]
    assert result["appended_identity"] is None
    assert not result["screen_evaluated"]
    assert not result["violation_triggered"]
    assert result["regulator_state"] == state


def test_unique_active_classification() -> None:
    assert unique_active_seller(A_ONLY) == "A"
    assert unique_active_seller(B_ONLY) == "B"
    assert unique_active_seller(BOTH_TIE) is None
    assert unique_active_seller(BOTH_UNEQUAL) is None
    assert unique_active_seller(NEITHER) is None


def test_fine_applies_to_both_without_reset_or_mutation() -> None:
    state = {"unique_active_history": ["A"] * 19}
    result = apply(A_ONLY, state)
    assert result["final_net_profits"] == [76.0, -8.0]
    assert result["pattern_fines"] == [8.0, 8.0]
    assert len(state["unique_active_history"]) == 19
    assert result["regulator_state"]["unique_active_history"] == ["A"] * 20
    next_result = apply(A_ONLY, result["regulator_state"])
    assert next_result["violation_triggered"]
    assert len(next_result["regulator_state"]["unique_active_history"]) == 21


def test_history_persists_across_analytical_boundaries() -> None:
    # The regulator receives state, not a stage. Carrying that state across
    # any external transition preserves all previously recorded identities.
    state = make_initial_regulator_state()
    for _ in range(19):
        state = apply(A_ONLY, state)["regulator_state"]
    result_after_transition = apply(A_ONLY, state)
    assert result_after_transition["screen_evaluated"]
    assert result_after_transition["regulator_state_summary"]["total_unique_active_events"] == 20
    assert summarize_regulator_state(state)["recent_unique_active_sellers"] == ["A"] * 19


def test_state_validation_copies_history() -> None:
    state = {"unique_active_history": ["A"]}
    copy = validate_regulator_state(state)
    copy["unique_active_history"].append("B")
    assert state["unique_active_history"] == ["A"]


def test_boolean_period_is_rejected_as_scientifically_unreachable_configuration() -> None:
    # The notebook accepted True as integer 1. Production always supplies
    # the configured integer n_max; a boolean is not a scientific period.
    with pytest.raises(TypeError):
        detect_repeating_period("A" * 20, max_period=True)


def test_exhaustive_binary_windows_count_472_of_2_to_20() -> None:
    # Every binary length-20 history is checked by the implemented detector.
    translate = str.maketrans("01", "AB")
    classified = sum(
        detect_repeating_period(f"{bits:020b}".translate(translate)) is not None
        for bits in range(1 << 20)
    )
    assert classified == 472
