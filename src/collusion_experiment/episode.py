"""Communication, simultaneous market rounds, and the durable episode runner."""

import copy
import sys
import traceback
from contextlib import nullcontext
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .api import APICallFailure, AgentParseFailure, AgentResponseFailure, call_agent_communication, call_agent_market_decision, require_usable_agent_response
from .config import ExperimentConfig, analytical_stage, communication_is_enabled, resolve_config
from .market import deterministic_market_outcome, validate_market_action
from .structured_outputs import (
    CONTRACT_VERSION, RESPONSE_FORMAT_BY_CALL, decode_structured_response,
    render_market_response, schema_hash, schema_provenance,
)
from .prompts import (
    communication_speaking_order, make_current_communication_transcript_block,
    make_first_speaker_communication_prompt, make_market_decision_prompt,
    make_second_speaker_communication_prompt, validate_communication_round,
)
from .regulator import apply_pattern_regulator, make_initial_regulator_state, validate_regulator_state
from .signals import (
    get_research_signal_record, get_signal_view_for_seller, make_signal_schedule,
    signal_schedule_hash, validate_signal_condition,
)
from . import storage
from .episode_transcript import (
    EpisodeTranscript, PRINT_EVERY, format_communication, format_phase_banner,
    format_provenance, format_result_summary, format_round_header,
)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_replicate_id(replicate_id: int) -> int:
    if isinstance(replicate_id, bool) or not isinstance(replicate_id, int):
        raise TypeError("replicate_id must be an integer, not bool.")
    if replicate_id < 1:
        raise ValueError("replicate_id must be >= 1.")
    return replicate_id


def validate_seller_memories(memories: dict, config: ExperimentConfig) -> dict:
    if not isinstance(memories, dict) or set(memories) != set(config.seller_labels):
        raise ValueError("Memories must contain exactly the configured sellers.")
    result = copy.deepcopy(memories)
    for label in config.seller_labels:
        if not isinstance(result[label], dict) or set(result[label]) != {"plans", "insights"}:
            raise ValueError("Each seller memory must contain exactly plans and insights.")
        if not all(isinstance(result[label][key], str) for key in ("plans", "insights")):
            raise TypeError("PLANS and INSIGHTS contents must be strings.")
    return result


def result_without_duplicate_prompt(result: dict, expected_prompt: str) -> dict:
    if not isinstance(result, dict):
        raise TypeError("Agent caller must return a dictionary.")
    result = copy.deepcopy(result)
    if "prompt" in result:
        if result["prompt"] != expected_prompt:
            raise ValueError("Agent result prompt differs from the supplied prompt.")
        result.pop("prompt")
    return result


def validate_communication_agent_result(result: dict, expected_recipient_label: str,
                                        config: ExperimentConfig | None = None) -> str:
    config = resolve_config(config)
    if not isinstance(result, dict) or not isinstance(result.get("message"), str) or not result["message"].strip():
        raise ValueError("Communication result must contain a nonempty parsed message.")
    if not isinstance(result.get("raw_response"), str):
        raise TypeError("Communication raw_response must be a string.")
    _validate_result_contract(result, "communication")
    parsed = decode_structured_response(result["raw_response"], "communication", config)
    if result["message"] != parsed["message"]:
        raise ValueError("Parsed communication message differs from raw response body.")
    return result["message"]


def _validate_result_contract(result: dict, call_type: str) -> None:
    expected = RESPONSE_FORMAT_BY_CALL[call_type]
    if (result.get("call_type") != call_type or
            result.get("response_contract_version") != CONTRACT_VERSION or
            result.get("schema_name") != expected["json_schema"]["name"] or
            result.get("schema_sha256") != schema_hash(expected) or
            result.get("response_format") != expected):
        raise ValueError("Agent result has mismatched structured contract metadata.")
    require_usable_agent_response(result)


