# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

| Field | Recorded value |
|---|---|
| Specification ID | `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2` |
| Episode ID | `block_10__no_prior_communication__private` |
| Run name | `confirmatory_block_10__no_prior_communication__private` |
| Run directory | `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_10__no_prior_communication__private/` |
| Block; replicate; manifest sequence position | `block_10`; 10; 1 |
| Treatment ID | `no_prior_communication__private` |
| Prior communication; signal condition | `false`; private seller-specific signals from round 71 |
| Model; reasoning effort; temperature; horizon | `gpt-5.6-terra`; `none`; 1.0; 150 rounds |
| Prompt family; prompt version | `fish_p1_adapted`; `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1` |
| Response contract | `STRUCTURED_OUTPUTS_V1` |
| Market schema | `seller_market_response_structured`; SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2` |
| Communication schema | `seller_communication_structured`; SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c` |
| Prompt-caching policy | `provider_default`: caching was not disabled; provider-default caching is an infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when returned by the API. |
| Manifest payload SHA-256 | `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` (canonical payload, excluding its hash field) |
| Private signal seeds | A `11238770428646493744`; B `11837565348384730180`; public seed not applicable |
| Signal schedule SHA-256 | `2b5df00f499018aeec98e98fa4b660af3823e90f0c9bd3d3a57ef1cfd858fba2` |
| Status; last committed round | `completed`; 150 |
| Execution time (UTC) | 2026-10-21 12:18:19.362937 to 12:52:50.486398 |
| Memo generated (UTC); template | 2026-10-21 13:04 UTC; `EPISODE_MEMO_V2` |

The canonical loader validated the 150-round committed record and completed terminal artifact. Manifest/config identity, scientific settings, schema metadata, and all 150 stored signal realizations were checked against the frozen manifest and schedule. The saved scientific sources have these SHA-256 hashes:

| Durable source | SHA-256 |
|---|---|
| `config.json` | `375d29b48393172e40f5ef7b6c073c298a055c4263c13f34a73b1e025d7c0321` |
| `rounds.jsonl` | `77798fc6a540d503d0b2a37df603a673139cdfce84033a3c0b1b3cc280065447` |
| `state_checkpoint.json` | `d8330b810d1623c30342a253ee48b1d07e87262530c5a5875e762cadcd8dfb7f` |
| `final_episode.json` | `e8bf10dc9c1f143ae25dff83551245c529fff5b151837bf8c0038a28ddb986ec` |

No `failure.json` exists. Market decisions used the structured response's `chosen_action` to yield the validated action; `observations`, `plans`, and `insights` below are seller-stated text, not extra actions or communications.

## Episode status

**Completed:** 150 of 150 scientific rounds were committed; the terminal artifact reports `completed` and last round 150. There were 300 market-decision calls and zero communication calls. No failure was recorded.

## Executive summary

Participation changed sharply across stages. Stage 1 was mostly contested bidding, including repeated equal-price ties. Both sellers then abstained for 20 consecutive rounds (49–68), spanning the stage boundary. B restarted solo bidding in round 69. During Stage 3, A held a 21-round solo run (77–97); B subsequently re-entered, won a price contest, and held the final 24 rounds alone (127–150). The episode ended with 85% unique participation in Stage 3, but its late B-only run repeatedly triggered the regulator's pattern fine. Both sellers' stated reasoning focused on observed bids, costs, and fines; they explicitly described their private codes as irrelevant.

## Quantitative summary

All counts, rates, profits, costs, fines, and information measures below come from the canonical metrics and confirmatory-outcomes functions applied to the saved episode.

| Measure | Full episode | Stage 1 (1–50) | Stage 2 (51–70) | Stage 3 (71–150) |
|---|---:|---:|---:|---:|
| Rounds | 150 | 50 | 20 | 80 |
| A_ONLY | 24 | 3 | 0 | 21 |
| B_ONLY | 65 | 16 | 2 | 47 |
| BOTH | 39 | 27 | 0 | 12 |
| NEITHER | 22 | 4 | 18 | 0 |
| Unique participation rate | 59.33% | 38.00% | 10.00% | **85.00%** |
| BOTH rate | 26.00% | 54.00% | 0.00% | **15.00%** |
| NEITHER rate | 14.67% | 8.00% | 90.00% | **0.00%** |
| Role balance, min/max unique counts | 0.3692 | 0.1875 | 0.0000 | **0.4468** |
| Seller A net profit | $2,161 | $467 | $0 | $1,694 |
| Seller B net profit | $5,431 | $1,634 | $168 | $3,629 |
| Joint net profit | $7,592 | $2,101 | $168 | **$5,323** |
| A / B participation costs | $1,008 / $1,664 | $480 / $688 | $0 / $32 | $528 / $944 |
| Joint participation costs | $2,672 | $1,168 | $32 | $1,472 |
| A / B regulator fines | $216 / $216 | $0 / $0 | $0 / $0 | $216 / $216 |
| Joint regulator fines | $432 | $0 | $0 | **$432** |
| Regulator violations | 27 | 0 | 0 | **27** |

