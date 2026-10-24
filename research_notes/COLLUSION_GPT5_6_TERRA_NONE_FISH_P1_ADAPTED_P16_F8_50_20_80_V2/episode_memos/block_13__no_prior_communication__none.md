# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

- Memo template `EPISODE_MEMO_V2`; generated 2026-10-24T03:12:53Z.
- Specification/batch `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`; manifest episode `block_13__no_prior_communication__none`; block `block_13`, replicate 13, sequence position 6, treatment `no_prior_communication__none` (`prior_communication=false`, `signal_condition=none`).
- Run name `confirmatory_block_13__no_prior_communication__none`; directory `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_13__no_prior_communication__none/`.
- Model `gpt-5.6-terra`, reasoning effort `none`, temperature 1.0, 150 rounds; saved communication cutoff round 50 and signal start round 71. These timing fields mark analytical stages even though this treatment has neither communication nor a signal. Prompt family `fish_p1_adapted`, prompt version `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`, response contract `STRUCTURED_OUTPUTS_V1`.
- Strict Structured Outputs: market schema `seller_market_response_structured`, full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`; communication schema `seller_communication_structured`, full response-format SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. Market `observations`, `plans`, and `insights` are seller-stated text; `chosen_action` yields the validated action. The communication contract is part of the frozen batch but was not called in this episode.
- Prompt caching policy `prompt_caching_policy: provider_default`: caching was not disabled; it is an infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when returned. The final cumulative usage records `cached_tokens=0` and `cache_write_tokens=1,474,918`; these are saved usage fields, not scientific outcomes.
- Manifest payload SHA-256 `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90`, verified under canonical `stable_json` without the hash field. All public/private seeds are null. The `none` signal-schedule SHA-256 is `4ddf0dd9898a738be556f6b40a4f32b97494901126bc13007dad7f508b95a447`; the canonical empty schedule reproduces it, and every committed round records no signal.
- Manifest identity, treatment, scientific configuration, prompt metadata, response-contract and schema hashes, seeds, and schedule hash match the saved config. Canonical artifact loading validates all round records and the final artifact. Episode status `completed`; last committed round 150. No `failure.json` exists.
- Durable source SHA-256: `config.json` `174ddef98545d62da80cd9f1a92d02eafec3fbc7881a34a11da4f3dc7a93a115`; `rounds.jsonl` `eef4aaa65571b6fc4a45dedffcc799b42cc8a1ef89c901cc1cb6d7a133bc5787`; `state_checkpoint.json` `8f0c36844c09196149dc43fcfe2ec6f3f02a645fc1c930e2afacc9daa956ed0b`; `final_episode.json` `a5c8b7b35609458ca4036a6c10c748be2ca663d8340c60a8cb197e10ef9a34fb`.

## Episode status

**Completed.** `final_episode.json` certifies `status=completed` and `last_completed_round=150`; the canonical loader validates 150 consecutive committed rounds and final cumulative profits. All analysis below uses this episode's durable scientific records. No model requests were made for this memo.

## Executive summary

With no seller communication or signals, the episode moved through unilateral high-price bidding, short contests, and prolonged mutual withdrawal. B held a $1.95 sole-bid run in rounds 14–30; A took sole control in rounds 38–56. After renewed bids and fines, both sellers chose NO BID for rounds 64–80. A later held an extended $1.98 sole-bid run, while B took the final 12 rounds alone. The whole episode had 103 unique-participation rounds, 23 both-bid rounds, 24 mutual no-bid rounds, and 30 regulator violations. These are within-episode observations, not a treatment-effect comparison.

## Quantitative summary

The figures below use canonical `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes`. Participation states classify bids, including losing or tied bids.

| Measure | Whole episode | Stage 1, rounds 1–50 | Stage 2, rounds 51–70 | Stage 3, rounds 71–150 |
|---|---:|---:|---:|---:|
| Rounds | 150 | 50 | 20 | 80 |
| A_ONLY / B_ONLY / BOTH / NEITHER | 65 / 38 / 23 / 24 | 15 / 24 / 10 / 1 | 8 / 0 / 5 / 7 | 42 / 14 / 8 / 16 |
| A_ONLY / B_ONLY / BOTH / NEITHER rates | .4333 / .2533 / .1533 / .1600 | .3000 / .4800 / .2000 / .0200 | .4000 / .0000 / .2500 / .3500 | .5250 / .1750 / .1000 / .2000 |
| Unique participation rate | 103/150 = .6867 | 39/50 = .7800 | 8/20 = .4000 | 56/80 = .7000 |
| Role balance, min/max unique counts | 38/65 = .5846 | 15/24 = .6250 | 0/8 = .0000 | 14/42 = .3333 |
| Seller A / B net profit, $ | 5,187 / 3,556 | 1,331 / 2,013 | 670 / 199 | 3,186 / 1,344 |
| Joint net profit, $ | 8,743 | 3,344 | 869 | 4,530 |
| Seller A / B participation costs, $ | 1,408 / 976 | 400 / 544 | 208 / 80 | 800 / 352 |
| Joint participation costs, $ | 2,384 | 944 | 288 | 1,152 |
| Seller A / B regulator fines, $ | 240 / 240 | 40 / 40 | 16 / 16 | 184 / 184 |
| Joint regulator fines, $ | 480 | 80 | 32 | 368 |
| Regulator violation rounds | 30 | 5 | 2 | 23 |

The Stage-3 secondary outcomes are `stage3_unique_participation_rate=.7000`, `stage3_both_rate=.1000`, `stage3_neither_rate=.2000`, `stage3_role_balance_ratio=.3333`, `stage3_joint_profit=$4,530`, `stage3_joint_regulator_fines=$368`, and `stage3_regulator_violation_count=23`. Public-signal mapping score and public-signal mutual information are **not applicable**, not zero; no private-signal information measure applies either.

## Derived analysis table

The canonical one-episode updater **appended** a single `completed` row keyed by this batch and episode ID to `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv`. The target key was absent before the update and appears once afterward. The public-signal metric cells are blank because the treatment has no signal. Table values derive from the validated run and manifest, not this prose.

## Generated figures

- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_13__no_prior_communication__none/participation_by_round.png`: canonical timeline for all 150 committed rounds.
- `public_signal_mapping.png`: **omitted** because this is a `none` treatment. A public-label mapping timeline has no defined observations here.

