"""Default scientific tests must remain entirely offline."""

import socket
from dataclasses import asdict
import json

import pytest

from collusion_experiment.config import ExperimentConfig


@pytest.fixture(autouse=True)
def block_network_access(monkeypatch: pytest.MonkeyPatch):
    """Fail before DNS, TCP, or UDP access by any collected test."""
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access is forbidden in the default test suite")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket.socket, "sendto", forbidden)


@pytest.fixture
def synthetic_analysis_run(tmp_path):
    """Write small hand-verifiable durable artifacts; never call a model."""
    def create(name="synthetic", *, prior=False, condition="public", replicate=1,
               states=None, signals=None, status="completed", design=None):
        design = design or ExperimentConfig(num_rounds=8, communication_end_round=2,
                                            signal_start_round=5, pattern_window=2,
                                            pattern_max_period=2)
        states = states or ["A_ONLY", "BOTH", "NEITHER", "B_ONLY",
                            "A_ONLY", "B_ONLY", "A_ONLY", "B_ONLY"]
        signals = signals or ["KAPPA", "LAMBDA", "KAPPA", "LAMBDA"]
        directory = tmp_path / name
        directory.mkdir()
        config = {**asdict(design), "run_name": name, "replicate_id": replicate,
                  "prior_communication": prior, "signal_condition": condition,
                  "signal_schedule_hash": "synthetic-schedule-hash"}
        (directory / "config.json").write_text(json.dumps(config) + "\n")
        records = []
        cumulative = [0.0, 0.0]
        active = {"A_ONLY": (True, False), "B_ONLY": (False, True),
                  "BOTH": (True, True), "NEITHER": (False, False)}
        for number, state in enumerate(states, 1):
            bids = active[state]
            actions = [{"action_type": "bid", "price": 2.0} if bid else
                       {"action_type": "no_bid", "price": None} for bid in bids]
            profits = {"A_ONLY": [84.0, 0.0], "B_ONLY": [0.0, 84.0],
                       "BOTH": [-16.0, -16.0], "NEITHER": [0.0, 0.0]}[state].copy()
            violation = number == 7
            fines = [8.0, 8.0] if violation else [0.0, 0.0]
            profits = [profits[i] - fines[i] for i in (0, 1)]
            cumulative = [cumulative[i] + profits[i] for i in (0, 1)]
            public_signal = signals[number - design.signal_start_round] if condition == "public" and number >= design.signal_start_round else None
            private_signal_a = signals[number - design.signal_start_round] if condition == "private" and number >= design.signal_start_round else None
            private_signal_b = ({"KAPPA": "LAMBDA", "LAMBDA": "KAPPA"}[private_signal_a]
                                if private_signal_a is not None else None)
            record = {"round": number, "round_number": number,
                      "analytical_stage": 1 if number <= design.communication_end_round else
                      (2 if number < design.signal_start_round else 3),
                      "treatment": {"prior_communication": prior,
                                    "signal_condition": condition, "replicate_id": replicate},
                      "actions": actions, "net_profits": profits,
                      "participation_costs": [16.0 if bid else 0.0 for bid in bids],
                      "pattern_fines": fines, "cumulative_net_profits": cumulative.copy(),
                      "joint_cumulative_net_profit": sum(cumulative),
                      "regulator": {"violation_triggered": violation,
                                    "screen_evaluated": number >= 6 and state in ("A_ONLY", "B_ONLY")},
                      "signal_record": {"public_signal": public_signal,
                                        "private_signals": {"A": private_signal_a, "B": private_signal_b}}}
            records.append(record)
        (directory / "rounds.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))
        if status == "completed":
            final = {"status": "completed", "last_completed_round": design.num_rounds,
                     "run_name": name, "replicate_id": replicate,
                     "signal_schedule_hash": config["signal_schedule_hash"],
                     "cumulative_net_profits": cumulative,
                     "joint_cumulative_net_profit": sum(cumulative)}
            (directory / "final_episode.json").write_text(json.dumps(final) + "\n")
        elif status == "failed":
            failure = {"status": "failed", "last_completed_round": len(records),
                       "failure": {"exception_type": "SyntheticFailure", "message": "deliberate"}}
            (directory / "failure.json").write_text(json.dumps(failure) + "\n")
        return directory
    return create
