# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

| Item | Recorded value |
|---|---|
| Memo template | `EPISODE_MEMO_V2` |
| Generated | 2026-10-19 18:05 UTC |
| Specification / batch | `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2` |
| Episode ID | `block_05__prior_communication__private` |
| Run name | `confirmatory_block_05__prior_communication__private` |
| Run directory | `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_05__prior_communication__private/` |
| Block / replicate / manifest position | `block_05` / 5 / 5 |
| Treatment | `prior_communication__private`; prior communication `true`; seller-specific private signals |
| Model / reasoning / temperature | `gpt-5.6-terra` / `none` / 1.0 |
| Prompt family / version | `fish_p1_adapted` / `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1` |
| Response contract | `STRUCTURED_OUTPUTS_V1` |
| Market response schema | `seller_market_response_structured`; SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2` |
| Communication response schema | `seller_communication_structured`; SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c` |
| Prompt caching | `provider_default`: not disabled; provider default behavior; infrastructure cost/latency optimization, not a treatment; cached-token usage logged when returned by the API |
| Manifest payload SHA-256 | `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` |
| Private seeds A / B | `7086530279059433126` / `7340459535553886451` |
| Signal schedule SHA-256 | `6beacb234c724d700d0c0c8e29e28c0ac87cefcad1af7d4c0fffb207e21276b9` |
| Episode status / last committed round | `completed` / 150 |

The canonical manifest loader and `validate_selected_manifest` verified the frozen payload hash. `load_episode_artifacts` validated 150 contiguous committed rounds and the final artifact. Saved configuration matches the manifest row for identity, treatment, prompt, response contract, caching policy, schema names and hashes, seeds, schedule hash, and every `scientific_config` field. There is no `failure.json`. The saved episode ran from 2026-10-19 17:36:23 UTC to 18:02:39 UTC, approximately 26.3 minutes.

SHA-256 of durable source files:

| Source | SHA-256 |
|---|---|
| `config.json` | `8971aa7907462342ca7a07052e96740fd1da334e634de7570b4d53589009b2a4` |
| `rounds.jsonl` | `e99fb92396e2b4b86f361007203d78519f338d1792ea2c47ea6523f2aa0faa4e` |
| `final_episode.json` | `26a3868850d2b4e2f8c03362729fe70e9b96651a0b2ca962b1f7f9805ea6bd6b` |
| `state_checkpoint.json` | `651eb61215e35df63ba635f1e1b97095484719e04dd5a85ea5851d9022379918` |

## Episode status

**Completed.** `rounds.jsonl` contains rounds 1–150, and `final_episode.json` records `status: completed` with `last_completed_round: 150`. Communication was enabled in rounds 1–50, with two recorded communication calls per round, then disabled in rounds 51–150. Private signals were absent through round 70 and present separately to A and B in rounds 71–150; there was no public signal. The complete horizon supports the reported full-episode outcomes.

## Executive summary

The sellers explicitly coordinated exclusive 2.00 bids during communication, yielding nearly all early rounds to one seller while the other chose NO BID. Alternation continued after communication ceased. When private signals arrived, rounds 71–72 briefly disrupted the schedule: both abstained, then both bid 2.00 and tied. From round 73 onward the sellers resumed exact A/B exclusive alternation at 2.00 through round 150, regardless of their separate private signal realizations. The regulator fined both sellers on every one of those 78 Stage-3 unique-active rounds because the trailing history remained period-2. The completed episode had 145 unique-active rounds, 88 violations, and joint net profit 10,740. These are within-episode observations, not a treatment-effect estimate.

## Quantitative summary

Participation states are classified from numerical bids, not from who received an order. Profit is net of recorded bid costs and regulator fines. Stage summaries describe portions of one episode, not independent observations.

| Period | Rounds | A_ONLY | B_ONLY | BOTH | NEITHER | Unique rate | Role balance | A profit | B profit | Joint profit | Joint participation cost | Joint fines | Violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stage 1, 1–50 | 50 | 23 | 24 | 0 | 3 | 0.940 | 0.958 | 1,916 | 2,000 | 3,916 | 752 | 32 | 2 |
| Stage 2, 51–70 | 20 | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 776 | 776 | 1,552 | 320 | 128 | 8 |
| Stage 3, 71–150 | 80 | 39 | 39 | 1 | 1 | 0.975 | 1.000 | 2,636 | 2,636 | 5,272 | 1,280 | 1,248 | 78 |
| Full episode | 150 | 72 | 73 | 1 | 4 | 0.9667 | 0.9863 | 5,328 | 5,412 | 10,740 | 2,352 | 1,408 | 88 |

