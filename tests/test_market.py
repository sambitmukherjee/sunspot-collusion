"""Deterministic allocation and pre-regulator payoff checks."""

import math

import pytest

from collusion_experiment.market import (
    bid_price_to_cents,
    deterministic_market_outcome,
    make_bid_action,
    make_no_bid_action,
    validate_bid_price,
    validate_market_action,
)


def bid(price: float) -> dict:
    return make_bid_action(price)


NO_BID = make_no_bid_action()


@pytest.mark.parametrize(
    ("actions", "winner", "quantities", "costs", "profits"),
    [
        ([NO_BID, NO_BID], None, [0, 0], [0, 0], [0, 0]),
        ([bid(2.0), NO_BID], "A", [100, 0], [16, 0], [84, 0]),
        ([NO_BID, bid(2.0)], "B", [0, 100], [0, 16], [0, 84]),
        ([bid(1.99), bid(2.0)], "A", [100, 0], [16, 16], [83, -16]),
        ([bid(2.0), bid(1.99)], "B", [0, 100], [16, 16], [-16, 83]),
        ([bid(2.0), bid(2.0)], None, [0, 0], [16, 16], [-16, -16]),
        ([bid(1.75), bid(1.75)], None, [0, 0], [16, 16], [-16, -16]),
        ([bid(0.50), NO_BID], "A", [100, 0], [16, 0], [-66, 0]),
    ],
)
def test_canonical_market_outcomes(actions: list, winner: str | None, quantities: list, costs: list, profits: list) -> None:
    result = deterministic_market_outcome(actions)
    assert result["winner"] == winner
    assert result["quantities"] == quantities
    assert result["participation_costs"] == costs
    assert result["pre_regulator_net_profits"] == profits
    assert sum(result["pre_regulator_net_profits"]) == sum(profits)


def test_current_calibration_joint_payoff_comparison() -> None:
    clean = deterministic_market_outcome([bid(2.0), NO_BID])
    cover = deterministic_market_outcome([bid(1.99), bid(2.0)])
    neither = deterministic_market_outcome([NO_BID, NO_BID])
    assert sum(clean["pre_regulator_net_profits"]) == 84
    assert sum(cover["pre_regulator_net_profits"]) == 67
    assert sum(neither["pre_regulator_net_profits"]) == 0
    assert clean["pre_regulator_net_profits"] == [84, 0]  # also the patterned event's pre-fine payoff


def test_exact_integer_cent_comparison() -> None:
    assert bid_price_to_cents(1.99) == 199
    assert bid_price_to_cents(2.00) == 200
    assert deterministic_market_outcome([bid(1.99), bid(2.00)])["winner_index"] == 0


@pytest.mark.parametrize("price", [2.01, -0.01, 1.999, 0.001, math.nan, math.inf, -math.inf])
def test_invalid_prices_rejected(price: float) -> None:
    with pytest.raises(ValueError):
        validate_bid_price(price)


@pytest.mark.parametrize("price", [True, "1.00", None])
def test_non_numeric_prices_rejected(price: object) -> None:
    with pytest.raises(TypeError):
        validate_bid_price(price)


@pytest.mark.parametrize(
    "action",
    [
        None,
        {},
        {"action_type": "bid", "price": None},
        {"action_type": "no_bid", "price": 0.0},
        {"action_type": "unknown", "price": None},
        {"action_type": "bid", "price": 1.0, "extra": 1},
    ],
)
def test_malformed_actions_rejected(action: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        validate_market_action(action)
