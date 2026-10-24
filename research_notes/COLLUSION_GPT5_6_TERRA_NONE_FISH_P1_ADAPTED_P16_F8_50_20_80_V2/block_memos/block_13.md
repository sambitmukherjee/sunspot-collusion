# V2 Confirmatory Block Research Memo

> **Confirmatory integrity:** This descriptive and interpretive note does not change the frozen V2 protocol, manifest, treatment order, seeds, endpoints, or episode-replacement policy. Formal confirmatory inference is governed by `docs/v2_confirmatory_analysis_plan.md`.

## Provenance

- **Specification/batch:** `COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2`; **block:** `block_13`; **replicate:** 13; **memo template:** `BLOCK_MEMO_V2`; **generated:** 2026-10-24T03:19:03Z.
- **Frozen sources:** `configs/gpt5_6_terra_none_fish_p1_adapted_v2.yaml`, `configs/gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json`, and the V2 protocol and analysis plan. The verified canonical manifest payload SHA-256 is `1339cf3cc3a520e3722386f2ca1ee87d23df63b04be5251d47223bfc4a19fc90` (not the raw-file hash). The six entries occupy distinct positions and cover each communication × signal cell once.
- **Prompt and response:** `fish_p1_adapted`; `PROMPT_FISH_P1_ADAPTED_STRUCTURED_V1`; `STRUCTURED_OUTPUTS_V1`. Both call types use strict JSON Schema Structured Outputs. Market schema `seller_market_response_structured` has full response-format SHA-256 `b5a6b5f304c8adbc063c8fc0ad847d1c941c6b2fd92f461965dede40cfd4f1d2`; communication schema `seller_communication_structured` has `12cb0fc2ec790d1acce8f5d228e4238e74c01aff8552487a31c722f8e4ac367c`. Saved response-contract fields, schema names/hashes, and scientific configs match the manifest in all six runs. Seller `observations`, `plans`, and `insights` are stated text; validated `chosen_action` gives the market action. Decoded communication `message` text, not its JSON wrapper, enters the recipient prompt.
- **Prompt caching:** `prompt_caching_policy: provider_default` in the frozen config, manifest, and saved provenance. Caching is not disabled; it is a provider-default infrastructure cost/latency optimization, not a treatment. Cached-token usage is logged when returned by the API; an absent usage field is not a reported zero.
- **Run root:** `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/runs/`. Each run directory is named `confirmatory_<episode_id>` using the episode ID below. All six terminal records are `completed` with 150 committed rounds. The committed `rounds.jsonl` and terminal `final_episode.json`, interpreted through canonical metrics, are the scientific sources; checkpoints and logs support provenance.