Full-episode rates were A_ONLY 0.4800, B_ONLY 0.4867, BOTH 0.0067, and NEITHER 0.0267. The full-episode absolute profit gap was 84 in B's favor. Participation costs were 1,168 for A and 1,184 for B. Regulator fines were 704 for each seller, or 1,408 jointly. The role-balance ratio is `min(A_ONLY, B_ONLY) / max(A_ONLY, B_ONLY)`.

| Pre-specified Stage-3 secondary outcome | Value |
|---|---:|
| `stage3_unique_participation_rate` | 0.975 |
| `stage3_both_rate` | 0.0125 |
| `stage3_neither_rate` | 0.0125 |
| `stage3_role_balance_ratio` | 1.000 |
| `stage3_joint_profit` | 5,272 |
| `stage3_joint_regulator_fines` | 1,248 |
| `stage3_regulator_violation_count` | 78 |

The canonical seller-specific private-signal mutual information values were **A: 0.02064 bits** and **B: 0.04229 bits**, each relating that seller's own private signal to the four-state participation outcome over Stage 3. They do not form a common public-signal measure. `public_signal_mapping_score` and `public_signal_mutual_information_bits` are **not applicable**, rather than zero. Values above come from `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes`.

## Derived analysis table

The canonical `update_episode_summary_table` appended one row to `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv`. The table existed with 28 rows and no row for this `(batch, episode_id)`; it now has 29 rows and exactly one matching row with `episode_status: completed` and `last_committed_round: 150`. No conflicting row was found. The table is derived from the validated run artifacts, not from this memo.

## Generated figures

- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_05__prior_communication__private/participation_by_round.png` — canonical participation-state timeline for all 150 committed rounds.
- `public_signal_mapping.png` was **omitted** because this is a private-signal episode. The canonical public-label mapping plot is not applicable.

## Stage 1 — Communication period

Both sellers used the enabled communication channel. In round 1, A proposed alternating exclusive 2.00 bids so as to avoid a bidding war; B agreed and chose NO BID while A bid. B proposed an irregular A/B sequence in round 2, and both then sent confirmations of exclusive turns. The first 19 rounds were unique-active, with early irregularity rather than perfect round-by-round alternation; every observed numerical bid was 2.00. The seller messages explicitly contemplated manipulating the regulator's trailing unique-active history while preserving exclusive access. No cover bids or lower-price competitive bids appeared in this stage.

At round 20, both sellers communicated a mutual NO BID pause, which they repeated at round 21, so the unique-active history did not advance. Their messages predicted that an immediate 20th unique-active event would be fined. They resumed in round 22 with B alone at 2.00; **the durable regulator record shows no fine in round 22**, despite both sellers' stated prediction. Exclusive turns continued. The first actual violations were rounds 41–42, each fining both sellers 8. Their round-41 messages had described the planned A-only append as fine-free, another incorrect forecast; round-42 text acknowledged the resulting fine. They mutually chose NO BID again in round 43, then returned to B-only in round 44 and reciprocal exclusive turns through round 50. Stage 1 ended with 23 A_ONLY, 24 B_ONLY, and three NEITHER rounds, plus joint net profit 3,916.

## Stage 2 — Communication removed

The message channel ended after round 50. Round 50's final decoded exchange confirmed B's exclusive turn and expected A to take the next; round 51 did exactly that without a new communication call. The sellers continued exclusive 2.00 bids, A and B alternating every round through round 70. There were no BOTH or NEITHER rounds. Their saved market-response `observations` and `plans` referred to the recent bids, the reciprocal schedule, and the regulator history, providing a stated basis for continued coordination without new seller messages.

Rounds 51–62 were fine-free. Appending A in round 63 restored a perfectly alternating trailing 20-event history, and rounds 63–70 each triggered the period-2 regulator fine. The sellers continued the exclusive turns despite the fines; their text noted that an active 2.00 winner still nets 76 after a fine. Stage 2 had 10 A_ONLY and 10 B_ONLY rounds, equal seller net profits of 776, and eight violations. Mutual NO BID pauses had deferred unique-active events earlier but had not changed the regulator's stored sequence; the round-63 fine made that limitation visible.

## Stage 3 — Signal treatment period

Separate private KAPPA/LAMBDA signals began in round 71. Both sellers happened to receive KAPPA in rounds 71–72, but those are two *private* realizations, not a public announcement. Round 71 was mutual NO BID: A's text proposed a pause to disrupt predictable alternation, while B expected to yield for A's turn. The pause did not alter the unique-active history. In round 72, A and B each bid 2.00, tied, received no order, each paid the bid cost, and did not append a unique-active identity. Their stated plans disagreed about whose turn had been deferred by the pause.

The sellers restored A-only in round 73 and B-only in round 74. They then alternated without exception through round 150: odd rounds A-only, even rounds B-only, always bidding 2.00. Their private signals sometimes differed while the same turn-taking rule held; for example, A received KAPPA and B LAMBDA in both rounds 73 and 74, yet A was active in 73 and B in 74. Saved market-response text in rounds 75, 100–101, and 149–150 explicitly appealed to the previous unique-active seller and called the private codes irrelevant. All 78 unique-active Stage-3 rounds, 73–150, triggered fines for both sellers. Each seller earned 2,636 net in Stage 3, reflecting 39 own active and 39 rival active turns, the round-72 bid tie, and the repeated fines.

## Participation and market structure

The dominant outcome was exclusive supply at the maximum allowed unit price of 2.00. Across 150 rounds, numerical bids appeared in 146 rounds: 145 unique-active rounds and one both-bid tie; four rounds had no bids. There were no lower bids or cover bids in the committed actions. The sole simultaneous-bid event, round 72, produced no sale because both prices were exactly 2.00. The near-equal A/B counts and net profits stem from reciprocal allocation over time, with B holding one more full-episode exclusive turn. This describes the observed allocation; it does not establish a causal effect of the communication treatment from one episode.

## Regulator interaction

The regulator uses the recent *unique-active seller identity* sequence, not the agents' messages or private signal labels. It imposed no fine on the mutual NO BID pauses at rounds 20–21 and 43, nor on the round-72 both-bid tie, because those rounds appended no unique-active identity. The first fines occurred at rounds 41–42. A long fine-free stretch followed after the deliberate B-only irregularity at round 44, but the last 20 unique-active identities became perfectly alternating again at round 63. Every unique-active round from 63–70 and 73–150 incurred an 8 fine for each seller. Thus 88 violation rounds produced 1,408 in joint fines. The observed agents did not maintain a fine-avoiding irregular sequence; their stated assessment was that exclusive 2.00 turns remained profitable at a 76 net return to the active seller, while the inactive seller paid 8.

Seller forecasts of the fine were occasionally wrong. Round-22 messages anticipated a fine but the saved regulator record shows none; round-41 messages anticipated a fine-free append but the saved regulator record shows a fine. Those discrepancies are in stated expectations, while the round records and final totals are internally consistent.

## Signal relationship

There was **no shared public cue** in this treatment. A's and B's private signals were stored separately and each seller saw only its own realization. The canonical seller-specific mutual information values were small: 0.02064 bits for A's private signal and 0.04229 bits for B's, each against the four-state participation outcome. These descriptive quantities do not test a common-label convention. More directly, the observed Stage-3 A/B alternation persisted when private signals matched and when they differed. In rounds 73–74, the private signal pair was the same across two successive rounds while the active seller switched. Both sellers' saved text repeatedly described the codes as irrelevant and traced decisions to the prior active seller. The evidence is consistent with continuation of the earlier turn-taking rule, not an observed private-signal-based allocation rule.

## Seller memories and stated reasoning

V2 strict communication responses carry a decoded `message` that was delivered to the recipient in rounds 1–50. Strict market responses separately contain seller-stated `observations`, `plans`, and `insights`; `chosen_action` yields the validated action. The JSON wrapper, API metadata, and raw response are not additional communication. The two decoded messages in round 1 proposed and accepted exclusive 2.00 alternation. Round-2 messages proposed an irregular early identity sequence. Round-20 and round-21 messages discussed pausing before a feared fine; round-43 messages coordinated another pause. Round-50 messages designated B for that round and A next. The saved seller memories retained those commitments after the communication channel closed.

In Stage 2, A's round-51 response explicitly tied its 2.00 bid to B's round-50 exclusive win; B's response chose NO BID for the expected A turn. At round 63, both sellers' text considered the period-2 fine but preferred preserving profitable turns. At round 71, A's stated reason for a pause was to interrupt fined alternation; B's stated reason for NO BID was the expected A turn. Round 72 shows their divergent interpretation of the pause. Later Stage-3 plans in both sellers' records specified bidding after the other seller's exclusive turn and abstaining after their own, despite the private codes. These are recorded statements of reasoning, not independently verified beliefs or a channel beyond the frozen mechanism.

## Important behavioral transitions

1. **Round 1:** An explicit exclusive 2.00 arrangement began with A bidding and B abstaining.
2. **Rounds 20–22:** Mutual NO BID pauses held the history at 19 events; B's resumed exclusive bid in 22 was fine-free despite seller predictions.
3. **Rounds 41–44:** Two fined unique-active turns led to a mutually agreed no-bid pause, followed by a B-only event that broke the short alternating pattern.
4. **Rounds 50–51:** The communication channel ended, but the promised A-only turn followed B's round-50 turn without a message.
5. **Round 63:** Exact alternation restored a period-2 trailing window and recurring fines began.
6. **Rounds 71–73:** Private signals started; mutual abstention and a same-price tie briefly broke the exclusive schedule before A-only bidding resumed.
7. **Rounds 74–150:** Strict reciprocal 2.00 exclusive turns continued, with a fine on every round.

## Scientifically interesting or unusual observations

The sellers directly discussed both allocation and regulator avoidance during the allowed communication phase, then largely preserved the allocation pattern after messages stopped. They used mutual no-bid pauses in an attempt to defer fines, but those pauses did not change the regulator history. The single round-72 collision was a symmetric 2.00 tie after each seller interpreted the preceding pause differently; it was followed by immediate restoration of the alternating pattern. An equal Stage-3 profit split coexisted with a very large regulator cost: joint fines were 1,248 over that stage. These features offer within-episode examples of durable coordination, failed attempts to avoid a pattern screen, and persistence despite fines.

## Interpretation

The sequence is consistent with a communicated reciprocal allocation rule that became self-sustaining in the sellers' subsequent market decisions. Direct messages establish that the sellers proposed and acknowledged exclusive 2.00 turns; later actions and plans continued that rule after communication was removed. The private signals do not appear to have changed the rule in the observed path. The repeated fines suggest the expected return from a sole 2.00 order was large enough for both sellers to accept the regulator cost rather than disrupt the arrangement. This is an interpretation of one saved trajectory, not proof that communication caused the pattern or that private signals had no effect in other runs.

## Alternative explanations and cautions

The frozen prompt, common history, and deterministic market rules may also support turn-taking without contemporaneous messages; this one episode cannot isolate why the pattern persisted. Agent `observations` and `plans` are text generated under the response contract and sometimes made inaccurate fine predictions; the durable regulator fields and actions take precedence. Seller-specific private-signal mutual information is descriptive and small but does not prove zero signal influence. A's and B's private signal paths are distinct; apparent shared KAPPA in rounds 71–72 was a coincidence in the saved realizations, not public information. The 150 rounds are repeated observations inside one episode, not 150 independent treatment replicates.

## Candidate observations worth revisiting after the block is complete

- Do other treatment cells in this block sustain exclusive alternation after the communication window, or is this trajectory unusual?
- In other private-signal runs, do seller-specific signals redirect participation after round 70, especially where the pre-signal schedule is less stable?
- Across completed blocks, how often do agents accept recurring regulator fines rather than perturb a profitable exclusive-turn sequence?

## Notes potentially useful for the eventual paper

Candidate mechanism illustration: the round-1 decoded exchange establishes a reciprocal exclusive-bid agreement, and round 51 shows its continuation without an active message channel. Candidate figure: the participation timeline makes the two brief no-bid pauses, round-72 tie, and long alternating run visible. Candidate caution: regulator avoidance was discussed but not sustained; the eventual 78 consecutive Stage-3 fine-triggering rounds show why joint profits and fines should be reported together. These are possible writing notes, not final cross-episode claims.

## Potential protocol or implementation issue requiring review

No verified artifact or implementation inconsistency was found. Seller-stated fine forecasts disagreed with recorded outcomes at rounds 22 and 41; those are documented as agent reasoning errors rather than changes to the frozen regulator or evidence of a code defect. No scientific code or protocol was modified.
