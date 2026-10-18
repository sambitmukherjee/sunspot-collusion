"""Deterministic, treatment-specific signal schedule checks."""

import random
import inspect

import pytest

from collusion_experiment import signals


def test_none_has_no_schedule_or_rng_consumption(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(seed: int) -> None:
        raise AssertionError("none treatment must not construct an RNG")

    monkeypatch.setattr(signals, "make_signal_rng", fail_if_called)
    state = signals.make_signal_schedule("none")
    assert state["rounds"] == {}
    assert signals.get_research_signal_record(state, 71) == {
        "public_signal": None, "private_signals": {"A": None, "B": None}
    }
    assert signals.get_signal_view_for_seller(state, 71, "A") == {
        "available": False, "visibility": "none", "signal": None
    }


def test_public_schedule_starts_at_71_and_is_common() -> None:
    state = signals.make_signal_schedule("public", public_signal_seed=123)
    assert min(state["rounds"]) == 71
    assert max(state["rounds"]) == 150
    assert len(state["rounds"]) == 80
    assert signals.get_signal_view_for_seller(state, 70, "A")["available"] is False
    expected = random.Random(123).choice(("KAPPA", "LAMBDA"))
    assert state["rounds"][71]["public_signal"] == expected
    for round_number in range(71, 151):
        a = signals.get_signal_view_for_seller(state, round_number, "A")
        b = signals.get_signal_view_for_seller(state, round_number, "B")
        assert a == b
        assert a["visibility"] == "public"
        assert state["rounds"][round_number]["private_signals"] == {"A": None, "B": None}


def test_private_schedule_starts_at_71_and_views_are_separate() -> None:
    state = signals.make_signal_schedule("private", private_signal_seed_A=11, private_signal_seed_B=29)
    assert min(state["rounds"]) == 71
    assert max(state["rounds"]) == 150
    assert len(state["rounds"]) == 80
    assert signals.get_signal_view_for_seller(state, 70, "B")["available"] is False
    expected_a = random.Random(11).choice(("KAPPA", "LAMBDA"))
    expected_b = random.Random(29).choice(("KAPPA", "LAMBDA"))
    assert state["rounds"][71]["private_signals"] == {"A": expected_a, "B": expected_b}
    assert any(
        record["private_signals"]["A"] != record["private_signals"]["B"]
        for record in state["rounds"].values()
    )
    for round_number in range(71, 151):
        a = signals.get_signal_view_for_seller(state, round_number, "A")
        b = signals.get_signal_view_for_seller(state, round_number, "B")
        assert set(a) == set(b) == {"available", "visibility", "signal"}
        assert a["visibility"] == b["visibility"] == "private"
        assert a["signal"] == state["rounds"][round_number]["private_signals"]["A"]
        assert b["signal"] == state["rounds"][round_number]["private_signals"]["B"]
        assert state["rounds"][round_number]["public_signal"] is None


def test_schedules_and_hashes_reproduce_with_matching_seeds() -> None:
    public_a = signals.make_signal_schedule("public", public_signal_seed=43)
    public_b = signals.make_signal_schedule("public", public_signal_seed=43)
    public_other = signals.make_signal_schedule("public", public_signal_seed=44)
    assert public_a == public_b
    assert signals.signal_schedule_hash(public_a) == signals.signal_schedule_hash(public_b)
    assert public_a["rounds"] != public_other["rounds"]
    assert signals.signal_schedule_hash(public_a) != signals.signal_schedule_hash(public_other)

    private_a = signals.make_signal_schedule("private", private_signal_seed_A=7, private_signal_seed_B=8)
    private_b = signals.make_signal_schedule("private", private_signal_seed_A=7, private_signal_seed_B=8)
    assert private_a == private_b
    assert signals.signal_schedule_hash(private_a) == signals.signal_schedule_hash(private_b)


def test_signal_schedule_is_unaffected_by_market_regulator_or_message_activity() -> None:
    from collusion_experiment.market import deterministic_market_outcome, make_bid_action, make_no_bid_action
    from collusion_experiment.regulator import apply_pattern_regulator, make_initial_regulator_state

    baseline = signals.make_signal_schedule("public", public_signal_seed=987)
    baseline_hash = signals.signal_schedule_hash(baseline)
    actions = [make_bid_action(2.00), make_no_bid_action()]
    market = deterministic_market_outcome(actions)
    apply_pattern_regulator(actions, market["pre_regulator_net_profits"], make_initial_regulator_state())
    assert not {"communication", "history", "market", "regulator_state"} & set(
        inspect.signature(signals.make_signal_schedule).parameters
    )
    for round_number in (70, 71, 72, 150):
        signals.get_signal_view_for_seller(baseline, round_number, "A")
    regenerated = signals.make_signal_schedule("public", public_signal_seed=987)
    assert baseline == regenerated
    assert signals.signal_schedule_hash(baseline) == baseline_hash


def test_fixed_seed_hashes_match_notebook_serialization() -> None:
    assert signals.signal_schedule_hash(signals.make_signal_schedule("public", public_signal_seed=123)) == (
        "99685d8a569deba3667111902cc32c0fb61c0cc84afdd6046f18549e6cb26622"
    )
    assert signals.signal_schedule_hash(
        signals.make_signal_schedule("private", private_signal_seed_A=11, private_signal_seed_B=29)
    ) == "ec04d690e7b5dec60dbdffd435e7f4bb754b7b0154a6f3e7ac677d2f93aeb115"


@pytest.mark.parametrize("condition", ["PUBLIC", "other", ""])
def test_invalid_treatment_rejected(condition: str) -> None:
    with pytest.raises(ValueError):
        signals.make_signal_schedule(condition)


@pytest.mark.parametrize("round_number", [0, 151, -1])
def test_invalid_round_rejected(round_number: int) -> None:
    state = signals.make_signal_schedule("public", public_signal_seed=1)
    with pytest.raises(ValueError):
        signals.get_signal_view_for_seller(state, round_number, "A")


def test_seed_validation_and_treatment_specific_seed_rules() -> None:
    assert signals.validate_signal_seed(0, "seed") == 0
    assert signals.seed_from_label("replicate one") == signals.seed_from_label("replicate one")
    assert signals.seed_from_label("replicate one") != signals.seed_from_label("replicate two")
    for bad_seed in (None, True, 1.5, "1"):
        with pytest.raises(TypeError):
            signals.validate_signal_seed(bad_seed, "seed")
    with pytest.raises(ValueError):
        signals.make_signal_schedule("none", public_signal_seed=1)
    with pytest.raises(ValueError):
        signals.make_signal_schedule("public", public_signal_seed=1, private_signal_seed_A=2)
    with pytest.raises(ValueError):
        signals.make_signal_schedule("private", private_signal_seed_A=1, private_signal_seed_B=1)
    with pytest.raises(TypeError):
        signals.make_signal_schedule("private", private_signal_seed_A=1, private_signal_seed_B=None)
