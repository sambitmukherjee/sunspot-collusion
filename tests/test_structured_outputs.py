"""Offline checks for the separately versioned structured response contract."""

from dataclasses import replace
import json
import re
from pathlib import Path
from types import SimpleNamespace as Obj

import pytest
import yaml

from collusion_experiment.api import (
    AgentParseFailure, AgentResponseFailure, call_agent_communication,
    call_agent_market_decision,
)
from collusion_experiment.config import STRUCTURED_CONFIG
from collusion_experiment.episode import execute_round, run_episode
from collusion_experiment.prompts import market_decision_instructions, make_first_speaker_instructions
from collusion_experiment.regulator import make_initial_regulator_state
from collusion_experiment.signals import make_signal_schedule
from collusion_experiment.structured_outputs import (
    ACTION_PATTERN, COMMUNICATION_RESPONSE_FORMAT, CONTRACT_VERSION,
    MARKET_RESPONSE_FORMAT, canonical_payload, decode_structured_response,
    render_market_response, schema_hash,
)


def market_json(action="1.95", observations="observed", plans="plan", insights="insight"):
    return json.dumps({"observations": observations, "plans": plans,
                       "insights": insights, "chosen_action": action}, ensure_ascii=False)


def communication_json(message):
    return json.dumps({"message": message}, ensure_ascii=False)


