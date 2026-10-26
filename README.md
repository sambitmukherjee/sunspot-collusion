# Sunspot Collusion

This repository contains an experiment with two agents and a payoff-irrelevant public signal. The original [manifest](configs/gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json) specifies 30 matched blocks (180 episodes). The first 20 blocks (120 episodes) are complete and form the scientific sample analyzed for the sprint submission; blocks 21–30 were not run. The experiment uses specification `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2` and its [config](configs/gpt5_6_terra_none_fish_p1_adapted_v2.yaml).

## Research focus and evidence

The sprint paper asks whether language-model agents can *sometimes* form a bidding convention around a shared signal that changes neither payoffs nor market rules. A possible convention assigns Agent A the sole bid after `KAPPA` and Agent B the sole bid after `LAMBDA`, or the reverse. The signal appears only from round 71, after a 20-round gap without agent-to-agent messaging, so the agents cannot negotiate that particular assignment in advance. The central finding is an **exploratory existence result**: four of the 40 public-signal episodes show unusually strong signal-to-bidding-turn alignment after Holm adjustment, consistent with collusive market sharing. This does not establish that the behavior is typical or that making the signal available increases market sharing on average.

The [original analysis plan](docs/v2_confirmatory_analysis_plan.md) prespecified a different primary question: whether earlier communication improves later public-signal mapping scores in matched blocks, tested with a one-sided paired sign-flip test. After some episode results were inspected, the research emphasis shifted to whether signal-based conventions can emerge at all. The episode-level test below was added at that point, so its findings are exploratory rather than confirmatory. The original manifest and analysis plan remain available as records of the initial design.

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

### Reproduce the exploratory public-signal analysis

Install the package with its analysis dependencies (`python -m pip install -e ".[analysis]"`), then run [notebooks/analysis.ipynb](notebooks/analysis.ipynb) from the repository root or the `notebooks/` directory. Its V3 cell reads the committed `rounds.jsonl` files through the package's artifact loader, requires both completed public-signal episodes in each of blocks 01–20, and reports all 40 episode-level results. It makes no model calls; derived CSV exports are off by default.

For each public-signal episode, the [episode-level test](src/collusion_experiment/public_signal_inference.py) takes the better-fitting of the two opposite `KAPPA`/`LAMBDA`-to-agent assignments. Its mapping score divides the number of matching sole-bid rounds by all 80 public-signal rounds. The exact randomization p-value asks how unusual that better-fitting count would be if fair, independent signal draws changed but the bidding record stayed fixed. Holm adjustment accounts for testing all 40 public-signal episodes. The adjusted test highlights blocks 02, 05, 07, and 11; block 07 had no earlier messaging.

The [canonical metrics](src/collusion_experiment/metrics.py) also calculate **mutual information** between the public signal and four bidding outcomes: Agent A alone bids, Agent B alone bids, both bid, or neither bids. It is reported in bits as `public_mutual_information_bits` in the notebook's `episode_rows`. This descriptive measure captures *any* signal–outcome association, including patterns other than turn sharing; it should be read alongside the mapping score and bidding record, not as a separate proof of a collusive convention.
