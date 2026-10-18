"""Frozen Chat Completions response contracts and strict offline decoding."""

import hashlib
import json
import re

from .market import make_bid_action, make_no_bid_action

CONTRACT_VERSION = "STRUCTURED_OUTPUTS_V1"
MARKET_SCHEMA_NAME = "seller_market_response_structured"
COMMUNICATION_SCHEMA_NAME = "seller_communication_structured"
MARKET_KEYS = ("observations", "plans", "insights", "chosen_action")
ACTION_PATTERN = r"^(NO BID|[01]\.[0-9]{2}|2\.00)$"

MARKET_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": MARKET_SCHEMA_NAME,
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "observations": {"type": "string", "description": "My observations and thoughts."},
                "plans": {"type": "string", "description": "New content for PLANS.txt. This replaces the previous contents."},
                "insights": {"type": "string", "description": "New content for INSIGHTS.txt. This replaces the previous contents."},
                "chosen_action": {
                    "type": "string",
                    "description": "My chosen market action: exactly NO BID or a numerical unit-price bid from 0.00 through 2.00 inclusive, written with two decimal places.",
                    "pattern": ACTION_PATTERN,
                },
            },
            "required": list(MARKET_KEYS),
            "additionalProperties": False,
        },
    },
}

COMMUNICATION_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": COMMUNICATION_SCHEMA_NAME,
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                },
            },
            "required": ["message"],
            "additionalProperties": False,
        },
    },
}

RESPONSE_FORMAT_BY_CALL = {
    "communication": COMMUNICATION_RESPONSE_FORMAT,
    "market_decision": MARKET_RESPONSE_FORMAT,
}


def canonical_payload(value: dict) -> str:
    """Serialize in declaration order so the hash covers the actual wire schema."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def schema_hash(value: dict) -> str:
    return hashlib.sha256(canonical_payload(value).encode("utf-8")).hexdigest()


def schema_provenance() -> dict:
    return {
        call_type: {"name": response_format["json_schema"]["name"],
                    "sha256": schema_hash(response_format),
                    "response_format": response_format}
        for call_type, response_format in RESPONSE_FORMAT_BY_CALL.items()
    }


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Duplicate JSON key: {key!r}.")
        value[key] = item
    return value


def decode_structured_response(raw: str, call_type: str, config) -> dict:
    if call_type not in RESPONSE_FORMAT_BY_CALL:
        raise ValueError(f"Unsupported structured call type: {call_type!r}.")
    if config.response_contract_version != CONTRACT_VERSION:
        raise ValueError("Unsupported structured response contract version.")
    if not isinstance(raw, str):
        raise TypeError("Response content must be a JSON string.")
    value = json.loads(raw, object_pairs_hook=_unique_pairs)
    expected = MARKET_KEYS if call_type == "market_decision" else ("message",)
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("Structured response has missing or extra fields.")
    if any(not isinstance(value[key], str) for key in expected):
        raise TypeError("Every structured response field must be a string.")
    if call_type == "communication":
        if not value["message"].strip():
            raise ValueError("Communication message must be nonempty.")
        return value
    action_text = value["chosen_action"]
    if re.fullmatch(ACTION_PATTERN, action_text) is None:
        raise ValueError("Invalid chosen_action; expected NO BID or a two-decimal 0.00–2.00 price.")
    # The grammar fixes exactly two fractional digits, so integer cents are
    # exact before converting to the market core's canonical float action.
    action = (make_no_bid_action() if action_text == "NO BID" else
              make_bid_action(int(action_text.replace(".", "")) / 100, config))
    return {**value, "action_text": action_text, "action": action,
            "action_type": action["action_type"], "price": action["price"]}


def render_market_response(value: dict) -> str:
    """Render validated fields without changing any generated string."""
    return ("My observations and thoughts:\n" + value["observations"] +
            "\nNew content for PLANS.txt:\n" + value["plans"] +
            "\nNew content for INSIGHTS.txt:\n" + value["insights"] +
            "\nMy chosen action:\n" + value["chosen_action"])