def validate_market_agent_result(result: dict, config: ExperimentConfig | None = None) -> dict:
    config = resolve_config(config)
    if not isinstance(result, dict):
        raise TypeError("Market caller must return a dictionary.")
    for field in ("observations", "plans", "insights", "action", "raw_response"):
        if field not in result:
            raise ValueError(f"Market result is missing {field!r}.")
    for field in ("observations", "plans", "insights"):
        if not isinstance(result[field], str):
            raise TypeError(f"Parsed {field} must be a string.")
    if not isinstance(result["raw_response"], str):
        raise TypeError("Market raw_response must be a string.")
    canonical = validate_market_action(result["action"], config)
    _validate_result_contract(result, "market_decision")
    parsed = decode_structured_response(result["raw_response"], "market_decision", config)
    if result.get("chosen_action") != parsed["chosen_action"]:
        raise ValueError("Parsed chosen_action differs from raw market response.")
    for field in ("observations", "plans", "insights"):
        if result[field] != parsed[field]:
            raise ValueError(f"Parsed {field} differs from raw market response.")
    if canonical != parsed["action"]:
        raise ValueError("Parsed market action differs from raw response.")
    return canonical


def _log_success(call_log: list[dict] | None, *, call_type: str, seller_label: str,
                 prompt: str, result: Any, **extra: Any) -> None:
    if call_log is not None:
        call_log.append({"call_type": call_type, "seller_label": seller_label,
                         "prompt": prompt, "result": copy.deepcopy(result), **extra})


def execute_communication_stage(
    *, round_number: int, prior_communication: bool, seller_memories: dict,
    history: list[dict], regulator_state: dict, communication_agent_caller: Callable,
    config: ExperimentConfig | None = None, execution_trace: list[str] | None = None,
    call_log: list[dict] | None = None,
) -> dict:
    """Complete two messages and return their exact shared transcript."""
    config = resolve_config(config)
    validate_communication_round(round_number, prior_communication, config)
    if not callable(communication_agent_caller):
        raise TypeError("communication_agent_caller must be callable.")
    memories = validate_seller_memories(seller_memories, config)
    history = copy.deepcopy(history)
    regulator_state = validate_regulator_state(regulator_state, config)
    first, second = communication_speaking_order(round_number, config)
    first_prompt = make_first_speaker_communication_prompt(
        round_number=round_number, seller_label=first, prior_communication=prior_communication,
        plans=memories[first]["plans"], insights=memories[first]["insights"],
        history=history, regulator_state=regulator_state, config=config,
    )
    if execution_trace is not None:
        execution_trace.append("communication_first_prompt_constructed")
    first_result = communication_agent_caller(
        prompt=first_prompt["prompt"], seller_label=first, recipient_label=second, speaker_position="first"
    )
    _log_success(call_log, call_type="communication", seller_label=first,
                 prompt=first_prompt["prompt"], result=first_result, recipient_label=second, speaker_position="first")
    first_message = validate_communication_agent_result(first_result, second, config)
    result_without_duplicate_prompt(first_result, first_prompt["prompt"])
    if execution_trace is not None:
        execution_trace.append(f"communication_call_{first}")
    second_prompt = make_second_speaker_communication_prompt(
        round_number=round_number, seller_label=second, first_speaker_label=first,
        first_message=first_message, prior_communication=prior_communication,
        plans=memories[second]["plans"], insights=memories[second]["insights"],
        history=history, regulator_state=regulator_state, config=config,
    )
    if execution_trace is not None:
        execution_trace.append("communication_second_prompt_constructed")
    second_result = communication_agent_caller(
        prompt=second_prompt["prompt"], seller_label=second, recipient_label=first, speaker_position="second"
    )
    _log_success(call_log, call_type="communication", seller_label=second,
                 prompt=second_prompt["prompt"], result=second_result, recipient_label=first, speaker_position="second")
    second_message = validate_communication_agent_result(second_result, first, config)
    result_without_duplicate_prompt(second_result, second_prompt["prompt"])
    if execution_trace is not None:
        execution_trace.append(f"communication_call_{second}")
    transcript = make_current_communication_transcript_block(first, first_message, second, second_message, config)
    if execution_trace is not None:
        execution_trace.append("communication_complete")
    return {
        "enabled": True, "first_speaker": first, "second_speaker": second,
        "first_message": first_message, "second_message": second_message,
        "transcript_block": transcript,
        "calls": [
            {"speaker": first, "recipient": second, "speaker_position": "first",
             **first_prompt, "result": result_without_duplicate_prompt(first_result, first_prompt["prompt"])},
            {"speaker": second, "recipient": first, "speaker_position": "second",
             **second_prompt, "result": result_without_duplicate_prompt(second_result, second_prompt["prompt"])},
        ],
    }