| Position | Episode ID | Status | `config.json` SHA-256 | `rounds.jsonl` SHA-256 | `state_checkpoint.json` SHA-256 | `final_episode.json` SHA-256 |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `block_13__no_prior_communication__private` | completed | `2caa550bb9695dcb0573dd641486b8d28018803b106eafd6492c14427004089b` | `8ae7cee94817014367de9207bd093f6d0c5e9344ba945b18ae10f8eeadc2029a` | `95855ef3a29255e19d9f50e4fcbbbbd9d2281974a6dde1f4b867e2cc3b49bc52` | `1dad60e23ec8afaa57f496968283ca56e551d688148804f2315e3022fdb1aaeb` |
| 2 | `block_13__no_prior_communication__public` | completed | `58c81a01f74a1fa42fc009ea7e483771a6dbcc859e434699602e2d0e4b66d383` | `a6538c1396c3d3d5a412a3af2189bc3966bb7d1aea0d419c3bcf400a29fdf0aa` | `db603db98140ccd844b2a76cb8977d39c8bfc54dfc1133a270d1912407537c28` | `000518371430b69732af51b0ff48f308083478761cb40e51533ba38fdcdb0616` |
| 3 | `block_13__prior_communication__none` | completed | `74c63c6a8a9fc45714b31fb31626028d1503b11056464a3229f09019ba61919c` | `055d23920802ea95d80b96f7e3bb715cf49f5862689915d72320b13ebc12d996` | `4304dcd3a6242711f3d94651a7a4eab1b1bdd7b0b822ce68827aabbd124fbd9e` | `89a4ea2e3b61915ab32121a3b58b115948cbdec1f361fa6d7de68ccbacb9dc05` |
| 4 | `block_13__prior_communication__private` | completed | `3dd833a21250ce9112430b70aa82f281ff0b6fe4e11519611ce78d8b90ca716e` | `a438da2baf9e8ea4734897c7b099b03de85495f45ed24df81a5366281246226b` | `a6088935e67be0a84eb727f1cc09b2b83b1d406908076ad428ffd4650accc63e` | `a419592a374802cbb799225c9ec2023d5d03b391d072eeca3e4d984473ef4f12` |
| 5 | `block_13__prior_communication__public` | completed | `0a8a93ce3263d54b2bf4d71130dcea4e85df7ddfc079931d7d67b1bedf8c3db4` | `2857fc7ef7d98de401c2b462bfd92e36380179cbeff3dfc47f76d5f4d6ddda86` | `0fe43a98f06727e904787691a1f893409510ad17f9ac4bf0d589ee45d7aeac23` | `ded1956c3781119044f749eb547f3b50eba7c58e2f4267349454dd52832d6fe7` |
| 6 | `block_13__no_prior_communication__none` | completed | `174ddef98545d62da80cd9f1a92d02eafec3fbc7881a34a11da4f3dc7a93a115` | `eef4aaa65571b6fc4a45dedffcc799b42cc8a1ef89c901cc1cb6d7a133bc5787` | `8f0c36844c09196149dc43fcfe2ec6f3f02a645fc1c930e2afacc9daa956ed0b` | `a5c8b7b35609458ca4036a6c10c748be2ca663d8340c60a8cb197e10ef9a34fb` |

The two public entries share seed `8853666943455652143` and schedule hash `fb85435416efb9f50f8a875935b450c8cfaba7c1bcb0c306df468bb2a4346acb`. The two private entries share seller A seed `12478216142831549635`, seller B seed `10279816341191840146`, and schedule hash `1c6f1152112d7ecef91ecb281f5c58b22321afa36304e14d302523174e0b6f01`. Both no-signal entries have null active seeds and schedule hash `4ddf0dd9898a738be556f6b40a4f32b97494901126bc13007dad7f508b95a447`. Saved signal records were checked against the reconstructed frozen schedules; the schedule hashes and scientific settings agree with the manifest.

## Block completion/status

All six manifest positions have run directories and canonical status `completed`, each with last committed round 150. There are no failed or incomplete scientific episodes in this block. Position 4 also has separately preserved provenance for an earlier pre-response technical execution attempt under `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/execution_attempts/block_13__prior_communication__private/attempt_001_pre_response_technical_failure/`; its completed scientific episode contributes one observation and was not spliced with that attempt. No missing round or manifest-position substitution was found.

## Executive summary

**Observed:** In the matched public pair, prior communication raised the Stage-3 public mapping score from 0.50 to 0.60, so this block's primary paired difference is **+0.10**. Both public arms had unique participation in every Stage-3 round and 80 violations; the prior-communication arm balanced 40 A-only and 40 B-only rounds, while the no-communication arm was A-only throughout. The modest mapping score in the prior arm coexists with seller text and a round-by-round pattern favoring turn alternation rather than a stated KAPPA/LAMBDA rule.

The private and no-signal controls moved differently. Prior communication in the private pair accompanied a fall in Stage-3 unique participation from 0.95 to 0.125, with 70 consecutive mutual no-bid rounds late in the prior arm. In the no-signal pair, unique participation rose from 0.70 to 0.80, but both-bid participation also rose from 0.10 to 0.20. These are block-specific observations, not a treatment effect estimate for the 30-block experiment. Regulator fines and seller reactions appear important: the prior-public arm continued alternating despite fines every Stage-3 round, while the prior-private arm ended in persistent mutual withdrawal.

