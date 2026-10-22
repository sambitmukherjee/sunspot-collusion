# V2 Confirmatory Block Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. Formal confirmatory inference is governed by `docs/v2_confirmatory_analysis_plan.md`.

## Provenance

- Memo template: `BLOCK_MEMO_V2`; generated 2026-10-22T13:47:00Z.
- Specification/batch: `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`; block: `block_11`; replicate: 11.
- Canonical manifest payload SHA-256: `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` (excluding the hash field itself).
- Prompt family/version: `fish_p1_adapted` / `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; response contract: `STRUCTURED_OUTPUTS_V1`, with strict JSON Schema Structured Outputs.
- Market schema: `seller_market_response_structured`, full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`. Communication schema: `seller_communication_structured`, full response-format SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. Decoded communication `message` text, rather than its JSON wrapper, was shown to the other seller; the market `chosen_action` field yielded the validated action.
- Prompt caching: `prompt_caching_policy: provider_default`. Caching was not disabled. Provider-default caching is an infrastructure cost/latency optimization, not an experimental treatment; cached-token usage is logged when returned by the API.

The ordered manifest positions and run directories are below. The base of every listed run directory is `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/`.

| Position | Episode ID | Run directory under the base above | Validated status / last committed round |
| ---: | --- | --- | --- |
| 1 | `block_11__no_prior_communication__private` | `confirmatory_block_11__no_prior_communication__private/` | completed / 150 |
| 2 | `block_11__no_prior_communication__none` | `confirmatory_block_11__no_prior_communication__none/` | completed / 150 |
| 3 | `block_11__prior_communication__public` | `confirmatory_block_11__prior_communication__public/` | completed / 150 |
| 4 | `block_11__prior_communication__private` | `confirmatory_block_11__prior_communication__private/` | completed / 150 |
| 5 | `block_11__no_prior_communication__public` | `confirmatory_block_11__no_prior_communication__public/` | completed / 150 |
| 6 | `block_11__prior_communication__none` | `confirmatory_block_11__prior_communication__none/` | completed / 150 |

The two public entries share public seed `7922304033520780134` and signal schedule SHA-256 `fe056903b383fc4b12ea6c66a8e14439548cc2eacc1c876f44229e467b3f2995`. The private entries share A/B seeds `13140984580078846000` / `52555195821639269` and schedule SHA-256 `bc2f077e46b81c0de664ee65561158b6527b0d739db6132820c70f8a3d19242f`. Both no-signal entries have null active seeds and schedule SHA-256 `4ddf0dd9898a738be556f6b40a4f32b97494901126bc13007dad7f508b95a447`. These are frozen design checks, not outcome comparisons.

Source-artifact SHA-256 values, computed from each validated run directory:

| Position | `config.json` | `rounds.jsonl` | `state_checkpoint.json` | `final_episode.json` |
| ---: | --- | --- | --- | --- |
| 1 | `0a369d1cec898c853fa21a506f8ef0e8a6649eef5ea53d5506d24f4a25c4189d` | `f7b5abbc51defebb02dfce8945fb0b329bbf9024864071896bf242a53d032792` | `edf27089552ef67a94ebff3261d57e728106c769bd6b3b39999b7129d5509a08` | `a7252dd010c7f9e950e4cd7f26830acef7436346a6c708ae755fde8e54cff509` |
| 2 | `f9702bf194e255cab21785ac1ae83dacea8b72941af2b3c9f3cc2478d890ca03` | `083c04cb006879f57a9b7080e01cfd87ef087ba57601631a117611e7be3838dd` | `01e21bd548dd012ccfaaf2bbaab90c4562b606111126cc1227eb7002042fef7e` | `853d523a89a398fee9f5ae8b7b24594716554c49bdb108df7e66b0d9142db5fa` |
| 3 | `d57401d596c4147b55c57d286b533d6f347616fc02c065817550224b1d0f056a` | `21a00deebedff3069c046a9caa1de60d31f677db197df90aebcb8a555667798d` | `f2f35e33686ce50cbf2c7af6a45f1170e70e5245ba50af6dff037ae525a77880` | `3be3b3b57f6b8c829ca56524c55ae4a6ec480b944c405454ad137864461f5867` |
| 4 | `a2c4568040f9fcc79ca1826d4bf1aeac81589db1de88233913bbc22234b13b5d` | `80e4361892867a03a4ce00f3c4b8021d24c9423eb7ee4d066763a99eacf38794` | `581c87c9b4179e889c8e7258bfce60d2e5ea9fd00ba5a7d565071feece924937` | `db8e245dc0493a6864a21d6e999de7896901f81f41ec4e5d9a5c6a38b55e174a` |
| 5 | `8abd3c4a9b675ec68d5069d3d7792fe07120771eac26ebb60f6a6609c3e65909` | `5cfb84693ad143d3224773e295fc6111e0a38716091f5d377076b5da0ff8b5bf` | `035fe2798490b40d54a802753f65b1cf954435cbafed7f13c41c3fee18de10c3` | `dd17ad38c665d7ea86fc8b06838038cc837631208aeb398c8400525644171bc8` |
| 6 | `cf6c225a7d2149f84d9524553518d85b0b2e8ede77ee5ed02385db6b49363b0a` | `18f7b136ebcefd90801dcf2cf10821e55063ef70399a78585e8174cae00b714d` | `39d1af691217b62fc3b05663a90d27caa5f483f084fbfe539ec4954e18af5c9c` | `15e21cf7d8f0c47a4cb0ef8386f7e74af53e422b6f9fe7cba7f404e5c23e54a7` |

## Block completion/status

**Fully attempted and completed:** all six distinct manifest positions have validated `completed` terminal artifacts and 150 committed sequential rounds each; there are no failed or incomplete positions. The canonical manifest validator confirmed the frozen configuration, manifest hash, treatment cells, seeds, schedules, prompt provenance, and scientific settings. For every run, the saved run name, replicate, treatment, specification, prompt family/version, response contract, prompt-caching policy, schema names/hashes, and scientific config match its manifest row. The public/private pair schedules are shared as specified, and the no-signal seeds are null. This block memo uses only these six run records and, for qualitative orientation, their episode memos.

## Executive summary

**Observed:** In the matched public pair, prior communication coincided with a 0.95 public-label mapping score and 95% unique participation during Stage 3; the no-prior arm scored 0 and had 80 mutual no-bid rounds. The observed prior-minus-no-prior primary block difference is **+0.95**. The public ON seller text eventually named KAPPA→A and LAMBDA→B, and rounds 83–150 followed that mapping without exception. The private pair went in the opposite participation direction: the prior-communication arm stopped bidding from round 50 onward, while the no-prior arm had 35% unique participation and 60% BOTH in Stage 3. In the no-signal pair, prior communication coincided with continuous 2.00 exclusive turns and high regulator fines; the no-prior arm had contested bids and longer unilateral spells. One block illustrates heterogeneous trajectories; it does not establish the across-block effect.

## Six-episode quantitative overview

The rows follow manifest sequence order. Stage-3 state counts are `A_ONLY/B_ONLY/BOTH/NEITHER` over 80 rounds. `N/A` means a public-signal metric is not defined for private or no-signal treatments; `undefined` means no unique Stage-3 rounds for role balance. Monetary amounts and counts are exact. Every status is completed and every last committed round is 150.