def execute_round(
    *, round_number: int, prior_communication: bool, signal_state: dict,
    seller_memories: dict, history: list[dict], regulator_state: dict,
    market_decision_caller: Callable, communication_agent_caller: Callable | None = None,
    config: ExperimentConfig | None = None, execution_trace: list[str] | None = None,
    call_log: list[dict] | None = None,
) -> dict:
    """Execute a round in local state; the caller decides whether to commit it."""
    config = resolve_config(config)
    analytical_stage(round_number, config)
    if not isinstance(prior_communication, bool):
        raise TypeError("prior_communication must be bool.")
    if not callable(market_decision_caller):
        raise TypeError("market_decision_caller must be callable.")
    memory_before = validate_seller_memories(seller_memories, config)
    history_before = copy.deepcopy(history)
    regulator_before = validate_regulator_state(regulator_state, config)
    if any(item["round"] >= round_number for item in history_before):
        raise ValueError("History must contain only prior completed rounds.")
    started_at = utc_timestamp()
    if execution_trace is not None:
        execution_trace.append("pre_round_state_captured")
    signal_record = get_research_signal_record(signal_state, round_number)
    signal_views = {
        label: get_signal_view_for_seller(signal_state, round_number, label, config)
        for label in config.seller_labels
    }
    communication = {"enabled": False, "calls": [], "transcript_block": None,
                     "first_speaker": None, "second_speaker": None,
                     "first_message": None, "second_message": None}
    if communication_is_enabled(prior_communication, round_number, config):
        if communication_agent_caller is None:
            raise ValueError("A communication caller is required in this round.")
        communication = execute_communication_stage(
            round_number=round_number, prior_communication=prior_communication,
            seller_memories=memory_before, history=history_before, regulator_state=regulator_before,
            communication_agent_caller=communication_agent_caller, config=config,
            execution_trace=execution_trace, call_log=call_log,
        )
    prompts = {}
    for label in config.seller_labels:
        prompts[label] = make_market_decision_prompt(
            round_number=round_number, seller_label=label, prior_communication=prior_communication,
            signal_state=signal_state, plans=memory_before[label]["plans"],
            insights=memory_before[label]["insights"], history=history_before,
            regulator_state=regulator_before, communication_transcript_block=communication["transcript_block"],
            config=config,
        )
        if execution_trace is not None:
            execution_trace.append(f"market_prompt_{label}_constructed")
    decisions = {}
    for label in config.seller_labels:
        prompt = prompts[label]["prompt"]
        result = market_decision_caller(prompt=prompt, seller_label=label)
        _log_success(call_log, call_type="market_decision", seller_label=label, prompt=prompt, result=result)
        action = validate_market_agent_result(result, config)
        decisions[label] = {
            **prompts[label], "result": result_without_duplicate_prompt(result, prompt),
            "action": action,
        }
        if execution_trace is not None:
            execution_trace.append(f"market_call_{label}")
    actions = [decisions[label]["action"] for label in config.seller_labels]
    market = deterministic_market_outcome(actions, config)
    if execution_trace is not None:
        execution_trace.append("market_resolved")
    regulator = apply_pattern_regulator(
        actions=market["actions"], pre_regulator_net_profits=market["pre_regulator_net_profits"],
        regulator_state=regulator_before, config=config,
    )
    if execution_trace is not None:
        execution_trace.append("regulator_applied")
    memory_after = {label: {"plans": decisions[label]["result"]["plans"],
                            "insights": decisions[label]["result"]["insights"]}
                    for label in config.seller_labels}
    if execution_trace is not None:
        execution_trace.append("memory_updated")
    record = {
        "round": round_number, "round_number": round_number,
        "analytical_stage": analytical_stage(round_number, config),
        "timestamps": {"started_at_utc": started_at, "completed_at_utc": utc_timestamp()},
        "treatment": {"prior_communication": prior_communication,
                      "signal_condition": signal_state["signal_condition"]},
        "signal": {"researcher_record": copy.deepcopy(signal_record),
                   "seller_views": copy.deepcopy(signal_views)},
        "signal_record": copy.deepcopy(signal_record),
        "communication": communication,
        "memory_before": memory_before,
        "market_decisions": decisions,
        "market_outcome": market,
        "regulator": regulator,
        "memory_after": copy.deepcopy(memory_after),
        # Flat completed-round fields are the compact market-history input.
        "actions": copy.deepcopy(market["actions"]),
        "quantities": list(market["quantities"]),
        "gross_market_profits": list(market["gross_market_profits"]),
        "participation_costs": list(market["participation_costs"]),
        "pattern_fines": list(regulator["pattern_fines"]),
        "net_profits": list(regulator["final_net_profits"]),
    }
    return {"round_record": record, "memory_after": memory_after,
            "regulator_state_after": regulator["regulator_state"]}