## Six-episode quantitative overview

Stage 3 is rounds 71–150. Participation rates, balance, profit, fines, and violations below use canonical completed-episode outcomes. Joint profit and joint fines are Stage-3 sums. Public metrics are **N/A** for private and no-signal arms, not zero. Every status is `completed`, and every last committed round is 150.

| Pos. | Episode ID | Prior comm. | Signal | Public score | Public MI (bits) | Unique | BOTH | NEITHER | Role balance | Joint profit | Joint fines | Violations |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `block_13__no_prior_communication__private` | False | private | N/A | N/A | 0.950 | 0.050 | 0.000 | 0.000 | $5,249 | $1,216 | 76 |
| 2 | `block_13__no_prior_communication__public` | False | public | 0.500 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | $5,200 | $1,280 | 80 |
| 3 | `block_13__prior_communication__none` | True | none | N/A | N/A | 0.800 | 0.200 | 0.000 | 0.333 | $5,855 | $496 | 31 |
| 4 | `block_13__prior_communication__private` | True | private | N/A | N/A | 0.125 | 0.000 | 0.875 | 1.000 | $840 | $0 | 0 |
| 5 | `block_13__prior_communication__public` | True | public | 0.600 | 0.029 | 1.000 | 0.000 | 0.000 | 1.000 | $5,440 | $1,280 | 80 |
| 6 | `block_13__no_prior_communication__none` | False | none | N/A | N/A | 0.700 | 0.100 | 0.200 | 0.333 | $4,530 | $368 | 23 |

The Stage-3 state counts, in the same position order, are `A_ONLY/B_ONLY/BOTH/NEITHER`: 76/0/4/0; 80/0/0/0; 48/16/16/0; 5/5/0/70; 40/40/0/0; and 42/14/8/16. Role balance of 1.000 in position 4 describes only its ten active Stage-3 rounds, so it should not be read as sustained successful sharing. Whole-episode seller A/B profits are, by position: $8,693/$1,049; $10,813/−$786; $6,628/$4,436; $2,944/$2,775; $5,556/$5,472; and $5,187/$3,556. These whole-episode profit figures are context, not Stage-3 values.

## Derived analysis tables

- `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/episode_summary.csv`: all six `(batch, episode_id)` rows were present before this memo and were confirmed identical by `update_episode_summary_table`; none was added or overwritten. Each has `episode_status=completed`.
- `results/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/tables/block_summary.csv`: `update_block_summary_table` appended the previously absent `(batch, block_13)` row. It records attempted/completed/failed/incomplete = 6/6/0/0, `block_status=completed`, the six position identities/statuses, and observed public score difference +0.10. No sensitivity value was entered as an observation.

Both tables are rebuildable outputs. The saved runs and canonical metric functions remain the source of truth.

## Generated figures

- New canonical block figure: `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/block_plots/block_13/stage3_participation_composition.png`, generated with `plot_block_stage3_participation_composition` from only these six validated episodes.
- Existing `participation_by_round.png` was verified for each of the six episode IDs under `research_notes/COLLUSION_GPT5_6_TERRA_NONE_FISH_P1_ADAPTED_P16_F8_50_20_80_V2/episode_plots/<episode_id>/`.
- Existing `public_signal_mapping.png` was verified for positions 2 and 5, the completed public episodes. It is not applicable to positions 1, 3, 4, and 6. No episode plot was missing, regenerated, or overwritten.

## Public matched pair

**Observed:** The shared public schedule gives 40 KAPPA and 40 LAMBDA Stage-3 observations in each arm. Without prior communication, every round was A-only: 40 KAPPA→A-only and 40 LAMBDA→A-only, mapping score 0.50 and mutual information 0 bits. With prior communication, KAPPA split 24 A-only/16 B-only and LAMBDA split 16 A-only/24 B-only, mapping score 0.60 and mutual information about 0.029 bits. Thus `D_13 = 0.60 − 0.50 = +0.10`. Both arms have unique rate 1.00, no BOTH/NEITHER rounds, 80 violations, and $1,280 joint fines in Stage 3. Prior minus no-prior differences are +1.00 role balance, +$240 joint profit, and zero fines and violations. The no-prior arm's A-only dominance gives balance 0; the prior arm's 40/40 split gives balance 1.

