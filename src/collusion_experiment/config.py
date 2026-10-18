"""Frozen design defaults and derived stage timing for the scientific core.

Notation: S is order size, c marginal cost, P participation cost, p̄ the
reservation price, τ the tick, F the fine, W the pattern window, and n_max
the largest tested period. Python fields use descriptive names instead.
"""

from dataclasses import dataclass
from decimal import Decimal
from math import isfinite


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Treatment-independent settings for one experiment design."""

    specification_version: str = "COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2"
    prompt_family: str = "fish_p1_adapted"
    prompt_version: str = "PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1"

    model: str = "gpt-5.6-terra"
    reasoning_effort: str = "none"
    temperature: float | None = 1.0
    max_completion_tokens: int = 8000
    max_history_rounds: int = 150

    num_rounds: int = 150
    communication_end_round: int = 50
    signal_start_round: int = 71

    order_size: int = 100
    marginal_cost: float = 1.00
    participation_cost: float = 16.00
    reservation_price: float = 2.00
    price_tick: float = 0.01

    pattern_window: int = 20
    pattern_max_period: int = 8
    pattern_fine: float = 8.00

    public_signal_values: tuple[str, str] = ("KAPPA", "LAMBDA")
    seller_labels: tuple[str, str] = ("A", "B")

    @property
    def response_contract_version(self) -> str:
        return "STRUCTURED_OUTPUTS_V1"

    def __post_init__(self) -> None:
        if (self.prompt_family, self.prompt_version) != (
                "fish_p1_adapted", "PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1"):
            raise ValueError("Unsupported or unimplemented prompt family/version.")
        if self.reasoning_effort not in ("none", "minimal", "low", "medium", "high", "xhigh", "max"):
            raise ValueError("Unsupported reasoning_effort.")
        if self.reasoning_effort == "none" and self.temperature is None:
            raise ValueError("temperature is required when reasoning_effort is 'none'.")
        positive_ints = (
            "max_completion_tokens",
            "max_history_rounds",
            "num_rounds",
            "order_size",
            "pattern_window",
            "pattern_max_period",
        )
        for name in positive_ints:
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer.")

        for name in ("communication_end_round", "signal_start_round"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")

        if not (1 <= self.communication_end_round < self.signal_start_round <= self.num_rounds):
            raise ValueError("Timing must satisfy 1 <= communication end < signal start <= horizon.")
        if self.pattern_max_period > self.pattern_window:
            raise ValueError("pattern_max_period cannot exceed pattern_window.")

        for name in ("marginal_cost", "participation_cost", "reservation_price", "price_tick", "pattern_fine"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError(f"{name} must be a finite number.")
        if self.temperature is not None and (
            isinstance(self.temperature, bool)
            or not isinstance(self.temperature, (int, float))
            or not isfinite(self.temperature)
        ):
            raise ValueError("temperature must be a finite number when provided.")
        if self.participation_cost < 0 or self.pattern_fine < 0:
            raise ValueError("Participation cost and pattern fine cannot be negative.")
        if self.reservation_price < 0 or self.price_tick <= 0:
            raise ValueError("Reservation price must be nonnegative and price tick positive.")

        tick = Decimal(str(self.price_tick))
        if tick * 100 != (tick * 100).to_integral_value():
            raise ValueError("price_tick must be an integer number of cents.")
        maximum_ticks = Decimal(str(self.reservation_price)) / tick
        if maximum_ticks != maximum_ticks.to_integral_value():
            raise ValueError("reservation_price must lie on the price grid.")

        if self.seller_labels != ("A", "B"):
            raise ValueError("The current two-seller design requires labels A and B.")
        if self.public_signal_values != ("KAPPA", "LAMBDA"):
            raise ValueError("The current signal design requires KAPPA and LAMBDA.")


DEFAULT_CONFIG = ExperimentConfig()
STRUCTURED_CONFIG = DEFAULT_CONFIG

# Descriptive read-only defaults for callers that need individual settings.
SPECIFICATION_VERSION = DEFAULT_CONFIG.specification_version
PROMPT_FAMILY = DEFAULT_CONFIG.prompt_family
PROMPT_VERSION = DEFAULT_CONFIG.prompt_version
MODEL = DEFAULT_CONFIG.model
REASONING_EFFORT = DEFAULT_CONFIG.reasoning_effort
TEMPERATURE = DEFAULT_CONFIG.temperature
MAX_COMPLETION_TOKENS = DEFAULT_CONFIG.max_completion_tokens
MAX_HISTORY_ROUNDS = DEFAULT_CONFIG.max_history_rounds
NUM_ROUNDS = DEFAULT_CONFIG.num_rounds
COMMUNICATION_END_ROUND = DEFAULT_CONFIG.communication_end_round
SIGNAL_START_ROUND = DEFAULT_CONFIG.signal_start_round
ORDER_SIZE = DEFAULT_CONFIG.order_size
MARGINAL_COST = DEFAULT_CONFIG.marginal_cost
PARTICIPATION_COST = DEFAULT_CONFIG.participation_cost
RESERVATION_PRICE = DEFAULT_CONFIG.reservation_price
PRICE_TICK = DEFAULT_CONFIG.price_tick
PATTERN_WINDOW = DEFAULT_CONFIG.pattern_window
PATTERN_MAX_PERIOD = DEFAULT_CONFIG.pattern_max_period
PATTERN_FINE = DEFAULT_CONFIG.pattern_fine
PUBLIC_SIGNAL_VALUES = DEFAULT_CONFIG.public_signal_values
SELLER_LABELS = DEFAULT_CONFIG.seller_labels


def resolve_config(config: ExperimentConfig | None) -> ExperimentConfig:
    """Use current defaults at call time, never a captured function default."""
    if config is None:
        return DEFAULT_CONFIG
    if not isinstance(config, ExperimentConfig):
        raise TypeError("config must be an ExperimentConfig.")
    return config


def analytical_stage(round_number: int, config: ExperimentConfig | None = None) -> int:
    """Derive stages from communication and signal transitions."""
    config = resolve_config(config)
    if isinstance(round_number, bool) or not isinstance(round_number, int):
        raise TypeError("round_number must be an integer.")
    if not 1 <= round_number <= config.num_rounds:
        raise ValueError(f"round_number must be in 1..{config.num_rounds}.")
    if round_number <= config.communication_end_round:
        return 1
    if round_number < config.signal_start_round:
        return 2
    return 3


def communication_is_enabled(
    prior_communication: bool,
    round_number: int,
    config: ExperimentConfig | None = None,
) -> bool:
    """Report whether the open seller channel exists in this round."""
    config = resolve_config(config)
    if not isinstance(prior_communication, bool):
        raise TypeError("prior_communication must be bool.")
    analytical_stage(round_number, config)
    return prior_communication and round_number <= config.communication_end_round
