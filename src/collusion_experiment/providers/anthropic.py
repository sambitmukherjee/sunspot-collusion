"""Reserved Anthropic transport; no SDK or network call is implemented."""


def call_raw(**_kwargs):
    raise NotImplementedError("Anthropic provider calls are not implemented.")