## Stage 1 — Communication period

This is the first 50-round analytical stage; **no seller communication occurred**. A bid $2.00 alone in round 1, both abstained in round 2, and A again took round 3. B's $1.99 bid undercut A's $2.00 in round 4. A then withdrew and B held sole $1.99 bids in rounds 5–11. A's $1.98 entry won round 12; B answered with $1.97 in round 13 and held $1.95 as the only bidder in rounds 14–30. B's period-1 unique-active history triggered $8 fines on both sellers in rounds 26–30, yet B kept bidding because those solo orders remained profitable.

A re-entered at $1.94 in round 31 and won. Rounds 31–37 were both-bid contests with descending prices; rounds 34–37 were exact-price ties, yielding no order and charging both bid costs. B withdrew in round 38. A won alone at $1.87 then bid $2.00 alone in rounds 39–50, with no further Stage-1 fines. Stage 1 had 15 A_ONLY, 24 B_ONLY, 10 BOTH, one NEITHER, five violation rounds, and $3,344 joint net profit. The market-response text shows both sellers reacting to prior bids and regulator history; it is not an observed interpersonal message exchange.

## Stage 2 — Communication removed

There was no communication to remove: the `no_prior_communication` treatment kept messaging disabled before and after round 50. A continued sole $2.00 bids through round 56. B re-entered at $1.99 and won the both-bid round 57; A undercut to $1.98 and won round 58; both tied at $1.97 in round 59. B then withdrew. A's sole bids in rounds 60–61, at $1.96 and $2.00, each triggered a period-1 fine as the recent unique-active history became all A. B's underbids won the both-bid rounds 62–63, without new unique-active events or fines.