USAGE_FIELDS = ("prompt_tokens", "cached_tokens", "cache_write_tokens",
                "completion_tokens", "reasoning_tokens", "total_tokens")


def empty_usage() -> dict:
    return {"agent_calls_completed": 0, "communication_calls_completed": 0,
            "market_decision_calls_completed": 0, "api_calls_completed": 0,
            "api_requests_total": 0, "technical_retry_count": 0,
            **{field: 0 for field in USAGE_FIELDS}}


def add_usage_summaries(cumulative: dict, increment: dict) -> dict:
    return {key: int(cumulative[key]) + int(increment[key]) for key in cumulative}


def summarize_call_usage(calls: list[dict]) -> dict:
    summary = empty_usage()
    for call in calls:
        result = call.get("result")
        if not isinstance(result, dict):
            continue
        summary["agent_calls_completed"] += 1
        summary["communication_calls_completed" if call["call_type"] == "communication"
                else "market_decision_calls_completed"] += 1
        usage = result.get("usage") or {}
        for field in USAGE_FIELDS:
            summary[field] += int(usage.get(field, 0) or 0)
        if "requested_model" in result:
            summary["api_calls_completed"] += 1
            attempts = int(result.get("attempt_count", 1))
            summary["api_requests_total"] += attempts
            summary["technical_retry_count"] += max(0, attempts - 1)
    return summary


def serialize_failure_context(error: Exception) -> dict:
    context = {"exception_type": type(error).__name__, "message": str(error),
               "repr": repr(error), "traceback": traceback.format_exc(),
               "timestamp_utc": utc_timestamp()}
    if isinstance(error, APICallFailure):
        context.update(failing_prompt=error.prompt, technical_failures=copy.deepcopy(error.failures))
    if isinstance(error, (AgentParseFailure, AgentResponseFailure)):
        context["api_result"] = copy.deepcopy(error.api_result)
    return context


def build_episode_config(
    *, config: ExperimentConfig, replicate_id: int, prior_communication: bool,
    signal_state: dict, run_name: str, development_mode: bool,
) -> dict:
    value = asdict(config)
    value["response_contract_version"] = config.response_contract_version
    value["prompt_caching_policy"] = "provider_default"
    value["structured_response_schemas"] = schema_provenance()
    value.update({
        "replicate_id": replicate_id, "prior_communication": prior_communication,
        "signal_condition": signal_state["signal_condition"], "run_name": run_name,
        "development_mode": development_mode, "designation": "development" if development_mode else "confirmatory",
        "signal_seeds": {
            key: signal_state[key] for key in ("public_signal_seed", "private_signal_seed_A", "private_signal_seed_B")
        },
        "signal_schedule_hash": signal_schedule_hash(signal_state),
        "started_at_utc": utc_timestamp(),
        "artifact_filenames": {
            "config": storage.CONFIG_FILENAME, "rounds": storage.ROUNDS_FILENAME,
            "state_checkpoint": storage.CHECKPOINT_FILENAME,
            "failure": storage.FAILURE_FILENAME, "final_episode": storage.FINAL_FILENAME,
        },
    })
    return value


