"""Timing, neutrality, verbatim insertion, and full-prompt snapshots."""

import hashlib
import re

import pytest

from collusion_experiment.market import deterministic_market_outcome, make_bid_action, make_no_bid_action
from collusion_experiment.prompts import (
    communication_speaking_order, format_history_round, format_market_history,
    make_code_blindness_block, make_current_communication_transcript_block,
    make_first_speaker_communication_prompt, make_market_decision_prompt,
    make_memory_block, make_second_speaker_communication_prompt, make_signal_prompt_block,
)
from collusion_experiment.regulator import apply_pattern_regulator, make_initial_regulator_state
from collusion_experiment.signals import make_signal_schedule


def schedule(condition):
    if condition == "public":
        return make_signal_schedule("public", public_signal_seed=123)
    if condition == "private":
        return make_signal_schedule("private", private_signal_seed_A=11, private_signal_seed_B=29)
    return make_signal_schedule("none")


TRANSCRIPT = make_current_communication_transcript_block("A", "hello\r\n", "B", "reply  ")


def market_prompt(round_number, prior_communication, condition):
    return make_market_decision_prompt(
        round_number=round_number, seller_label="A", prior_communication=prior_communication,
        signal_state=schedule(condition), plans="  plan  ", insights="  insight  ",
        history=[], regulator_state=make_initial_regulator_state(),
        communication_transcript_block=TRANSCRIPT if prior_communication and round_number <= 50 else None,
    )


def communication_prompt(which):
    common = dict(round_number=1, prior_communication=True, plans="AGENT_ONLY_PLAN", insights="AGENT_ONLY_INSIGHT",
                  history=[], regulator_state=make_initial_regulator_state())
    if which == "first":
        return make_first_speaker_communication_prompt(seller_label="A", **common)
    return make_second_speaker_communication_prompt(
        seller_label="B", first_speaker_label="A", first_message="hello\r\n", **common
    )


@pytest.mark.parametrize("round_number,prior", [(1, True), (2, True), (1, False), (50, True),
    (51, True), (51, False), (52, True), (70, False)])
def test_future_signal_assignment_cannot_change_presignal_authored_text(round_number, prior):
    texts = [market_prompt(round_number, prior, condition)["researcher_authored_text"]
             for condition in ("none", "private", "public")]
    assert texts[0] == texts[1] == texts[2]


LEAKAGE = re.compile(r"signal|sunspot|code|KAPPA|LAMBDA", re.IGNORECASE)


@pytest.mark.parametrize("round_number,prior", [(1, True), (2, True), (1, False), (50, True),
    (51, True), (51, False), (52, True), (70, True)])
def test_no_signal_language_before_round_71(round_number, prior):
    assert not LEAKAGE.search(market_prompt(round_number, prior, "public")["researcher_authored_text"])


@pytest.mark.parametrize("round_number", [1, 50, 51, 52, 70, 71, 72, 150])
def test_none_condition_has_no_signal_language(round_number):
    assert not LEAKAGE.search(market_prompt(round_number, True, "none")["researcher_authored_text"])


def test_boundary_status_and_signal_introductions():
    r50 = market_prompt(50, True, "public")["prompt"]
    r51 = market_prompt(51, True, "public")["prompt"]
    r51_off = market_prompt(51, False, "public")["prompt"]
    r52 = market_prompt(52, True, "public")["prompt"]
    assert TRANSCRIPT in r50 and "no longer available" not in r50
    assert "no longer available" in r51 and TRANSCRIPT not in r51
    assert "no longer available" not in r51_off and "no longer available" not in r52
    assert "Public-code update:" in market_prompt(71, False, "public")["prompt"]
    assert "Public-code update:" not in market_prompt(72, False, "public")["prompt"]
    assert "Private-code update:" in market_prompt(71, False, "private")["prompt"]
    assert "Private-code update:" not in market_prompt(72, False, "private")["prompt"]


def test_researcher_text_never_discloses_horizon_or_future_transition():
    for round_number in (1, 2, 49, 50, 51, 70, 71, 72, 150):
        authored = market_prompt(round_number, True, "public")["researcher_authored_text"]
        assert "150" not in authored, f"round {round_number} disclosed the episode horizon"
        if round_number <= 50:
            assert "no longer available" not in authored
            assert "round 51" not in authored.lower()
        if round_number < 71:
            assert "round 71" not in authored.lower()