| Pos. | Treatment (`prior communication`, signal) | Status / last | Public score | Public MI (bits) | Stage-3 states A/B/BOTH/NEITHER | Stage-3 unique / BOTH / NEITHER rates | Stage-3 role balance | Stage-3 joint profit | Stage-3 joint fines | Stage-3 violations |
| ---: | --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | OFF, private | completed / 150 | N/A | N/A | 2 / 26 / 48 / 4 | 0.35 / 0.60 / 0.05 | 0.0769 | 2979 | 96 | 6 |
| 2 | OFF, none | completed / 150 | N/A | N/A | 23 / 35 / 22 / 0 | 0.725 / 0.275 / 0 | 0.6571 | 3112 | 256 | 16 |
| 3 | ON, public | completed / 150 | 0.95 | 0.9778 | 31 / 45 / 2 / 2 | 0.95 / 0.025 / 0.025 | 0.6889 | 6192 | 128 | 8 |
| 4 | ON, private | completed / 150 | N/A | N/A | 0 / 0 / 0 / 80 | 0 / 0 / 1.00 | undefined | 0 | 0 | 0 |
| 5 | OFF, public | completed / 150 | 0.00 | 0.0000 | 0 / 0 / 0 / 80 | 0 / 0 / 1.00 | undefined | 0 | 0 | 0 |
| 6 | ON, none | completed / 150 | N/A | N/A | 40 / 40 / 0 / 0 | 1.00 / 0 / 0 | 1.00 | 5440 | 1280 | 80 |

For context, full-episode seller A/B profits by position were 1007/4696, 3010/3663, 4868/6212, 1928/1928, 1456/100, and 5524/5524. Stage-1 unique-participation rates in the same order were 0.86, 0.86, 0.88, 0.96, 0.42, and 1.00; Stage-2 rates were 0.60, 0.65, 0.90, 0, 0, and 1.00. These stage comparisons are descriptive diagnostics, not independent tests.

## Derived analysis tables

`results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv` already had exactly one canonical row for each of the six attempted block 11 positions, all with `episode_status=completed`; no episode row needed to be added or changed. It has 66 rows in the active batch after verification.

The canonical block updater **appended** the block 11 row to `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/block_summary.csv`: the table had 10 rows and no block 11 row before, and now has 11 rows and exactly one block 11 row. The row records six attempted/six completed episodes, `block_status=completed`, all six position identities/statuses, public scores 0.00 and 0.95, and observed public difference +0.95. It also stores the pre-specified Stage-3 secondary paired values and prior-minus-no-prior differences. Both CSVs are rebuildable from validated run artifacts; no memo value was copied into them.

## Generated figures

The canonical block figure is `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/block_plots/block_11/stage3_participation_composition.png`. It shows the six completed cells in fixed none/private/public × communication OFF/ON order, using the saved Stage-3 composition; it is descriptive, not a new confirmatory endpoint.

All six episode directories under `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/` already contained their applicable, nonempty canonical plots. Positions 1, 2, 4, and 6 each have `participation_by_round.png` only; a public mapping plot is inapplicable to their private/none treatments. Positions 3 and 5 each have both `participation_by_round.png` and `public_signal_mapping.png` (10-round windows). No applicable episode figure was missing or regenerated; none was overwritten. No multi-block distribution or paired-difference plot was made for this one block.

## Public matched pair

Both public arms used the same frozen public schedule. The canonical primary scores were 0.95 with prior communication and 0.00 without, so `D_11 = 0.95 − 0.00 = +0.95` in the specified prior-minus-no-prior direction. Public mutual information was 0.9778 versus 0 bits. Stage-3 unique-participation rates were 0.95 versus 0; BOTH rates 0.025 versus 0; NEITHER rates 0.025 versus 1.00. The prior arm had 6192 Stage-3 joint profit, 128 joint fines, and eight violations, versus 0 for each in the no-prior arm. The prior arm's Stage-3 role balance was 0.6889; the no-prior role balance is undefined because it had no unique-bidder rounds.

