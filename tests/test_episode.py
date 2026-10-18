"""Offline communication and round/episode execution invariants."""

import json
from pathlib import Path
from types import SimpleNamespace as Obj

import pytest

from collusion_experiment.api import AgentParseFailure
from collusion_experiment.config import ExperimentConfig
from collusion_experiment.episode import (
    add_usage_summaries, communication_speaking_order, empty_usage, execute_communication_stage,
    execute_round, run_episode, summarize_call_usage,
)
from collusion_experiment.regulator import make_initial_regulator_state
from collusion_experiment.signals import make_signal_schedule
from structured_helpers import communication_result, market_result


SMALL = ExperimentConfig(num_rounds=5, communication_end_round=2,
                         signal_start_round=4, pattern_window=2, pattern_max_period=2)


def schedule(condition="none"):
    if condition == "public":
        return make_signal_schedule(condition, public_signal_seed=123, config=SMALL)
    if condition == "private":
        return make_signal_schedule(condition, private_signal_seed_A=11,
                                    private_signal_seed_B=29, config=SMALL)
    return make_signal_schedule(condition, config=SMALL)


def memories():
    return {"A": {"plans": "", "insights": ""}, "B": {"plans": "", "insights": ""}}


def fake_market(*, prompt, seller_label):
    return market_result(prompt=prompt, action="1.42" if seller_label == "A" else "NO BID",
                         observations="observe", plans=f"NEW_{seller_label}_PLAN",
                         insights=f"NEW_{seller_label}_INSIGHT", config=SMALL,
                         response_id=f"response-{seller_label}", model="fake-model",
                         usage={"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5})


def fake_comm(*, prompt, seller_label, recipient_label, speaker_position):
    message = f"  {seller_label} says hello\r\n"
    return communication_result(prompt=prompt, message=message, config=SMALL,
                                response_id=f"comm-{seller_label}")


@pytest.mark.parametrize("round_number,first,second", [(1, "A", "B"), (2, "B", "A")])
def test_communication_order_and_verbatim_second_prompt(round_number, first, second):
    seen = []
    def caller(**kwargs):
        seen.append(kwargs)
        return fake_comm(**kwargs)
    result = execute_communication_stage(
        round_number=round_number, prior_communication=True, seller_memories=memories(),
        history=[], regulator_state=make_initial_regulator_state(),
        communication_agent_caller=caller, config=SMALL,
    )
    assert communication_speaking_order(round_number, SMALL) == (first, second)
    assert [call["seller_label"] for call in seen] == [first, second]
    assert f"  {first} says hello\r\n" in seen[1]["prompt"]
    assert f"  {second} says hello\r\n" not in seen[0]["prompt"]
    assert result["first_message"] == f"  {first} says hello\r\n"
    assert result["second_message"] == f"  {second} says hello\r\n"
    assert result["first_message"] in result["transcript_block"]
    assert result["calls"][0]["prompt"] == seen[0]["prompt"]


@pytest.mark.parametrize("round_number,prior", [(1, False), (3, True)])
def test_communication_stage_rejects_unavailable_round(round_number, prior):
    with pytest.raises(ValueError):
        execute_communication_stage(
            round_number=round_number, prior_communication=prior, seller_memories=memories(),
            history=[], regulator_state=make_initial_regulator_state(),
            communication_agent_caller=fake_comm, config=SMALL,
        )


def test_both_prompts_precede_actions_and_use_same_pre_round_state(monkeypatch):
    from collusion_experiment import episode
    trace = []
    prompts = {}
    initial_memories = memories()
    initial_regulator = make_initial_regulator_state()
    captured_regulator_kwargs = []
    original_regulator = episode.apply_pattern_regulator
    def regulator_spy(**kwargs):
        captured_regulator_kwargs.append(kwargs)
        return original_regulator(**kwargs)
    monkeypatch.setattr(episode, "apply_pattern_regulator", regulator_spy)
    def market_caller(*, prompt, seller_label):
        assert trace.index("market_prompt_A_constructed") < len(trace)
        assert trace.index("market_prompt_B_constructed") < len(trace)
        prompts[seller_label] = prompt
        if seller_label == "B":
            assert "NEW_A_PLAN" not in prompt and "1.42" not in prompt
        return fake_market(prompt=prompt, seller_label=seller_label)
    result = execute_round(
        round_number=1, prior_communication=True, signal_state=schedule("none"),
        seller_memories=initial_memories, history=[], regulator_state=initial_regulator,
        market_decision_caller=market_caller, communication_agent_caller=fake_comm,
        config=SMALL, execution_trace=trace,
    )
    assert trace.index("market_prompt_B_constructed") < trace.index("market_call_A")
    assert trace.index("market_call_B") < trace.index("market_resolved")
    transcript = result["round_record"]["communication"]["transcript_block"]
    assert transcript in prompts["A"] and transcript in prompts["B"]
    assert "NEW_B_PLAN" not in prompts["A"]
    assert initial_memories == memories() and initial_regulator == make_initial_regulator_state()
    assert result["memory_after"]["A"]["plans"] == "NEW_A_PLAN"
    assert result["memory_after"]["B"]["plans"] == "NEW_B_PLAN"
    assert result["regulator_state_after"]["unique_active_history"] == ["A"]
    assert set(captured_regulator_kwargs[0]) == {"actions", "pre_regulator_net_profits", "regulator_state", "config"}


def test_failed_second_market_call_does_not_mutate_scientific_state(monkeypatch):
    from collusion_experiment import episode
    memory_before = memories()
    regulator_before = make_initial_regulator_state()
    calls = []
    def market_caller(*, prompt, seller_label):
        if seller_label == "B":
            raise AgentParseFailure("malformed", api_result={"prompt": prompt,
                "raw_response": "PLANS only", "usage": {"prompt_tokens": 2}})
        return fake_market(prompt=prompt, seller_label=seller_label)
    def forbidden_regulator(**kwargs):
        raise AssertionError("Regulator must not run after malformed response")
    monkeypatch.setattr(episode, "apply_pattern_regulator", forbidden_regulator)
    with pytest.raises(AgentParseFailure):
        execute_round(
            round_number=3, prior_communication=False, signal_state=schedule("none"),
            seller_memories=memory_before, history=[], regulator_state=regulator_before,
            market_decision_caller=market_caller, config=SMALL, call_log=calls,
        )
    assert memory_before == memories() and regulator_before == make_initial_regulator_state()
    assert len(calls) == 1 and calls[0]["seller_label"] == "A"


def test_malformed_raw_market_output_fails_even_if_injected_fields_claim_success():
    def malformed_market(*, prompt, seller_label):
        result = fake_market(prompt=prompt, seller_label=seller_label)
        result["raw_response"] = '{"observations":"obs","plans":"plan"}'
        return result
    with pytest.raises(ValueError):
        execute_round(
            round_number=3, prior_communication=False, signal_state=schedule("none"),
            seller_memories=memories(), history=[], regulator_state=make_initial_regulator_state(),
            market_decision_caller=malformed_market, config=SMALL,
        )


def test_canonical_round_51_has_no_communication_and_has_removal_notice():
    canonical = ExperimentConfig()
    signal_state = make_signal_schedule("none", config=canonical)
    result = execute_round(
        round_number=51, prior_communication=True, signal_state=signal_state,
        seller_memories=memories(), history=[], regulator_state=make_initial_regulator_state(),
        market_decision_caller=fake_market, config=canonical,
    )
    assert result["round_record"]["communication"]["enabled"] is False
    assert "no longer available" in result["round_record"]["market_decisions"]["A"]["prompt"]


def test_injected_client_uses_task_wrappers_without_network(tmp_path):
    class FakeClient:
        def __init__(self):
            self.calls = []
            self.chat = Obj(completions=Obj(create=self.create))
        def create(self, **kwargs):
            self.calls.append(kwargs)
            prompt = kwargs["messages"][0]["content"]
            seller = "A" if "You are acting as Seller A." in prompt else "B"
            raw = fake_market(prompt=prompt, seller_label=seller)["raw_response"]
            return Obj(id=f"fake-{len(self.calls)}", model="fake-returned-model",
                       choices=[Obj(message=Obj(content=raw), finish_reason="stop")],
                       usage=Obj(prompt_tokens=2, completion_tokens=3, total_tokens=5))
    client = FakeClient()
    result = run_episode(
        replicate_id=1, prior_communication=False, signal_condition="none",
        save_dir=tmp_path, run_name="client_fake", client=client, config=SMALL,
        development_mode=True,
    )
    first = json.loads((Path(result["run_dir"]) / "rounds.jsonl").read_text().splitlines()[0])
    assert first["market_decisions"]["A"]["result"]["response_id"] == "fake-1"
    assert first["market_decisions"]["A"]["result"]["requested_model"] == SMALL.model
    assert result["cumulative_usage"]["prompt_tokens"] == 2 * SMALL.num_rounds * 2
    assert len(client.calls) == SMALL.num_rounds * 2


def test_usage_aggregates_task_calls_tokens_and_retry_attempts():
    calls = [
        {"call_type": "communication", "result": {"requested_model": "fake", "attempt_count": 2,
            "usage": {"prompt_tokens": 100, "cached_tokens": 20, "completion_tokens": 30,
                      "reasoning_tokens": 4, "total_tokens": 130}}},
        {"call_type": "market_decision", "result": {"requested_model": "fake", "attempt_count": 1,
            "usage": {"prompt_tokens": 200, "cached_tokens": 50, "cache_write_tokens": 5,
                      "completion_tokens": 40, "reasoning_tokens": 6, "total_tokens": 240}}},
    ]
    one_round = summarize_call_usage(calls)
    assert one_round["agent_calls_completed"] == one_round["api_calls_completed"] == 2
    assert one_round["communication_calls_completed"] == one_round["market_decision_calls_completed"] == 1
    assert one_round["api_requests_total"] == 3 and one_round["technical_retry_count"] == 1
    assert {field: one_round[field] for field in ("prompt_tokens", "cached_tokens", "cache_write_tokens",
            "completion_tokens", "reasoning_tokens", "total_tokens")} == {
                "prompt_tokens": 300, "cached_tokens": 70, "cache_write_tokens": 5,
                "completion_tokens": 70, "reasoning_tokens": 10, "total_tokens": 370,
            }
    assert add_usage_summaries(empty_usage(), one_round) == one_round


@pytest.mark.parametrize("prior", [False, True])
@pytest.mark.parametrize("condition", ["none", "private", "public"])
def test_full_offline_episode_all_six_cells_and_boundaries(tmp_path, prior, condition):
    kwargs = {"public_signal_seed": 123} if condition == "public" else (
        {"private_signal_seed_A": 11, "private_signal_seed_B": 29} if condition == "private" else {})
    calls = []
    market_calls = []
    def communication_caller(**kw):
        calls.append(kw)
        return fake_comm(**kw)
    def market_caller(**kw):
        market_calls.append(kw)
        return fake_market(**kw)
    result = run_episode(
        replicate_id=1, prior_communication=prior, signal_condition=condition,
        save_dir=tmp_path, run_name=f"run_{int(prior)}_{condition}",
        market_decision_caller=market_caller, communication_agent_caller=communication_caller,
        config=SMALL, development_mode=True, **kwargs,
    )
    run_dir = Path(result["run_dir"])
    records = [json.loads(line) for line in (run_dir / "rounds.jsonl").read_text().splitlines()]
    checkpoint = json.loads((run_dir / "state_checkpoint.json").read_text())
    final = json.loads((run_dir / "final_episode.json").read_text())
    config_artifact = json.loads((run_dir / "config.json").read_text())
    assert [item["round_number"] for item in records] == [1, 2, 3, 4, 5]
    assert len(calls) == (4 if prior else 0)
    assert len(market_calls) == 10
    for index, record in enumerate(records):
        for seller_offset, label in enumerate(("A", "B")):
            assert market_calls[2 * index + seller_offset]["prompt"] == record["market_decisions"][label]["prompt"]
        if prior and index < 2:
            for position in (0, 1):
                assert calls[2 * index + position]["prompt"] == record["communication"]["calls"][position]["prompt"]
    assert records[1]["communication"]["enabled"] is prior
    assert records[2]["communication"]["enabled"] is False
    assert ("no longer available" in records[2]["market_decisions"]["A"]["prompt"]) is prior
    assert records[2]["signal"]["seller_views"]["A"]["available"] is False
    assert records[3]["signal"]["seller_views"]["A"]["available"] is (condition != "none")
    assert records[3]["regulator"]["regulator_state"]["unique_active_history"] == ["A"] * 4
    assert checkpoint["last_completed_round"] == final["last_completed_round"] == 5
    assert checkpoint["status"] == final["status"] == "completed"
    assert final["seller_memories"]["A"]["plans"] == "NEW_A_PLAN"
    assert config_artifact["specification_version"] == SMALL.specification_version
    assert config_artifact["signal_schedule_hash"] == final["signal_schedule_hash"]
    assert "api_key" not in json.dumps(config_artifact).lower()
    running_profit = [0.0, 0.0]
    running_usage = empty_usage()
    for record in records:
        running_profit = [running_profit[i] + record["net_profits"][i] for i in (0, 1)]
        assert record["cumulative_net_profits"] == running_profit
        assert record["joint_cumulative_net_profit"] == sum(running_profit)
        running_usage = add_usage_summaries(running_usage, record["round_usage"])
        assert record["cumulative_usage"] == running_usage
    assert final["cumulative_net_profits"] == running_profit
    assert final["cumulative_usage"] == running_usage
    assert result["status"] == "completed"


@pytest.mark.parametrize("condition,seeds", [
    ("public", {"public_signal_seed": 123}),
    ("private", {"private_signal_seed_A": 11, "private_signal_seed_B": 29}),
])
def test_signal_schedule_matches_across_communication_arms(tmp_path, condition, seeds):
    artifacts = []
    for prior in (False, True):
        result = run_episode(
            replicate_id=7, prior_communication=prior, signal_condition=condition,
            save_dir=tmp_path, run_name=f"matched_{condition}_{int(prior)}",
            market_decision_caller=fake_market, communication_agent_caller=fake_comm,
            config=SMALL, development_mode=True, **seeds,
        )
        directory = Path(result["run_dir"])
        config_artifact = json.loads((directory / "config.json").read_text())
        records = [json.loads(line) for line in (directory / "rounds.jsonl").read_text().splitlines()]
        artifacts.append((config_artifact, records))
    assert artifacts[0][0]["signal_schedule_hash"] == artifacts[1][0]["signal_schedule_hash"]
    assert [record["signal_record"] for record in artifacts[0][1]] == [
        record["signal_record"] for record in artifacts[1][1]
    ]