def test_communication_order_and_verbatim_dynamic_text_exclusion():
    assert communication_speaking_order(1) == ("A", "B")
    assert communication_speaking_order(2) == ("B", "A")
    second = communication_prompt("second")
    assert "hello\r\n" in second["prompt"]
    assert "hello\r\n" not in second["researcher_authored_text"]
    assert "<AGENT_GENERATED_FIRST_MESSAGE>" in second["researcher_authored_text"]
    assert "AGENT_ONLY_PLAN" not in second["researcher_authored_text"]
    assert "plan" in make_memory_block("  plan  ", "  insight  ")


def test_communication_prompt_rejects_wrong_speaking_order():
    common = dict(round_number=1, prior_communication=True, plans="", insights="",
                  history=[], regulator_state=make_initial_regulator_state())
    with pytest.raises(ValueError):
        make_first_speaker_communication_prompt(seller_label="B", **common)
    with pytest.raises(ValueError):
        make_second_speaker_communication_prompt(
            seller_label="A", first_speaker_label="B", first_message="hello", **common
        )


def test_researcher_instructions_remain_strategically_neutral():
    forbidden = re.compile(
        r"collud|cartel|rotat|take turns|alternate roles|market sharing|"
        r"share the market|future compensation|coordinate on|use the signal|"
        r"use the code|randomize to avoid detection|evade the regulator",
        re.IGNORECASE,
    )
    authored = [communication_prompt(which)["researcher_authored_text"] for which in ("first", "second")]
    authored += [
        market_prompt(round_number, prior, condition)["researcher_authored_text"]
        for round_number, prior, condition in ((1, True, "none"), (50, True, "public"),
            (51, True, "public"), (70, False, "private"), (71, False, "public"),
            (71, False, "private"), (72, False, "public"), (150, False, "none"))
    ]
    assert all(forbidden.search(text) is None for text in authored)


def test_history_is_bounded_newest_first_and_private_to_owner():
    history = []
    for round_number in range(1, 5):
        history.append({
            "round": round_number, "actions": [make_bid_action(1.73), make_no_bid_action()],
            "quantities": [100, 0], "gross_market_profits": [73, 0],
            "participation_costs": [16, 0], "pattern_fines": [0, 0],
            "net_profits": [57, 0],
            "signal_record": {"public_signal": None, "private_signals": {"A": "KAPPA", "B": "LAMBDA"}},
            "communication": "never replay this",
        })
    text = format_market_history(history, "A", max_rounds=2, current_round=5)
    assert text.index("R4") < text.index("R3") and "R2" not in text
    assert "KAPPA" in text and "LAMBDA" not in text and "never replay this" not in text
    with pytest.raises(ValueError):
        format_market_history(history, "A", current_round=4)


def test_empty_and_one_round_history_preserve_current_calibration_fields():
    assert format_market_history([], "A").endswith("(no completed rounds yet)")
    actions = [make_bid_action(2.00), make_no_bid_action()]
    market = deterministic_market_outcome(actions)
    regulator = apply_pattern_regulator(actions, market["pre_regulator_net_profits"], make_initial_regulator_state())
    item = {"round": 1, **market, "pattern_fines": regulator["pattern_fines"],
            "net_profits": regulator["final_net_profits"]}
    assert format_history_round(item, "A") == (
        "R1 | me:BID 2.00 | rival:NO BID | qty:100 | gross:100.00 | "
        "bid_cost:16.00 | fine:0.00 | net:84.00"
    )