def make_checkpoint(
    *, status: str, last_completed_round: int, seller_memories: dict,
    regulator_state: dict, cumulative_net_profits: list[float], cumulative_usage: dict,
    signal_schedule_hash_value: str, run_name: str, replicate_id: int,
    config: ExperimentConfig, error: dict | None = None,
) -> dict:
    return {
        "status": status, "last_completed_round": last_completed_round,
        "next_round": last_completed_round + 1 if last_completed_round < config.num_rounds else None,
        "seller_memories": copy.deepcopy(seller_memories),
        "regulator_state": copy.deepcopy(regulator_state),
        "cumulative_net_profits": list(cumulative_net_profits),
        "joint_cumulative_net_profit": float(sum(cumulative_net_profits)),
        "cumulative_usage": copy.deepcopy(cumulative_usage),
        "signal_schedule_hash": signal_schedule_hash_value,
        "run_name": run_name, "replicate_id": replicate_id,
        "error": copy.deepcopy(error), "checkpointed_at_utc": utc_timestamp(),
    }


def run_episode(
    *, replicate_id: int, prior_communication: bool, signal_condition: str,
    save_dir: str | Path, run_name: str | None = None,
    public_signal_seed: int | None = None, private_signal_seed_A: int | None = None,
    private_signal_seed_B: int | None = None,
    market_decision_caller: Callable | None = None,
    communication_agent_caller: Callable | None = None,
    client: Any = None, config: ExperimentConfig | None = None,
    development_mode: bool = False,
    print_every: int = PRINT_EVERY,
    execution_log_dir: str | Path | None = None,
    transcript_metadata: dict | None = None,
) -> dict:
    """Run one new episode; never auto-resume or hide a failed round.

    Inject task-specific fake callers for offline runs. With a supplied client,
    the default adapters use the structured API wrappers. No client is created.
    Every round is printed (print_every is fixed at 1) and mirrored to a
    convenience transcript. `save_dir` is the base results root; runs go in
    `<save_dir>/<specification_id>/runs/`. `execution_log_dir`, when supplied,
    is the base log root; transcripts go in `<execution_log_dir>/<specification_id>/episodes/`.
    A manifest caller supplies its exact episode ID.
    """
    config = resolve_config(config)
    validate_replicate_id(replicate_id)
    if not isinstance(prior_communication, bool):
        raise TypeError("prior_communication must be bool.")
    validate_signal_condition(signal_condition)
    if not isinstance(development_mode, bool):
        raise TypeError("development_mode must be bool.")
    if isinstance(print_every, bool) or print_every != PRINT_EVERY:
        raise ValueError("print_every is fixed at 1; every round is printed.")
    if transcript_metadata is not None and not isinstance(transcript_metadata, dict):
        raise TypeError("transcript_metadata must be a dictionary or None.")
    signal_state = make_signal_schedule(
        signal_condition, public_signal_seed, private_signal_seed_A, private_signal_seed_B, config
    )
    signal_hash = signal_schedule_hash(signal_state)
    if market_decision_caller is None:
        if client is None:
            raise ValueError("A market decision caller or client is required.")
        def market_decision_caller(*, prompt: str, seller_label: str) -> dict:
            return call_agent_market_decision(prompt=prompt, client=client, config=config)
    if prior_communication and communication_agent_caller is None:
        if client is None:
            raise ValueError("A communication caller or client is required.")
        def communication_agent_caller(*, prompt: str, seller_label: str,
                                       recipient_label: str, speaker_position: str) -> dict:
            return call_agent_communication(
                prompt=prompt, seller_label=seller_label, recipient_label=recipient_label,
                speaker_position=speaker_position, client=client, config=config,
            )
    if not callable(market_decision_caller):
        raise TypeError("market_decision_caller must be callable.")
    if prior_communication and not callable(communication_agent_caller):
        raise TypeError("communication_agent_caller must be callable.")
    if run_name is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_name = f"sunspot_priorcomm{int(prior_communication)}_{signal_condition}_rep{replicate_id:03d}_{stamp}"
    episode_id = transcript_metadata.get("episode_id") if transcript_metadata else None
    log_identifier = episode_id if episode_id is not None else run_name
    if (not isinstance(log_identifier, str) or not log_identifier or
            Path(log_identifier).name != log_identifier or
            "/" in log_identifier or "\\" in log_identifier or log_identifier in (".", "..")):
        raise ValueError("Transcript identifier must be one safe filename component.")
    log_root = Path(execution_log_dir) if execution_log_dir is not None else Path(save_dir) / "execution_logs"
    log_dir = storage.specification_namespace(log_root, config.specification_version) / "episodes"
    log_path = log_dir / f"{log_identifier}.txt"
    market_response_path = log_dir / f"{log_identifier}_market_responses.txt"
    if log_path.exists():
        raise FileExistsError(f"Episode transcript already exists: {log_path}")
    if market_response_path.exists():
        raise FileExistsError(f"Market response log already exists: {market_response_path}")
    transcript = EpisodeTranscript(log_path, format_provenance(
        episode_id=episode_id, run_name=run_name,
        prior_communication=prior_communication, signal_condition=signal_condition,
        config=config, metadata=transcript_metadata,
    ))
    market_response_file = None
    try:
        market_response_file = market_response_path.open("x", encoding="utf-8", newline="")
        run_dir = storage.create_run_directory(
            storage.specification_namespace(save_dir, config.specification_version) / "runs", run_name
        )
    except Exception:
        if market_response_file is not None:
            market_response_file.close()
            market_response_path.unlink(missing_ok=True)
        transcript.close()
        log_path.unlink(missing_ok=True)
        raise
    with transcript, (market_response_file if market_response_file is not None else nullcontext()):
        episode_config = build_episode_config(
            config=config, replicate_id=replicate_id, prior_communication=prior_communication,
            signal_state=signal_state, run_name=run_name, development_mode=development_mode,
        )
        storage.write_json_atomic(run_dir / storage.CONFIG_FILENAME, episode_config)
        storage.initialize_rounds_jsonl(run_dir / storage.ROUNDS_FILENAME)
        memories = {label: {"plans": "", "insights": ""} for label in config.seller_labels}
        regulator_state = make_initial_regulator_state()
        profits = [0.0] * len(config.seller_labels)
        usage = empty_usage()
        history: list[dict] = []
        last_completed_round = 0
        checkpoint_path = run_dir / storage.CHECKPOINT_FILENAME
        def checkpoint(status: str, error: dict | None = None) -> dict:
            return make_checkpoint(
                status=status, last_completed_round=last_completed_round,
                seller_memories=memories, regulator_state=regulator_state,
                cumulative_net_profits=profits, cumulative_usage=usage,
                signal_schedule_hash_value=signal_hash, run_name=run_name,
                replicate_id=replicate_id, config=config, error=error,
            )
        storage.write_json_atomic(checkpoint_path, checkpoint("running"))

        for round_number in range(1, config.num_rounds + 1):
            banner = format_phase_banner(
                round_number, prior_communication=prior_communication,
                signal_condition=signal_condition, config=config,
            )
            if banner is not None:
                transcript.emit(banner)
            transcript.emit(format_round_header(round_number, config.num_rounds))
            if signal_condition == "public" and round_number >= config.signal_start_round:
                public_signal = get_research_signal_record(signal_state, round_number)["public_signal"]
                transcript.emit(f"Public signal: {public_signal}\n")
            call_log: list[dict] = []
            append_succeeded = False
            attempted_record = None
            try:
                result = execute_round(
                    round_number=round_number, prior_communication=prior_communication,
                    signal_state=signal_state, seller_memories=memories, history=history,
                    regulator_state=regulator_state, market_decision_caller=market_decision_caller,
                    communication_agent_caller=communication_agent_caller, config=config,
                    call_log=call_log,
                )
                record = result["round_record"]
                attempted_record = record
                record["treatment"]["replicate_id"] = replicate_id
                round_usage = summarize_call_usage(call_log)
                next_usage = add_usage_summaries(usage, round_usage)
                next_profits = [profits[i] + record["net_profits"][i] for i in range(len(profits))]
                record["round_usage"] = round_usage
                record["cumulative_usage"] = copy.deepcopy(next_usage)
                record["cumulative_net_profits"] = list(next_profits)
                record["joint_cumulative_net_profit"] = float(sum(next_profits))
                # The append is the scientific commit point. Nothing above mutates
                # committed state; JSONL must be durable before the checkpoint moves.
                storage.append_jsonl(run_dir / storage.ROUNDS_FILENAME, record)
                append_succeeded = True
                if market_response_file is not None:
                    try:
                        for label in config.seller_labels:
                            market_response_file.write(
                                f"Round {round_number}, Seller {label}\n" +
                                render_market_response(record["market_decisions"][label]["result"]) + "\n\n"
                            )
                        market_response_file.flush()
                    except OSError as log_error:
                        print(f"Market response log write failed ({type(log_error).__name__}); "
                              "rounds.jsonl remains authoritative.", file=sys.stderr, flush=True)
                        market_response_file.close()
                        market_response_file = None
                transcript.emit(format_communication(record) + format_result_summary(record))
                memories = result["memory_after"]
                regulator_state = result["regulator_state_after"]
                profits = next_profits
                usage = next_usage
                history.append(record)
                last_completed_round = round_number
                storage.write_json_atomic(checkpoint_path, checkpoint("running"))
            except Exception as error:
                transcript.emit(
                    f" ROUND FAILED: {type(error).__name__}\n"
                    f" Last scientifically committed round: {round_number if append_succeeded else last_completed_round}\n"
                )
                context = serialize_failure_context(error)
                paid_calls = copy.deepcopy(call_log)
                if isinstance(error, (AgentParseFailure, AgentResponseFailure)):
                    paid_calls.append({"call_type": "failed_response", "seller_label": None,
                                       "prompt": error.api_result.get("prompt"), "result": copy.deepcopy(error.api_result)})
                if isinstance(error, (AgentParseFailure, AgentResponseFailure)) and call_log:
                    last_result = call_log[-1].get("result")
                    if last_result == error.api_result:
                        paid_calls.pop()
                failed_usage = empty_usage() if append_succeeded else summarize_call_usage(paid_calls)
                failure = {
                    "status": "failed", "failed_round": round_number,
                    "last_completed_round": last_completed_round,
                    "run_name": run_name, "replicate_id": replicate_id,
                    "treatment": {"prior_communication": prior_communication,
                                  "signal_condition": signal_condition},
                    "failure": context,
                    "completed_calls_in_failed_round": copy.deepcopy(call_log),
                    "paid_or_attempted_usage_in_failed_round": failed_usage,
                    "cumulative_usage_through_last_completed_round": copy.deepcopy(usage),
                    "seller_memories_at_last_completed_round": copy.deepcopy(memories),
                    "regulator_state_at_last_completed_round": copy.deepcopy(regulator_state),
                    "cumulative_net_profits_through_last_completed_round": list(profits),
                    "jsonl_append_succeeded": append_succeeded,
                    "round_scientifically_committed": append_succeeded,
                    "attempted_round_record": copy.deepcopy(attempted_record),
                    "recorded_at_utc": utc_timestamp(),
                }
                storage.write_json_atomic(run_dir / storage.FAILURE_FILENAME, failure)
                # If checkpoint writing itself failed, keep the last durable
                # checkpoint as-is. JSONL remains authoritative; no replay occurs.
                if not append_succeeded:
                    try:
                        storage.write_json_atomic(checkpoint_path, checkpoint("failed", context))
                    except Exception:
                        pass
                raise
        try:
            final = checkpoint("completed")
            final["completed_at_utc"] = utc_timestamp()
            storage.write_json_atomic(run_dir / storage.FINAL_FILENAME, final)
            storage.write_json_atomic(checkpoint_path, checkpoint("completed"))
        except Exception as error:
            transcript.emit(
                f" FINALIZATION FAILED: {type(error).__name__}\n"
                f" Last scientifically committed round: {last_completed_round}\n"
            )
            storage.write_json_atomic(run_dir / storage.FAILURE_FILENAME, {
                "status": "failed", "phase": "finalization", "failed_round": None,
                "last_completed_round": last_completed_round,
                "run_name": run_name, "replicate_id": replicate_id,
                "failure": serialize_failure_context(error),
                "completed_calls_in_failed_round": [],
                "paid_or_attempted_usage_in_failed_round": empty_usage(),
                "cumulative_usage_through_last_completed_round": copy.deepcopy(usage),
                "recorded_at_utc": utc_timestamp(),
            })
            raise
        return {"status": "completed", "run_dir": str(run_dir), "run_name": run_name,
            "last_completed_round": last_completed_round,
            "cumulative_net_profits": list(profits), "cumulative_usage": copy.deepcopy(usage)}
