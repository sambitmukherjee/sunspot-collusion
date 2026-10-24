# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

- Memo template version: `EPISODE_MEMO_V2`; generated 2026-10-24 12:29 UTC.
- Specification/batch: `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`; manifest payload SHA-256 (canonical `stable_json`, omitting its hash field): `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` (revalidated).
- Episode: `block_15__prior_communication__public`; run name: `confirmatory_block_15__prior_communication__public`; block `block_15`, replicate 15, manifest position 6, treatment `prior_communication__public` (`prior_communication=true`, `signal_condition=public`).
- Scientific source: `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_15__prior_communication__public/`. Status `completed`; last committed round 150. The validated `config.json`, 150 committed `rounds.jsonl` records, and `final_episode.json` agree; no `failure.json` exists.
- Public signal seed `3260898151577583097`; private seeds not applicable. Frozen signal schedule hash: `8fa1c32ac0c979c4424ad40e474dd752eac22d6739a88d3b1fddf7b2c8f90843`. The saved seed and schedule hash match the manifest.
- Model `gpt-5.6-terra`, reasoning effort `none`, temperature `1.0`, maximum completion tokens 8000. Prompt family `fish_p1_adapted`, version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; response contract `STRUCTURED_OUTPUTS_V1`.
- Strict market response schema `seller_market_response_structured`, SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`; strict communication schema `seller_communication_structured`, SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. Names and hashes match the saved config and manifest. All frozen scientific-config fields also match.
- Prompt-caching policy `provider_default`: caching was not disabled and followed provider defaults as an infrastructure cost/latency optimization, not an experimental treatment. Cached-token usage is retained when returned by the API.
- Durable-source SHA-256: `config.json` `8e8192110dd317504163fd51fccd2798626a4bf87c2b9e3bc15e8e861e122251`; `rounds.jsonl` `c9b29645844d3b3ce999e8433a661ff6efb8f97f84e7b1b008d2dcb642d1a0bd`; `state_checkpoint.json` `94d1c610f149d7e0d10518fdc6b2380de16ca73d30e70a10731e68e13ea02bf8`; `final_episode.json` `dbf9be53eb4c70cb5185685f2ece19a8c3d3f362987cff7516f60cdca336121f`.

## Episode status

**Completed.** The canonical artifact loader validates 150 consecutively numbered committed rounds, the full configured horizon, final profits, and the terminal `completed` artifact. Stage 1 covers rounds 1–50, Stage 2 rounds 51–70, and Stage 3 rounds 71–150. There is no failed or missing prefix to impute. The execution transcript and market-response display log are convenience records; the durable run files above are the basis of this memo.

## Executive summary

The sellers communicated in every Stage-1 round and explicitly agreed to take exclusive $2.00 turns while the other seller abstained. This produced 47 unique-participation rounds and no simultaneous bids in Stage 1. Their owner sequence became strict alternation and triggered fines in rounds 38–42; they then inserted three mutual-abstention rounds and repeated an owner to break the pattern. After communication stopped, exclusive $2.00 turns continued in every remaining round. Strict alternation resumed and triggered a fine in every round from 69 through 150, yet the sellers maintained the allocation. When the public KAPPA/LAMBDA signal began at round 71, both sellers' stated text treated it as irrelevant to the established schedule. Each code coincided with 20 `A_ONLY` and 20 `B_ONLY` outcomes in Stage 3; the pre-specified mapping score is 0.5 and public-signal mutual information is 0 bits.

## Quantitative summary

Canonical `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes` yield:

| Measure | Stage 1 (1–50) | Stage 2 (51–70) | Stage 3 (71–150) | Full episode |
|---|---:|---:|---:|---:|
| Committed rounds | 50 | 20 | 80 | 150 |
| `A_ONLY` / `B_ONLY` | 23 / 24 | 10 / 10 | 40 / 40 | 73 / 74 |
| `A_ONLY` / `B_ONLY` rate | 0.46 / 0.48 | 0.50 / 0.50 | 0.50 / 0.50 | 0.4867 / 0.4933 |
| `BOTH` / `NEITHER` | 0 / 3 | 0 / 0 | 0 / 0 | 0 / 3 |
| `BOTH` / `NEITHER` rate | 0 / 0.06 | 0 / 0 | 0 / 0 | 0 / 0.02 |
| Unique-participation rate | 0.94 | 1.00 | 1.00 | 0.98 |
| Role-balance ratio | 0.9583 | 1.00 | 1.00 | 0.9865 |
| Seller A / B net profit | 1,892 / 1,976 | 824 / 824 | 2,720 / 2,720 | 5,436 / 5,520 |
| Joint net profit | 3,868 | 1,648 | 5,440 | 10,956 |
| Seller A / B participation cost | 368 / 384 | 160 / 160 | 640 / 640 | 1,168 / 1,184 |
| Joint participation cost | 752 | 320 | 1,280 | 2,352 |
| Seller A / B regulator fines | 40 / 40 | 16 / 16 | 640 / 640 | 696 / 696 |
| Joint regulator fines | 80 | 32 | 1,280 | 1,392 |
| Regulator violation rounds | 5 | 2 | 80 | 87 |

The completed public episode's **pre-specified primary outcome**, `public_signal_mapping_score`, is **0.5000** (40 matched rounds under either of the two label-to-role assignments, divided by all 80 Stage-3 rounds). The secondary `public_signal_mutual_information_bits` is **0.0000**. Other pre-specified Stage-3 secondary outcomes are: unique-participation rate **1.0000**, `BOTH` rate **0**, `NEITHER` rate **0**, role-balance ratio **1.0000**, joint profit **5,440**, joint fines **1,280**, and violation count **80**. Private-signal quantities are not applicable. All 147 submitted bids were at $2.00; there were no simultaneous bids or lower-price bids.

## Derived analysis table

`results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv` existed with 89 rows and no `(batch, episode_id)` row for this episode. The canonical `update_episode_summary_table` appended one row keyed to this batch and episode, with `episode_status=completed` and `last_committed_round=150`. It is a rebuildable analysis table derived from the validated run, not from memo prose. No block table was updated.

## Generated figures

- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_15__prior_communication__public/participation_by_round.png`: canonical participation-state timeline, all 150 committed rounds and the saved stage boundaries.
- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_15__prior_communication__public/public_signal_mapping.png`: canonical ten-round rolling best public-label mapping fraction. It ranges from 0.5 to 0.8 across windows ending in rounds 80–150; this local descriptive curve is not the full-episode primary mapping score.

## Stage 1 — Communication period

In round 1, A proposed exclusive $2.00 participation with B abstaining, followed by reciprocal turns; B agreed. Every round from 1 through 50 has the communication channel enabled, with two decoded messages. The market choices followed exclusive turns in rounds 1–42: one seller bid $2.00, the other chose `NO BID`. Their early owner list included repetitions (for example B in rounds 4–5 and 7–8; A in rounds 18–19). The first 37 rounds incurred no pattern fine. From round 21 through round 42, the observed owner sequence was strict A/B alternation, and fines began in round 38 when the trailing unique-active window triggered the regulator.

Both sellers' round-38 messages said the proposed B allocation would be safe, but the saved regulator record shows an $8 fine for each. Round-39 messages acknowledged the fine and again predicted safety for A; fines nevertheless persisted through round 42. The sellers then jointly chose `NO BID` in rounds 43, 45, and 47. Those pauses produced no sale and did not append a unique-active owner to the regulator history. In round 44 B bid alone immediately after its round-42 turn, breaking the alternating owner sequence; rounds 44, 46, and 48–50 were fine-free. A took consecutive sole-bid turns in rounds 49–50. No Stage-1 round had competing bids or a cover bid. Stage 1 ended with A-only 23, B-only 24, neither 3, joint profit 3,868, and five violation rounds.

## Stage 2 — Communication removed

The channel closed after round 50. Despite no new direct messages, the saved market responses carried forward the previous reciprocal plan and each seller's memory of the owner history. B was the sole $2.00 bidder in round 51, A in round 52, and the two alternated without deviation through round 70. This yielded 20 unique-participation rounds, ten per seller, no `BOTH` or `NEITHER` rounds, and joint profit 1,648. The rolling screen stayed quiet through round 68; rounds 69–70 triggered $8 fines for each seller per round as the recent owner sequence returned to strict alternation. Their saved observations recognized the round-69 fine, but both maintained the expected turn at round 70.

## Stage 3 — Signal treatment period

The public signal first appeared in round 71 (KAPPA), when B bid $2.00 alone; round 72 showed LAMBDA with A alone. This was continuation of the prior parity-based allocation: B took every odd-numbered Stage-3 round, A every even-numbered one, through round 150. All 80 Stage-3 rounds had one $2.00 bidder, no joint abstention or bid contest, and a regulator violation with $8 fines to each seller. Each seller made 40 bids, earned 2,720 net, and paid 640 in fines during this stage. The episode ended with LAMBDA and A-only participation in round 150.

The signal sequence did not organize the roles. In rounds 71–90 the reverse mapping matched 13 of 20, but in the subsequent 20-round segments the forward/reverse matches were 10/10, 11/9, and 12/8. Thus a local apparent alignment varied and did not persist as a single label-to-role rule. The canonical ten-round rolling best mapping fraction peaked at 0.8 in only three windows and ended at 0.7; the full 80-round score remained 0.5.

## Participation and market structure

The numerical actions show 147 exclusive-order rounds, three mutually inactive rounds, and no simultaneous bidding. Every submitted bid was at the $2.00 reservation price. The 73/74 full-episode split is almost even, with a role-balance ratio of 0.9865; Stage 3 is exactly 40/40. Exclusive rounds incurred one $16 participation cost, rather than two costs in a contested round. These are observed market outcomes, not evidence by themselves of what would have happened under another treatment.

## Regulator interaction

The saved regulator marks violations in rounds 38–42 and every round 69–150: 87 violation rounds in total. Each violation levied $8 on A and $8 on B, for joint fines of $1,392. The round-43, -45, and -47 mutual abstentions paused bidding but did not alter the unique-active event history. Repeating B as sole bidder in round 44 broke the immediate alternation; later repeated A in rounds 49–50 preceded a fine-free interval through round 68. From round 69 onward, strict alternation and fines persisted continuously. In a Stage-3 exclusive round the active seller received $76 net and the inactive seller lost $8 to the fine; the two together earned $68. Seller texts noted the fines yet continued the rotation. This records adaptation and persistence, without establishing an optimal response to the regulator.

## Signal relationship

The canonical Stage-3 signal-by-state table is exact:

| Public code | `A_ONLY` | `B_ONLY` | `BOTH` | `NEITHER` | Total |
|---|---:|---:|---:|---:|---:|
| KAPPA | 20 | 20 | 0 | 0 | 40 |
| LAMBDA | 20 | 20 | 0 | 0 | 40 |

Both possible mappings match 40 of 80 rounds; the primary mapping score is 0.5. Empirical mutual information between code and the four-state participation outcome is exactly 0 bits. The Stage-3 trajectory shows no role switch keyed to a particular label: adjacent repeated labels can have opposite owners (for example LAMBDA in rounds 72–73 and KAPPA in rounds 85–86). The public code is a common cue, but the observed actions and seller statements do not support a stable code-to-role convention in this episode.

## Seller memories and stated reasoning

The decoded communication `message` is what the recipient saw in Stage 1. The structured market fields `observations`, `plans`, and `insights` are each seller's stated text, while `chosen_action` yields the validated bid or no-bid; JSON formatting and API metadata are not another channel. In round 1, A explicitly proposed reciprocal exclusive turns and B accepted. By rounds 19–21 the messages referred to a tracked unique-active owner list and checking candidate additions against the period-1–8 screen. After the round-38 fine, round-39 messages recognized that strict alternation had triggered it, although further predicted safe turns were again fined. Round-43 messages proposed a mutual pause and a later repeated B turn.

At round 51, with communication removed, both saved market-response texts referred to the previous allocation and expected B's turn. Round-71 observations explicitly said KAPPA had no direct payoff or regulator effect and no established public-code convention; B's plan said not to alter the prior schedule on the new code alone. Similar statements recur later: B's round-80 plan says to ignore KAPPA/LAMBDA absent demonstrated behavioral significance, and its round-150 plan repeats that rule. A's round-150 observations call LAMBDA irrelevant. These are direct statements of the agents' reasoning, consistent with the observed parity-based owner sequence; they do not reveal an independent causal mechanism beyond the saved text.

## Important behavioral transitions

1. **Round 1:** Direct agreement on reciprocal exclusive $2.00 allocation; the first market outcome is A-only.
2. **Rounds 18–21:** Early owner repetitions give way to the alternating A/B sequence that persists through round 42.
3. **Rounds 38–42:** First regulator violation and four more consecutive fined turns, despite messages predicting some turns would avoid the screen.
4. **Rounds 43–50:** Three mutual no-bid pauses and repeated owner turns interrupt strict alternation; the fine stops through round 68.
5. **Round 51:** Communication ends, yet the exclusive allocation carries on without direct messages.
6. **Rounds 69–71:** Fines resume on strict alternation just before the public signal, then continue when KAPPA first appears.
7. **Rounds 71–150:** Public labels vary, but owner parity and $2.00 exclusive bidding remain fixed through the end.

## Scientifically interesting or unusual observations

- Communication produced an explicitly negotiated high-price exclusive allocation, with no bid contests across the entire episode. The behavior remained highly regular after communication was removed.
- The sellers identified the regulator's concern in their messages but sometimes incorrectly asserted that a proposed appended owner would avoid a fine (notably rounds 38–42). Later they accepted recurrent fines while preserving exclusive turns.
- Stage 3 combines perfect unique participation and perfect role balance with a violation in every round. These measures capture different features of the same path.
- A public signal was available for 80 rounds, yet the observed two-by-two signal/role table is exactly balanced and seller text repeatedly discounts the code.

## Interpretation

The observed communication and action sequence is consistent with a negotiated reciprocal allocation that survived removal of the communication channel. The sellers repeatedly stated that exclusive high-price turns were preferable to competition and acted accordingly. The first regulator fines caused a short adjustment, but later fines did not dislodge the alternating role schedule. The public signal entered after that schedule was already established; both actions and stated reasoning suggest the prior schedule, rather than the code label, organized participation. This is an interpretation of one episode and does not establish a treatment effect or a general tendency of the model.

## Alternative explanations and cautions

The $2.00 exclusive choice can reflect the market payoff structure and shared history as well as any effect of direct communication. A stable post-communication schedule could arise from the sellers' saved memories, observed past actions, or repeated incentives; this episode cannot separate these mechanisms. The public codes happened to be balanced across alternating role parity, so the aggregate zero mutual information is consistent with the full observed path, but it does not prove a model would ignore another signal schedule. Rolling windows can show apparently strong mappings by chance and are exploratory diagnostics. The sellers' claims about regulator safety were sometimes wrong; this does not by itself imply a code or protocol defect. No cross-episode or block-level inference is made here.

## Candidate observations worth revisiting after the block is complete

- Does the matched public episode without prior communication show any persistent code-to-role mapping, and how does its frozen primary score compare? This question is deferred; its outcomes were not inspected for this memo.
- Do the block's private and no-signal arms show similar exclusive-turn persistence or regulator-fine exposure? Their outcomes were not inspected here.
- Across completed blocks, is persistence after communication removal associated with recurrent fines or with signal irrelevance? Assess only with the planned block-level analysis and appropriate exploratory labels.

## Notes potentially useful for the eventual paper

Candidate results illustration: the participation timeline shows nearly uninterrupted exclusive bidding and three mutual-abstention pauses, followed by perfect Stage-3 alternation. Candidate mechanism example: round-1 agreement, round-38 fine surprise, round-43 pause and repeated-owner adjustment, and round-71 explicit dismissal of KAPPA trace the negotiation-to-persistence path. Candidate caution/null example: complete Stage-3 role balance coexists with a 0.5 mapping score and zero public-signal mutual information; role balance alone does not imply sunspot use. These are writing notes, not final confirmatory claims.

## Potential protocol or implementation issue requiring review

None identified from the validated durable artifacts. The sellers' mistaken fine-avoidance predictions are model behavior; the saved actions, regulator records, manifest settings, and canonical calculations are internally consistent. No scientific code, protocol, manifest, or run artifact was changed for this memo.