The prior arm's Stage-3 cross-tab was KAPPA: 31 A_ONLY and two NEITHER; LAMBDA: 45 B_ONLY and two BOTH. Rounds 71–76 matched KAPPA→A_ONLY/LAMBDA→B_ONLY while the sellers' plans still referred mainly to the earlier reciprocal turn rule. Rounds 77–82 included the four exceptions: LAMBDA/BOTH in 77 and 82, and KAPPA/NEITHER in 79 and 80. Seller B's saved plan by round 80 called the public code a convention; A's round-83 and round-84 plans moved toward and then named the same label-to-role rule. Every round 83–150 matched that orientation, 68 consecutive matches, with no regulator violation after round 81. These sustained actions plus seller statements support a within-episode descriptive convention reading, while the early code/role alignment could initially have been a chance overlap with the pre-existing turn sequence.

In the no-prior public arm, rounds 24–28 were simultaneous bidding or ties, followed by mutual NO BID from round 29 through 150. Both labels occurred in Stage 3—33 KAPPA and 47 LAMBDA—but all 80 outcomes were NEITHER. The zero score thus reflects absent role-bearing participation, not active but inconsistent code use. Seller text in early Stage 3 described no established shared code rule. The public-pair difference is an observed result for one matched block, not the across-block sign-flip test or a causal estimate on its own.

## Private matched pair

The private arms shared the frozen A/B private seed pair and schedule, but each seller saw only its own draw. Public mapping is not applicable. In the prior arm, explicit Stage-1 messages supported balanced 2.00 exclusive turns: 24 A_ONLY and 24 B_ONLY in Stage 1, plus two mutual pauses. Fines appeared in rounds 38–39 and 41–49. The agreed mutual pause at round 50 became the start of uninterrupted NEITHER through round 150. Stage 2 and Stage 3 therefore added no profit, fine, or violation despite varying seller-specific private labels. Canonical private mutual information was 0 bits for each seller because the four-state participation outcome was constant in Stage 3.

The no-prior private arm had no seller messages. Its Stage 3 comprised two A_ONLY, 26 B_ONLY, 48 BOTH, and four NEITHER rounds. Long contested-price episodes in rounds 71–81 and 85–116, then B's solo rounds 123–142, explain more than any simple private-label rule; A's seller-specific mutual information was 0.0406 bits and B's 0.0430 bits. There is no saved basis for treating those private values as a common cue or claiming that one seller observed the other's private draw. In prior-minus-no-prior order, the paired Stage-3 differences were −0.35 unique-participation rate, −2979 joint profit, −96 joint fines, and −6 violations. Prior-arm role balance is undefined with no unique participation, so a numeric role-balance difference is unavailable. This pair shows divergent realized histories, not an identified effect of private information in one block.

## No-signal matched pair

Neither arm received a Stage-3 signal. With prior communication, Stage-1 messages explicitly arranged reciprocal exclusive 2.00 turns. After the channel closed at round 51, the sellers continued a strict A-odd/B-even sole-bidder sequence through round 150. Stage 3 had 40 A_ONLY and 40 B_ONLY, 100% unique participation, role balance 1.00, and 5440 joint net profit. The same deterministic schedule triggered a fine to both sellers in all 80 Stage-3 rounds; all 80 were period-2 violations.

Without prior communication, Stage-3 play comprised 23 A_ONLY, 35 B_ONLY, 22 BOTH, and no NEITHER. It was organized in long unilateral spells and renewed price contests: B bid alone in rounds 80–111, while A supplied alone in rounds 136–150. Stage-3 unique participation was 0.725, role balance 0.6571, joint net profit 3112, and 16 violations. Prior-minus-no-prior differences were +0.275 unique-participation rate, +2328 joint profit, +1024 joint fines, and +64 violations. The control pair is consistent with persistence of a communicated role rule in the prior arm, but the one-block comparison cannot establish why the no-prior arm adopted its own history-dependent spells.

## Cross-treatment behavioral patterns

The six Stage-3 cells were markedly heterogeneous. The public ON arm had a sustained cue-associated split; the public OFF and private ON arms were entirely inactive; the private OFF arm mostly contested or let B bid alone; the none ON arm alternated exclusively; and the none OFF arm cycled through solo spells and competition. High unique participation did not imply low regulator cost: the none ON arm had the maximum Stage-3 unique rate and also 80 violations. Conversely, zero Stage-3 fines in two cells followed zero bids. These observations are features of the six validated episodes, not independent estimates of treatment effects.

