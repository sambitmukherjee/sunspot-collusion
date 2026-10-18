"""Offline checks for researcher-facing episode text."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from collusion_experiment.config import ExperimentConfig
from collusion_experiment.episode import run_episode
from collusion_experiment.episode_transcript import (
    EpisodeTranscript, format_action, format_phase_banner, format_result_summary,
    format_round_header,
)
from structured_helpers import communication_result, market_result


SHORT = ExperimentConfig(num_rounds=4, communication_end_round=2,
                         signal_start_round=4, pattern_window=2, pattern_max_period=2)


def fake_communication(*, prompt, seller_label, recipient_label, speaker_position):
    return communication_result(prompt=prompt,
                                message=f"{seller_label} line one\n{seller_label} line two",
                                config=SHORT)


def fake_market(*, prompt, seller_label):
    action = "1.95" if seller_label == "A" else "NO BID"
    return market_result(prompt=prompt, action=action, observations="obs",
                         plans="plan", insights="insight", config=SHORT)


def invoke(tmp_path, *, prior_communication=True, signal_condition="public",
           market_caller=fake_market, print_every=1, metadata=None,
           execution_log_dir=None):
    return run_episode(
        replicate_id=1, prior_communication=prior_communication,
        signal_condition=signal_condition, save_dir=tmp_path,
        run_name="offline", public_signal_seed=2,
        market_decision_caller=market_caller,
        communication_agent_caller=fake_communication if prior_communication else None,
        config=SHORT, development_mode=True, print_every=print_every,
        execution_log_dir=execution_log_dir or tmp_path / "execution_logs",
        transcript_metadata=metadata,
    )


def test_round_order_banners_provenance_and_identical_console_file(tmp_path, capsys):
    metadata = {"episode_id": "block_01__test", "block_id": "block_01",
                "sequence_position": 1, "manifest_payload_sha256": "abc123"}
    result = invoke(tmp_path, metadata=metadata)
    console = capsys.readouterr().out
    path = tmp_path / "execution_logs" / SHORT.specification_version / "episodes" / "block_01__test.txt"
    transcript = path.read_text()
    header, round_text = transcript.split("\n\n", 1)
    assert "Episode ID: block_01__test" in header
    assert "Run name: offline" in header
    assert "Block: block_01" in header
    assert "Manifest position: 1" in header
    assert "Treatment: prior_communication=True, signal_condition=public" in header
    assert f"Specification: {SHORT.specification_version}" in header
    assert f"Prompt family: {SHORT.prompt_family}" in header
    assert f"Prompt version: {SHORT.prompt_version}" in header
    assert "Manifest SHA-256: abc123" in header
    assert console == round_text
    assert round_text.startswith("Beginning of Phase 1. The communication channel is available.\n\nRound 1/4:")
    assert round_text.count("Beginning of Phase 1.") == 1
    assert round_text.count("Beginning of Phase 2.") == 1
    assert round_text.count("Beginning of Phase 3.") == 1
    assert "\nBeginning of Phase 2. The communication channel will be turned off now.\n\nRound 3/4:" in round_text
    assert "\nBeginning of Phase 3. The public sunspot will appear now.\n\nRound 4/4:" in round_text
    odd = round_text.split("Round 1/4:\n", 1)[1].split("Round 2/4:\n", 1)[0]
    even = round_text.split("Round 2/4:\n", 1)[1].split("Beginning of Phase 2.", 1)[0]
    assert odd.index(" Message A -> B:\nA line one\nA line two") < odd.index(" Message B -> A:\nB line one\nB line two")
    assert even.index(" Message B -> A:\nB line one\nB line two") < even.index(" Message A -> B:\nA line one\nA line two")
    assert odd.index(" Message B -> A:") < odd.index(" A=BID 1.95, B=NO BID, fine=(")
    assert even.index(" Message A -> B:") < even.index(" A=BID 1.95, B=NO BID, fine=(")
    assert "Message" not in round_text.split("Round 3/4:\n", 1)[1]
    records = [json.loads(line) for line in (Path(result["run_dir"]) / "rounds.jsonl").read_text().splitlines()]
    assert round_text.count("Public signal:") == 1
    assert f"Round 4/4:\nPublic signal: {records[3]['signal_record']['public_signal']}\n" in round_text
    for record in records:
        assert format_result_summary(record) in round_text


@pytest.mark.parametrize("prior,phase1,phase2", [
    (True, "The communication channel is available.", "The communication channel will be turned off now."),
    (False, "No communication channel is available in this treatment.",
     "No communication channel is available in this treatment."),
])
def test_phase_1_and_2_banner_variants(prior, phase1, phase2):
    assert format_phase_banner(1, prior_communication=prior, signal_condition="none", config=SHORT) == f"Beginning of Phase 1. {phase1}\n\n"
    assert format_phase_banner(3, prior_communication=prior, signal_condition="none", config=SHORT) == f"\nBeginning of Phase 2. {phase2}\n\n"


@pytest.mark.parametrize("signal,detail", [
    ("public", "The public sunspot will appear now."),
    ("private", "The private signals will appear now."),
    ("none", "No signal will appear in this treatment."),
])
def test_phase_3_banner_variants_and_frozen_transition(signal, detail):
    assert format_phase_banner(4, prior_communication=True, signal_condition=signal, config=SHORT) == f"\nBeginning of Phase 3. {detail}\n\n"
    frozen = ExperimentConfig()
    assert format_phase_banner(50, prior_communication=True, signal_condition=signal, config=frozen) is None
    assert format_phase_banner(51, prior_communication=True, signal_condition=signal, config=frozen).startswith("\nBeginning of Phase 2.")
    assert format_phase_banner(71, prior_communication=True, signal_condition=signal, config=frozen).startswith("\nBeginning of Phase 3.")
    assert format_round_header(1, 150) == "Round   1/150:\n"
    assert format_round_header(10, 150) == "Round  10/150:\n"
    assert format_round_header(150, 150) == "Round 150/150:\n"


def test_formatting_reads_values_without_mutating_record():
    record = {"actions": [{"action_type": "bid", "price": 2.0},
                          {"action_type": "no_bid", "price": None}],
              "pattern_fines": [8.0, 8.0], "net_profits": [71.0, -8.0],
              "cumulative_net_profits": [158.0, 80.0]}
    before = deepcopy(record)
    assert format_action(record["actions"][0]) == "BID 2.00"
    assert format_result_summary(record) == (
        " A=BID 2.00, B=NO BID, fine=(8.00, 8.00), "
        "net=(71.00, -8.00), cum=(158.00, 80.00)\n"
    )
    assert record == before


def test_failed_round_has_marker_without_uncommitted_result(tmp_path, capsys):
    def fail_on_b(*, prompt, seller_label):
        if seller_label == "B":
            raise RuntimeError("model failed")
        return fake_market(prompt=prompt, seller_label=seller_label)
    with pytest.raises(RuntimeError, match="model failed"):
        invoke(tmp_path, market_caller=fail_on_b)
    console = capsys.readouterr().out
    text = (tmp_path / "execution_logs" / SHORT.specification_version / "episodes" / "offline.txt").read_text()
    assert "Round 1/4:\n ROUND FAILED: RuntimeError\n Last scientifically committed round: 0\n" in console
    assert " A=BID" not in console
    assert console in text
    assert (tmp_path / SHORT.specification_version / "runs" / "offline" / "rounds.jsonl").read_text() == ""


def test_unwritable_log_fails_before_any_caller(tmp_path):
    calls = []
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory")
    def counted_market(**kwargs):
        calls.append(kwargs)
        return fake_market(**kwargs)
    with pytest.raises(OSError):
        invoke(tmp_path, market_caller=counted_market, execution_log_dir=blocked)
    assert calls == []
    assert not (tmp_path / SHORT.specification_version / "runs" / "offline").exists()


def test_late_log_write_failure_does_not_change_scientific_commit(tmp_path, monkeypatch, capsys):
    original_init = EpisodeTranscript.__init__
    class BrokenFile:
        def write(self, _):
            raise OSError("disk full")
        def flush(self):
            pass
        def close(self):
            pass
    def broken_init(self, path, header):
        original_init(self, path, header)
        self._file.close()
        self._file = BrokenFile()
    monkeypatch.setattr(EpisodeTranscript, "__init__", broken_init)
    result = invoke(tmp_path)
    assert result["last_completed_round"] == 4
    lines = (Path(result["run_dir"]) / "rounds.jsonl").read_text().splitlines()
    assert len(lines) == 4
    assert "Execution transcript write failed" in capsys.readouterr().err


def test_print_every_is_fixed_to_one_and_banners_do_not_enter_prompts(tmp_path):
    prompts = []
    def captured_market(**kwargs):
        prompts.append(kwargs["prompt"])
        return fake_market(**kwargs)
    def captured_communication(**kwargs):
        prompts.append(kwargs["prompt"])
        return fake_communication(**kwargs)
    with pytest.raises(ValueError, match="fixed at 1"):
        invoke(tmp_path, print_every=2)
    assert not (tmp_path / SHORT.specification_version / "runs").exists()
    run_episode(replicate_id=1, prior_communication=True, signal_condition="none",
                save_dir=tmp_path, run_name="checked",
                market_decision_caller=captured_market,
                communication_agent_caller=captured_communication,
                config=SHORT, development_mode=True,
                execution_log_dir=tmp_path / "logs")
    assert prompts and all("Beginning of Phase" not in prompt for prompt in prompts)
