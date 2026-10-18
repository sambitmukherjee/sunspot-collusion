# Active configuration

The active scientific config and manifest in this folder are:

- [gpt5_6_terra_none_fish_p1_adapted_v2.yaml](gpt5_6_terra_none_fish_p1_adapted_v2.yaml)
- [gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json](gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json)

They define 30 matched blocks and 180 planned episodes. The config records strict Structured Outputs schema names and hashes, the primary analysis, and `prompt_caching_policy: provider_default`. Prompt caching is not disabled; it follows the provider default as an infrastructure cost and latency optimization rather than an experimental treatment. Cached-token usage is logged when the API returns it. The [protocol](../docs/v2_confirmatory_protocol.md) documents deterministic manifest regeneration and output namespaces. No episode execution is authorized by these files alone.

The active completion-token limit is 8,000.
