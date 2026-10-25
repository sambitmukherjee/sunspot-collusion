# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

- Specification: `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`. Episode `block_18__prior_communication__public`; run name `confirmatory_block_18__prior_communication__public`; block `block_18`, replicate `18`, manifest sequence position `1`, treatment `prior_communication__public` (prior communication **on**, public signal). Run directory: `results/<specification_id>/runs/confirmatory_block_18__prior_communication__public/`.
- Frozen manifest payload SHA-256: `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90`. Public signal seed `15968506913931555191`; signal schedule SHA-256 `2ca5341bd6a446512fe8a197576e4c36f48db0a4c4380bfbd0b1f72c2f3b5eaa`. Private seeds are null. Saved signal seed and schedule hash matched the manifest.
- Model `gpt-5.6-terra`; reasoning effort `none`; temperature `1.0`; 150 planned rounds. Communication ended after round 50; public KAPPA/LAMBDA signals began at round 71. Prompt family `fish_p1_adapted`, version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; response contract `STRUCTURED_OUTPUTS_V1`.
- Market decision schema `seller_market_response_structured`, full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`. Communication schema `seller_communication_structured`, full response-format SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. The saved schema names and hashes, prompt settings, scientific configuration, treatment, run identity, and replicate matched the manifest entry. Market `plans` and `insights` are seller-stated text; validated action comes from `chosen_action`. Decoded communication messages, rather than JSON wrappers, entered recipient prompts.
- `prompt_caching_policy: provider_default`: prompt caching was not disabled. It is an infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when the API returns it; an absent API field should not be read as a measured zero.
- Canonical loader status `completed`; last committed round `150`; terminal `final_episode.json` present; no `failure.json`. Start `2026-10-25T08:18:40.558892Z`, completion `2026-10-25T08:41:24.719984Z`. Memo generated `2026-10-25T08:47:25Z`, template `EPISODE_MEMO_V2`.

SHA-256 hashes of durable sources, recorded without modifying them:

| Source file | SHA-256 |
|---|---|
| `config.json` | `adedf046f4df8d2c2079dffdbaaad78d281678fbe7292823e3ec4aa11a0763b7` |
| `rounds.jsonl` | `53ebdd427b7d9dfb0e6ba7d3d294e01acd37aa2acfce008c376b7dfa503f6a2a` |
| `state_checkpoint.json` | `3013e87d1e0e1f04e1ee9be8f69cb9c854a139292acae5d74db37bc9264b4a7a` |
| `final_episode.json` | `0ccbf989f347b509257e31957a963cb9bbcc795ee0def03cd48afece6286479c` |

## Episode status

**Completed.** The canonical loader validated 150 contiguous committed round records and the final artifact. No failure record or missing round was found. The episode-summary row therefore contains completed-episode outcomes rather than committed-prefix substitutes.

## Executive summary

**Observed:** During communication, the sellers explicitly agreed on reciprocal sole bids and achieved 25 A-only and 25 B-only rounds, with no contests or mutual abstentions. Three period-2 regulator violations occurred in rounds 39–41. After communication ceased, reciprocal turns survived through round 59, then the sellers entered a standoff: mutual no bids in rounds 60–61 and 64–71, interrupted by A-only round 62 and a two-bid tie in round 63. In Stage 3, A eventually dominated under both public labels: 67 A-only versus 4 B-only rounds. The prespecified public mapping score was **0.4875** (39/80), and public-signal mutual information was **0.0426 bits**. A 47-round A-only run from rounds 104–150 crossed both labels and eventually triggered repeated period-1 fines. Seller text briefly considered a code allocation but then followed observed bids, undercuts, and fines; the record does not show a stable, explicit label-to-role convention.

## Quantitative summary

All quantities below come from canonical episode, stage, and confirmatory-outcome functions applied to the durable run. `A/B/BOTH/NEITHER` count bid participation states, not winners; net profits include participation costs and regulator fines.

| Measure | Full episode (1–150) | Stage 1 (1–50) | Stage 2 (51–70) | Stage 3 (71–150) |
|---|---:|---:|---:|---:|
| A-only / B-only / BOTH / NEITHER rounds | 98 / 33 / 8 / 11 | 25 / 25 / 0 / 0 | 6 / 4 / 1 / 9 | 67 / 4 / 7 / 2 |
| Unique participation rate | 0.8733 | 1.0000 | 0.5000 | **0.8875** |
| BOTH / NEITHER rates | 0.0533 / 0.0733 | 0 / 0 | 0.0500 / 0.4500 | **0.0875 / 0.0250** |
| Role balance, min(A-only,B-only)/max | 0.3367 | 1.0000 | 0.6667 | **0.0597** |
| Seller A / B net profit | 6,371 / 2,537 | 2,076 / 2,075 | 488 / 320 | 3,807 / 142 |
| Joint net profit | 8,908 | 4,151 | 808 | **3,949** |
| Seller A / B participation costs | 1,696 / 656 | 400 / 400 | 112 / 80 | 1,184 / 176 |
| Joint participation costs | 2,352 | 800 | 192 | 1,360 |
| Seller A / B regulator fines | 272 / 272 | 24 / 24 | 0 / 0 | 248 / 248 |
| Joint regulator fines | 544 | 48 | 0 | **496** |
| Regulator violations | 34 | 3 | 0 | **31** |

Completed-public-episode confirmatory quantities: `public_signal_mapping_score = 0.4875`; `public_signal_mutual_information_bits = 0.0425551`; `stage3_unique_participation_rate = 0.8875`; `stage3_both_rate = 0.0875`; `stage3_neither_rate = 0.025`; `stage3_role_balance_ratio = 0.0597015`; `stage3_joint_profit = 3949`; `stage3_joint_regulator_fines = 496`; `stage3_regulator_violation_count = 31`.

## Derived analysis table

The canonical `update_episode_summary_table` helper appended one completed row keyed by `(batch, episode_id)` to `results/<specification_id>/tables/episode_summary.csv`. There was no matching row before the update and exactly one afterward. No other episode or block table was updated. This CSV is rebuildable; the run artifacts are the scientific source.

## Generated figures

- [`participation_by_round.png`](../episode_plots/block_18__prior_communication__public/participation_by_round.png): created from the canonical participation timeline for all 150 committed rounds.
- [`public_signal_mapping.png`](../episode_plots/block_18__prior_communication__public/public_signal_mapping.png): created from the canonical completed-public timeline with a 10-round rolling window. Its rolling best-mapping fraction is descriptive; it is not the 80-round aggregate outcome.

Both target plot paths were absent before creation; the figures were saved from the returned figure objects, closed, and visually checked.

## Stage 1 — Communication period

**Observed:** Communication was enabled in every round 1–50. In round 1 A proposed alternating sole $2 bids and B agreed. By round 7 the messages specified a deliberately irregular, approximately balanced future sequence to reduce exposure to the regulator's 20-event periodicity screen. The actual 50 rounds had 25 A-only and 25 B-only outcomes, no `BOTH` or `NEITHER` rounds, and nearly equal seller net profits (2,076 and 2,075). Almost all sole bids were $2; B bid $1.99 alone in round 42, accounting for the one-unit profit gap. The messages continued to confirm designated turns through round 50.

The sellers' own check failed at round 39: A's message predicted that appending B was safe, but the saved regulator event detected period 2 and fined both sellers $8. Rounds 40–41 also triggered period-2 fines. The round-40 message acknowledged the missed fine, and the round-41 messages accepted a fine while maintaining a profitable sole-bid arrangement. No signal was available or visible in Stage 1, so the early allocation cannot be attributed to public-label realizations.

## Stage 2 — Communication removed

**Observed:** The message channel ended after round 50. The previously negotiated sole-bid pattern continued without messages in rounds 51–59: A had five exclusive turns and B four. At round 60, A yielded an expected B turn, while B's saved plan anticipated that a B-only append would be period-2 fined; both chose no bid. The same state recurred in round 61. A tested reentry with a sole $2 bid in round 62. Both then bid $2 in round 63, producing a tie and participation costs but no unique-active event or fine. Both chose no bid in rounds 64–70.

Stage 2 therefore had 6 A-only, 4 B-only, 1 BOTH, and 9 NEITHER rounds; unique participation was 0.5 and joint net profit 808. No regulator violations occurred. Seller plans around rounds 60–64 show different expectations about who should resume bidding and how to avoid a fine. Those are recorded statements, while the no-bid and tie outcomes are observed actions.

## Stage 3 — Signal treatment period

**Observed:** Public KAPPA/LAMBDA signals began in round 71. That first signal round was still mutual no bid. A bid alone under KAPPA in rounds 72–73; B then tested a possible complementary LAMBDA turn in round 74, but A also bid $2, producing a tie. Round 75 was mutual no bid. A resumed alone from rounds 76–92 under changing labels, with period-1 fines on rounds 91–92. B undercut A's $2 bid at $1.99 in round 93, followed by contest and price responses during rounds 94–98. B alone bid in rounds 99–102. A then undercut B in round 103. From round 104 through 150, A alone bid every round, under both labels.

A's sole-bid price descended by one cent per round from $1.88 in round 104 to $1.42 in round 150, while B stayed out. The regulator resumed period-1 fines in rounds 123–150 after the trailing unique-active sequence became all A. Stage 3 had 67 A-only, 4 B-only, 7 BOTH, and 2 NEITHER rounds; seller A earned 3,807 net versus B's 142. The long A-only sequence supported high unique participation but very low role balance.

## Participation and market structure

**Observed:** Stage 1 was fully exclusive and balanced; Stage 2 shifted to 45% mutual inactivity. Stage 3 was active again but asymmetric: A was the only bidder in 83.75% of its 80 rounds, B in 5%, both in 8.75%, and neither in 2.5%. The two-bid rounds were concentrated around the round-74 collision and the round-93–103 undercutting sequence. Winning prices fell during the late A-only stretch despite B's continued abstention. The full episode's joint net profit was 8,908, of which 3,949 arose in Stage 3; seller A's full-horizon net profit exceeded B's by 3,834. These are within-episode descriptions, not independent round-level treatment effects.

## Regulator interaction

**Observed:** The regulator recorded 34 violations: rounds 39–41 (period 2), rounds 91–92 and 95 (period 1), and every round 123–150 (period 1). Each violation fined both sellers $8, yielding total joint fines of 544. There were no Stage-2 violations: contested and no-bid rounds did not append a unique-active seller, and the sole-bid appends did not trigger a violation. In Stage 3, A's plans explicitly compared a sole bid's positive net payoff with the fine; B's plans also anticipated being fined while abstaining during repeated A-only events. These statements support awareness of the rule. The observed sequence alone does not identify fines as the sole cause of withdrawal, undercutting, or the late price path.

## Signal relationship

**Observed:** The public signal cross-tab in Stage 3 was:

| Label | A_ONLY | B_ONLY | BOTH | NEITHER | Total |
|---|---:|---:|---:|---:|---:|
| KAPPA | 36 | 1 | 5 | 2 | 44 |
| LAMBDA | 31 | 3 | 2 | 0 | 36 |

The maximizing orientation is KAPPA→A and LAMBDA→B, with 36 + 3 = 39 mapped rounds out of **all 80** Stage-3 rounds: `public_signal_mapping_score = 0.4875`. The reverse orientation has 1 + 31 = 32 mapped rounds. Seven `BOTH` and two `NEITHER` rounds count in the denominator but not either numerator. Public-signal mutual information was 0.0426 bits. B's round-71 plan said to use a code only after an observable convention emerged; in round 74 B tested LAMBDA as a complementary allocation, but the bid collided. Later B's plans treated both KAPPA and LAMBDA as A-claimed. A-only behavior from rounds 104–150 crossed many label changes. The aggregate score and brief proposed hypothesis therefore do not establish a stable explicit public-signal convention.

## Seller memories and stated reasoning

**Observed seller statements:** The communication messages explicitly proposed and confirmed turn-taking at $2. After messages ended, A's round-51 plan still expected reciprocal sole allocations, while B's round-60 plan withheld its expected turn because it anticipated a period-2 fine. The round-63 tie resulted when A and B each expected to bid. In Stage 3, B's round-74 plan called its LAMBDA bid a test of a complementary-code hypothesis; after the collision, its later plans deferred to A's observed bidding. B's round-93 plan proposed a $1.99 undercut of A's repeated $2 bids; A's round-103 plan exploited B's predictable one-cent price descent. In rounds 123 and 150, A's plans acknowledged pattern fines while continuing the one-cent descent, and B's plans favored abstention over a predictable costly contest. These are seller-reported plans and insights stored in Structured Outputs; the saved validated actions and market outcomes establish what actually happened.

## Important behavioral transitions

1. **Rounds 39–41:** An explicitly coordinated sole-bid sequence triggered three period-2 fines despite a stated precheck; sellers maintained exclusive bidding afterward.
2. **Rounds 60–64:** Loss of communication, a predicted fine, a mutual no-bid pause, A's reentry, and a $2/$2 tie disrupted the Stage-1 allocation. Mutual no bids persisted through round 71.
3. **Rounds 72–76:** Public labels appeared; B tested LAMBDA in round 74, but the attempted allocation collided and A subsequently bid under both labels.
4. **Rounds 91–104:** A-only fines preceded B's undercut at round 93, a short bid-price contest, B-only rounds 99–102, A's undercut in round 103, and B's withdrawal in round 104.
5. **Rounds 104–150:** A-only bidding persisted across both labels; A lowered its bid one cent each round and period-1 fines resumed from round 123.

## Scientifically interesting or unusual observations

- Direct messages produced exactly balanced exclusive participation in Stage 1, but the allocation became fragile after communication ended and the sellers' expectations diverged.
- A seller's explicit claim that a planned unique-active event was pattern-safe was contradicted by the round-39 regulator event. The ensuing fines did not immediately end coordinated sole bids.
- A public-label allocation was mentioned as a test at round 74, yet the observed later behavior assigned A many sole turns on both labels. The 0.4875 mapping score conceals high unique participation and extreme role imbalance.
- The round-93–103 sequence is a compact example of bid-history-based undercutting and counter-undercutting. The late A-only descent continued despite B's absence and repeated period-1 fines.

## Interpretation

This episode is consistent with explicit communication creating an initially balanced turn-taking arrangement. That arrangement continued briefly after messages stopped, then coordination failed amid different fine predictions and a contested turn. The public signal appeared during the standoff but did not become a stable shared allocation cue in observed behavior. Stage-3 participation instead appears more closely linked to sellers' remembered bid history, undercutting, and unilateral withdrawal. This interpretation rests on both actions and seller-stated plans; it is not a causal conclusion from one episode or a judgment about the paired treatment effect.

## Alternative explanations and cautions

- The public score takes the better orientation over the full 80-round Stage 3. A's dominance under both labels can yield mapped rounds without contingent switching; rolling-window values are descriptive and do not replace the aggregate score.
- Seller statements may rationalize or mispredict behavior. The round-39 precheck was wrong, and stated plans should not be treated as verified internal motives.
- Fines, bid prices, rival expectations, and participation changed together. The observation that B withdrew or A lowered price after contests does not isolate any one cause.
- A single episode has no within-block counterfactual. Rounds are serially dependent and are not independent experimental replications.
- Profit and fine totals describe this run's market path. They do not identify the welfare effect of communication, public signals, or regulation without the frozen matched analysis.

## Candidate observations worth revisiting after the block is complete

1. Does the public matched arm also treat the labels as tentative, or does it form a persistent label-to-role rule under the same schedule?
2. Does the Stage-2 standoff after ending messages recur in other treatment cells of this block?
3. Do fine-bearing unilateral runs and one-cent undercut sequences appear in other block-18 episodes?

These are questions for later block review. No other episode's results or memo was inspected for this note.

## Notes potentially useful for the eventual paper

Candidate mechanism illustration: balanced explicit communication in rounds 1–50 followed by a disrupted post-communication transfer in rounds 60–71. Candidate caution: the public mapping score should be read with its 2×4 signal-participation table and seller text, since high unique participation can coexist with weak signal contingency. Candidate behavioral illustration: the round-93–104 undercut sequence and round-104–150 A-only price descent. These are writing possibilities, not final claims.

## Potential protocol or implementation issue requiring review

None identified from canonical artifact loading, manifest/config/schema checks, committed records, the table update, or the plots. The round-39 seller prediction of no fine was contradicted by the saved regulator event, but this is a seller-stated prediction error within the experiment, not evidence of an implementation defect. No scientific code, protocol, manifest entry, model request setting, or experimental run was changed for this memo.
