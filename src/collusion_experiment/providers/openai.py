"""OpenAI Chat Completions transport with injected-client retry semantics."""

import time
from datetime import datetime, timezone
from typing import Any, Callable

from ..api_errors import APICallFailure, AgentResponseFailure
from ..config import ExperimentConfig, resolve_config
from ..structured_outputs import CONTRACT_VERSION, RESPONSE_FORMAT_BY_CALL, schema_hash

TECHNICAL_MAX_ATTEMPTS = 3
TECHNICAL_INITIAL_BACKOFF_SECONDS = 2.0
TECHNICAL_BACKOFF_MULTIPLIER = 2.0

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _attr(value: Any, name: str, default: Any = None) -> Any:
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def model_dump_if_available(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return model_dump_if_available(value.model_dump())
    if isinstance(value, dict):
        return {key: model_dump_if_available(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [model_dump_if_available(item) for item in value]
    if hasattr(value, "__dict__"):
        return model_dump_if_available(dict(value.__dict__))
    return value if isinstance(value, (str, int, float, bool)) else repr(value)


def _first(value: Any, names: tuple[str, ...], default: Any = None) -> Any:
    for name in names:
        result = _attr(value, name)
        if result is not None:
            return result
    return default


def extract_chat_completion_usage(completion: Any) -> dict:
    usage = _attr(completion, "usage")
    if usage is None:
        return {
            "usage_available": False, "prompt_tokens": 0, "cached_tokens": 0,
            "cache_write_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
            "total_tokens": 0, "raw_usage": None,
        }
    prompt_details = _first(usage, ("prompt_tokens_details", "prompt_token_details"))
    completion_details = _first(usage, ("completion_tokens_details", "completion_token_details"))
    return {
        "usage_available": True,
        "prompt_tokens": int(_attr(usage, "prompt_tokens", 0) or 0),
        "cached_tokens": int(_first(prompt_details, ("cached_tokens",), 0) or 0),
        "cache_write_tokens": int(_first(prompt_details, ("cache_write_tokens", "cache_creation_tokens"), 0) or 0),
        "completion_tokens": int(_attr(usage, "completion_tokens", 0) or 0),
        "reasoning_tokens": int(_first(completion_details, ("reasoning_tokens",), 0) or 0),
        "total_tokens": int(_attr(usage, "total_tokens", 0) or 0),
        "raw_usage": model_dump_if_available(usage),
    }


def summarize_api_exception(exc: Exception) -> dict:
    return {
        "exception_type": type(exc).__name__, "message": str(exc),
        "status_code": _attr(exc, "status_code"), "request_id": _attr(exc, "request_id"),
        "timestamp_utc": utc_timestamp(),
    }


def is_retryable_technical_error(exc: Exception) -> bool:
    # The client is injected; avoid requiring the network SDK in offline runs.
    if type(exc).__name__ in ("APIConnectionError", "APITimeoutError"):
        return True
    status = _attr(exc, "status_code")
    return isinstance(status, int) and (status in (408, 409, 429) or status >= 500)


def retry_after_seconds_from_exception(exc: Exception) -> float | None:
    headers = _attr(_attr(exc, "response"), "headers")
    try:
        value = headers.get("retry-after") if headers is not None else None
        seconds = float(value) if value is not None else None
    except (AttributeError, TypeError, ValueError):
        return None
    return seconds if seconds is not None and seconds >= 0 else None


def technical_retry_delay(exc: Exception, failed_attempt_number: int) -> float:
    retry_after = retry_after_seconds_from_exception(exc)
    if retry_after is not None:
        return retry_after
    return TECHNICAL_INITIAL_BACKOFF_SECONDS * TECHNICAL_BACKOFF_MULTIPLIER ** (failed_attempt_number - 1)


def call_chat_completion_raw(
    *, prompt: str, client: Any, config: ExperimentConfig | None = None,
    call_type: str | None = None,
    max_attempts: int = TECHNICAL_MAX_ATTEMPTS, sleep_fn: Callable[[float], None] = time.sleep,
) -> dict:
    """Retry transient transport/API errors with the identical prompt."""
    config = resolve_config(config)
    if not isinstance(prompt, str) or not prompt:
        raise ValueError("prompt must be a nonempty string.")
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be an integer >= 1.")
    request_kwargs = {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
        "reasoning_effort": config.reasoning_effort,
        "max_completion_tokens": config.max_completion_tokens,
    }
    if config.response_contract_version != CONTRACT_VERSION or call_type not in RESPONSE_FORMAT_BY_CALL:
        raise ValueError("A supported structured call type is required.")
    response_format = RESPONSE_FORMAT_BY_CALL[call_type]
    request_kwargs["response_format"] = response_format
    if config.reasoning_effort == "none":
        request_kwargs["temperature"] = config.temperature
    request_started_at_utc = utc_timestamp()
    failures: list[dict] = []
    for attempt in range(1, max_attempts + 1):
        try:
            completion = client.chat.completions.create(**request_kwargs)
            break
        except Exception as exc:
            failure = summarize_api_exception(exc)
            failure.update(attempt_number=attempt, retryable=is_retryable_technical_error(exc))
            failures.append(failure)
            if not failure["retryable"] or attempt == max_attempts:
                raise APICallFailure("API call failed before a Chat Completion was returned.", prompt=prompt, failures=failures) from exc
            delay = technical_retry_delay(exc, attempt)
            failure["retry_delay_seconds"] = delay
            sleep_fn(delay)
    choices = _attr(completion, "choices")
    if not choices:
        raise AgentResponseFailure("Chat Completion contained no choices.", api_result={
            "prompt": prompt, "response_id": _attr(completion, "id"),
            "requested_model": config.model, "model": _attr(completion, "model"),
            "raw_response": None, "technical_failures": failures,
            "call_type": call_type, "response_contract_version": config.response_contract_version,
            "schema_name": response_format["json_schema"]["name"],
            "response_format": response_format,
        })
    choice = choices[0]
    usage = extract_chat_completion_usage(completion)
    return {
        "prompt": prompt,
        "requested_model": config.model,
        "requested_reasoning_effort": config.reasoning_effort,
        "requested_temperature": request_kwargs.get("temperature"),
        "requested_max_completion_tokens": config.max_completion_tokens,
        "response_id": _attr(completion, "id"),
        "request_id": _attr(completion, "_request_id"),
        "model": _attr(completion, "model"),
        "finish_reason": _attr(choice, "finish_reason"),
        "raw_response": _attr(_attr(choice, "message"), "content"),
        "refusal": _attr(_attr(choice, "message"), "refusal"),
        "tool_calls": model_dump_if_available(_attr(_attr(choice, "message"), "tool_calls")),
        "function_call": model_dump_if_available(_attr(_attr(choice, "message"), "function_call")),
        "choice_count": len(choices),
        "call_type": call_type,
        "response_contract_version": config.response_contract_version,
        "schema_name": response_format["json_schema"]["name"],
        "schema_sha256": schema_hash(response_format),
        "response_format": response_format,
        "request_parameters": {key: value for key, value in request_kwargs.items() if key != "messages"},
        "usage": usage,
        "attempt_count": len(failures) + 1,
        "technical_failures": failures,
        "request_started_at_utc": request_started_at_utc,
        "response_received_at_utc": utc_timestamp(),
    }

# Provider interface: API boundary selects this callable for OpenAI.
call_raw = call_chat_completion_raw
