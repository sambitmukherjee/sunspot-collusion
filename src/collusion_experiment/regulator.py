"""Unique-active-history pattern regulator.

W is the number of recent unique-active events, n_max the largest tested
period, and F the fine assessed to each seller on a triggering event.
"""

from .config import ExperimentConfig, resolve_config
from .market import validate_action_pair


def detect_repeating_period(
    identity_window: list | tuple | str,
    max_period: int | None = None,
    config: ExperimentConfig | None = None,
) -> int | None:
    """Return the smallest period generating a complete W-symbol window."""
    config = resolve_config(config)
    sequence = tuple(identity_window)
    if len(sequence) != config.pattern_window:
        raise ValueError(f"Expected exactly {config.pattern_window} identities.")
    if any(label not in config.seller_labels for label in sequence):
        raise ValueError("Pattern history may contain only seller labels.")
    if max_period is None:
        max_period = config.pattern_max_period
    if isinstance(max_period, bool) or not isinstance(max_period, int):
        raise TypeError("max_period must be an integer.")
    if not 1 <= max_period <= config.pattern_window:
        raise ValueError("max_period must be in 1..pattern_window.")

    for period in range(1, max_period + 1):
        # Equivalent to sequence[i] == sequence[i % period] for every i.
        # The final block may be incomplete.
        if sequence[period:] == sequence[:-period]:
            return period
    return None


def make_initial_regulator_state() -> dict:
    """Create an empty state once at episode initialization."""
    return {"unique_active_history": []}


def validate_regulator_state(state: dict, config: ExperimentConfig | None = None) -> dict:
    """Validate and copy the append-only unique-active history."""
    config = resolve_config(config)
    if not isinstance(state, dict):
        raise TypeError("Regulator state must be a dictionary.")
    if set(state) != {"unique_active_history"}:
        raise ValueError("Regulator state must contain only unique_active_history.")
    history = state["unique_active_history"]
    if not isinstance(history, list):
        raise TypeError("unique_active_history must be a list.")
    if any(label not in config.seller_labels for label in history):
        raise ValueError("History may contain only seller labels.")
    return {"unique_active_history": list(history)}


def unique_active_seller(actions: list | tuple, config: ExperimentConfig | None = None) -> str | None:
    """Return A/B only when exactly one seller makes a numerical bid."""
    config = resolve_config(config)
    actions = validate_action_pair(actions, config)
    bidder_indices = [i for i, action in enumerate(actions) if action["action_type"] == "bid"]
    return config.seller_labels[bidder_indices[0]] if len(bidder_indices) == 1 else None


def summarize_regulator_state(state: dict, config: ExperimentConfig | None = None) -> dict:
    """Summarize event count and recent identities, oldest to newest."""
    config = resolve_config(config)
    history = validate_regulator_state(state, config)["unique_active_history"]
    return {
        "total_unique_active_events": len(history),
        "recent_unique_active_sellers": history[-config.pattern_window:],
    }


def apply_pattern_regulator(
    actions: list | tuple,
    pre_regulator_net_profits: list | tuple,
    regulator_state: dict,
    config: ExperimentConfig | None = None,
) -> dict:
    """Append a fresh unique-active identity, screen, and assess any fines.

    This function has no stage input and never clears the prior history.
    Inputs are not mutated.
    """
    config = resolve_config(config)
    actions = validate_action_pair(actions, config)
    if not isinstance(pre_regulator_net_profits, (list, tuple)) or len(pre_regulator_net_profits) != 2:
        raise ValueError("pre_regulator_net_profits must contain two entries.")
    pre_profits = [float(value) for value in pre_regulator_net_profits]
    new_history = validate_regulator_state(regulator_state, config)["unique_active_history"]
    appended_identity = unique_active_seller(actions, config)
    unique_active_event = appended_identity is not None
    screen_evaluated = False
    detected_period = None

    if unique_active_event:
        new_history.append(appended_identity)
        if len(new_history) >= config.pattern_window:
            screen_evaluated = True
            detected_period = detect_repeating_period(
                new_history[-config.pattern_window:], config=config
            )

    violation_triggered = detected_period is not None
    pattern_fines = [float(config.pattern_fine)] * 2 if violation_triggered else [0.0, 0.0]
    final_profits = [profit - fine for profit, fine in zip(pre_profits, pattern_fines)]
    new_state = {"unique_active_history": new_history}
    return {
        "unique_active_event": unique_active_event,
        "appended_identity": appended_identity,
        "screen_evaluated": screen_evaluated,
        "detected_period": detected_period,
        "violation_triggered": violation_triggered,
        "pattern_fines": pattern_fines,
        "final_net_profits": final_profits,
        "regulator_state": new_state,
        "regulator_state_summary": summarize_regulator_state(new_state, config),
    }