## Communication-period patterns

Stage 1 covered rounds 1–50 for every treatment, before any public/private signal was revealed. In all three communication-ON arms, decoded messages proposed reciprocal exclusive 2.00 turns. The realized Stage-1 unique-participation rates were 0.88 (public ON), 0.96 (private ON), and 1.00 (none ON), with no BOTH round in any of these arms. The public ON arm inserted six mutual pauses and encountered four regulator violations; private ON inserted two pauses and encountered 11; none ON had no pause and one violation. Message transcripts show explicit agreement and attempts to track the regulator, though seller safety predictions sometimes failed.

The three communication-OFF arms had no messages. Their Stage-1 unique rates were 0.86 (private OFF), 0.86 (none OFF), and 0.42 (public OFF), with six, seven, and seven BOTH rounds respectively. Private OFF shifted from an A-only spell in rounds 8–21 to B-only in rounds 23–41, then B's fine-bearing solo extension; none OFF saw early ties, A-only rounds 14–34, and B-only entry after round 35. Public OFF had A-only rounds 4–21, price competition in rounds 24–28, and mutual withdrawal from round 29. Because future signal labels were unavailable in Stage 1, these differences cannot be ascribed to an early response to KAPPA/LAMBDA.

## Post-communication transfer patterns

At round 51 the three prior-communication arms lost the message channel. Public ON retained 18 unique-bidder rounds out of 20 in Stage 2, then developed the public-label mapping after the signal appeared at round 71. None ON kept its exclusive A/B schedule throughout Stage 2 and all of Stage 3 without any new cue. Private ON, by contrast, remained at mutual NO BID from its round-50 pause through both later stages; its private cues at round 71 did not restart bidding. These are distinct forms of post-communication persistence or cessation, not a uniform transfer result.

The OFF arms had no channel to remove. Public OFF was already mutually inactive by round 29 and stayed so through signal introduction. Private OFF entered Stage 2 with both bidding in rounds 51–57, later shifted to B-only, and continued price contests and B-dominant spells during private-signal Stage 3. None OFF retained B-only play at the round-50 boundary, then alternated between competition and solo spells in Stage 3. Changes at rounds 51 or 71 should be read against each episode's preceding trajectory, not treated as automatic responses to the stage label.

## Regulator interaction across the block

Full-episode violation counts in position order were 25, 27, 28, 11, 0, and 97; the corresponding joint fines were 400, 432, 448, 176, 0, and 1552. Stage-3 violations were 6, 16, 8, 0, 0, and 80. Public ON's early Stage-3 fines ended after round 81 as the later label-associated participation stabilized. Private ON accumulated 11 Stage-1 fines but no further fines after mutual withdrawal at round 50. None ON incurred its first fine in round 35, then fines every round 55–150, without abandoning exclusive alternation. The OFF private and none arms experienced fines during prolonged single-seller spells and later competition; public OFF had no violation because its short early activity never generated a screened violating sequence. Regulator events and fine timing are observed; the sellers' own prospective safety checks, and the apparent relationship between fines and later behavior, are interpretive evidence rather than proof of a causal response.

## Seller-memory and mechanism evidence

In the ON arms, Stage-1 decoded messages established stated exclusive-turn arrangements; the saved `plans` and `insights` carried those arrangements after communication stopped. The public ON arm offers the strongest direct text support for a later cue rule: B described a code convention by round 80, and A named KAPPA as its apparent turn and LAMBDA as B's by round 84, accompanying the round-83-onward perfect mapping. Earlier rounds 71–76 matched the same labels while A still wrote that it was following prior turns independently of the public code, an important distinction between observed correlation and stated mechanism. Private ON seller text instead described fear of renewed fines or collision and no reliable restart, consistent with—but not proving—the long mutual abstention. None ON text described keeping reciprocal 2.00 turns despite recurring period-2 fines. OFF arms had only individual memories and market responses: their bid changes and withdrawal spells are observed, while any implied tacit coordination remains an interpretation. JSON wrappers, response metadata, and seller-to-self memories are not additional seller communication.