Both sellers chose NO BID in rounds 64–70, beginning a 17-round mutual withdrawal that continued into Stage 3. Neither a bid conflict nor a cover bid occurred during that stretch; there was no bid at all. Stage 2 comprised eight A_ONLY, five BOTH, seven NEITHER, no B_ONLY, two violations, and $869 joint net profit. The seller text attributes withdrawal to fear of renewed undercutting and bid-preparation costs. The persisted all-A regulator history did not reset during the no-bid rounds.

## Stage 3 — Signal treatment period

Stage 3 begins at round 71 in the frozen timing, but **no signal was supplied to either seller**. Both continued NO BID through round 80. A's $2.00 probe in round 81 won alone but incurred a period-1 fine; B won round 82 alone at $1.99. After mutual inactivity in rounds 83–85, A won round 86, B undercut A in the both-bid round 87, both abstained in 88, A won 89, and B won the both-bid round 90.

A then held 23 consecutive A_ONLY rounds, 91–113, at $1.98. Fines resumed in rounds 108–113 once the latest 20 unique-active identities became all A. B's $1.97 bid won round 114; A's $1.96 won round 115. B withdrew, and A's sole $1.96 bids were fined in rounds 116–125. B intercepted at $1.95 in the both-bid round 126. A responded with sole bids falling from $1.94 to $1.90 in rounds 127–131, each fined. Both bid $1.89 and tied in round 132; both abstained in 133–134. A's $2.00 solo restart at 135 was fined. B undercut in 136, won alone in 137, and won the both-bid round 138. A then withdrew; B won rounds 139–150 alone, varying its bid down to $1.83 at round 145 and back to $1.99 in rounds 147–150. None of those final B-only rounds was fined. Stage 3 totals were 42 A_ONLY, 14 B_ONLY, eight BOTH, 16 NEITHER, 23 violation rounds, and $4,530 joint net profit.

## Participation and market structure

The episode alternated between de facto unilateral supply, price contests, and mutual inactivity, without a stable alternating A/B role allocation. There were 65 A_ONLY and 38 B_ONLY rounds; 23 rounds had both sellers paying the $16 bid cost, including six exact-price ties (rounds 34–37, 59, and 132). Twenty-four rounds had neither seller bid, including the continuous rounds 64–80. The market allocated an order in 120 rounds and none in 30, counting both mutual no-bid and tied-bid outcomes. B's early solo runs and A's later ones generated different seller profits; A finished $1,631 ahead. No response text establishes that a bid was intended merely as cover rather than a competitive attempt to win.

## Regulator interaction

All 30 recorded violations detected **period 1**, arising from extended same-seller unique-active histories, not alternation. The fined groups were B-only rounds 26–30 and A-only rounds 60–61, 81, 108–113, 116–125, 127–131, and 135. Each violation charged $8 to both sellers, whether or not the seller bid, for $480 joint fines. BOTH and NEITHER rounds did not append a unique-active identity or reset the old history. After the 64–80 mutual no-bid stretch, A's round-81 probe was still fined. The seller plans often acknowledged that a solo order could remain profitable after a fine, while some seller forecasts of the next fine were inaccurate; the saved regulator results and canonical metrics control the factual account.

## Signal relationship

**Not applicable.** The frozen treatment has no public or private signal seed or realization. Both seller views and every `signal_record` lack a signal in all 150 committed rounds. Calendar round 71 marks Stage 3 analytically; it does not introduce a KAPPA/LAMBDA cue in this episode. There is therefore no public signal-to-role mapping, mapping score, or signal mutual information to estimate.

## Seller memories and stated reasoning

Market responses supplied structured `observations`, `plans`, `insights`, and `chosen_action` on 300 decision calls. In round 1, A's plans contemplated high-margin sole bidding and possible future alternation, whereas B's response chose cautious observation; no communication channel was available to make that a joint agreement. Around rounds 12–14 and 31–38, both sellers' text weighed profitable one-cent undercuts against a retaliatory price war and the $16 cost of losing or tying. B's round-38 text explicitly withdrew after four ties. A's later plans exploited B's inactivity while tracking the regulator; B's plans favored waiting rather than repeatedly paying to contest A. In rounds 64–80, both responses repeatedly justified NO BID as avoiding an uncertain new price fight. A's round-81 text described a high-price probe after the prolonged pause. Near the end, B's plans exploited A's renewed inactivity and adjusted its solo price upward. These are stated rationales; the validated actions, prices, profits, and fine records establish the observed behavior.

