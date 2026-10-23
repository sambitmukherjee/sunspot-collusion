# V2 Confirmatory Block Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. Formal confirmatory inference is governed by `docs/v2_confirmatory_analysis_plan.md`.

## Provenance

- Memo template: `BLOCK_MEMO_V2`; generated 2026-10-23 05:47 UTC.
- Specification/batch: `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`; block `block_12`, replicate 12. The manifest payload SHA-256, calculated with the repository's canonical `stable_json` after excluding the hash field, is `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90`.
- Prompt family `fish_p1_adapted`; version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; response contract `STRUCTURED_OUTPUTS_V1`; model `gpt-5.6-terra`, reasoning effort `none`. Market schema `seller_market_response_structured`, full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`; communication schema `seller_communication_structured`, SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. The decoded communication `message` enters the recipient prompt; structured `plans` and `insights` remain seller-stated text, while `chosen_action` yields the validated action.
- Prompt-caching policy: `provider_default`; caching was not disabled. It is an infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when returned by the API. No usage comparison is used here.
- All six saved configurations match their exact manifest rows on run name, replicate, treatment, specification, prompt family/version, response contract, caching policy, both response-schema names and hashes, signal seeds and schedule hashes, and all frozen scientific settings. The public pair shares its public seed and schedule hash; the private pair shares both seller-specific seeds and schedule hash; the none pair has null signal seeds. No manifest or scientific source was changed.

Ordered episode identities and statuses are below. Each durable run directory is `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/<run name>/`, using that row's exact run name.

| Position | Episode ID | Run name | Status | Last committed round |
|---:|---|---|---|---:|
| 1 | `block_12__no_prior_communication__public` | `confirmatory_block_12__no_prior_communication__public` | completed | 150 |
| 2 | `block_12__no_prior_communication__private` | `confirmatory_block_12__no_prior_communication__private` | completed | 150 |
| 3 | `block_12__prior_communication__private` | `confirmatory_block_12__prior_communication__private` | completed | 150 |
| 4 | `block_12__no_prior_communication__none` | `confirmatory_block_12__no_prior_communication__none` | completed | 150 |
| 5 | `block_12__prior_communication__public` | `confirmatory_block_12__prior_communication__public` | completed | 150 |
| 6 | `block_12__prior_communication__none` | `confirmatory_block_12__prior_communication__none` | completed | 150 |

SHA-256 fingerprints of the validated durable run sources are given below in position order. Each row refers to the run directory above. No `failure.json` exists in these canonical completed runs.

| Pos. | `config.json` | `rounds.jsonl` | `state_checkpoint.json` | `final_episode.json` |
|---:|---|---|---|---|
| 1 | `9d90cd2b146834b7f31ae394bb1dd18f1a46495e7ccde6dc640c5d2c97294469` | `c64dccd7e783bf203a069ad1e22c34faf91e311be0dd3ce756d8facf69c351b6` | `c101abfe4cb9094ee61a18f7c9681428c1050ad1d6b0b240e03e49a8a771fb47` | `71327d6546e1e90bb75aa4e4a4b70fc9ed001f3927f51c7c2870513e2c8527ff` |
| 2 | `f89711381b6118168917c97fc0b69b3cc6475a068cf666840f293c2533472101` | `f5fef0afb5dc821f841fb67d462b978d4f99cf3826d82147d9260e73a23aafdb` | `871ce09720ecd316775656be5ac9d043232a3c4594c291df604433671cf1f59e` | `ad35622e16cdf79978c37efd88653d5f946ee9a54f4eab82e8af1413e226114d` |
| 3 | `25c89d954b30cca4aba9d2385f977ca640ef487505503a19e35921cce792cab6` | `4b9a2ecafb87190ff95e50fb2a89051579a8694965b1c385d4bb03d5eee98427` | `d2c64fa7f03361464a52b7decd0cd8a6be03c4a11f0bee46c92ea26c141b63c1` | `e9e65861db5294ed690e713ed3816ae0eda8b4b8e51b2050f8d98ed66197753e` |
| 4 | `4bcf59c9e1104e14ee70a7f1d934629102437bbc1485f70dff1f06ff55cbf35f` | `62b14962acde5dc8198d00f99a3dd6762315a064e8514a89d25f4bf9bc09f6bf` | `31d7582153cd36c82a62e03b77b6faefeb75f5fe684c9eb7e6debee5a6772d90` | `3f890f9291c1ed45a3c911721a30ed9b0cb4d2d720293c12249195e01b1e5d35` |
| 5 | `490ef68c8320f96d6703b8aa5b838b475fda7882fea5e1f74e8418bb20e83362` | `bf1bede9f3c6be6f35d054bf9dfa470f61ca6f5e680b9350b97035d8dd0f87cd` | `404fd25f7a235eefc6885e075128311909e691b491fb7a5fc5489931935af654` | `9606b4318c400f1b624f47110f5709568c444cc5c7344a79484ad1ae7448b40f` |
| 6 | `007f8e9cec7fcb7446298a0a415c7684b6d099252ee0cb17b5119c2a163f89e5` | `660117fe39d8b066e87e3a225b86828dca6027a9bdc1288c75c466a60d0d1a6f` | `5dd548e394bf7ac492f9e14aaf280bd480408b6806798301f6550997b35dc31d` | `fba46a96dc03e9a80383857dd2b1af5a73b036f63fec8c6ba95b4d24622d8441` |

## Block completion/status

**Fully attempted and completed: six of six episodes, each with 150 sequential committed rounds and a validated `final_episode.json`.** The canonical artifact loader, not the console logs or episode memos, establishes completion. No failed or incomplete scientific episode enters this block comparison. The block table has `block_status=completed`.

Position 4 also has a preserved, separate first execution attempt that failed before any usable model response or scientific round because the restricted execution environment could not resolve `api.openai.com`. Its archived provenance is at `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/execution_attempts/block_12__no_prior_communication__none/attempt_001_pre_response_technical_failure/provenance.json`. The unchanged manifest episode completed on attempt 2; `attempt_002_outcome.json` in that episode's execution-attempts directory links the successful canonical run. The pre-response failure is execution provenance, not a second scientific observation or a missing block outcome.

## Executive summary

The two matched public episodes used exactly the same KAPPA/LAMBDA schedule, but neither showed a sustained public-label-to-seller rule. Prior communication produced balanced $2.00 turn-taking across all 80 Stage-3 rounds, whereas the no-prior arm had A alone in all 80; the public mapping scores were 0.5125 and 0.5375 respectively, so the observed prior-minus-no-prior difference was **−0.025**. The private pair showed lower Stage-3 regulator fines and more balanced roles with prior communication, alongside more bid conflicts. The no-signal pair diverged sharply: after an explicitly coordinated pause, the prior-communication arm chose mutual NO BID in every Stage-3 round, while the no-prior arm remained active in 78 of 80 rounds. These are within-block observations; one block does not establish a treatment effect.

## Six-episode quantitative overview

All values below are recomputed with the canonical `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes` functions. Stage 3 is rounds 71–150. `ON` and `OFF` refer to prior communication in rounds 1–50. Public mapping and mutual information are **N/A** for private and none treatments. Balance is undefined if there is no unique-participation round. Rates are fractions of the 80 Stage-3 rounds.

| Pos. | Treatment | Episode ID | Status / last round | Public score | Public MI (bits) | Stage-3 unique | BOTH | NEITHER | Role balance | Stage-3 joint net | Stage-3 joint fines | Stage-3 violations |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | public OFF | `block_12__no_prior_communication__public` | completed / 150 | 0.5375 | 0 | 1.0000 | 0 | 0 | 0 | $5,088 | $1,152 | 72 |
| 2 | private OFF | `block_12__no_prior_communication__private` | completed / 150 | N/A | N/A | 0.8875 | 0.1125 | 0 | 0.0143 | $4,430 | $1,120 | 70 |
| 3 | private ON | `block_12__prior_communication__private` | completed / 150 | N/A | N/A | 0.7875 | 0.2000 | 0.0125 | 0.7500 | $5,083 | $192 | 12 |
| 4 | none OFF | `block_12__no_prior_communication__none` | completed / 150 | N/A | N/A | 0.8750 | 0.1000 | 0.0250 | 0.1864 | $5,871 | $384 | 24 |
| 5 | public ON | `block_12__prior_communication__public` | completed / 150 | 0.5125 | 0.000453 | 1.0000 | 0 | 0 | 1.0000 | $5,440 | $1,280 | 80 |
| 6 | none ON | `block_12__prior_communication__none` | completed / 150 | N/A | N/A | 0 | 0 | 1.0000 | undefined | $0 | $0 | 0 |

Stage-3 state counts in the same order (`A_ONLY`, `B_ONLY`, `BOTH`, `NEITHER`) are: position 1 `(80,0,0,0)`, 2 `(1,70,9,0)`, 3 `(36,27,16,1)`, 4 `(59,11,8,2)`, 5 `(40,40,0,0)`, and 6 `(0,0,0,80)`. Full-episode seller A/B net profits were, respectively: position 1 `$6,951/$3,193`; 2 `$475/$8,408`; 3 `$5,734/$4,404`; 4 `$7,580/$2,241`; 5 `$5,456/$5,540`; 6 `$1,848/$1,596`. These profits include participation costs and regulator fines.

Canonical Stage-1 state counts (`A_ONLY`, `B_ONLY`, `BOTH`, `NEITHER`) were position 1 `(5,38,6,1)`, 2 `(0,30,20,0)`, 3 `(26,24,0,0)`, 4 `(29,7,8,6)`, 5 `(24,26,0,0)`, and 6 `(22,19,0,9)`. Stage-2 counts in the same order were `(11,8,1,0)`, `(0,16,4,0)`, `(8,3,1,8)`, `(3,9,4,4)`, `(10,9,0,1)`, and `(0,0,0,20)`. Those stage descriptions explain the timing of the Stage-3 differences; they are not independent treatment replicates.

## Derived analysis tables

The six canonical rows in `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv` were **already present and identical** to rows rebuilt from their validated runs; the updater left them unchanged. Each has the unique `(batch, episode_id)` key and `episode_status=completed`. The canonical block updater **appended** the new `(batch, block_12)` row to `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/block_summary.csv`. It records six attempted/completed positions, `block_status=completed`, and the observed public difference of −0.025. These tables are rebuildable derived products; no memo prose was used to populate them.

## Generated figures

- Generated: `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/block_plots/block_12/stage3_participation_composition.png`, using the canonical `plot_block_stage3_participation_composition` on this block's six validated episodes. It displays one completed Stage-3 composition per treatment cell.
- Verified existing, without overwriting: `participation_by_round.png` for each of the six episode IDs in `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/<episode_id>/`.
- Verified existing, without overwriting: `public_signal_mapping.png` for positions 1 and 5 in their corresponding episode plot directories. This plot is not applicable to the four private/none episodes. No plot was missing or regenerated.

## Public matched pair

**Observed primary block contrast, prior minus no prior:** `0.5125 − 0.5375 = −0.025`. The two arms share the frozen public seed and schedule: KAPPA occurred 43 times and LAMBDA 37 times in Stage 3. In public OFF, A_ONLY occurred in all 80 rounds; the score 43/80 simply favors the more common label under a fixed A-only state, and public mutual information was 0 bits. The seller switch to A_ONLY occurred at round 60, before the public labels appeared at round 71. Public ON instead continued an alternating exclusive $2.00 allocation: B on odd rounds and A on even rounds 71–150. KAPPA paired with A_ONLY/B_ONLY 21/22 times and LAMBDA 19/18; the best fixed mapping matched 41/80 rounds, with mutual information 0.000453 bits. The public-ON seller text at round 71 explicitly called KAPPA payoff-irrelevant and continued the earlier turn rule. Both labels appeared under both roles. Neither episode supplies behavioral or textual evidence of a stable public-label convention; the rolling mapping figures reflect local label composition, not sustained adoption.

Both public arms had unique participation in all 80 Stage-3 rounds, but role balance was 0 in OFF and 1 in ON. Public ON had $5,440 Stage-3 joint net profit versus $5,088 OFF, a canonical paired difference of +$352; joint fines were $1,280 versus $1,152 (+$128), and violations 80 versus 72 (+8). The ON arm's repeated period-2 role sequence was fined in every Stage-3 round. The OFF arm's all-A history began a continuous fine sequence at round 79. These shared-schedule comparisons describe this block; they are not the experiment-wide sign-flip test.

## Private matched pair

Each private arm used the matched frozen A/B private-signal streams; each seller saw only its own label. In private OFF, B was already dominant before signals: B_ONLY occurred in 30 of 50 Stage-1 rounds and 16 of 20 Stage-2 rounds. Stage 3 then had 70 B_ONLY, 1 A_ONLY, 9 BOTH, and no NEITHER rounds. In private ON, the 50 communication rounds had explicit, balanced exclusive $2.00 allocations, 26 A_ONLY and 24 B_ONLY, without a fine. After communication ended, round 55 incurred a fine, rounds 56–62 were mutually inactive, and later roles shifted: A alone at rounds 66–84, B alone for much of rounds 93–117, and A again at rounds 130–150. Its Stage 3 had 36 A_ONLY, 27 B_ONLY, 16 BOTH, and 1 NEITHER.

Canonical prior-minus-no-prior Stage-3 differences were unique participation −0.1000, BOTH +0.0875, NEITHER +0.0125, role balance +0.7357, joint profit +$653, joint fines −$928, and violation count −58. Seller-specific private-label mutual information was small: OFF A 0.0115 bits and B 0.0191; ON A 0.0150 and B 0.0350. These values do not identify a common cue or demonstrate that either seller inferred the other's private state. The greater role balance in ON coexisted with more contested bids and some post-communication instability; it should not be described as a simple uninterrupted transfer of the early agreement.

## No-signal matched pair

Neither arm received Stage-3 labels. None OFF developed long sole-seller spells, price contests, and occasional mutual pauses without direct communication; Stage 3 had 59 A_ONLY, 11 B_ONLY, 8 BOTH, and 2 NEITHER rounds. None ON had 41 uncontested $2.00 bids through round 42, then 108 consecutive mutual NO BID rounds 43–150. Its Stage-3 activity was zero. The canonical prior-minus-no-prior Stage-3 differences were unique participation −0.875, BOTH −0.100, NEITHER +0.975, joint profit −$5,871, joint fines −$384, and violations −24; the role-balance difference is undefined because ON had no unique Stage-3 round.

The ON sellers explicitly coordinated both the early exclusive turns and the subsequent pause. At round 43 they stated that either next exclusive identity would trigger a regulator fine. Applying the canonical period detector to the stored post-round-42 history, however, finds **neither candidate append** periodic for lengths 1–8. This check identifies a mistaken seller-stated forecast at the transition, not an observed counterfactual bid. In contrast, OFF continued to trade without a new cue. The control pair illustrates sharply different trajectories in this block, but does not by itself establish that communication caused inactivity.

## Cross-treatment behavioral patterns

Public ON and private ON both began with explicit high-price exclusive allocations, yet public ON preserved balanced turn-taking through Stage 3 while private ON moved through pauses, price contests, and long single-seller spells. None ON shared the early exclusive pattern but became permanently inactive after round 42. Among OFF arms, public became all-A from round 60, private was heavily B-dominant, and none alternated longer spells with contests. Thus Stage-3 participation was sensitive to the history formed before signals, and the same communication availability did not correspond to one uniform later pattern. The histories are observed; the source of differences across independent episode trajectories is not identified by this block alone.

## Communication-period patterns

The three ON episodes had actual messages in rounds 1–50. Public ON and private ON recorded exactly one $2.00 bidder in every such round, with nearly balanced role counts (24/26 and 26/24 A_ONLY/B_ONLY). None ON had 41 exclusive $2.00 bids and 9 mutual no-bid rounds, including rounds 43–50. Messages named the planned active seller and discussed modifying the 20-event identity suffix to avoid fines; actions largely followed those allocations. Public ON incurred two Stage-1 violations at rounds 36–37; private ON and none ON incurred none.

The three OFF episodes had no seller communication despite the temporal Stage-1 label. Public OFF had six BOTH rounds, private OFF 20, and none OFF eight, including observable ties or undercutting contests; their Stage-1 regulator violations were 7, 11, and 10 respectively. Future signal assignments were not revealed in Stage 1, so these early differences cannot be credited to later KAPPA/LAMBDA realizations.

## Post-communication transfer patterns

Public ON continued the earlier exclusive arrangement when direct messages ceased at round 51. Its round-58 mutual pause did not append a regulator identity or reset the history; B resumed exclusive bidding in round 59, and the alternating rule persisted through the public-label phase. Private ON also continued sole $2.00 turns briefly, but the round-55 fine preceded seven consecutive mutual no-bid rounds (56–62), followed by a round-64 tied bid and an A-only stretch from round 66. None ON's mutual pause began at round 43, **before** communication ceased, and continued through every Stage-2 and Stage-3 round. Thus persistence after round 50 differs among ON treatments and cannot be ascribed solely to removal of the channel.

In OFF treatments the round-51 boundary removed no active channel. Public OFF switched to A as sole bidder at round 60, private OFF remained B-dominant at the signal boundary, and none OFF returned to A-only bidding at round 68. At round 71, public ON retained its role-turn schedule despite the common label; public OFF stayed A_ONLY. Private arms saw separate seller-specific labels and retained patterns already developing by round 70. None arms received no new cue. These timing facts constrain interpretation of any Stage-3 association.

## Regulator interaction across the block

Full-episode violation counts and joint fines in manifest order were: position 1 `80 / $1,280`, 2 `97 / $1,552`, 3 `14 / $224`, 4 `34 / $544`, 5 `95 / $1,520`, and 6 `0 / $0`. Every triggering event fined both sellers $8, so joint fines equal $16 times violations. BOTH and NEITHER rounds did not append a unique-active identity; they could pause the screen but did not erase its history.

The public OFF all-A Stage-3 run became fine-triggering at round 79 and remained so through 150. Public ON's alternating history triggered the period-2 fine at rounds 36–37, escaped briefly after a repeated B identity at round 38, and became continuously fine-triggering again from round 59. Private OFF's B-dominant history generated 70 Stage-3 violations; private ON had 12, around long single-seller runs and a few other append events. None OFF had 24 Stage-3 violations, predominantly in A-only stretches; none ON had none because it never appended an identity after round 42. The continuation of bidding while fines applied is consistent with positive immediate net payoffs on many exclusive sales; the records do not reveal responses to a different regulator rule.

## Seller-memory and mechanism evidence

In the ON arms, decoded communication messages explicitly assigned who should bid and who should abstain. The saved structured `plans` and `insights` carried these seller-stated intentions into later calls. Public ON's round-71 market `observations` referred to the prior exclusive schedule and described KAPPA as irrelevant to it; the exact actions continued alternating. Private ON's messages likewise discussed safe identity appends, but later observed conflicts show that the early arrangement did not remain stable. None ON's round-43 messages agreed to joint abstention on a mistaken fine forecast, and later `observations` repeated that belief. These texts are evidence of stated reasoning, not proof that a particular belief caused each subsequent action. OFF-arm text largely framed bids around observed prices, expected retaliation, and net payoffs; it did not show an explicit public-label convention or a shared private cue.

## Scientifically interesting or unusual observations

- Under the identical public schedule, both arms had 100% unique Stage-3 participation yet very different role balance: 0 in OFF and 1 in ON. Neither showed a substantial public-label association.
- Public ON sustained an explicit high-price turn schedule even while every Stage-3 round incurred a period-2 fine; public OFF sustained a single-seller state through repeated fines.
- Private ON combined more balanced Stage-3 roles and fewer fines than private OFF with **more** BOTH rounds, so role balance, joint profit, and coordination stability do not move in a single direction.
- None ON stopped trading from round 43 onward after a seller-stated regulator forecast that the saved regulator state does not support. The pause persisted after messages ended and throughout the no-signal period.

## Interpretation

**Observed:** prior communication was followed by explicit exclusive allocations in all three ON arms during Stage 1. Later outcomes separated: public ON preserved balanced turn-taking, private ON partly unraveled and reorganized, and none ON remained mutually inactive. The public score contrast of −0.025 shows no favorable mapping difference for prior communication in this block, despite the ON arm's role balance. **Interpretation:** early messages can establish a history-based rule, but the later path may depend on fine forecasts, turn expectations, and price competition. The six episode trajectories support those possibilities without identifying one causal account or a block-independent effect.

## Alternative explanations and cautions

This is one of 30 planned matched blocks, so these differences can reflect stochastic model choices and path dependence. The public score is sensitive to label frequency when one seller always participates; a score just above 0.5 is not evidence of a signal convention. Public ON's nearly zero mutual information and exact odd/even rule help interpret its score, while the no-prior arm's zero mutual information establishes a constant Stage-3 state. Private labels were seller-specific, so aggregate signal associations cannot be treated as common knowledge. Seller text sometimes miscalculates the regulator screen, and the no-signal ON counterfactual check does not tell us what either seller would actually have done after a different bid. The 80 rounds within an episode are not independent primary treatment comparisons. Formal inference remains reserved for the frozen across-block analysis.

## Candidate cross-block questions

- How often does prior communication produce balanced high-price turn-taking without public-label mapping?
- Does a pause after an unexpected fine or a mistaken fine forecast persist beyond the communication window in other blocks?
- Are private-treatment role balance and regulator fines generally more favorable after prior communication even when bid conflicts rise?
- Do no-prior public episodes often settle into one seller's persistent role before labels appear?

These are questions for later analysis; no other block was inspected or used to adapt execution here.

## Notes potentially useful for the eventual paper

Candidate illustration: the six-cell Stage-3 composition figure makes the distinction between balanced turn-taking, single-seller persistence, and mutual inactivity visible. Candidate mechanism examples: public ON maintained an odd/even turn rule while labels changed; none ON sustained a pause built on an incorrect seller-stated fine prediction. Candidate caution: a positive public mapping score can arise from label imbalance with a constant seller role. These are possible writing notes, not final results claims.

## Potential protocol or implementation issue requiring review

No artifact, manifest, table, schema, or plotting inconsistency was found. The none-ON sellers' post-round-42 fine prediction conflicts with the canonical period detector on the saved state, but this is an error in seller-stated reasoning rather than evidence of a regulator implementation defect. No scientific code, protocol, or episode artifact was changed.
