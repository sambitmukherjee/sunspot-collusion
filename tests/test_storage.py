"""Durable JSON commit order and failure artifact fault injection."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from collusion_experiment import storage
from collusion_experiment.api import AgentParseFailure, APICallFailure
from collusion_experiment.config import ExperimentConfig
from collusion_experiment.episode import run_episode
from structured_helpers import market_result


SMALL = ExperimentConfig(num_rounds=4, communication_end_round=2,
                         signal_start_round=3, pattern_window=2, pattern_max_period=2)


def run_path(root, name="run", config=SMALL):
    return storage.specification_namespace(root, config.specification_version) / "runs" / name


def market(*, prompt, seller_label):
    return market_result(prompt=prompt, action="1.42" if seller_label == "A" else "NO BID",
                         observations="obs", plans=f"plan-{seller_label}", insights="insight",
                         config=SMALL,
                         usage={"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5})


def invoke(tmp_path, *, run_name="run", market_caller=market, config=SMALL):
    return run_episode(
        replicate_id=1, prior_communication=False, signal_condition="none",
        save_dir=tmp_path, run_name=run_name, market_decision_caller=market_caller,
        config=config, development_mode=True,
    )


def load(path):
    return json.loads(Path(path).read_text())


def records(run_dir):
    return [json.loads(line) for line in (run_dir / "rounds.jsonl").read_text().splitlines()]


def schema_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from schema_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_keys(child)


def test_stable_json_and_atomic_write(tmp_path):
    path = tmp_path / "value.json"
    storage.write_json_atomic(path, {"z": "é", "a": 1})
    assert path.read_text() == '{"a":1,"z":"é"}\n'
    assert list(tmp_path.glob(".value.json.*")) == []
    with pytest.raises(ValueError):
        storage.stable_json({"invalid": float("nan")})


def test_run_directory_collision_never_reuses_existing_artifacts(tmp_path):
    first = storage.create_run_directory(tmp_path, "replicate_1")
    (first / "sentinel.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        storage.create_run_directory(tmp_path, "replicate_1")
    assert (first / "sentinel.txt").read_text() == "keep"


def test_specification_namespace_applies_to_all_generated_roots(tmp_path):
    for root_name in ("data", "results", "research_notes", "execution_logs"):
        root = tmp_path / root_name
        assert storage.specification_namespace(root, "FUTURE_SPEC_V2") == root / "FUTURE_SPEC_V2"
    for unsafe in ("", ".", "..", "../other", "part/name", "part\\name"):
        with pytest.raises(ValueError):
            storage.specification_namespace(tmp_path, unsafe)


def test_episode_paths_follow_an_explicit_specification(tmp_path):
    future = replace(SMALL, specification_version="FUTURE_SPEC_V2")
    result = invoke(tmp_path, config=future)
    assert Path(result["run_dir"]) == run_path(tmp_path, config=future)
    assert (tmp_path / "execution_logs" / "FUTURE_SPEC_V2" / "episodes" / "run.txt").is_file()


def test_jsonl_line_is_terminated_and_fsync_rollback(tmp_path, monkeypatch):
    path = tmp_path / "rounds.jsonl"
    storage.initialize_rounds_jsonl(path)
    storage.append_jsonl(path, {"round": 1})
    storage.append_jsonl(path, {"round": 2})
    assert records(tmp_path) == [{"round": 1}, {"round": 2}]
    assert path.read_bytes().endswith(b"\n")
    original_fsync = storage.os.fsync
    attempts = 0
    def fail_first_fsync(fd):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("fsync failed during append")
        return original_fsync(fd)
    monkeypatch.setattr(storage.os, "fsync", fail_first_fsync)
    with pytest.raises(OSError):
        storage.append_jsonl(path, {"round": 3})
    assert records(tmp_path) == [{"round": 1}, {"round": 2}]


def test_successful_commit_and_artifact_schema(tmp_path):
    result = invoke(tmp_path)
    run_dir = Path(result["run_dir"])
    assert run_dir == run_path(tmp_path)
    assert [record["round_number"] for record in records(run_dir)] == [1, 2, 3, 4]
    checkpoint = load(run_dir / "state_checkpoint.json")
    final = load(run_dir / "final_episode.json")
    configuration = load(run_dir / "config.json")
    assert checkpoint["last_completed_round"] == 4 and checkpoint["next_round"] is None
    assert final["last_completed_round"] == 4 and final["status"] == "completed"
    assert configuration["max_history_rounds"] == SMALL.max_history_rounds == 150
    assert configuration["pattern_fine"] == SMALL.pattern_fine
    assert configuration["signal_seeds"]["public_signal_seed"] is None
    for field in (
        "specification_version", "prompt_family", "prompt_version", "model", "reasoning_effort",
        "temperature", "max_completion_tokens", "num_rounds",
        "communication_end_round", "signal_start_round", "order_size", "marginal_cost",
        "participation_cost", "reservation_price", "price_tick", "pattern_window",
        "pattern_max_period", "pattern_fine", "prior_communication",
        "signal_condition", "replicate_id", "signal_seeds", "signal_schedule_hash",
    ):
        assert field in configuration, f"missing config provenance field: {field}"
    assert configuration["prompt_version"] == "PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1"
    assert configuration["prompt_family"] == "fish_p1_adapted"
    assert "DLF" not in configuration["prompt_version"]
    obsolete_market_keys = {"market_seed", "market_rng", "market_draw", "mu",
                            "stochastic_buyer_probability"}
    assert not obsolete_market_keys & set(schema_keys(configuration))
    assert not obsolete_market_keys & set(schema_keys(records(run_dir)[0]))
    assert "api_key" not in json.dumps(configuration).lower()
    assert records(run_dir)[0]["market_decisions"]["A"]["prompt"]
    assert json.loads(records(run_dir)[0]["market_decisions"]["A"]["result"]["raw_response"])["chosen_action"] == "1.42"


def test_append_failure_keeps_prior_scientific_state(tmp_path, monkeypatch):
    original_append = storage.append_jsonl
    attempts = 0
    def fail_second(path, value):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise OSError("injected JSONL append failure")
        return original_append(path, value)
    monkeypatch.setattr(storage, "append_jsonl", fail_second)
    with pytest.raises(OSError):
        invoke(tmp_path)
    run_dir = run_path(tmp_path)
    assert [item["round_number"] for item in records(run_dir)] == [1]
    checkpoint = load(run_dir / "state_checkpoint.json")
    failure = load(run_dir / "failure.json")
    assert checkpoint["last_completed_round"] == failure["last_completed_round"] == 1
    assert checkpoint["next_round"] == 2
    assert checkpoint["seller_memories"]["A"]["plans"] == "plan-A"
    assert checkpoint["regulator_state"]["unique_active_history"] == ["A"]
    assert failure["failed_round"] == 2 and failure["jsonl_append_succeeded"] is False
    assert "append failure" in failure["failure"]["message"]


def test_checkpoint_failure_after_append_does_not_duplicate_round(tmp_path, monkeypatch):
    original_write = storage.write_json_atomic
    checkpoint_writes = 0
    def fail_second_checkpoint(path, value):
        nonlocal checkpoint_writes
        if Path(path).name == "state_checkpoint.json":
            checkpoint_writes += 1
            if checkpoint_writes == 2:
                raise OSError("injected checkpoint write failure")
        return original_write(path, value)
    monkeypatch.setattr(storage, "write_json_atomic", fail_second_checkpoint)
    with pytest.raises(OSError):
        invoke(tmp_path)
    run_dir = run_path(tmp_path)
    assert [item["round_number"] for item in records(run_dir)] == [1]
    checkpoint = load(run_dir / "state_checkpoint.json")
    failure = load(run_dir / "failure.json")
    assert checkpoint["last_completed_round"] == 0
    assert failure["last_completed_round"] == 1
    assert failure["jsonl_append_succeeded"] is True
    assert "checkpoint write failure" in failure["failure"]["message"]


def test_failed_b_response_retains_a_call_without_committing_memory(tmp_path):
    def failing_market(*, prompt, seller_label):
        if seller_label == "B":
            raise AgentParseFailure("incomplete structured response", api_result={
                "prompt": prompt, "raw_response": "PLANS only", "usage": {"prompt_tokens": 7,
                "completion_tokens": 1, "total_tokens": 8},
            })
        return market(prompt=prompt, seller_label=seller_label)
    with pytest.raises(AgentParseFailure):
        invoke(tmp_path, market_caller=failing_market)
    run_dir = run_path(tmp_path)
    assert records(run_dir) == []
    checkpoint = load(run_dir / "state_checkpoint.json")
    failure = load(run_dir / "failure.json")
    assert checkpoint["last_completed_round"] == 0 and checkpoint["next_round"] == 1
    assert checkpoint["seller_memories"]["A"]["plans"] == ""
    assert checkpoint["regulator_state"]["unique_active_history"] == []
    assert checkpoint["cumulative_net_profits"] == [0.0, 0.0]
    assert not (run_dir / "final_episode.json").exists()
    assert len(failure["completed_calls_in_failed_round"]) == 1
    assert failure["completed_calls_in_failed_round"][0]["seller_label"] == "A"
    assert failure["completed_calls_in_failed_round"][0]["prompt"]
    assert failure["failure"]["api_result"]["raw_response"] == "PLANS only"
    assert failure["failure"]["api_result"]["prompt"]
    assert failure["paid_or_attempted_usage_in_failed_round"]["prompt_tokens"] == 10
    assert failure["cumulative_usage_through_last_completed_round"]["prompt_tokens"] == 0


def test_technical_failure_context_is_durable(tmp_path):
    def failing_market(*, prompt, seller_label):
        raise APICallFailure("transport failed", prompt=prompt, failures=[{
            "exception_type": "APITimeoutError", "attempt_number": 1, "retryable": True,
        }])
    with pytest.raises(APICallFailure):
        invoke(tmp_path, market_caller=failing_market)
    failure = load(run_path(tmp_path) / "failure.json")
    assert failure["failure"]["failing_prompt"]
    assert failure["failure"]["technical_failures"][0]["retryable"] is True


def test_final_artifact_failure_preserves_completed_jsonl_and_checkpoint(tmp_path, monkeypatch):
    original_write = storage.write_json_atomic
    def fail_final(path, value):
        if Path(path).name == "final_episode.json":
            raise OSError("injected final artifact failure")
        return original_write(path, value)
    monkeypatch.setattr(storage, "write_json_atomic", fail_final)
    with pytest.raises(OSError):
        invoke(tmp_path)
    run_dir = run_path(tmp_path)
    assert [item["round_number"] for item in records(run_dir)] == [1, 2, 3, 4]
    assert load(run_dir / "state_checkpoint.json")["last_completed_round"] == 4
    failure = load(run_dir / "failure.json")
    assert failure["phase"] == "finalization"
    assert failure["last_completed_round"] == 4
