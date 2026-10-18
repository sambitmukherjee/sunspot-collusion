# Reproducibility and artifacts

The active specification is `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`, prompt family `fish_p1_adapted`, prompt version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`, and response contract `STRUCTURED_OUTPUTS_V1`. The [config](../configs/gpt5_6_terra_none_fish_p1_adapted_v2.yaml) and [manifest](../configs/gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json) are validated before a dry run or execution. The [protocol](v2_confirmatory_protocol.md) records the deterministic schedule and payload hash.

The active maximum completion limit is 8,000 tokens. The manifest contains 180 positions and records the scientific config in each episode row.

## Structured response contract

OpenAI Chat Completions routes communication to strict schema `seller_communication_structured` (full response-format SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`) and market decisions to strict schema `seller_market_response_structured` (SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`). The canonical ordered response formats are in [structured_outputs.py](../src/collusion_experiment/structured_outputs.py). The hash covers UTF-8 JSON serialized in declaration order, without spaces and with Unicode preserved.

Market responses have required strings in this order: `observations`, `plans`, `insights`, `chosen_action`. The action is `NO BID` or an exact two-decimal one-cent-grid price from `0.00` through `2.00`. Empty plans or insights replace the previous content with an empty string. Communication has one required free-form `message`; only its decoded value enters the recipient prompt. The transport checks refusal and finish status before decoding, and completed JSON is checked for exact keys and valid values. Both sellers' market prompts are built from the same pre-action state.

## Prompt caching and model provenance

Prompt caching is not disabled. The batch uses the provider's default behavior (`prompt_caching_policy: provider_default` in the config, manifest, and episode provenance). Caching is an infrastructure cost and latency optimization rather than an experimental treatment. Cached-token usage is logged when returned by the API. Scientific call records retain prompts, raw and decoded responses, request parameters, returned model metadata, token usage, and technical retries.

## Paths and data integrity

Generated files use `data/<specification_id>/`, `results/<specification_id>/`, `research_notes/<specification_id>/`, and `execution_logs/<specification_id>/`. Each scientific run writes `config.json`, `rounds.jsonl`, `state_checkpoint.json`, and either `final_episode.json` or `failure.json` under `results/<specification_id>/runs/<run_name>/`. `rounds.jsonl` is the scientific commit log. Episode console and market-response display logs are convenience views under the execution-log namespace and do not enter seller context.

`results/<specification_id>/tables/episode_summary.csv` has one row per attempted episode, keyed by `(batch, episode_id)`; `block_summary.csv` has one row per fully attempted six-position block, keyed by `(batch, block)`. Both are rebuildable from validated source artifacts. Failed or incomplete episodes retain status but receive no invented full-episode outcomes. Missing matched outcomes remain blank. Memos and plots are manual, read-only interpretations, never inputs to later execution.

The local offline suite runs with `pytest -q` and blocks network access. The hosted model service can change behavior over time, so bitwise reproduction of model outputs is not claimed; saved prompts, responses, timestamps, settings, seeds, and hashes provide the audit trail.
