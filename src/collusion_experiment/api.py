"""Provider-neutral agent-call boundary and parsed task wrappers."""

import time
from typing import Any, Callable

from .api_errors import APICallFailure, AgentParseFailure, AgentResponseFailure
from .config import ExperimentConfig, resolve_config
from .providers import get_raw_caller
from .structured_outputs import (
    CONTRACT_VERSION, RESPONSE_FORMAT_BY_CALL, decode_structured_response, schema_hash,
)
from .providers.openai import (
    TECHNICAL_INITIAL_BACKOFF_SECONDS, TECHNICAL_BACKOFF_MULTIPLIER,
    extract_chat_completion_usage, is_retryable_technical_error,
    model_dump_if_available, retry_after_seconds_from_exception,
    summarize_api_exception, technical_retry_delay, utc_timestamp,
)

TECHNICAL_MAX_ATTEMPTS = 3


def call_chat_completion_raw(
    *, prompt: str, client: Any, config: ExperimentConfig | None = None,
    call_type: str | None = None,
    max_attempts: int = TECHNICAL_MAX_ATTEMPTS, sleep_fn: Callable[[float], None] = time.sleep,
    provider: str = "openai",
) -> dict:
    """Call the selected provider using the active structured contract."""
    return get_raw_caller(provider)(
        prompt=prompt, client=client, config=config, call_type=call_type,
        max_attempts=max_attempts, sleep_fn=sleep_fn,
    )


def require_usable_agent_response(api_result: dict) -> str:
    raw = api_result["raw_response"]
    finish = api_result["finish_reason"]
    if api_result.get("refusal"):
        raise AgentResponseFailure("The model refused this scientific call.", api_result=api_result)
    if finish == "length":
        raise AgentResponseFailure("The model response was truncated at the token limit.", api_result=api_result)
    if finish != "stop":
        raise AgentResponseFailure(f"Unexpected finish reason: {finish!r}.", api_result=api_result)
    if (api_result.get("choice_count") != 1 or
            api_result.get("tool_calls") or api_result.get("function_call")):
        raise AgentResponseFailure("Interrupted or ambiguous model completion.", api_result=api_result)
    if not isinstance(raw, str) or not raw.strip():
        raise AgentResponseFailure("The API returned no usable text content.", api_result=api_result)
    return raw


def _structured_result(api_result: dict, call_type: str, config: ExperimentConfig) -> dict:
    expected = RESPONSE_FORMAT_BY_CALL[call_type]
    if (api_result.get("call_type") != call_type or
            api_result.get("response_contract_version") != CONTRACT_VERSION or
            api_result.get("schema_name") != expected["json_schema"]["name"] or
            api_result.get("schema_sha256") != schema_hash(expected) or
            api_result.get("response_format") != expected):
        raise AgentResponseFailure("Structured response contract metadata mismatch.", api_result=api_result)
    raw = require_usable_agent_response(api_result)
    try:
        parsed = decode_structured_response(raw, call_type, config)
    except (TypeError, ValueError) as exc:
        raise AgentParseFailure("Failed to decode structured model response.", api_result=api_result) from exc
    return {**api_result, **parsed}


def call_agent_market_decision(
    *, prompt: str, client: Any, config: ExperimentConfig | None = None,
    max_attempts: int = TECHNICAL_MAX_ATTEMPTS, sleep_fn: Callable[[float], None] = time.sleep,
    provider: str = "openai",
) -> dict:
    config = resolve_config(config)
    api_result = call_chat_completion_raw(prompt=prompt, client=client, config=config, call_type="market_decision", max_attempts=max_attempts, sleep_fn=sleep_fn, provider=provider)
    return _structured_result(api_result, "market_decision", config)


def call_agent_communication(
    *, prompt: str, seller_label: str, recipient_label: str, speaker_position: str,
    client: Any, config: ExperimentConfig | None = None,
    max_attempts: int = TECHNICAL_MAX_ATTEMPTS, sleep_fn: Callable[[float], None] = time.sleep,
    provider: str = "openai",
) -> dict:
    config = resolve_config(config)
    if seller_label not in config.seller_labels or recipient_label not in config.seller_labels or seller_label == recipient_label:
        raise ValueError("Sender and recipient must be different known sellers.")
    if speaker_position not in ("first", "second"):
        raise ValueError("speaker_position must be 'first' or 'second'.")
    api_result = call_chat_completion_raw(prompt=prompt, client=client, config=config, call_type="communication", max_attempts=max_attempts, sleep_fn=sleep_fn, provider=provider)
    parsed = _structured_result(api_result, "communication", config)
    return {**parsed, "seller_label": seller_label, "recipient_label": recipient_label,
            "speaker_position": speaker_position}