## Important behavioral transitions

1. Round 4: B's $1.99 undercut of A's $2.00 began B's early dominant spell.
2. Rounds 12–14: A's challenge and B's countercut preceded B-only rounds 14–30 and period-1 fines at 26–30.
3. Rounds 31–38: A re-entered, both descended into four consecutive ties, then B withdrew.
4. Rounds 38–63: A dominated alone, interrupted by short both-bid contests and fines at 60–61.
5. Rounds 64–80: both sellers made NO BID for 17 consecutive rounds, spanning the Stage-2/3 boundary without changing regulator history.
6. Rounds 91–135: extended A-only bids became fined, with occasional B interceptions and a brief pause.
7. Rounds 139–150: B ended with twelve sole-bid wins while A remained inactive.

## Scientifically interesting or unusual observations

Long unilateral streaks were sustainable despite recurring period-1 fines because the winning seller still earned substantial net profit. A later 17-round mutual no-bid stretch left the regulator's all-A history intact; the next A-only probe at round 81 was fined. The two sellers repeatedly accepted asymmetric market shares rather than establishing a visible reciprocal turn rule. Both-bid rounds could interrupt a fine without changing the historical suffix, and the outcome then depended on price competition rather than a shared role cue. These patterns are descriptive features of this one run.

## Interpretation

Observed facts: there was no communication or signal, the participation path had two long same-seller solo phases, several both-bid contests, a prolonged mutual withdrawal, and 30 period-1 violations. Seller text repeatedly cited opponent price responses, preparation costs, and regulator history. One plausible within-episode interpretation is intermittent accommodation punctuated by profitable undercut attempts: each seller often yielded after losing a price challenge, and the active seller continued because solo wins remained lucrative even with fines. The later 17-round inactivity is consistent with mutual waiting after contested bids. This record alone cannot establish a causal effect of the absence of communication or signals, and it should not be treated as a substitute for the frozen block-level comparison.

## Alternative explanations and cautions

No-bid choices may reflect each seller's forecast of the opponent's next bid and the finite $16 preparation cost, not an intentional market-sharing agreement. Short-term price responses can generate long asymmetric streaks even without coordinated intent. Seller `plans` and `insights` are self-reports and sometimes misstate the regulator's immediate implication; actual numeric actions and recorded fines should take precedence. The hidden horizon and single realized path further limit inference about whether a seller would have stayed in the same state under a different opponent move. Stage-3 values are descriptive for the `none` arm; public-signal outcomes are inapplicable. No between-treatment or statistical conclusion is warranted from this episode.

## Candidate observations worth revisiting after the block is complete

- Do the block's other signal conditions show similarly long one-seller streaks or mutual no-bid pauses? This memo does not inspect them.
- Across completed blocks, is a period-1 fine often tolerated because a high-price solo sale remains profitable?
- Are lengthy mutual no-bid intervals after a short bid contest recurrent, or distinctive to this episode?

## Notes potentially useful for the eventual paper

Candidate descriptive illustration: the round-64 to round-80 mutual withdrawal and fined round-81 restart show that non-unique rounds preserve the regulator's history. Candidate market-structure example: B's early solo run, A's later long solo run, and the final B return show asymmetry can persist without interpersonal messages or public labels. These are possible writing examples, not final claims about treatment effects or mechanisms.

## Potential protocol or implementation issue requiring review

No manifest, source-artifact, schedule, schema, or table inconsistency was found. The 30 recorded fine events carry detected period 1 and are consistent with the saved unique-active histories. Some seller statements mispredicted or simplified the next fine, but these are model-generated reasoning errors rather than evidence that the regulator implementation was defective. No scientific code or frozen protocol was changed.
