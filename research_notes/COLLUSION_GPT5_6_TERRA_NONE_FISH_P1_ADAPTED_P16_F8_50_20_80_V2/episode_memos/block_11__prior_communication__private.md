# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

- Memo template: `EPISODE_MEMO_V2`; generated 2026-10-22T12:20:30Z.
- Specification/batch: `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`. The active YAML and manifest validated with canonical manifest payload SHA-256 `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90`, excluding the manifest's own hash field.
- Episode `block_11__prior_communication__private`; run `confirmatory_block_11__prior_communication__private`; block `block_11`; replicate 11; manifest sequence position 4; treatment `prior_communication__private`. Prior communication was enabled and seller signals were **private**. Run directory: `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_11__prior_communication__private/`.
- Private signal seeds: A `13140984580078846000`, B `52555195821639269`; public seed null. Frozen and saved signal-schedule SHA-256: `bc2f077e46b81c0de664ee65561158b6527b0d739db6132820c70f8a3d19242f`.
- Model `gpt-5.6-terra`; reasoning effort `none`; temperature `1.0`; maximum completion tokens 8,000. Prompt family `fish_p1_adapted`; prompt version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; response contract `STRUCTURED_OUTPUTS_V1`. Market response schema `seller_market_response_structured`, full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`; communication response schema `seller_communication_structured`, SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. Saved schema names and hashes match the manifest. `observations`, `plans`, and `insights` below mean decoded seller text; `chosen_action` yields the validated market action. JSON syntax and transport fields are not interpreted as seller communication.
- Prompt-caching policy `provider_default`: caching was not disabled, is an infrastructure cost/latency optimization rather than a treatment, and cached-token usage is logged when the API returns it. The saved raw usage has a returned `cached_tokens` field of 0; this is a logged zero, not an absent field.
- Frozen scientific configuration and saved run config agree, including 150 rounds, communication through round 50, private signals from round 71, order size 100, $16 participation cost, $8 pattern fine, and all model/request settings. The saved run has `status=completed` and last committed round 150.
- Durable-source SHA-256: `config.json` `a2c4568040f9fcc79ca1826d4bf1aeac81589db1de88233913bbc22234b13b5d`; `rounds.jsonl` `80e4361892867a03a4ce00f3c4b8021d24c9423eb7ee4d066763a99eacf38794`; `final_episode.json` `db8e245dc0493a6864a21d6e999de7896901f81f41ec4e5d9a5c6a38b55e174a`; `state_checkpoint.json` `581c87c9b4179e889c8e7258bfce60d2e5ea9fd00ba5a7d565071feece924937`. No `failure.json` exists.

## Episode status

**Completed.** `load_episode_artifacts` validated 150 sequential committed rounds and a terminal `final_episode.json` reporting `status=completed` and `last_completed_round=150`; final profits agree with the round log. Execution ran from 2026-10-22T11:49:49.354667Z to 2026-10-22T12:15:44.788610Z. No technical retry was recorded. Completion of the configured horizon does not imply continued market participation: both sellers chose `NO BID` in every round from 50 through 150.

## Executive summary

- During the communication period, the sellers explicitly arranged reciprocal exclusive $2.00 bids. Of its 50 rounds, 48 were unique-participation rounds, balanced 24 A_ONLY and 24 B_ONLY; rounds 40 and 50 were mutual no-bid pauses.
- A fine-bearing alternating sequence began at round 38. Eleven Stage-1 unique-active events incurred regulator fines, including every exclusive event from rounds 41–49. Seller messages sometimes predicted a proposed append was fine-free when the saved regulator outcome fined it.
- Round 50's agreed pause became an uninterrupted **101-round mutual no-bid sequence** through round 150. Communication stopped after round 50, and the later private signals did not coincide with any renewed entry.
- The full-episode role balance is 1.0 among the 48 unique rounds, but Stage 2 and Stage 3 have no unique rounds; their role-balance ratios are undefined. The two seller-specific private-signal mutual-information values are each 0 bits because Stage-3 participation was always NEITHER.

## Quantitative summary

The values below come from the canonical `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes` functions on this episode's validated artifacts. Participation states describe submitted numerical bids, not inferred intent. Net profits include bid costs and fines.

| Scope | Rounds | A_ONLY | B_ONLY | BOTH | NEITHER | Unique rate | Role balance | A net | B net | Joint net | Joint participation cost | Joint fines | Violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full episode | 150 | 24 | 24 | 0 | 102 | 0.32 | 1.00 | 1,928 | 1,928 | 3,856 | 768 | 176 | 11 |
| Stage 1, rounds 1–50 | 50 | 24 | 24 | 0 | 2 | 0.96 | 1.00 | 1,928 | 1,928 | 3,856 | 768 | 176 | 11 |
| Stage 2, rounds 51–70 | 20 | 0 | 0 | 0 | 20 | 0.00 | undefined | 0 | 0 | 0 | 0 | 0 | 0 |
| Stage 3, rounds 71–150 | 80 | 0 | 0 | 0 | 80 | 0.00 | undefined | 0 | 0 | 0 | 0 | 0 | 0 |

Full-episode state rates are A_ONLY 0.16, B_ONLY 0.16, BOTH 0, and NEITHER 0.68. Each seller incurred 384 in participation costs and 88 in regulator fines. The canonical private-signal mutual-information quantities are **A-specific 0.0 bits** and **B-specific 0.0 bits**; each seller's own private labels varied, but Stage-3 participation did not. The derived Stage-3 outcomes are unique participation 0, BOTH 0, NEITHER 1, joint profit 0, joint fines 0, and 0 violations; Stage-3 role balance is undefined because neither seller entered alone. Public-signal mapping score and public-signal mutual information are **not applicable** to this private treatment, not zero.

## Derived analysis table

The canonical one-episode updater appended one row keyed by this batch and episode ID to `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv`. Before the update, the table contained 63 rows and no target row; afterward, it contained 64 rows and one target row with `episode_status=completed`. No conflict or overwrite occurred. The CSV is derived from the durable run and is not an input to this memo's interpretation.

## Generated figures

- [Participation by committed round](../episode_plots/block_11__prior_communication__private/participation_by_round.png), from the canonical `plot_episode_participation_timeline` function. The stage boundaries are based on the saved episode timing.
- `public_signal_mapping.png` was omitted: this is a private-signal treatment, so a public-label mapping plot would be inapplicable.

## Stage 1 — Communication period

Decoded seller messages in round 1 proposed and accepted alternating exclusive participation: one seller bid $2.00, the other chose `NO BID`, then roles reversed. The arrangement was followed in the first two rounds and, with some irregular identity choices, throughout rounds 1–39. Messages in rounds 15–20 specified upcoming A/B allocations and emphasized checking the regulator's trailing 20 unique-active identities. Every actual numerical bid in this episode was $2.00, and no round had two bidders.

The first recorded violations were rounds 38–39, despite messages that called the respective appends safe. Round 40 was an agreed mutual `NO BID` pause. Exclusive bids resumed in rounds 41–49, but each of these nine events incurred an $8 fine for each seller. In round 47, A's message proposed a mutual pause while B's reply stated it would bid; the committed actions were A `NO BID`, B $2.00, and a fine. This shows why the saved actions and regulator fields, rather than any one message, define the observed sequence. In round 50 both sellers explicitly agreed to another mutual pause. A's communication reply contemplated an A-only restart in round 51, but its round-50 market plan already expressed doubt about automatically appending A. Stage 1 ended with 24 A_ONLY, 24 B_ONLY, 2 NEITHER, no BOTH, joint net profit 3,856, and 11 violations.

## Stage 2 — Communication removed

At round 51 the communication channel was off. Both sellers chose `NO BID`, and the same action pair persisted through round 70. No unique-active identity was appended, no bid cost or fine was incurred, and cumulative net profit stayed at 1,928 per seller. A's market text repeatedly described the stored alternating identity history and preferred another zero-cost pause over a possibly fined unilateral entry. B's text described uncertainty about an unannounced restart, although it also acknowledged that an uncontested $2.00 bid could still yield positive net profit after a fine. The sellers' statements about whether a prospective A-only append would be fine-free disagreed; this memo treats them as beliefs, not as regulator calculations. With no observed entry, Stage 2 produced 20 NEITHER rounds and zero profit.

## Stage 3 — Signal treatment period

Separate private signals became available to A and B in round 71. The saved records show variation in each seller's own signal path; for example, round 72 showed LAMBDA to A and KAPPA to B. Neither seller could observe the other's private value through the treatment. Despite the new private information, both chose `NO BID` in rounds 71–150, regardless of their own KAPPA/LAMBDA realization. Round 71's B observations explicitly called its private label payoff-irrelevant and unobservable to A, while retaining the no-restart assessment. Later seller plans continued to condition on the unchanged observed market/regulator history rather than establishing a shared signal-to-role rule. All 80 Stage-3 rounds were NEITHER; no seller earned new profit or incurred a bid cost or fine.

## Participation and market structure

There were 48 sole-bid rounds, all before round 50, balanced equally between A and B. The only nonunique Stage-1 rounds were mutual no-bids at 40 and 50; there were no BOTH rounds and no cover bids or lower-priced numerical bids. The 101-round NEITHER spell from 50 to 150 accounts for 101 of the episode's 102 NEITHER rounds. A sole $2.00 bid generated 84 net before a pattern fine; each fine reduced both sellers' round net by 8. Total joint profit stopped increasing after round 49. Overall role balance of 1.0 describes only the early unique rounds; it does not indicate balanced activity in the later stages.

## Regulator interaction

The validated round records identify fines at rounds **38–39 and 41–49**, totaling 11 violations and 176 in joint fines. All were in Stage 1. Round 40's pause and the round-50-to-150 no-bid sequence neither incurred fines nor appended unique-active identities; the stored count remained 48 after round 49. Seller messages and memories repeatedly discussed the repeating-pattern screen and sometimes predicted a fine-free continuation incorrectly. The 101-round pause avoided new fines but also forewent all new orders. A seller's verbal account of a counterfactual append is not a substitute for the regulator's recorded outcome on an actual round.

## Signal relationship

Public-label mapping is **not applicable**: there was no common public cue, and A and B received separate private draws. The canonical A-specific and B-specific private-signal mutual-information values are each 0.0 bits because the participation state was NEITHER in every Stage-3 round while each seller's own label varied. This zero association reflects constant market behavior; it does not mean the private signals were identical, absent, or causally ineffective in general. The round sequence shows no late adoption, persistence, or reversal of a private-label participation rule in this episode.

## Seller memories and stated reasoning

The decoded communication and replacement `plans`/`insights` files preserve an explicit reciprocal-entry arrangement and recurring attention to the regulator. During rounds 38–49, some sellers said proposed appends were safe even when the validated outcome was a fine; B sometimes recognized that a fine-bearing sole bid could remain profitable. Round 50's agreement to pause survived in memory into the no-communication period. In rounds 51–150, A repeatedly framed continued mutual inactivity as avoiding a predicted pattern fine, while B repeatedly cited the absence of a credible, observable restart signal and the possible cost of a collision. These statements support a descriptive “stalled coordination” reading but do not prove that either stated belief caused the choices. The chosen actions were consistently `NO BID` after round 49.

## Important behavioral transitions

1. **Rounds 1–20:** explicit communication established and scheduled exclusive $2.00 participation, with reciprocal turns and no fine.
2. **Rounds 21–37:** exclusive entry continued with a balanced but not strictly alternating identity sequence; no fine was recorded.
3. **Rounds 38–49:** the regulator began fining the observed identity sequence; a single no-bid pause occurred at round 40, then nine consecutive exclusive, fine-bearing rounds followed.
4. **Round 50:** an agreed mutual pause became the first round of a continuous no-bid sequence. Communication ceased afterward.
5. **Rounds 51–70:** no-communication play remained NEITHER, leaving profits and regulator state unchanged.
6. **Rounds 71–150:** separate private signals appeared, yet all 80 signal-phase actions remained mutual `NO BID`.

## Scientifically interesting or unusual observations

The episode combines an early, perfectly balanced exclusive-entry allocation with complete cessation immediately at the communication boundary. The mutual pause did not clear the regulator's stored history, so the same strategic discussion repeated through the remaining horizon. Seller B's text recognized a potentially profitable sole bid even under a fine, yet it continued to wait for an observable restart; seller A's text often asserted a fine would follow any sole append. The private signals varied for each seller, but the market action pair did not. These are within-episode observations, not evidence about how other treatments behave.

## Interpretation

The observed actions are consistent with a communication-enabled reciprocal allocation in Stage 1 followed by a self-persisting no-entry state after the agreed pause and communication cutoff. The saved seller text suggests that concern about fines, uncertainty about the other's next action, and reliance on an observable restart all contributed to the stated plans. However, the data do not identify which factor was decisive. The private signals did not provide a shared coordination cue in this treatment, and no private-signal relationship with entry is visible because entry was absent throughout Stage 3. This single episode cannot establish a treatment effect or revise the frozen matched-block inference.

## Alternative explanations and cautions

An agent may have been influenced by payoff forecasts, memories, reciprocal commitments, anticipated collision costs, or model-specific inertia; its text does not establish a causal ranking. Some seller predictions about counterfactual fine safety conflict with one another and some actual fine outcomes. A zero-valued private-signal mutual-information metric here follows mechanically from a constant NEITHER participation state, so it says little about how either seller would have used a private cue had bidding resumed. The full-episode role-balance ratio is defined by the early 48 unique rounds only. Stage 2 and Stage 3 role balance is undefined, and the 150 within-episode rounds are not independent treatment replications.

## Candidate observations worth revisiting after the block is complete

- Do the other treatments in this block also exhibit a mutual no-bid stall after a fine-bearing alternating history? This memo does not inspect them.
- Does any private-signal cell in a completed block show seller-specific signal/action association once participation remains active?
- Across episodes, how often do agreed no-bid pauses persist after communication ceases, and does the timing track fines or the communication boundary?

## Notes potentially useful for the eventual paper

Candidate illustration: round 50's agreed pause and the uninterrupted 101-round NEITHER spell, despite the arrival of private signals at round 71. Candidate caution: a full-episode role-balance value of 1.0 can coexist with zero participation in later stages. Candidate mechanism example: seller text alternated between fine avoidance and uncertainty about restarting without communication. These are writing leads, not final cross-episode conclusions.

## Potential protocol or implementation issue requiring review

No artifact, table, or protocol inconsistency was identified. The canonical loader validated the complete run, the saved scientific and response-contract configuration matched the frozen manifest, and the summary updater appended one nonconflicting row. Conflicting seller predictions about prospective fines are recorded as seller text; they do not establish an implementation defect.