def response(raw, *, finish="stop", refusal=None):
    return Obj(id="resp", _request_id="request", model="fake-model",
               choices=[Obj(message=Obj(content=raw, refusal=refusal), finish_reason=finish)],
               usage=Obj(prompt_tokens=10, completion_tokens=5, total_tokens=15,
                         prompt_tokens_details=Obj(cached_tokens=4)))


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.chat = Obj(completions=Obj(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


def test_exact_schemas_order_pattern_and_hashes():
    market = MARKET_RESPONSE_FORMAT["json_schema"]
    communication = COMMUNICATION_RESPONSE_FORMAT["json_schema"]
    assert market["name"] == "seller_market_response_structured"
    assert communication["name"] == "seller_communication_structured"
    assert market["strict"] is communication["strict"] is True
    assert MARKET_RESPONSE_FORMAT["type"] == COMMUNICATION_RESPONSE_FORMAT["type"] == "json_schema"
    assert list(market["schema"]["properties"]) == market["schema"]["required"] == [
        "observations", "plans", "insights", "chosen_action"]
    assert list(communication["schema"]["properties"]) == communication["schema"]["required"] == ["message"]
    assert communication["schema"]["properties"]["message"] == {"type": "string"}
    assert market["schema"]["additionalProperties"] is communication["schema"]["additionalProperties"] is False
    assert all(item["type"] == "string" for item in market["schema"]["properties"].values())
    assert market["schema"]["properties"]["chosen_action"]["pattern"] == ACTION_PATTERN
    for valid in ("NO BID", "0.00", "0.01", "1.95", "1.99", "2.00"):
        assert re.fullmatch(ACTION_PATTERN, valid)
    for invalid in ("NO_BID", "BID 1.95", "-0.01", "1.9", "1.999", "2.01", "2.1"):
        assert re.fullmatch(ACTION_PATTERN, invalid) is None
    assert schema_hash(MARKET_RESPONSE_FORMAT) == schema_hash(json.loads(canonical_payload(MARKET_RESPONSE_FORMAT)))
    assert schema_hash(MARKET_RESPONSE_FORMAT) == "b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2"
    assert schema_hash(COMMUNICATION_RESPONSE_FORMAT) == "12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c"


def test_v2_config_records_versions_hashes_and_default_caching():
    path = Path(__file__).resolve().parents[1] / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml"
    draft = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert draft["design_status"] == "confirmatory"
    assert draft["specification_version"] == STRUCTURED_CONFIG.specification_version
    assert draft["prompt_family"] == STRUCTURED_CONFIG.prompt_family
    assert draft["prompt_version"] == STRUCTURED_CONFIG.prompt_version
    assert draft["response_contract_version"] == STRUCTURED_CONFIG.response_contract_version
    assert draft["infrastructure"]["prompt_caching_policy"] == "provider_default"
    for call_type, response_format in (("communication", COMMUNICATION_RESPONSE_FORMAT),
                                       ("market_decision", MARKET_RESPONSE_FORMAT)):
        assert draft["schemas"][call_type]["name"] == response_format["json_schema"]["name"]
        assert draft["schemas"][call_type]["response_format_sha256"] == schema_hash(response_format)


def test_agent_facing_output_contract_only_changes_formatting():
    market = market_decision_instructions(STRUCTURED_CONFIG)
    assert market.index("observations") < market.index("plans") < market.index("insights") < market.index("chosen_action")
    assert "My chosen action:\n" not in market
    communication = make_first_speaker_instructions(1, "A", STRUCTURED_CONFIG)
    assert "message string" in communication
    assert "Message to Seller B:" not in communication
    assert "Seller B will see your message" in communication


def test_provider_routes_exact_formats_and_keeps_request_metadata():
    client = FakeClient([response(communication_json("hello")), response(market_json())])
    comm = call_agent_communication(prompt="comm", seller_label="A", recipient_label="B",
                                    speaker_position="first", client=client, config=STRUCTURED_CONFIG)
    market = call_agent_market_decision(prompt="market", client=client, config=STRUCTURED_CONFIG)
    assert [call["response_format"] for call in client.calls] == [COMMUNICATION_RESPONSE_FORMAT, MARKET_RESPONSE_FORMAT]
    assert client.calls[0]["messages"] == [{"role": "user", "content": "comm"}]
    assert client.calls[1]["messages"] == [{"role": "user", "content": "market"}]
    assert all(call["reasoning_effort"] == "none" and call["temperature"] == 1.0 for call in client.calls)
    assert comm["message"] == "hello" and market["action"] == {"action_type": "bid", "price": 1.95}
    assert market["response_contract_version"] == comm["response_contract_version"] == CONTRACT_VERSION
    assert market["schema_sha256"] == schema_hash(MARKET_RESPONSE_FORMAT)
    assert comm["schema_sha256"] == schema_hash(COMMUNICATION_RESPONSE_FORMAT)
    assert market["usage"]["cached_tokens"] == 4
    assert len(client.calls) == 2
    medium = replace(STRUCTURED_CONFIG, reasoning_effort="medium", temperature=None)
    medium_client = FakeClient([response(market_json())])
    call_agent_market_decision(prompt="same", client=medium_client, config=medium)
    assert not {"temperature", "top_p", "logprobs", "top_logprobs"} & medium_client.calls[0].keys()


@pytest.mark.parametrize("raw", [
    "{}", '{"observations":null,"plans":"","insights":"","chosen_action":"1.95"}',
    '{"observations":0,"plans":"","insights":"","chosen_action":"1.95"}',
    '{"observations":"","plans":"","insights":"","chosen_action":"1.95","extra":"x"}',
    '{"observations":"","observations":"again","plans":"","insights":"","chosen_action":"1.95"}',
    '{"observations":', '[{"observations":""}]',
    '{"observations":"","plans":"","insights":"","chosen_action":1.95}',
    *[market_json(action=x) for x in ("NO_BID", "BID 1.95", "-0.01", "1.9", "1.999", "2.01", "2.1")],
])
def test_bad_market_json_is_terminal_without_retry(raw):
    client = FakeClient([response(raw)])
    with pytest.raises(AgentParseFailure):
        call_agent_market_decision(prompt="market", client=client, config=STRUCTURED_CONFIG)
    assert len(client.calls) == 1


@pytest.mark.parametrize("raw", ['{}', '{"message":null}', '{"message":42}',
                                 '{"message":"a","extra":"b"}',
                                 '{"message":"a","message":"b"}', '{"message":'])
def test_bad_communication_json_is_terminal(raw):
    client = FakeClient([response(raw)])
    with pytest.raises(AgentParseFailure):
        call_agent_communication(prompt="comm", seller_label="A", recipient_label="B",
                                 speaker_position="first", client=client, config=STRUCTURED_CONFIG)
    assert len(client.calls) == 1


@pytest.mark.parametrize("finish,refusal,raw", [
    ("length", None, market_json()), ("content_filter", None, market_json()),
    ("tool_calls", None, market_json()), (None, None, market_json()),
    ("stop", "refused", market_json()), ("stop", None, None),
])
def test_interrupted_or_refused_market_response_is_terminal(finish, refusal, raw):
    client = FakeClient([response(raw, finish=finish, refusal=refusal)])
    with pytest.raises(AgentResponseFailure):
        call_agent_market_decision(prompt="market", client=client, config=STRUCTURED_CONFIG)
    assert len(client.calls) == 1


def test_empty_memory_replacement_and_exact_rendering():
    raw = market_json(action="NO BID", observations="  α\r\n\t", plans="", insights="")
    parsed = decode_structured_response(raw, "market_decision", STRUCTURED_CONFIG)
    assert parsed["plans"] == parsed["insights"] == ""
    assert parsed["action"] == {"action_type": "no_bid", "price": None}
    assert render_market_response(parsed) == (
        "My observations and thoughts:\n  α\r\n\t\nNew content for PLANS.txt:\n"
        "\nNew content for INSIGHTS.txt:\n\nMy chosen action:\nNO BID")


def test_even_round_speaker_order_and_pre_action_market_prompts():
    config = replace(STRUCTURED_CONFIG, num_rounds=3, communication_end_round=2,
                     signal_start_round=3, pattern_window=2, pattern_max_period=2)
    client = FakeClient([response(communication_json(" B first\r\n")),
                         response(communication_json("A second\n")),
                         response(market_json()), response(market_json("NO BID"))])

    def comm_caller(**kwargs):
        return call_agent_communication(client=client, config=config, **kwargs)

    def market_caller(**kwargs):
        return call_agent_market_decision(prompt=kwargs["prompt"], client=client, config=config)

    trace = []
    result = execute_round(round_number=2, prior_communication=True,
                           signal_state=make_signal_schedule("none", config=config),
                           seller_memories={"A": {"plans": "", "insights": ""},
                                            "B": {"plans": "", "insights": ""}},
                           history=[], regulator_state=make_initial_regulator_state(),
                           market_decision_caller=market_caller,
                           communication_agent_caller=comm_caller,
                           config=config, execution_trace=trace)
    record = result["round_record"]
    assert record["communication"]["first_speaker"] == "B"
    assert record["communication"]["second_speaker"] == "A"
    assert record["communication"]["first_message"] == " B first\r\n"
    assert record["communication"]["transcript_block"] in record["market_decisions"]["A"]["prompt"]
    assert record["communication"]["transcript_block"] in record["market_decisions"]["B"]["prompt"]
    assert trace.index("market_prompt_B_constructed") < trace.index("market_call_A")
    assert "chosen_action" in record["market_decisions"]["A"]["prompt"]
    assert "Message to Seller A:" not in client.calls[0]["messages"][0]["content"]


def test_structured_transport_retry_reuses_identical_request():
    class TransientError(Exception):
        status_code = 429

    class RetryClient(FakeClient):
        def create(self, **kwargs):
            self.calls.append(kwargs)
            outcome = self.responses.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

    client = RetryClient([TransientError("temporary"), response(market_json())])
    delays = []
    result = call_agent_market_decision(prompt="identical", client=client,
                                        config=STRUCTURED_CONFIG, sleep_fn=delays.append)
    assert client.calls[0] == client.calls[1]
    assert len(client.calls) == 2 and delays == [2.0]
    assert result["attempt_count"] == 2
    assert result["technical_failures"][0]["retryable"] is True


@pytest.mark.parametrize("prior", [True, False])
@pytest.mark.parametrize("condition", ["none", "public", "private"])
def test_complete_short_episode_logs_commits_and_fidelity(tmp_path, capsys, prior, condition):
    config = replace(STRUCTURED_CONFIG, num_rounds=3, communication_end_round=1,
                     signal_start_round=2, pattern_window=2, pattern_max_period=2)
    message_a = '  Ω "quote"\t\r\n\r\n{"x":1}\rtrailing  '
    message_b = '\tReply\n\nwith LF\r and CR\r\n  '
    outcomes = []
    if prior:
        outcomes.extend([response(communication_json(message_a)), response(communication_json(message_b))])
    for number in range(1, 4):
        outcomes.extend([response(market_json("1.95", plans=f"A{number}")),
                         response(market_json("NO BID", plans=f"B{number}"))])
    client = FakeClient(outcomes)
    seeds = ({"public_signal_seed": 100} if condition == "public" else
             {"private_signal_seed_A": 100, "private_signal_seed_B": 200} if condition == "private" else {})
    result = run_episode(replicate_id=1, prior_communication=prior,
                         signal_condition=condition, save_dir=tmp_path / "results",
                         execution_log_dir=tmp_path / "execution_logs", run_name="fake",
                         client=client, config=config, **seeds)
    records = [json.loads(line) for line in (tmp_path / "results" / config.specification_version /
               "runs" / "fake" / "rounds.jsonl").read_text().splitlines()]
    assert result["last_completed_round"] == len(records) == 3
    assert records[0]["memory_before"]["A"]["plans"] == ""
    assert records[1]["memory_before"]["A"]["plans"] == "A1"
    assert records[2]["memory_after"]["B"]["plans"] == "B3"
    assert records[0]["market_decisions"]["A"]["result"]["raw_response"] == market_json("1.95", plans="A1")
    assert records[0]["market_decisions"]["A"]["result"]["chosen_action"] == "1.95"
    config_data = json.loads((tmp_path / "results" / config.specification_version / "runs" / "fake" / "config.json").read_text())
    assert config_data["response_contract_version"] == CONTRACT_VERSION
    assert config_data["prompt_caching_policy"] == "provider_default"
    assert config_data["structured_response_schemas"]["market_decision"]["sha256"] == schema_hash(MARKET_RESPONSE_FORMAT)
    log_dir = tmp_path / "execution_logs" / config.specification_version / "episodes"
    with (log_dir / "fake_market_responses.txt").open(encoding="utf-8", newline="") as handle:
        market_log = handle.read()
    assert market_log.count("My observations and thoughts:") == 6
    assert market_log.index("Round 1, Seller A") < market_log.index("Round 1, Seller B")
    assert market_log.index("New content for PLANS.txt:") < market_log.index("New content for INSIGHTS.txt:") < market_log.index("My chosen action:")
    console = capsys.readouterr().out
    with (log_dir / "fake.txt").open(encoding="utf-8", newline="") as handle:
        transcript = handle.read()
    assert console == transcript[transcript.index("Beginning of Phase 1."):]
    assert "My observations and thoughts:" not in transcript
    assert '"chosen_action"' not in transcript
    if condition == "public":
        assert "Round 1/3:\nPublic signal:" not in console
        for number in (2, 3):
            signal = records[number - 1]["signal_record"]["public_signal"]
            assert f"Round {number}/3:\nPublic signal: {signal}\n" in console
        assert console.count("Public signal:") == 2
    else:
        assert "Public signal:" not in console
    if prior:
        assert records[0]["communication"]["first_message"] == message_a
        assert records[0]["communication"]["second_message"] == message_b
        assert records[0]["communication"]["transcript_block"] in records[0]["market_decisions"]["A"]["prompt"]
        assert records[0]["communication"]["transcript_block"] in records[0]["market_decisions"]["B"]["prompt"]
        assert message_a in client.calls[1]["messages"][0]["content"]
        assert message_a in records[0]["market_decisions"]["A"]["prompt"]
        assert message_b in records[0]["market_decisions"]["B"]["prompt"]
        assert '\\r\\n' not in records[0]["communication"]["transcript_block"]
        assert '"message"' not in records[0]["communication"]["transcript_block"]
    else:
        assert not records[0]["communication"]["enabled"]
    if condition == "private":
        for label in ("A", "B"):
            other = "B" if label == "A" else "A"
            views = records[1]["signal"]["seller_views"]
            prompt = records[1]["market_decisions"][label]["prompt"]
            assert f"Code: {views[label]['signal']}" in prompt
            if views[label]["signal"] != views[other]["signal"]:
                assert f"Code: {views[other]['signal']}" not in prompt


def test_failed_second_round_does_not_commit_market_text_or_memory(tmp_path):
    config = replace(STRUCTURED_CONFIG, num_rounds=3, communication_end_round=1,
                     signal_start_round=2, pattern_window=2, pattern_max_period=2)
    client = FakeClient([response(market_json(plans="committed")), response(market_json()),
                         response(market_json(plans="uncommitted")), response("bad json")])
    with pytest.raises(AgentParseFailure):
        run_episode(replicate_id=1, prior_communication=False, signal_condition="none",
                    save_dir=tmp_path / "results", execution_log_dir=tmp_path / "logs",
                    run_name="failure", client=client, config=config)
    run_dir = tmp_path / "results" / config.specification_version / "runs" / "failure"
    assert len((run_dir / "rounds.jsonl").read_text().splitlines()) == 1
    checkpoint = json.loads((run_dir / "state_checkpoint.json").read_text())
    failure = json.loads((run_dir / "failure.json").read_text())
    assert checkpoint["last_completed_round"] == 1
    assert checkpoint["seller_memories"]["A"]["plans"] == "committed"
    assert failure["failure"]["api_result"]["raw_response"] == "bad json"
    with (tmp_path / "logs" / config.specification_version / "episodes" /
          "failure_market_responses.txt").open(encoding="utf-8", newline="") as handle:
        log = handle.read()
    assert "Round 1, Seller A" in log and "Round 2" not in log
    assert "uncommitted" not in log