## Scientifically interesting or unusual observations

- A shared public schedule accompanied very different realized Stage-3 outcomes: a 68-round perfect label/role run in the ON arm and 80 NEITHER rounds in the OFF arm.
- The public ON arm's first six Stage-3 matches preceded both sellers' explicit adoption of a code rule, illustrating why score and mutual information alone do not establish when a convention formed.
- Prior communication did not uniformly preserve active market sharing: private ON became completely inactive after round 49, while none ON continued exclusive alternation through round 150.
- The no-signal prior arm kept balanced high-price sole bids despite 80 consecutive Stage-3 regulator violations, whereas the public prior arm's cue-associated pattern had no violation after round 81.
- The OFF private and none arms displayed long role spells and bid conflicts without seller-to-seller messages, so exclusive participation by itself is not proof of an explicit agreement.

## Interpretation

This block is consistent with several possible routes from past interaction to later market behavior. Explicit early communication preceded durable no-signal alternation in one arm, a later public-label rule in another, and complete inactivity in the private arm. The public pair supplies a large positive observed block difference on the frozen primary outcome, with direct seller text supporting a within-episode public convention after its early transition. The private and no-signal controls show that the same prior-communication assignment did not produce one uniform continuation. Formal inference still rests on the frozen 30-block paired analysis; a single block does not identify the average treatment effect or a unique mechanism.

## Alternative explanations and cautions

The public ON arm began Stage 3 with an alternating schedule already in place, and the first six labels happened to match it. Sellers' later code-rule statements are stronger evidence for a later convention than that initial alignment, but their text remains self-report. The public OFF arm had withdrawn long before its first public cue; its zero mapping score reflects zero role-bearing outcomes. Private signals were separate seller observations, not shared randomness. Fines do not have a uniform observed effect across arms: they coincided with withdrawal in private ON, continued profitable alternation in none ON, and other changing bid patterns elsewhere. The six episodes are matched within one block, but their rounds are repeated observations, not independent units; interim numerical differences should not be interpreted as an experiment-wide causal result. Seller predictions about the regulator sometimes conflicted with validated fines, so outcomes take precedence over prose.

## Candidate cross-block questions

- Across completed blocks, how often does a public-label mapping arise after prior communication, and how often does it first overlap an existing time or history rule?
- How often do prior-communication private arms retain active sharing versus lapse into sustained mutual no-bid play after the channel closes?
- Does no-signal exclusive turn-taking persist despite repeated fines in other blocks, and how does its regulator cost compare with signal-conditioned rules?
- Are long no-prior role spells and price-contest phases common across treatments, or distinctive to this block?

These are questions for the pre-specified later synthesis, not additional tests run for this memo.

## Notes potentially useful for the eventual paper

Candidate illustrations include the public ON arm's transition from an inherited turn rule to a seller-stated KAPPA/A, LAMBDA/B rule; the public OFF arm's zero mapping from universal nonparticipation; and the none ON arm's persistence of balanced exclusive turns with large regulator cost. The private ON arm is a caution against treating prior communication as uniformly productive. Any eventual text should label these as block-specific examples, retain the distinction between seller statements and observed actions, and report formal across-block inference separately.

## Potential protocol or implementation issue requiring review

No artifact, table, or implementation inconsistency was identified. All six durable runs validate; the paired seeds and schedule hashes match the manifest; the episode and block tables contain unique, consistent rows; and all applicable plots exist. Occasional disagreement between seller-stated regulator predictions and recorded fines is seller behavior, not evidence of a code defect. No scientific code or frozen protocol was changed for this memo.
