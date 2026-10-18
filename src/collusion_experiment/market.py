"""Deterministic two-seller market, before pattern regulation.

S is order size, c marginal cost, P the cost paid by every numerical bidder,
p̄ the reservation price, and τ the price tick.
"""

from decimal import Decimal
from math import isfinite
from numbers import Real

from .config import ExperimentConfig, resolve_config


def validate_bid_price(price: Real, config: ExperimentConfig | None = None) -> float:
    """Require a finite numerical bid on the configured grid and range."""
    config = resolve_config(config)
    if isinstance(price, bool) or not isinstance(price, Real):
        raise TypeError("Bid price must be a real numeric value, not bool.")
    numeric_price = float(price)
    if not isfinite(numeric_price):
        raise ValueError("Bid price must be finite.")

    decimal_price = Decimal(str(price))
    if decimal_price < 0 or decimal_price > Decimal(str(config.reservation_price)):
        raise ValueError("Bid price is outside the allowed range.")
    ticks = decimal_price / Decimal(str(config.price_tick))
    if ticks != ticks.to_integral_value():
        raise ValueError("Bid price must lie on the price grid.")
    return numeric_price


def validate_market_action(action: dict, config: ExperimentConfig | None = None) -> dict:
    """Return a canonical BID or NO BID action without mutating the input."""
    config = resolve_config(config)
    if not isinstance(action, dict):
        raise TypeError("Market action must be a dictionary.")
    if set(action) != {"action_type", "price"}:
        raise ValueError("Market action must have exactly action_type and price.")
    if action["action_type"] == "no_bid":
        if action["price"] is not None:
            raise ValueError("A no_bid action must have price=None.")
        return {"action_type": "no_bid", "price": None}
    if action["action_type"] == "bid":
        if action["price"] is None:
            raise ValueError("A bid action must contain a price.")
        return {"action_type": "bid", "price": validate_bid_price(action["price"], config)}
    raise ValueError(f"Unknown action_type: {action['action_type']!r}")


def make_no_bid_action() -> dict:
    """Construct a canonical NO BID action."""
    return {"action_type": "no_bid", "price": None}


def make_bid_action(price: Real, config: ExperimentConfig | None = None) -> dict:
    """Construct a validated numerical bid."""
    return validate_market_action({"action_type": "bid", "price": price}, config)


def validate_action_pair(actions: list | tuple, config: ExperimentConfig | None = None) -> list[dict]:
    """Validate two seller actions in stable A/B order."""
    config = resolve_config(config)
    if not isinstance(actions, (list, tuple)):
        raise TypeError("actions must be a list or tuple.")
    if len(actions) != len(config.seller_labels):
        raise ValueError("Expected exactly two seller actions.")
    return [validate_market_action(action, config) for action in actions]


def bid_price_to_cents(price: Real, config: ExperimentConfig | None = None) -> int:
    """Convert a valid grid price to exact integer cents."""
    config = resolve_config(config)
    validated = validate_bid_price(price, config)
    cents = Decimal(str(validated)) * 100
    return int(cents)


def deterministic_winner(actions: list | tuple, config: ExperimentConfig | None = None) -> int | None:
    """Return 0 for A, 1 for B, or None when there is no sale."""
    config = resolve_config(config)
    a, b = validate_action_pair(actions, config)
    a_bids = a["action_type"] == "bid"
    b_bids = b["action_type"] == "bid"
    if not a_bids and not b_bids:
        return None
    if a_bids and not b_bids:
        return 0
    if b_bids and not a_bids:
        return 1
    a_cents = bid_price_to_cents(a["price"], config)
    b_cents = bid_price_to_cents(b["price"], config)
    if a_cents == b_cents:
        return None
    return 0 if a_cents < b_cents else 1


def market_quantities(winner_index: int | None, config: ExperimentConfig | None = None) -> list[int]:
    """Allocate the entire order to the winner, if any."""
    config = resolve_config(config)
    if winner_index is None:
        return [0, 0]
    if winner_index not in (0, 1):
        raise ValueError("winner_index must be 0, 1, or None.")
    quantities = [0, 0]
    quantities[winner_index] = config.order_size
    return quantities


def gross_market_profits(
    actions: list | tuple,
    quantities: list | tuple,
    config: ExperimentConfig | None = None,
) -> list[float]:
    """Compute q × (bid − c) for the allocated seller."""
    config = resolve_config(config)
    actions = validate_action_pair(actions, config)
    if not isinstance(quantities, (list, tuple)) or len(quantities) != 2:
        raise ValueError("quantities must contain exactly two entries.")
    profits = []
    for action, quantity in zip(actions, quantities):
        quantity = int(quantity)
        if quantity not in (0, config.order_size):
            raise ValueError("Invalid market quantity.")
        if quantity == 0:
            profits.append(0.0)
        else:
            if action["action_type"] != "bid":
                raise ValueError("A seller with positive quantity must have bid.")
            profits.append(float(quantity * (action["price"] - config.marginal_cost)))
    return profits


def participation_costs(actions: list | tuple, config: ExperimentConfig | None = None) -> list[float]:
    """Charge P to every numerical bidder, including losers and tied bidders."""
    config = resolve_config(config)
    actions = validate_action_pair(actions, config)
    return [float(config.participation_cost) if action["action_type"] == "bid" else 0.0 for action in actions]


def pre_regulator_net_profits(gross_profits: list | tuple, bid_costs: list | tuple) -> list[float]:
    """Subtract participation costs before any regulator fine."""
    if len(gross_profits) != 2 or len(bid_costs) != 2:
        raise ValueError("Profit and cost vectors must each have two entries.")
    return [float(gross - cost) for gross, cost in zip(gross_profits, bid_costs)]


def deterministic_market_outcome(actions: list | tuple, config: ExperimentConfig | None = None) -> dict:
    """Return the notebook-equivalent complete pre-regulator market record."""
    config = resolve_config(config)
    canonical_actions = validate_action_pair(actions, config)
    winner_index = deterministic_winner(canonical_actions, config)
    quantities = market_quantities(winner_index, config)
    gross_profits = gross_market_profits(canonical_actions, quantities, config)
    bid_costs = participation_costs(canonical_actions, config)
    pre_profits = pre_regulator_net_profits(gross_profits, bid_costs)
    return {
        "actions": canonical_actions,
        "prices": [action["price"] for action in canonical_actions],
        "active_sellers": [action["action_type"] == "bid" for action in canonical_actions],
        "winner_index": winner_index,
        "winner": None if winner_index is None else config.seller_labels[winner_index],
        "quantities": quantities,
        "gross_market_profits": gross_profits,
        "participation_costs": bid_costs,
        "pre_regulator_net_profits": pre_profits,
    }