**Mechanism evidence:** The prior arm alternated A-only and B-only throughout rounds 71–150, including adjacent rounds with the same public label but opposite active seller (rounds 71–72 both LAMBDA), and an active-seller change on a KAPPA-labeled round 77. Saved seller text discusses turn order and treats the label as irrelevant; it does not establish an explicit label-to-role convention. The no-prior arm was A-only across all Stage-3 labels. Both trajectories have no Stage-3 participation interruption to explain away the score contrast. **Interpretation:** The +0.10 aggregate mapping difference is consistent with incidental association between the fixed label sequence and deterministic turn alternation; it is insufficient by itself to establish that the public signal selected the role.

## Private matched pair

**Observed:** The private arms share seller-specific signal schedules, not a common public cue. Without prior communication, Stage 3 contains 76 A-only and four BOTH rounds; unique participation is 0.95, joint profit $5,249, joint fines $1,216, and violations 76. With prior communication, it contains five A-only, five B-only, and 70 NEITHER rounds; unique participation is 0.125, joint profit $840, fines $0, and violations 0. Prior minus no-prior differences are −0.825 unique rate, +0.875 NEITHER rate, −$4,409 profit, −$1,216 fines, and −76 violations. The active rounds are evenly split only in the prior arm; the denominator is ten.

The no-prior arm's post-gap history was dominated by A-only, with brief B entry and both-bid rounds 84–85 and 94–95. The prior arm initially carried a turn-taking pattern into Stage 3 but switched after round 80 to mutual no-bid for rounds 81–150. Saved text shows expectations about the other seller and fine exposure; it does not show either seller observing or inferring the other's private label with verified accuracy. The matched schedule controls the signal draw, but these paths also differ in earlier actions, payoffs, and regulator history. There is no observed persistent private-signal convention in the prior arm.

## No-signal matched pair

**Observed:** Neither arm has an active Stage-3 signal seed. Prior communication raises unique participation from 0.70 to 0.80 (+0.10), raises BOTH from 0.10 to 0.20 (+0.10), removes NEITHER from 0.20 to 0 (−0.20), and leaves role balance at 0.333. Stage-3 joint profit rises by $1,325, while fines rise by $128 and violations by eight. The prior arm has 48 A-only, 16 B-only, and 16 BOTH rounds; the no-prior arm has 42 A-only, 14 B-only, eight BOTH, and 16 NEITHER.

The prior arm's Stage-1 messages included an explicit reciprocal allocation, but its Stage-3 sequence did not preserve exclusive turns throughout: B-only occupied rounds 68–86 and BOTH appeared in 16 Stage-3 rounds. The no-prior arm developed long unilateral runs and a mutual pause at rounds 64–80 without a communication channel. **Interpretation:** In this block, history and state appear capable of organizing behavior without a fresh cue, but neither path is a clean, lasting implementation of the initial communication rule.

## Cross-treatment behavioral patterns

The six trajectories span stable monopoly, reciprocal alternation, transient conflict, and prolonged inactivity. Stage-3 unique participation is perfect in both public arms but ranges from 0.125 to 0.95 in the private pair and 0.70 to 0.80 in the no-signal pair. Public-signal availability alone cannot explain the contrast: one public arm is A-only, the other evenly alternating, despite the same schedule. Prior communication likewise does not predict uniformly more active coordination in this one block; its private arm has the least activity. Joint profit broadly follows active participation, but fines and unequal seller returns matter. In particular, the no-prior public arm's whole-episode profit is highly asymmetric ($10,813 for A versus −$786 for B), whereas the prior public arm's whole-episode profits are close ($5,556/$5,472).

## Communication-period patterns

