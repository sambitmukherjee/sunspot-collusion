"""Provider-neutral failure types for agent calls."""


class APICallFailure(RuntimeError):
    """No provider response was returned; context is suitable for failure logs."""

    def __init__(self, message: str, *, prompt: str, failures: list[dict]):
        super().__init__(message)
        self.prompt = prompt
        self.failures = failures


class AgentResponseFailure(RuntimeError):
    """A provider response exists, but its text or finish reason is unusable."""

    def __init__(self, message: str, *, api_result: dict):
        super().__init__(message)
        self.api_result = api_result


class AgentParseFailure(ValueError):
    """A completed model response violates the required response grammar."""

    def __init__(self, message: str, *, api_result: dict):
        super().__init__(message)
        self.api_result = api_result
