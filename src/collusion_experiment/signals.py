"""Pre-generated, payoff-irrelevant public and private signal schedules.

X_t is the common public signal and X_t^i is seller i's private signal.
No market or regulator state is read here.
"""

import hashlib
import json
import random

from .config import ExperimentConfig, resolve_config


SIGNAL_CONDITIONS = ("none", "private", "public")


def validate_signal_condition(signal_condition: str) -> str:
    """Validate the treatment's signal condition."""
    if signal_condition not in SIGNAL_CONDITIONS:
        raise ValueError(f"Unknown signal_condition: {signal_condition!r}.")
    return signal_condition


def validate_signal_seed(seed: int, seed_name: str) -> int:
    """Require an explicit integer seed for each used stream."""
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError(f"{seed_name} must be an integer, not bool.")
    return seed


def seed_from_label(label: str) -> int:
    """Derive a stable 64-bit unsigned seed from a caller-supplied label."""
    if not isinstance(label, str) or not label:
        raise ValueError("label must be a nonempty string.")
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def make_signal_rng(seed: int) -> random.Random:
    """Construct a dedicated reproducible signal RNG."""
    return random.Random(seed)


def sample_signal(rng: random.Random, config: ExperimentConfig | None = None) -> str:
    """Draw one fair KAPPA/LAMBDA signal."""
    config = resolve_config(config)
    if not isinstance(rng, random.Random):
        raise TypeError("rng must be a dedicated random.Random instance.")
    return rng.choice(config.public_signal_values)


def make_signal_schedule(
    signal_condition: str,
    public_signal_seed: int | None = None,
    private_signal_seed_A: int | None = None,
    private_signal_seed_B: int | None = None,
    config: ExperimentConfig | None = None,
) -> dict:
    """Pre-generate all signal draws for the configured signal rounds.

    The schedule is hidden research state. No draws occur before signal start
    or in the no-signal treatment. Passing the same seeds across communication
    arms produces matching schedules without using communication in the RNG.
    """
    config = resolve_config(config)
    signal_condition = validate_signal_condition(signal_condition)
    if signal_condition == "none":
        if any(seed is not None for seed in (public_signal_seed, private_signal_seed_A, private_signal_seed_B)):
            raise ValueError("The none condition must not receive signal seeds.")
    elif signal_condition == "public":
        public_signal_seed = validate_signal_seed(public_signal_seed, "public_signal_seed")
        if private_signal_seed_A is not None or private_signal_seed_B is not None:
            raise ValueError("A public episode must not use private seeds.")
    else:
        private_signal_seed_A = validate_signal_seed(private_signal_seed_A, "private_signal_seed_A")
        private_signal_seed_B = validate_signal_seed(private_signal_seed_B, "private_signal_seed_B")
        if public_signal_seed is not None:
            raise ValueError("A private episode must not use a public seed.")
        if private_signal_seed_A == private_signal_seed_B:
            raise ValueError("Private A and B streams must use distinct seeds.")

    rounds = {}
    if signal_condition == "public":
        rng = make_signal_rng(public_signal_seed)
        for round_number in range(config.signal_start_round, config.num_rounds + 1):
            rounds[round_number] = {
                "public_signal": sample_signal(rng, config),
                "private_signals": {"A": None, "B": None},
            }
    elif signal_condition == "private":
        rng_a = make_signal_rng(private_signal_seed_A)
        rng_b = make_signal_rng(private_signal_seed_B)
        for round_number in range(config.signal_start_round, config.num_rounds + 1):
            rounds[round_number] = {
                "public_signal": None,
                "private_signals": {
                    "A": sample_signal(rng_a, config),
                    "B": sample_signal(rng_b, config),
                },
            }

    return {
        "signal_condition": signal_condition,
        "signal_start_round": config.signal_start_round,
        "num_rounds": config.num_rounds,
        "public_signal_seed": public_signal_seed,
        "private_signal_seed_A": private_signal_seed_A,
        "private_signal_seed_B": private_signal_seed_B,
        "rounds": rounds,
    }


def signal_schedule_hash(signal_state: dict) -> str:
    """Hash the realized schedule using the notebook's canonical JSON form."""
    payload = {
        "signal_condition": signal_state["signal_condition"],
        "signal_start_round": signal_state["signal_start_round"],
        "num_rounds": signal_state["num_rounds"],
        "rounds": signal_state["rounds"],
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_signal_round(signal_state: dict, round_number: int) -> None:
    """Require a round inside the schedule's episode horizon."""
    if isinstance(round_number, bool) or not isinstance(round_number, int):
        raise TypeError("round_number must be an integer.")
    if not 1 <= round_number <= signal_state["num_rounds"]:
        raise ValueError(f"round_number must be in 1..{signal_state['num_rounds']}.")


def get_research_signal_record(signal_state: dict, round_number: int) -> dict:
    """Return the research-level record, including both private draws."""
    validate_signal_round(signal_state, round_number)
    if round_number < signal_state["signal_start_round"] or signal_state["signal_condition"] == "none":
        return {"public_signal": None, "private_signals": {"A": None, "B": None}}
    record = signal_state["rounds"][round_number]
    return {
        "public_signal": record["public_signal"],
        "private_signals": dict(record["private_signals"]),
    }


def get_signal_view_for_seller(
    signal_state: dict,
    round_number: int,
    seller_label: str,
    config: ExperimentConfig | None = None,
) -> dict:
    """Reveal only this seller's current cue, never the rival's private cue."""
    config = resolve_config(config)
    validate_signal_round(signal_state, round_number)
    if seller_label not in config.seller_labels:
        raise ValueError(f"Unknown seller label: {seller_label!r}.")
    if round_number < signal_state["signal_start_round"] or signal_state["signal_condition"] == "none":
        return {"available": False, "visibility": "none", "signal": None}

    record = signal_state["rounds"][round_number]
    if signal_state["signal_condition"] == "public":
        return {"available": True, "visibility": "public", "signal": record["public_signal"]}
    return {
        "available": True,
        "visibility": "private",
        "signal": record["private_signals"][seller_label],
    }