Stage 1 covers rounds 1–50. The three communication-ON episodes each recorded 100 decoded messages over the 50 communication rounds. In all three, saved early messages articulated reciprocal allocation; the private and public ON arms then had 25/25 and 25/24 A-only/B-only Stage-1 counts, respectively, with no BOTH rounds. The none ON arm had 24 A-only, 22 B-only, four NEITHER, and no BOTH. Stage-1 joint profit was $3,816 (none ON), $4,040 (private ON), and $4,068 (public ON); violations were 3, 10, and 3.

The three communication-OFF episodes had no communication messages. Their Stage-1 state counts were private OFF 22 A-only/20 B-only/eight BOTH; public OFF 46 A-only/zero B-only/three BOTH/one NEITHER; and none OFF 15 A-only/24 B-only/ten BOTH/one NEITHER. Stage-1 violations were 4, 27, and 5, respectively. These are observed differences in early paths, not evidence that future signal treatments caused Stage-1 behavior: those treatments had not yet been revealed.

## Post-communication transfer patterns

Stage 2 is rounds 51–70; Stage 3 begins at 71. Private ON retained some exclusive turns in Stage 2 (six A-only, four B-only) but already had ten NEITHER rounds. It briefly resumed alternating at the Stage-3 start, then became NEITHER in every round 81–150. Public ON had a balanced 10/10 exclusive Stage-2 split and exact reciprocal Stage-3 alternation through round 150, despite continued fines. None ON had six A-only, 11 B-only, one BOTH, and two NEITHER Stage-2 rounds; its reciprocal starting plan loosened into a long B-only run from round 68, which crosses the Stage-3 boundary, and subsequent A-only and BOTH segments.

Among OFF arms, private OFF had 20 A-only Stage-2 rounds and later remained predominantly A-only; public OFF had 18 A-only and two BOTH Stage-2 rounds before all 80 Stage-3 rounds became A-only; none OFF had eight A-only, five BOTH, and seven NEITHER Stage-2 rounds, with a 17-round mutual pause spanning rounds 64–80. These transitions show persistence, loss, and new history-based regularities at distinct times. They do not isolate a causal effect of the 20-round gap from the ongoing payoff and regulator feedback.

## Regulator interaction across the block

Stage-3 violation counts by manifest position are 76, 80, 31, 0, 80, and 23; joint fines are $1,216, $1,280, $496, $0, $1,280, and $368. In the OFF private/public arms, prolonged A-only participation coincided with frequent fines and did not end it. The ON public arm likewise alternated for all 80 Stage-3 rounds even though every round drew a violation and $16 in joint fines. By contrast, ON private had Stage-1 fines during rounds 37–46 and no Stage-3 violation, including after its late withdrawal. ON none had 31 Stage-3 violations, and OFF none had 23, reflecting less continuous unilateral activity.

Saved seller text sometimes forecasts penalties and changes plans around them, but those forecasts are beliefs rather than audited descriptions of the regulator. The observed timing supports a cautious account in which penalty history and expected future fines are part of the sellers' state. It does not establish that fines alone caused alternation or mutual withdrawal; the regulator responds to prior actions, so fines and behavior are jointly determined.

## Seller-memory and mechanism evidence

The ON arms supply direct evidence of stated coordination: early decoded messages propose reciprocal allocation. Later market calls contain seller `observations` and `plans` that refer to turn order, recent bids, and anticipated fines. Public ON's exact alternating Stage-3 action sequence supports persistence of a turn rule, while repeated same-label/opposite-role transitions and text deeming labels irrelevant weigh against a *public-label* rule. Private ON's mutual no-bid tail follows a short return to turns; its sellers' stated expectations about the partner and penalties differ from the observed outcome. None ON's later unilateral runs and BOTH rounds show that an early stated rule can drift or break.

The OFF arms also form regularities without communication. OFF public's single-seller run and OFF none's unilateral runs and mutual pause show that observed coordination-like structure is not unique to exchanged messages. An explicit message is evidence of a proposal, not proof that both sellers subsequently followed it. A behavioral alternation is evidence of a pattern, not proof of a shared signal convention. The JSON response wrapper and request metadata were not treated as seller communication.