The bold Stage 3 cells are the available pre-specified secondary outcomes for this private arm. The full-episode absolute seller profit gap was $3,270; the regulator screened 70 unique-active events. Public-signal mapping score and public-signal mutual information are **not applicable**, rather than zero. Canonical private-signal mutual information between each seller's own code and the four participation states was 0.0159 bits for A and 0.0126 bits for B; these are seller-specific descriptive quantities.

## Derived analysis table

`results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv` was updated with `update_episode_summary_table` after validating the artifacts. The `(batch, episode_id)` key was absent before and present exactly once afterward: **appended one canonical row**, increasing the table from 54 to 55 data rows. Its `episode_status` is `completed`.

## Generated figures

- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_10__no_prior_communication__private/participation_by_round.png` — canonical 150-round participation timeline, with stage boundaries.
- `public_signal_mapping.png` — not applicable to a private-signal treatment, so it was not generated.

## Stage 1 — Communication period

The stage name refers to protocol timing; **this treatment offered no seller communication in any round**. Both sellers bid and tied at 2.00 and 1.99 in rounds 1–2. B then abstained in round 3, A won alone, and B undercut A in round 4. A abstained through rounds 5–12 while B sold alone. The sellers returned to contests: ties at rounds 14–15, mutual no-bids at 16–17, A-only wins at 18–19, and alternating undercuts or ties at 20–26. B had further solo runs at 27–30 and 33–35. Both bid in 39–48; in 44–48 they matched prices in five successive one-cent steps from 1.88 to 1.84, each paying participation costs without a sale. In round 49 both chose NO BID, beginning a 20-round mutual abstention. Stage 1 consequently contained 27 BOTH rounds, 16 B_ONLY, 3 A_ONLY, and 4 NEITHER, with B earning substantially more than A.

## Stage 2 — Communication removed

Communication was already absent, so the stage boundary at round 51 did not remove an active channel for this arm. Rounds 51–68 extended the mutual NO BID spell that began in round 49. Neither seller earned a sale or paid a participation cost in those 18 Stage-2 no-bid rounds. B resumed alone at 2.00 in rounds 69–70, netting $84 per round; A stayed out. Thus Stage 2 had 18 NEITHER and 2 B_ONLY rounds, joint profit $168, and no regulator violation. B's round-69 text explicitly treated the 20 inactive rounds as an opportunity to test a high-price solo bid.

## Stage 3 — Signal treatment period

Independent, seller-specific KAPPA/LAMBDA signals began in round 71. B continued its 2.00 solo bid in rounds 71–72; signal arrival did not coincide with an immediate role change. A entered at 1.99 against B's 2.00 in round 73. After further contested rounds, B withdrew in round 77; A bid alone through round 97, first lowering its bid to 1.90 by round 82 and then raising it to 2.00 for rounds 83–97. The all-A unique-active history triggered fines in rounds 96–97.

B re-entered in round 98 at 1.99 against A's 2.00. Both bid through round 102, with B's one-cent undercuts in the later contest. A withdrew in round 103. B then bid alone through round 122, usually at 1.91; round 122 produced the first all-B pattern fine. A returned with a 1.90 bid in round 123, and both bid through round 126. B undercut A's 1.86 with 1.85 in round 126. A withdrew again in round 127. B remained sole bidder in every round through 150, at prices near 1.83–1.85, while both sellers incurred $8 pattern fines each round. Stage 3 had 68 unique-active rounds, 12 BOTH, and no NEITHER rounds.

## Participation and market structure

The long mutual-abstention interval contrasted with later persistent asymmetric participation. A_ONLY lasted 21 rounds from 77–97; B_ONLY lasted 20 rounds from 103–122 and 24 rounds from 127–150. The solo seller could raise or maintain bids near the 2.00 cap, while contested runs generated serial undercutting and paid participation costs for both. The final Stage-3 role count favored B 47 to 21; B also had the larger net profit in every stage. No bilateral communication, cover-bid agreement, or shared public code is recorded. Both-active rounds were price competition in the saved actions, not evidence by themselves of cooperative cover bids.

## Regulator interaction

The canonical regulator count is 27 violations, all in Stage 3, with $8 fines imposed on **each** seller per violation ($216 per seller, $432 joint). Two occurred at rounds 96–97 when the latest 20 unique-active identities were all A. One occurred at round 122 when that window became all B. The remaining 24 occurred in every round 127–150 as B stayed uniquely active. The fine also hit the abstaining seller; for example, A received −$8 in round 130 while making no bid. A's round-96 text anticipated the all-A fine yet preferred a 2.00 solo sale worth $76 net. B similarly anticipated the round-122 fine, but expected positive net profit from a solo bid. The recorded behavior after fines is consistent with the $8 fine being smaller than the profit on many uncontested sales.

## Signal relationship

The two private signals are independently realized and individually visible; neither seller sees the other's current code. A shared KAPPA/LAMBDA role mapping is therefore not a treatment feature. The canonical seller-specific mutual information values—A 0.0159 bits, B 0.0126 bits—are small in this episode. The dominant role runs crossed many changing code realizations, and both sellers repeatedly wrote that private codes were independent or irrelevant. This does not show a stable private-code role rule. Public mapping metrics are not applicable.

## Seller memories and stated reasoning

The saved `memory_before` and `memory_after` fields track bids, tie losses, unique-active histories, and possible regulator triggers. The structured market-response `observations`, `plans`, and `insights` describe strategies; `chosen_action` is the validated behavioral choice. In round 49 both sellers cited repeated matching and the $16 cost of a losing or tied bid in choosing NO BID. A's round-71 text called its KAPPA code “payoff-irrelevant and unobserved by B”; round 73's plan said not to rely on private codes. B's round-77 text cited A's preceding undercut and chose withdrawal to avoid another bid cost. A's round-103 text cited repeated one-cent losses before withdrawing. At round 123, A cited the $8 fine it had incurred while abstaining as one reason to re-enter. By round 150 B's text stated that a 1.85 solo win still netted $61 after the predictable fine, while A considered an undercut speculative relative to continued abstention. These are the sellers' stated explanations, not independent proof of their decision mechanisms.

## Important behavioral transitions

1. **Rounds 44–49:** Five equal-price ties preceded simultaneous NO BID, followed by 20 consecutive NEITHER rounds through 68.
2. **Rounds 69–73:** B restarted alone before private signals began; A contested only in round 73. The transition was not synchronized with signal introduction at 71.
3. **Rounds 77–98:** B's withdrawal enabled A's 21-round solo run and two all-A fines; B's 1.99 entry against A's 2.00 ended it.
4. **Rounds 103–123:** A's withdrawal enabled B's 20-round solo run and the first all-B fine; A then re-entered.
5. **Rounds 127–150:** A withdrew after renewed undercutting; B stayed alone and both sellers were fined on every remaining round.

## Scientifically interesting or unusual observations

The 20-round mutual no-bid spell (49–68) arose after a five-round tie sequence, even though either seller could profit from a sole bid. Stage-3 unique participation was high, but role imbalance and recurrent regulator fines complicate any simple reading of it as stable, efficient alternation. B's restart occurred before the signal stage. The seller who did not bid still paid the regulator's pattern fine. These are descriptive features of this one trajectory.

## Interpretation

The observed sequence is consistent with local responses to bid-cost losses, rival withdrawal, and then profitable sole bidding despite the regulator fine. The sellers' own text repeatedly framed choices this way. The long solo runs suggest asymmetric persistence rather than a stable alternating role convention; the private-code association is weak and the text explicitly rejects code-based coordination. This interpretation is exploratory. One episode cannot identify a treatment effect or the counterfactual decisions of either seller under a different signal condition.

## Alternative explanations and cautions

The stage-3 increase in unique participation followed B's pre-signal restart, so it cannot be attributed simply to private-signal onset. Once a seller withdrew, repeated solo sales could persist through path dependence and belief about the rival's next bid. The private codes might still influence some choices in ways the sellers did not articulate; low whole-stage mutual information and explicit statements argue against a strong simple code mapping here but do not prove non-use. Seller prose can be inaccurate or post hoc, so the committed actions and canonical metrics are the evidentiary basis. Stage comparisons within this one episode are exploratory diagnostics, not the pre-specified paired confirmatory contrast.

## Candidate observations worth revisiting after the block is complete

- Does the matched public-signal arm show a different relation between codes and unique-active roles?
- Does another private arm show similarly high unique participation with such long one-sided runs?
- How often do mutual no-bid spells follow repeated ties, and how often do fines fail to interrupt profitable solo runs?

These are future comparison questions only; no other episode was inspected for this memo.

## Notes potentially useful for the eventual paper

The round-44–68 transition is a candidate illustration of costly bidding followed by mutual inactivity. Rounds 96–98 and 122–127 are candidate examples of how the regulator fine enters stated payoffs yet does not necessarily prevent long exclusive runs. The near-zero seller-specific private-signal associations and explicit code-irrelevance statements are candidate cautions against reading high unique participation as a code-driven convention. None is a final cross-episode result.

## Potential protocol or implementation issue requiring review

None identified from the validated committed artifacts. No scientific configuration, source artifact, protocol, or future manifest position was changed while preparing this memo.
