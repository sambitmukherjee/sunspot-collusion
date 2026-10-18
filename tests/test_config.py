"""Timing and frozen configuration checks for the clean scientific core."""

from dataclasses import FrozenInstanceError, replace

import pytest

from collusion_experiment import config


def test_frozen_confirmatory_defaults() -> None:
    c = config.DEFAULT_CONFIG
    assert (c.specification_version, c.prompt_family, c.prompt_version) == (
        "COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2",
        "fish_p1_adapted", "PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1"
    )
    assert (c.model, c.reasoning_effort, c.temperature, c.max_completion_tokens) == (
        "gpt-5.6-terra", "none", 1.0, 8000
    )
    assert (c.max_history_rounds, c.num_rounds, c.communication_end_round, c.signal_start_round) == (
        150, 150, 50, 71
    )
    assert (c.order_size, c.marginal_cost, c.participation_cost, c.reservation_price, c.price_tick) == (
        100, 1.0, 16.0, 2.0, 0.01
    )
    assert (c.pattern_window, c.pattern_max_period, c.pattern_fine) == (20, 8, 8.0)
    assert c.public_signal_values == ("KAPPA", "LAMBDA")
    assert c.seller_labels == ("A", "B")
    assert config.NUM_ROUNDS == c.num_rounds
    assert config.MAX_HISTORY_ROUNDS == 150
    with pytest.raises(FrozenInstanceError):
        c.num_rounds = 151


@pytest.mark.parametrize(
    ("round_number", "stage"),
    [(1, 1), (50, 1), (51, 2), (70, 2), (71, 3), (150, 3)],
)
def test_stage_boundaries(round_number: int, stage: int) -> None:
    assert config.analytical_stage(round_number) == stage


def test_stage_boundaries_derive_from_config() -> None:
    alternate = replace(config.DEFAULT_CONFIG, num_rounds=12, communication_end_round=3, signal_start_round=7)
    assert [config.analytical_stage(round_number, alternate) for round_number in (3, 4, 6, 7, 12)] == [1, 2, 2, 3, 3]
    assert config.communication_is_enabled(True, 3, alternate)
    assert not config.communication_is_enabled(True, 4, alternate)
    assert not hasattr(config.DEFAULT_CONFIG, "stage1_end_round")
    assert not hasattr(config.DEFAULT_CONFIG, "stage2_end_round")


@pytest.mark.parametrize("round_number", [0, 151, -1])
def test_stage_rejects_out_of_horizon_round(round_number: int) -> None:
    with pytest.raises(ValueError):
        config.analytical_stage(round_number)


def test_communication_treatment_and_input_validation() -> None:
    assert config.communication_is_enabled(True, 50)
    assert not config.communication_is_enabled(True, 51)
    assert not config.communication_is_enabled(False, 1)
    with pytest.raises(TypeError):
        config.communication_is_enabled(1, 1)
    with pytest.raises(TypeError):
        config.analytical_stage(True)


def test_invalid_configurations_are_rejected() -> None:
    base = config.DEFAULT_CONFIG
    for changes in (
        {"reasoning_effort": "unsupported"},
        {"prompt_family": "fish_p2_adapted", "prompt_version": "INVALID_PROMPT"},
        {"prompt_family": "fish_p1_adapted", "prompt_version": "INVALID_PROMPT"},
        {"temperature": None},
        {"signal_start_round": 50},
        {"communication_end_round": 0},
        {"num_rounds": 70},
        {"pattern_max_period": 21},
        {"price_tick": 0.015},
        {"reservation_price": 2.005},
        {"participation_cost": -1.0},
    ):
        with pytest.raises(ValueError):
            replace(base, **changes)


def test_medium_reasoning_can_be_represented_without_changing_default() -> None:
    medium = replace(config.DEFAULT_CONFIG, reasoning_effort="medium", temperature=None)
    assert (medium.reasoning_effort, medium.temperature) == ("medium", None)
    assert config.DEFAULT_CONFIG.reasoning_effort == "none"