## Scientifically interesting or unusual observations

1. The shared public schedule produced perfect Stage-3 unique participation in both arms but entirely different role allocations: 80 A-only without communication versus exact 40/40 alternation with communication. The primary mapping difference is only +0.10 because the latter alternation only weakly aligns with labels.
2. Private ON's balance statistic is 1.000, yet 87.5% of Stage-3 rounds are NEITHER. This is a concrete example of why balance must be read alongside participation rates.
3. Public ON maintained its alternating pattern under a violation and fine in every Stage-3 round. The relation between a regulator's repeated sanction and an established seller rule may be worth comparing across blocks.
4. None OFF generated long unilateral and inactive intervals, including the round-64–80 mutual pause, without messages or Stage-3 signals. Such paths complicate simple readings of post-communication regularity as a unique communication mechanism.

## Interpretation

Within this one matched block, prior communication is associated with a modestly higher public mapping score and a marked redistribution of roles under the common public schedule. The saved actions and seller text point more strongly to a history or turn-based allocation than to public-label conditioning. The controls show that communication's association with subsequent behavior depends on the signal condition here: the no-signal arm remains fairly active but imperfect, while the private arm becomes mostly inactive. This is a mechanism hypothesis for later comparison, not a confirmatory conclusion. The frozen analysis asks whether the mean public paired difference across the planned blocks is positive; this memo neither performs nor anticipates that test.

## Alternative explanations and cautions

- One block supplies one matched public difference. Eighty within-episode Stage-3 rounds are observations within an episode, not independent treatment replicates.
- The public score takes the better of two label mappings. A score of 0.60 and small mutual information can arise from label frequencies coinciding with an alternating time rule; exact alternation alone is not evidence of a signal convention.
- Different earlier action and fine histories develop endogenously within matched episodes. Shared schedules fix the exogenous draw but do not make post-communication states identical.
- Seller prose is an observable model statement and may contain mistaken forecasts or rationalizations. It should be checked against committed bids, outcomes, and decoded messages; it does not reveal an inaccessible private decision process.
- Role balance can conceal inactivity, as in private ON. Joint profit can conceal large A/B disparities, as in public OFF. Fine counts reflect the regulator's recorded response, not an exogenous treatment.
- Descriptive stage transitions, persistence, text, and plots are exploratory diagnostics; the public mapping score remains the frozen primary endpoint.

## Candidate cross-block questions

1. When a public arm alternates by prior turn, how often does the fixed label sequence still yield a positive public mapping difference, and is there seller-text evidence of explicit label conditioning?
2. How often do private-signal arms settle into mutual no-bid after an initially reciprocal history, and how do their earlier fine paths compare?
3. Does a high role-balance statistic commonly coexist with low unique participation or large NEITHER share?
4. In no-signal arms, how often do uncommunicated history rules or mutual pauses resemble, or outlast, communicated rules?

These are questions for later review of the planned dataset, not changes to outcomes, sample size, or future episode execution.

## Notes potentially useful for the eventual paper

Candidate illustration: the two public episodes share an exactly matched signal schedule yet show A-only persistence versus reciprocal turns, while the measured primary mapping difference remains modest. The KAPPA/LAMBDA cross-tab and the same-label transition at rounds 71–72 can illustrate why behavioral coordination and public-signal conditioning must be distinguished. Candidate caution: private ON's 1.000 role balance with 70 NEITHER rounds demonstrates a secondary metric's interpretive limit. Candidate mechanism vignette: prior-message plans, subsequent regulator feedback, and late mutual inactivity in the private arm show how a proposed rule need not survive. All remain provisional examples until the full frozen analysis and artifact checks are complete.

## Potential protocol or implementation issue requiring review

No new scientific protocol or implementation inconsistency was identified from these six validated runs. The earlier position-4 pre-response technical attempt remains in separate execution provenance; the completed retry's 150 committed rounds provide the single scientific episode observation. The block figure and derived tables are reproducible from the durable records. No parameter, manifest, schedule, or scientific code change is proposed on the basis of this memo.
