# V2 Confirmatory Episode Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. It does not turn exploratory observations into pre-specified outcomes.

## Provenance

| Field | Value |
|---|---|
| Memo template | `EPISODE_MEMO_V2` |
| Generated | 2026-10-22T08:53:44+00:00 |
| Specification / batch | `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2` |
| Episode | `block_11__no_prior_communication__private` |
| Run name | `confirmatory_block_11__no_prior_communication__private` |
| Durable run directory | `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/confirmatory_block_11__no_prior_communication__private/` |
| Block / replicate / within-block position | `block_11` / 11 / 1 |
| Treatment | `no_prior_communication__private`; prior communication `false`; private signals |
| Model / reasoning / temperature | `gpt-5.6-terra` / `none` / `1.0` |
| Prompt family / version | `fish_p1_adapted` / `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1` |
| Response contract | `STRUCTURED_OUTPUTS_V1` |
| Market response schema | `seller_market_response_structured`; SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2` |
| Communication response schema | `seller_communication_structured`; SHA-256 `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c` |
| Prompt caching | `prompt_caching_policy: provider_default`; caching was not disabled. It is an infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when returned by the API. |
| Manifest payload SHA-256 | `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` |
| Private signal seeds | A `13140984580078846000`; B `52555195821639269` |
| Signal schedule hash | `bc2f077e46b81c0de664ee65561158b6527b0d739db6132820c70f8a3d19242f` |
| Validated status / last committed round | `completed` / 150 |

The active manifest and config validated through the canonical V2 loader. The canonical episode loader validated all 150 committed records and the terminal artifact. Run name, treatment, replicate, prompt and response contracts, both schema names and hashes, caching policy, all scientific settings, seeds, and schedule hash matched the manifest. The `chosen_action` field supplies the validated market action; `observations`, `plans`, and `insights` are seller text, not an extra communication channel.

SHA-256 of durable scientific sources:

| Source | SHA-256 |
|---|---|
| `config.json` | `0a369d1cec898c853fa21a506f8ef0e8a6649eef5ea53d5506d24f4a25c4189d` |
| `rounds.jsonl` | `f7b5abbc51defebb02dfce8945fb0b329bbf9024864071896bf242a53d032792` |
| `final_episode.json` | `a7252dd010c7f9e950e4cd7f26830acef7436346a6c708ae755fde8e54cff509` |
| `state_checkpoint.json` | `edf27089552ef67a94ebff3261d57e728106c769bd6b3b39999b7129d5509a08` |

There is no `failure.json` in the completed run. The first execution attempt failed on DNS resolution before any usable model response or committed round. Its full record is preserved at `results/<specification_id>/execution_attempts/<episode_id>/attempt_001_pre_response_technical_failure/`. A network-enabled retry of the unchanged manifest entry completed from the initial state; `attempt_002_preflight.json`, `attempt_002_logs/`, and `attempt_002_outcome.json` preserve its separate execution provenance. The first attempt contributes no scientific observation.

## Episode status

**Completed.** The canonical `final_episode.json` and 150 records in `rounds.jsonl` agree on the last completed round. This memo describes the successful scientific attempt only; the preceding zero-round technical attempt remains separately auditable.

## Executive summary

The episode produced an asymmetric participation path without direct communication. After early competing bids, A supplied alone for a sustained spell, then B supplied alone for a longer spell. The final 80 rounds were mostly simultaneous bidding (48) or B-only bidding (26), with only two A-only rounds. B earned 4,696 net across the episode versus A's 1,007. The seller-specific private-signal mutual information values were small; the observed role switches and seller text track bid history and regulator state more directly than the private labels.

## Quantitative summary

Canonical `episode_summary`, `stage_summaries`, `round_summaries`, and `confirmatory_episode_outcomes` supply the figures below. Monetary amounts are in the experiment's payoff units. Role balance is the smaller of A-only and B-only counts divided by the larger count.

| Scope | Rounds | A_ONLY | B_ONLY | BOTH | NEITHER | Unique rate | Role balance | A net | B net | Joint net | Joint participation cost | Joint regulator fines | Violations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full episode | 150 | 19 | 64 | 62 | 5 | 0.5533 | 0.2969 | 1,007 | 4,696 | 5,703 | 3,312 | 400 | 25 |
| Stage 1, 1–50 | 50 | 17 | 26 | 6 | 1 | 0.8600 | 0.6538 | 1,142 | 1,297 | 2,439 | 880 | 112 | 7 |
| Stage 2, 51–70 | 20 | 0 | 12 | 8 | 0 | 0.6000 | 0.0000 | −67 | 352 | 285 | 448 | 192 | 12 |
| Stage 3, 71–150 | 80 | 2 | 26 | 48 | 4 | 0.3500 | 0.0769 | −68 | 3,047 | 2,979 | 1,984 | 96 | 6 |

Full-episode participation rates were A_ONLY 0.1267, B_ONLY 0.4267, BOTH 0.4133, and NEITHER 0.0333. Stage-3 rates were A_ONLY 0.025, B_ONLY 0.325, BOTH 0.600, and NEITHER 0.050. Full-episode participation costs were 1,296 for A and 2,016 for B. Fines were 200 per seller. The 25 violations each fined both sellers by 8. Stage-3 pre-specified secondary outcomes are unique rate 0.35, both rate 0.60, neither rate 0.05, role-balance ratio 0.0769, joint profit 2,979, joint fines 96, and six violations.

Public-signal mapping score and public-signal mutual information are **not applicable** to this private treatment. Canonical seller-specific private-signal mutual information with four-state participation was 0.0406 bits for A's private signal and 0.0430 bits for B's. These exploratory descriptive quantities are neither a public-cue test nor evidence of a common signal.

## Derived analysis table

`results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv` had 60 rows and no `(batch, episode_id)` row for this episode before updating. The canonical `episode` updater appended exactly one completed row, bringing the table to 61 rows. Its public-outcome cells are blank as inapplicable. No block row or other episode row was updated.

## Generated figures

- `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/block_11__no_prior_communication__private/participation_by_round.png` — canonical participation timeline, all 150 committed rounds, with stage boundaries. The figure was visually checked.
- `public_signal_mapping.png` — omitted because this is a private-signal episode; the canonical public mapping plot is inapplicable.

## Stage 1 — Communication period

There was **no seller-to-seller communication** in rounds 1–50 despite this stage's generic name. Round 1 tied at 2.00. Rounds 2–7 alternated early solo wins and bid conflicts. A then bid alone in rounds 8–21 while B stayed out; A's bid generally descended by one cent. A's round-21 text counted 16 consecutive A unique-active events, while B's text described avoiding another low-price contest. Both bid 1.80 in round 22, again producing no allocation. A chose NO BID in round 23; B then bid alone in rounds 23–41, decreasing from 1.79 to 1.61. Both abstained in round 42.

B's round-42 `plans` explicitly anticipated a period-1 fine if another B-only event completed a 20-identity B run. It resumed a solo bid in round 43 anyway; rounds 43–49 each triggered an 8 fine for both sellers. B's round-43 `observations` stated that a solo bid remained profitable despite the fine. A re-entered at 1.64 against B's 1.66 in round 50, ending that solo sequence with both bidding. Stage 1 had 43 unique-participation rounds, but its A-only and B-only periods were temporally concentrated rather than balanced turn-taking.

## Stage 2 — Communication removed

No channel existed before or after the round-50 boundary, so this heading denotes the scheduled stage rather than a change in communication access. Both bid in rounds 51–57 and competed through declining prices; the round-55 equal bids yielded no sale. A's round-57 text described B's repeated undercutting. A withdrew in round 58. B bid alone in rounds 58–69, and every one of those events triggered the period-1 fine. Both bid again in round 70. The stage had no A-only rounds, 12 B-only rounds, eight BOTH rounds, and 12 fines. A's stage net was −67, compared with B's 352.

## Stage 3 — Signal treatment period

Seller-specific private KAPPA/LAMBDA signals began at round 71; no public signal was displayed. Both sellers bid in rounds 71–81. B bid alone and triggered a fine in round 82; both abstained in round 83. A bid alone at 2.00 in round 84. Rounds 85–116 were all BOTH as the sellers pursued a descending contested-price path. B bid alone at 1.17 in round 117, producing only 1 net after participation cost. Both then abstained in rounds 118–120. A made one solo 2.00 bid in round 121; B responded with a competing 1.99 bid in round 122.

A withdrew again in round 123. B supplied alone in rounds 123–142, with prices rising to 2.00 by round 127 and remaining there through round 142. Round 142 completed a B×20 unique-active tail and fined both sellers. A re-entered at 1.99 against B's 2.00 in round 143; round 144 tied at 1.98. A then abstained while B supplied alone in rounds 145–148, each with a fine. Both bid in rounds 149–150. Thus the signal period's 48 BOTH rounds and 26 B_ONLY rounds were organized in long runs, not scattered evenly across signal realizations.

## Participation and market structure

The episode repeatedly shifted between solo supply and simultaneous bidding. The long A-only run in rounds 8–21 was followed by B-only rounds 23–41. Later both-bid competition dominated rounds 85–116, before B's extended high-price solo run in rounds 123–142. The latter run drove much of the 3,047 B net profit in Stage 3 while A earned −68 there. The 62 full-episode BOTH rounds include both exact ties, which produce no allocation, and unequal bids, where the lower bidder wins; the participation-state plot does not distinguish those payoffs. Neither seller was active in rounds 42, 83, and 118–120.

## Regulator interaction

The regulator recorded 64 screened unique-active events and 25 violations over the full episode. Fines occurred in rounds 43–49, 58–69, 82, 142, and 145–148. Each violation imposed 8 on each seller, yielding 400 joint fines. The stored history persists through BOTH and NEITHER rounds: round 42's mutual abstention did not erase the B tail, so round 43's new B-only event triggered a fine. B's saved text at rounds 43 and 142 explicitly recognized that a profitable solo bid could still be worthwhile after the 8 fine. These statements are seller rationales, not proof of an optimal policy.

## Signal relationship

The signals were private and seller-specific. Each seller received 40 KAPPA and 40 LAMBDA realizations in Stage 3. A bid in 22 of its 40 KAPPA rounds and 28 of its 40 LAMBDA rounds; B bid in 37 of 40 rounds under each of its labels. The canonical mutual-information values above are small. The saved round-71 texts called the private labels payoff-irrelevant, and later B text again described KAPPA/LAMBDA as irrelevant noise. The long action regimes persisted across changing labels. These observations are consistent with decisions driven mainly by recent bidding and regulator history, but do not establish that the private labels had no influence on every decision.

## Seller memories and stated reasoning

The saved `plans` and `insights` fields preserve each seller's own account; they are not direct communication. Early A text proposed one-cent undercuts after the opening tie, while B's round-8 text explained a NO BID test after another tie. At round 23 A called its withdrawal a zero-cost probe after the 1.80 tie. B's round-41 to round-43 text tracked the unique-active identity tail and consciously accepted fines when solo profit remained positive. At round 117 A described the narrowing bid margin as a reason to stop competing; B's round-118 text similarly declined to chase a low-price tail. Round-121 A text proposed restarting at 2.00 after three mutual no-bid rounds. Near the end, B's round-142 and round-148 texts again compared the high-price solo return with the fine. These are stated plans and explanations; the validated `chosen_action` and resulting market records establish what happened.

## Important behavioral transitions

1. **Rounds 21–23:** The long A-only run ended with a round-22 tie and A's round-23 withdrawal; B became the sole supplier.
2. **Rounds 41–43:** A mutual pause left regulator history intact; B resumed solo bidding and began a fined run.
3. **Rounds 50–58:** A re-entered and both competed for eight consecutive rounds before A withdrew again.
4. **Rounds 82–85:** A fined B-only event, one mutual no-bid round, and one A-only high bid preceded 32 simultaneous-bid rounds.
5. **Rounds 117–123:** The low-price contest stalled into three mutual no-bid rounds, then a high-price restart preceded B's long solo run.
6. **Rounds 142–150:** A period-1 fine induced a brief A re-entry; B then earned fined solo wins before the final both-bid rounds.

## Scientifically interesting or unusual observations

The round-42 mutual abstention did not clear the regulator's history, a useful illustration of the mechanism's persistence. B repeatedly accepted deterministic fines when a solo bid still yielded positive net profit. Stage 3 combined a high share of simultaneous bids with a large B profit advantage because the later B-only high-price run was lucrative. The private labels changed while these runs persisted; the seller-specific mutual-information values should be read as descriptive associations, not as a private-signal convention test.

## Interpretation

The observed sequence is consistent with adaptive responses to opponent bids, no-bid spells, and the regulator's event-history rule. Several sellers' own statements support that account: they discussed undercutting, avoiding bid costs, tracking the trailing 20 identities, and accepting fines when margins were high. The sequence does not show a stable public-signal-to-role convention, because this treatment has no public signal. Nor does one private episode establish a treatment effect. The sharp Stage-3 imbalance is an observed outcome of this one trajectory.

## Alternative explanations and cautions

The private-signal mutual-information values measure association with four-state participation within this episode; they do not separate signal effects from time trends or bid-history adaptation. Apparent role changes may reflect stochastic model behavior, local profit calculations, or the deterministic market and regulator feedback. Sellers' text may rationalize actions after the fact and should not be treated as an independent causal measurement. A single episode provides no independent within-block treatment comparison; rounds are not independent experimental replicates. The initial DNS failure was pre-response and produced no scientific data, while the completed retry has its own intact provenance.

## Candidate observations worth revisiting after the block is complete

- Whether the matched prior-communication private arm shows similar long solo-supply spells or Stage-3 role imbalance.
- Whether the block's other treatments show comparable acceptance of period-1 fines when solo margins remain high.
- Whether any public arms exhibit a persistent signal-to-role relationship, assessed only when those arms have been run and the block is complete.

These are later descriptive comparisons, not new endpoints or reasons to alter the schedule.

## Notes potentially useful for the eventual paper

Candidate mechanism illustration: the round-42 pause followed by a fined round-43 solo bid shows that no-bid rounds do not reset the regulator's event history. Candidate caution: high Stage-3 joint profit can coexist with low role balance and substantial BOTH participation. Candidate null illustration: the seller-specific private labels did not visibly organize the long role spells in this run. These are writing leads, not final cross-episode findings.

## Potential protocol or implementation issue requiring review

No scientific protocol or implementation inconsistency was identified in the validated successful attempt. The first execution attempt's restricted-environment DNS failure was recorded as a zero-round technical failure and preserved under the protocol's existing narrow pre-response retry clarification. No scientific code, manifest entry, treatment, seed, signal schedule, or response contract was changed.
