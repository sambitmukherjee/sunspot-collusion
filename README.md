# Sunspot Collusion

This repository prepares a 30-block, 180-episode confirmatory experiment with two sellers and a payoff-irrelevant public signal. The current specification is `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`. Its [config](configs/gpt5_6_terra_none_fish_p1_adapted_v2.yaml) and [manifest](configs/gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json) are the sole active scientific plan. Execution requires a separate human freeze decision; no confirmatory episode has been run.

## Design

Each block contains all six cells of prior communication (`False` or `True`) crossed with signal condition (`none`, `private`, or `public`). Each of the six cells appears exactly five times at each within-block position across 30 blocks. Public and private signal schedules are matched between the two prior-communication arms within each block.

| Phase | Rounds | Communication | Signal |
| --- | --- | --- | --- |
| 1 | 1–50 | Available only in the prior-communication arm | None |
| 2 | 51–70 | None | None |
| 3 | 71–150 | None | Assigned condition |

Both communication and market calls use strict OpenAI Chat Completions Structured Outputs. The market schema keeps the field order `observations`, `plans`, `insights`, `chosen_action`; the communication schema transmits only the decoded `message`. Scientific settings, manifest construction, hashes, and execution controls are documented in the [protocol](docs/v2_confirmatory_protocol.md). The [analysis plan](docs/v2_confirmatory_analysis_plan.md) specifies the primary paired-block test.

## Offline inspection

Install the project in a Python environment and run `pytest -q`. The default suite blocks network access.

```bash
python scripts/run_episode.py --episode-id block_01__no_prior_communication__public
python scripts/run_block.py --block block_11
```

Both commands validate the active V2 config and manifest and default to a no-call dry run. The manifest generator, runners, and summary tools are described in [scripts/README.md](scripts/README.md). The [episode notebook](notebooks/run_episode.ipynb) also defaults to offline inspection. Do not enable execution before the separate freeze decision.

## Artifacts and analysis

Scientific runs, when authorized, use `results/<specification_id>/runs/` and `execution_logs/<specification_id>/episodes/`. Rebuildable tables use `results/<specification_id>/tables/`. Data, research notes, and logs are isolated under the same specification ID. The [reproducibility guide](docs/reproducibility.md) details provenance and stored artifacts. No memo or plot is generated automatically during a scientific run.
