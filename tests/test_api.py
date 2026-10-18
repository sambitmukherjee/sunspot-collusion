"""Offline OpenAI transport and structured response checks."""

import json
import socket
from dataclasses import replace
from types import SimpleNamespace as Obj

import pytest

from collusion_experiment.api import (
    APICallFailure, AgentParseFailure, AgentResponseFailure, call_chat_completion_raw,
    call_agent_communication, call_agent_market_decision,
)
from collusion_experiment.config import DEFAULT_CONFIG
from collusion_experiment.structured_outputs import (
    COMMUNICATION_RESPONSE_FORMAT, MARKET_RESPONSE_FORMAT,
)

MARKET_TEXT = json.dumps({"observations": "observe", "plans": "plan",
                          "insights": "insight", "chosen_action": "1.73"})


def response(text=MARKET_TEXT, finish="stop"):
    return Obj(
        id="resp-1", _request_id="req-1", model="gpt-5.6-terra-returned",
        choices=[Obj(message=Obj(content=text, refusal=None, tool_calls=None,
                                 function_call=None), finish_reason=finish)],
        usage=Obj(prompt_tokens=40, completion_tokens=20, total_tokens=60,
                  prompt_tokens_details=Obj(cached_tokens=3),
                  completion_tokens_details=Obj(reasoning_tokens=4)),
    )


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.chat = Obj(completions=Obj(create=self.create))

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = self.outcomes.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class TransientError(Exception):
    def __init__(self, status_code):
        super().__init__("temporary outage")
        self.status_code = status_code
        self.request_id = "failed-request"


def test_default_suite_blocks_network_before_connect():
    with pytest.raises(AssertionError, match="Network access is forbidden"):
        socket.create_connection(("127.0.0.1", 1), timeout=0.01)


def test_default_market_completion_uses_structured_contract_and_preserves_usage():
    client = FakeClient([response()])
    result = call_agent_market_decision(prompt="exact\r\nprompt", client=client)
    request = client.calls[0]
    assert result["action"] == {"action_type": "bid", "price": 1.73}
    assert result["prompt"] == request["messages"][0]["content"] == "exact\r\nprompt"
    assert result["response_id"] == "resp-1" and result["request_id"] == "req-1"
    assert result["requested_model"] == "gpt-5.6-terra"
    assert result["model"] == "gpt-5.6-terra-returned"
    assert result["raw_response"] == MARKET_TEXT
    assert result["usage"]["cached_tokens"] == 3
    assert result["usage"]["reasoning_tokens"] == 4
    assert request["response_format"] == MARKET_RESPONSE_FORMAT
    assert request["reasoning_effort"] == "none"
    assert request["temperature"] == 1.0


@pytest.mark.parametrize("effort", ["minimal", "low", "medium", "high", "xhigh", "max"])
@pytest.mark.parametrize("call_type", ["communication", "market_decision"])
def test_higher_reasoning_omits_sampling_parameters(effort, call_type):
    config = replace(DEFAULT_CONFIG, reasoning_effort=effort, temperature=None)
    if call_type == "communication":
        client = FakeClient([response(json.dumps({"message": "hello"}))])
        result = call_agent_communication(
            prompt="comm", seller_label="A", recipient_label="B",
            speaker_position="first", client=client, config=config)
        expected = COMMUNICATION_RESPONSE_FORMAT
    else:
        client = FakeClient([response()])
        result = call_agent_market_decision(prompt="market", client=client, config=config)
        expected = MARKET_RESPONSE_FORMAT
    request = client.calls[0]
    assert request["response_format"] == expected
    assert request["reasoning_effort"] == effort
    assert not {"temperature", "top_p", "top_logprobs", "logprobs"} & request.keys()
    assert result["call_type"] == call_type
    assert result["requested_temperature"] is None


def test_communication_message_is_decoded_verbatim():
    message = " hello\r\n"
    raw = json.dumps({"message": message})
    client = FakeClient([response(raw)])
    result = call_agent_communication(
        prompt="comm", seller_label="A", recipient_label="B",
        speaker_position="first", client=client)
    assert result["raw_response"] == raw
    assert result["message"] == message
    assert client.calls[0]["response_format"] == COMMUNICATION_RESPONSE_FORMAT


def test_retryable_error_reuses_identical_structured_request():
    client = FakeClient([TransientError(429), response()])
    delays = []
    result = call_chat_completion_raw(prompt="same prompt", call_type="market_decision",
                                      client=client, sleep_fn=delays.append)
    assert len(client.calls) == 2 and client.calls[0] == client.calls[1]
    assert result["attempt_count"] == 2
    assert result["technical_failures"][0]["status_code"] == 429
    assert delays == [2.0]


def test_retry_exhaustion_keeps_context():
    client = FakeClient([TransientError(500), TransientError(503), TransientError(429)])
    with pytest.raises(APICallFailure) as raised:
        call_chat_completion_raw(prompt="same prompt", call_type="market_decision",
                                 client=client, sleep_fn=lambda _: None)
    assert raised.value.prompt == "same prompt"
    assert len(raised.value.failures) == 3 and len(client.calls) == 3


def test_invalid_structured_payload_is_not_retried():
    client = FakeClient([response('{"observations":"only one field"}')])
    with pytest.raises(AgentParseFailure):
        call_agent_market_decision(prompt="market", client=client)
    assert len(client.calls) == 1


def test_invalid_communication_payload_is_not_retried():
    client = FakeClient([response('{"message":""}')])
    with pytest.raises(AgentParseFailure):
        call_agent_communication(prompt="comm", seller_label="A", recipient_label="B",
                                 speaker_position="first", client=client)
    assert len(client.calls) == 1


@pytest.mark.parametrize("text,finish", [(MARKET_TEXT, "length"), (None, "stop"),
                                           ("  ", "stop"), (MARKET_TEXT, "content_filter")])
def test_unusable_completion_is_not_retried(text, finish):
    client = FakeClient([response(text, finish)])
    with pytest.raises(AgentResponseFailure):
        call_agent_market_decision(prompt="market", client=client)
    assert len(client.calls) == 1


def test_nonretryable_api_error_is_not_retried():
    client = FakeClient([TransientError(400)])
    with pytest.raises(APICallFailure) as raised:
        call_chat_completion_raw(prompt="market", call_type="market_decision", client=client)
    assert len(client.calls) == 1 and raised.value.failures[0]["retryable"] is False


@pytest.mark.parametrize("provider", ["anthropic", "deepseek"])
def test_unimplemented_provider_stubs_never_touch_client(provider):
    class ForbiddenClient:
        def __getattribute__(self, _):
            raise AssertionError("Stub accessed client or network")
    with pytest.raises(NotImplementedError, match="not implemented"):
        call_chat_completion_raw(prompt="offline", call_type="market_decision",
                                 client=ForbiddenClient(), provider=provider)
