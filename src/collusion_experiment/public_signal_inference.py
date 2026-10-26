"""Episode-level public-signal inference from saved, completed runs.

The exact test conditions on an episode's bidding record. Under the strong
null that replacing the fair signal sequence would leave those bids unchanged,
the number of matches to either fixed signal-to-agent assignment is binomial.
This is an exploratory analysis, added after some episodes were inspected.
"""

from math import comb, isfinite
from typing import Iterable

from .metrics import EpisodeArtifacts, public_signal_participation_table


def exact_mapping_p_value(forward_matches: int, reverse_matches: int) -> float:
    """Exact upper-tail probability for the better of two opposite assignments.

    Each sole-bid round matches exactly one assignment. With m such rounds,
    H (forward matches) is Binomial(m, 1/2) under the fixed-bids null. The
    statistic is max(H, m-H), including the choice of the better assignment.
    """
    if (type(forward_matches) is not int or type(reverse_matches) is not int
            or min(forward_matches, reverse_matches) < 0):
        raise ValueError("Match counts must be nonnegative integers.")
    m = forward_matches + reverse_matches
    if m == 0:
        return 1.0
    k = max(forward_matches, reverse_matches)
    upper_tail = sum(comb(m, j) for j in range(k, m + 1))
    return min(1.0, (2 * upper_tail) / (1 << m))


def holm_adjusted_p_values(p_values: Iterable[float]) -> list[float]:
    """Return Holm-adjusted p-values in the same order as the inputs."""
    values = list(p_values)
    if any(not isinstance(p, (int, float)) or not isfinite(p) or not 0 <= p <= 1
           for p in values):
        raise ValueError("P-values must be finite numbers between zero and one.")
    adjusted = [0.0] * len(values)
    running_max = 0.0
    for rank, index in enumerate(sorted(range(len(values)), key=lambda i: values[i])):
        running_max = max(running_max, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running_max)
    return adjusted


def public_signal_randomization_test(episode: EpisodeArtifacts) -> dict:
    """Test whether one signal-to-agent assignment fits unusually many rounds.

    The denominator of the mapping score is every public-signal round, while
    only sole-bid rounds enter the exact null distribution. Both-bid and
    neither-bid rounds match neither assignment.
    """
    table = public_signal_participation_table(episode)
    if table is None:
        raise ValueError("The episode must be completed and have public signals.")
    first, second = episode.design.public_signal_values
    counts = table["counts"]
    forward = counts[first]["A_ONLY"] + counts[second]["B_ONLY"]
    reverse = counts[first]["B_ONLY"] + counts[second]["A_ONLY"]
    n_rounds = sum(table["signal_totals"].values())
    if n_rounds == 0:
        raise ValueError("The episode has no public-signal rounds.")
    best = max(forward, reverse)
    if forward == reverse:
        assignment = "tie"
    elif forward > reverse:
        assignment = f"{first}->Agent A, {second}->Agent B"
    else:
        assignment = f"{first}->Agent B, {second}->Agent A"
    return {
        "block": episode.config["replicate_id"],
        "run_name": episode.config["run_name"],
        "earlier_communication": episode.config["prior_communication"],
        "public_signal_rounds": n_rounds,
        "sole_bid_rounds": forward + reverse,
        "forward_matches": forward,
        "reverse_matches": reverse,
        "better_assignment": assignment,
        "best_matches": best,
        "mapping_score": best / n_rounds,
        "exact_p": exact_mapping_p_value(forward, reverse),
    }


def public_signal_episode_tests(
    episodes: Iterable[EpisodeArtifacts], *, block_ids: Iterable[int] | None = None
) -> list[dict]:
    """Test public episodes and apply Holm over the entire selected family.

    If block_ids is supplied, require exactly two completed public episodes
    (earlier communication on/off) per block. This prevents an incomplete
    extract from silently changing the multiplicity correction.
    """
    requested = None if block_ids is None else set(block_ids)
    if requested is not None and any(type(block) is not int or block < 1 for block in requested):
        raise ValueError("Block IDs must be positive integers.")
    selected = [ep for ep in episodes if ep.config["signal_condition"] == "public"
                and (requested is None or ep.config["replicate_id"] in requested)]
    seen = set()
    for ep in selected:
        key = (ep.config["replicate_id"], ep.config["prior_communication"])
        if key in seen:
            raise ValueError(f"Duplicate public-signal episode for block/treatment {key}.")
        seen.add(key)
        if ep.status != "completed":
            raise ValueError(f"Public-signal episode is not complete: {ep.config['run_name']}.")
    if requested is not None:
        expected = {(block, prior) for block in requested for prior in (False, True)}
        if seen != expected:
            raise ValueError(f"Missing public-signal block/treatment positions: {sorted(expected - seen)}.")
    rows = [public_signal_randomization_test(ep) for ep in selected]
    rows.sort(key=lambda row: (row["block"], row["earlier_communication"]))
    for row, adjusted in zip(rows, holm_adjusted_p_values(row["exact_p"] for row in rows)):
        row["holm_adjusted_p"] = adjusted
    return rows