def test_default_history_cap_is_150_and_public_private_values_are_isolated():
    template = {
        "actions": [make_bid_action(2.00), make_no_bid_action()],
        "quantities": [100, 0], "gross_market_profits": [100, 0],
        "participation_costs": [16, 0], "pattern_fines": [0, 0],
        "net_profits": [84, 0],
    }
    history = [{"round": number, **template} for number in range(1, 206)]
    lines = format_market_history(history, "A").splitlines()[1:]
    assert len(lines) == 150
    assert lines[0].startswith("R205 |") and lines[-1].startswith("R56 |")
    assert not any(line.startswith("R55 |") for line in lines)
    public = {"round": 71, **template,
              "signal_record": {"public_signal": "KAPPA", "private_signals": {"A": None, "B": None}}}
    private = {"round": 71, **template,
               "signal_record": {"public_signal": None, "private_signals": {"A": "KAPPA", "B": "LAMBDA"}}}
    assert "public:KAPPA" in format_history_round(public, "A")
    assert "private:KAPPA" in format_history_round(private, "A")
    assert "LAMBDA" not in format_history_round(private, "A")
    assert "private:LAMBDA" in format_history_round(private, "B")
    assert "KAPPA" not in format_history_round(private, "B")


def test_all_150_decision_rounds_retain_the_full_prior_history_and_memories():
    template = {
        "actions": [make_bid_action(2.00), make_no_bid_action()],
        "quantities": [100, 0], "gross_market_profits": [100, 0],
        "participation_costs": [16, 0], "pattern_fines": [0, 0],
        "net_profits": [84, 0],
    }
    history = [{
        "round": number, **template,
        "signal_record": {
            "public_signal": None,
            "private_signals": {"A": "KAPPA", "B": "LAMBDA"}
            if number >= 71 else {"A": None, "B": None},
        },
    } for number in range(1, 150)]
    for current_round in range(1, 151):
        prior = history[:current_round - 1]
        rendered = format_market_history(prior, "A", current_round=current_round)
        assert rendered == format_market_history(
            prior, "A", max_rounds=200, current_round=current_round
        )
        rows = rendered.splitlines()[1:]
        if current_round == 1:
            assert rows == ["(no completed rounds yet)"]
        else:
            assert [int(row.split(" |", 1)[0][1:]) for row in rows] == list(
                range(current_round - 1, 0, -1)
            )
        assert "private:LAMBDA" not in rendered
    prompt = make_market_decision_prompt(
        round_number=150, seller_label="A", prior_communication=False,
        signal_state=schedule("private"), plans="KEEP PLAN", insights="KEEP INSIGHT",
        history=history, regulator_state=make_initial_regulator_state(),
    )["prompt"]
    assert format_market_history(history, "A", current_round=150) in prompt
    assert make_memory_block("KEEP PLAN", "KEEP INSIGHT") in prompt


def test_regulator_blindness_disclosures_follow_channel_and_signal_timing():
    assert "does not observe, read, or use messages" in market_prompt(50, True, "none")["researcher_authored_text"]
    assert "does not observe, read, or use messages" not in market_prompt(51, True, "none")["researcher_authored_text"]
    assert "does not observe, read, or use messages" not in market_prompt(50, False, "none")["researcher_authored_text"]
    assert make_code_blindness_block(schedule("public"), 70) is None
    assert make_code_blindness_block(schedule("private"), 70) is None
    assert "does not observe or use public-code values" in market_prompt(71, False, "public")["researcher_authored_text"]
    assert "does not observe or use your private-code value" in market_prompt(71, False, "private")["researcher_authored_text"]


def test_private_current_bulletins_expose_only_own_distinct_draw():
    private = schedule("private")
    own_a = private["rounds"][71]["private_signals"]["A"]
    own_b = private["rounds"][71]["private_signals"]["B"]
    assert own_a != own_b, "test seeds must give distinct first-round private draws"
    block_a = make_signal_prompt_block(private, 71, "A")
    block_b = make_signal_prompt_block(private, 71, "B")
    assert block_a.count("Code:") == block_b.count("Code:") == 1
    assert f"Code: {own_a}" in block_a and f"Code: {own_b}" not in block_a
    assert f"Code: {own_b}" in block_b and f"Code: {own_a}" not in block_b
    for label, own, rival in (("A", own_a, own_b), ("B", own_b, own_a)):
        rendered = make_market_decision_prompt(
            round_number=71, seller_label=label, prior_communication=False,
            signal_state=private, plans="", insights="", history=[],
            regulator_state=make_initial_regulator_state(),
        )
        assert f"Code: {own}" in rendered["prompt"]
        assert f"Code: {rival}" not in rendered["researcher_authored_text"]


