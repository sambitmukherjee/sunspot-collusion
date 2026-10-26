# Sunspot Collusion

This repository contains an experiment with two agents and a payoff-irrelevant public signal. The original [manifest](configs/gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json) specifies 30 matched blocks (180 episodes). The first 20 blocks (120 episodes) are complete and form the scientific sample analyzed for the sprint submission; blocks 21–30 were not run. The experiment uses specification `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2` and its [config](configs/gpt5_6_terra_none_fish_p1_adapted_v2.yaml).

## Sprint provenance

The experimental runner, config, manifest, and protocol were prepared before 23 October 2026. Before that date, I also ran preliminary exploratory work while adapting [Fish et al.'s](https://arxiv.org/abs/2404.00806) economic environment and tuning incentives. Those exploratory runs are excluded from the 120 reported episodes.

Using UTC completion times, all episodes in blocks 01–11 and three episodes in block 12 finished before 23 October. The other three episodes in block 12 and all episodes in blocks 13–20 finished on or after 23 October. Thus, 69 of the 120 reported episodes finished before that date and 51 finished on or after it. Blocks 12–20 were completed on or after 23 October.

## Design

Each block contains all six cells of prior communication (`False` or `True`) crossed with signal condition (`none`, `private`, or `public`). In the original 30-block manifest, each of the six cells appears exactly five times at each within-block position. Public and private signal schedules are matched between the two prior-communication arms within each block.

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

Both commands validate the V2 config and manifest and default to a no-call dry run. The manifest generator, runners, and summary tools are described in [scripts/README.md](scripts/README.md). The [episode notebook](notebooks/run_episode.ipynb) also defaults to offline inspection.

## Artifacts and analysis

Completed scientific runs are stored under `results/<specification_id>/runs/` and `execution_logs/<specification_id>/episodes/`. Rebuildable tables use `results/<specification_id>/tables/`. Data, research notes, and logs are isolated under the same specification ID. The [reproducibility guide](docs/reproducibility.md) details provenance and stored artifacts. No memo or plot is generated automatically during a scientific run.
