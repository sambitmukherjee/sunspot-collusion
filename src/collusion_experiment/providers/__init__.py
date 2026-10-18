"""Provider-neutral raw-call selection. Only OpenAI is implemented."""

from . import anthropic, deepseek, openai


def get_raw_caller(provider: str):
    callers = {"openai": openai.call_raw, "anthropic": anthropic.call_raw,
               "deepseek": deepseek.call_raw}
    try:
        return callers[provider]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Unknown agent provider: {provider!r}.") from exc
