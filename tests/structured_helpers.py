"""Offline structured model results for execution and storage tests."""

import json

from collusion_experiment.config import DEFAULT_CONFIG
from collusion_experiment.structured_outputs import (
    CONTRACT_VERSION, RESPONSE_FORMAT_BY_CALL, decode_structured_response, schema_hash,
)


def structured_result(call_type, raw, *, prompt, config=DEFAULT_CONFIG, **extra):
    response_format = RESPONSE_FORMAT_BY_CALL[call_type]
    return {
        "prompt": prompt,
        "raw_response": raw,
        "finish_reason": "stop",
        "choice_count": 1,
        "tool_calls": None,
        "function_call": None,
        "refusal": None,
        "call_type": call_type,
        "response_contract_version": CONTRACT_VERSION,
        "schema_name": response_format["json_schema"]["name"],
        "schema_sha256": schema_hash(response_format),
        "response_format": response_format,
        **decode_structured_response(raw, call_type, config),
        **extra,
    }


def market_result(*, prompt, action="1.42", observations="observe", plans="plan",
                  insights="insight", config=DEFAULT_CONFIG, **extra):
    raw = json.dumps({"observations": observations, "plans": plans,
                      "insights": insights, "chosen_action": action}, ensure_ascii=False)
    return structured_result("market_decision", raw, prompt=prompt, config=config, **extra)


def communication_result(*, prompt, message, config=DEFAULT_CONFIG, **extra):
    raw = json.dumps({"message": message}, ensure_ascii=False)
    return structured_result("communication", raw, prompt=prompt, config=config, **extra)