@pytest.mark.parametrize("prior", [False, True])
def test_every_presignal_round_is_independent_of_future_signal_assignment(prior):
    schedules = {condition: schedule(condition) for condition in ("none", "public", "private")}
    for round_number in range(1, 71):
        texts = []
        for condition in ("none", "public", "private"):
            rendered = make_market_decision_prompt(
                round_number=round_number, seller_label="A", prior_communication=prior,
                signal_state=schedules[condition], plans="", insights="", history=[],
                regulator_state=make_initial_regulator_state(),
                communication_transcript_block=TRANSCRIPT if prior and round_number <= 50 else None,
            )
            authored = rendered["researcher_authored_text"]
            assert not LEAKAGE.search(authored), f"future signal leaked in round {round_number}"
            texts.append(authored)
        assert texts[0] == texts[1] == texts[2], f"future signal assignment changed round {round_number} text"


@pytest.mark.parametrize("prior", [False, True])
def test_every_no_signal_round_remains_signal_free(prior):
    no_signal = schedule("none")
    for round_number in range(1, 151):
        rendered = make_market_decision_prompt(
            round_number=round_number, seller_label="A", prior_communication=prior,
            signal_state=no_signal, plans="", insights="", history=[],
            regulator_state=make_initial_regulator_state(),
            communication_transcript_block=TRANSCRIPT if prior and round_number <= 50 else None,
        )
        assert not LEAKAGE.search(rendered["researcher_authored_text"]), round_number


def test_communication_first_speaker_is_balanced_over_all_50_rounds():
    first_speakers = [communication_speaking_order(round_number)[0] for round_number in range(1, 51)]
    assert first_speakers.count("A") == first_speakers.count("B") == 25


@pytest.mark.parametrize("record", [
    ("comm_first", None, None, None), ("comm_second", None, None, None),
    ("market", 50, True, "none"), ("market", 51, True, "none"),
    ("market", 51, False, "none"), ("market", 70, True, "public"),
    ("market", 71, False, "none"), ("market", 71, False, "public"),
    ("market", 71, False, "private"), ("market", 72, False, "public"),
])
def test_prompt_snapshot(record):
    kind, round_number, prior, condition = record
    rendered = communication_prompt(kind.removeprefix("comm_")) if kind.startswith("comm_") else market_prompt(round_number, prior, condition)
    digest = hashlib.sha256(rendered["prompt"].encode()).hexdigest()
    assert digest == SNAPSHOTS[record]


SNAPSHOTS = {
    ('comm_first', None, None, None): "93737c0651fb78b255a096d198e5e6bc77535178f0cbcc73c75ce4ff04c1e12d",
    ('comm_second', None, None, None): "a191c71da75e2128a88bb50a5abcd827af2dc32af554da0f0d01e3b88828e821",
    ('market', 50, True, 'none'): "02cfde7dd29817948027ab5ae7129477dc21ba5f9d35291c53b3adc6bacd9c37",
    ('market', 51, True, 'none'): "e6617c09b00d5eba3d7f6b9a3ac201869cf46ddf850de6368757b493d8ea5314",
    ('market', 51, False, 'none'): "2dce964b57de25d20f3aa0bcf12bb601d0be0d2f8ffca4b4909543e6bb1fa8f4",
    ('market', 70, True, 'public'): "2dce964b57de25d20f3aa0bcf12bb601d0be0d2f8ffca4b4909543e6bb1fa8f4",
    ('market', 71, False, 'none'): "2dce964b57de25d20f3aa0bcf12bb601d0be0d2f8ffca4b4909543e6bb1fa8f4",
    ('market', 71, False, 'public'): "775635b636cbcaa66a1fa7ba577276628c5bcdb73bbda651ca5aee5d85d6f58f",
    ('market', 71, False, 'private'): "09dfd3237e6cedfcaa6c48054a0eb4ed8b801514dbdb64b5bea48ba5986125c8",
    ('market', 72, False, 'public'): "8ef501347a4cf6c33147d454fe756214a763791ae962d20b6dc422dfdd0a4bc0",
}
