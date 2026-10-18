"""Researcher-facing episode text. Scientific records remain in rounds.jsonl."""

from pathlib import Path
import sys
from typing import TextIO

from .config import ExperimentConfig

PRINT_EVERY = 1


def format_round_header(round_number: int, num_rounds: int) -> str:
    width = len(str(num_rounds))
    return f"Round {round_number:>{width}}/{num_rounds}:\n"


def format_phase_banner(round_number: int, *, prior_communication: bool,
                        signal_condition: str, config: ExperimentConfig) -> str | None:
    if round_number == 1:
        detail = ("The communication channel is available." if prior_communication else
                  "No communication channel is available in this treatment.")
        return f"Beginning of Phase 1. {detail}\n\n"
    if round_number == config.communication_end_round + 1:
        detail = ("The communication channel will be turned off now." if prior_communication else
                  "No communication channel is available in this treatment.")
        return f"\nBeginning of Phase 2. {detail}\n\n"
    if round_number == config.signal_start_round:
        detail = {"public": "The public sunspot will appear now.",
                  "private": "The private signals will appear now.",
                  "none": "No signal will appear in this treatment."}[signal_condition]
        return f"\nBeginning of Phase 3. {detail}\n\n"
    return None


def format_action(action: dict) -> str:
    return "NO BID" if action["action_type"] == "no_bid" else f"BID {action['price']:.2f}"


def format_communication(record: dict) -> str:
    if not record["communication"]["enabled"]:
        return ""
    return "".join(
        f" Message {call['speaker']} -> {call['recipient']}:\n"
        f"{call['result']['message']}\n"
        for call in record["communication"]["calls"]
    )


def format_result_summary(record: dict) -> str:
    actions = record["actions"]
    fines = record["pattern_fines"]
    net = record["net_profits"]
    cumulative = record["cumulative_net_profits"]
    return (f" A={format_action(actions[0])}, B={format_action(actions[1])}, "
            f"fine=({fines[0]:.2f}, {fines[1]:.2f}), "
            f"net=({net[0]:.2f}, {net[1]:.2f}), "
            f"cum=({cumulative[0]:.2f}, {cumulative[1]:.2f})\n")


def format_provenance(*, episode_id: str | None, run_name: str,
                      prior_communication: bool, signal_condition: str,
                      config: ExperimentConfig, metadata: dict | None) -> str:
    lines = []
    if episode_id is not None:
        lines.append(f"Episode ID: {episode_id}")
    lines.append(f"Run name: {run_name}")
    if metadata:
        if metadata.get("block_id") is not None:
            lines.append(f"Block: {metadata['block_id']}")
        if metadata.get("sequence_position") is not None:
            lines.append(f"Manifest position: {metadata['sequence_position']}")
    lines.extend((
        f"Treatment: prior_communication={prior_communication}, signal_condition={signal_condition}",
        f"Specification: {config.specification_version}",
        f"Prompt family: {config.prompt_family}",
        f"Prompt version: {config.prompt_version}",
    ))
    if metadata and metadata.get("manifest_payload_sha256") is not None:
        lines.append(f"Manifest SHA-256: {metadata['manifest_payload_sha256']}")
    return "\n".join(lines) + "\n\n"


class EpisodeTranscript:
    """Mirror round text to stdout and a flushed convenience file.

    Opening and writing provenance fail before model calls. Once execution
    starts, text-file failures warn and disable only this convenience file.
    """

    def __init__(self, path: Path, header: str):
        self.path = path
        self._file: TextIO | None = None
        self._console_enabled = True
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = path.open("x", encoding="utf-8", newline="\n")
        try:
            handle.write(header)
            handle.flush()
        except OSError:
            handle.close()
            path.unlink(missing_ok=True)
            raise
        self._file = handle

    def emit(self, value: str) -> None:
        if self._console_enabled:
            try:
                print(value, end="", flush=True)
            except OSError:
                self._console_enabled = False
        if self._file is not None:
            try:
                self._file.write(value)
                self._file.flush()
            except OSError as error:
                print(f"Execution transcript write failed ({type(error).__name__}); "
                      "rounds.jsonl remains authoritative.", file=sys.stderr, flush=True)
                try:
                    self._file.close()
                except OSError:
                    pass
                self._file = None

    def close(self) -> None:
        if self._file is not None:
            try:
                self._file.close()
            except OSError as error:
                print(f"Execution transcript close failed ({type(error).__name__}); "
                      "rounds.jsonl remains authoritative.", file=sys.stderr, flush=True)
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
