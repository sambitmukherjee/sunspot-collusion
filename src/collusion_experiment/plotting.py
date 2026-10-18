"""Small, read-only matplotlib figures for descriptive episode analysis."""

from collections import defaultdict
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

from .metrics import EpisodeArtifacts, public_mapping_rolling_accuracy, round_summaries, stage_summaries


BLOCK_TREATMENT_ORDER = tuple((condition, prior) for condition in ("none", "private", "public")
                              for prior in (False, True))
STAGE3_PARTICIPATION_COLORS = (
    ("A_ONLY", "a_only_rate", "#4C78A8"),
    ("B_ONLY", "b_only_rate", "#F58518"),
    ("BOTH", "both_rate", "#54A24B"),
    ("NEITHER", "neither_rate", "#B279A2"),
)


def _stage_boundaries(ax, episode: EpisodeArtifacts) -> None:
    for boundary in (episode.design.communication_end_round, episode.design.signal_start_round - 1):
        ax.axvline(boundary + 0.5, linestyle="--", linewidth=1)


def plot_episode_participation_timeline(episode: EpisodeArtifacts):
    """Participation state by committed round; stage lines use saved timing."""
    rows = round_summaries(episode)
    fig, ax = plt.subplots()
    positions = {"NEITHER": 0, "A_ONLY": 1, "B_ONLY": 2, "BOTH": 3}
    ax.scatter([row["round_number"] for row in rows],
               [positions[row["participation_state"]] for row in rows], s=18)
    ax.set_yticks(list(positions.values()), list(positions))
    ax.set_xlabel("Round")
    ax.set_ylabel("Participation state")
    ax.set_title(f"Participation: {episode.config['run_name']}")
    ax.set_xlim(0.5, episode.design.num_rounds + 0.5)
    _stage_boundaries(ax, episode)
    fig.tight_layout()
    return fig, ax


def plot_public_signal_mapping_timeline(episode: EpisodeArtifacts, *, window_size: int = 10):
    """Rolling best public-label mapping fraction, with all rounds in denominator."""
    if episode.config["signal_condition"] != "public":
        raise ValueError("A public-signal episode is required for this plot.")
    if window_size < 1:
        raise ValueError("window_size must be positive.")
    points = public_mapping_rolling_accuracy(episode, window_size=window_size)
    fig, ax = plt.subplots()
    ax.plot([point["round_number"] for point in points],
            [point["mapping_accuracy"] for point in points])
    ax.set_xlabel("Round (rolling window end)")
    ax.set_ylabel("Public mapping fraction")
    ax.set_ylim(0, 1)
    ax.set_xlim(episode.design.signal_start_round - 1.5, episode.design.num_rounds + 0.5)
    _stage_boundaries(ax, episode)
    fig.tight_layout()
    return fig, ax


def plot_treatment_metric_distribution(summaries: Iterable[dict], *, metric: str):
    """Plot one dot per completed episode; rounds are never plotted as replicates."""
    groups = defaultdict(list)
    for row in summaries:
        if row["status"] == "completed" and row.get(metric) is not None:
            groups[(row["prior_communication"], row["signal_condition"])].append(float(row[metric]))
    fig, ax = plt.subplots()
    keys = sorted(groups)
    for index, key in enumerate(keys):
        ax.scatter([index] * len(groups[key]), groups[key], s=24)
    ax.set_xticks(range(len(keys)), [f"{condition}\ncomm={prior}" for prior, condition in keys])
    ax.set_xlabel("Treatment")
    ax.set_ylabel(metric.replace("_", " "))
    ax.set_title("Completed episode values")
    fig.tight_layout()
    return fig, ax


def plot_paired_replicate_differences(pairs: Iterable[dict], *, metric: str):
    """Show completed True-minus-False episode-level paired differences."""
    valid = [row for row in pairs if row["status"] == "paired" and row["metric"] == metric]
    fig, ax = plt.subplots()
    ax.bar([str(row["replicate_id"]) for row in valid], [row["difference"] for row in valid])
    ax.axhline(0, linewidth=1)
    ax.set_xlabel("Replicate ID")
    ax.set_ylabel(f"Prior communication difference in {metric.replace('_', ' ')}")
    ax.set_title("Paired episode differences (True minus False)")
    fig.tight_layout()
    return fig, ax


def plot_block_stage3_participation_composition(
    episodes: Iterable[EpisodeArtifacts], *, block_id: str,
):
    """Six-cell descriptive Stage-3 composition; unavailable runs have no rates.

    The saved episode config determines Stage 3 through the canonical metrics
    layer. Failed, incomplete, and unstarted cells are visibly unavailable.
    """
    if not isinstance(block_id, str) or not block_id.startswith("block_") or not block_id[6:].isdigit():
        raise ValueError("block_id must have the form block_01.")
    expected_replicate = int(block_id[6:])
    by_cell = {}
    for episode in episodes:
        if episode.config["replicate_id"] != expected_replicate:
            raise ValueError("Every episode must belong to the requested block.")
        key = (episode.config["signal_condition"], episode.config["prior_communication"])
        if key not in BLOCK_TREATMENT_ORDER or key in by_cell:
            raise ValueError("Each core treatment may appear at most once in a block plot.")
        by_cell[key] = episode

    stage3 = {}
    unavailable = {}
    for key in BLOCK_TREATMENT_ORDER:
        episode = by_cell.get(key)
        if episode is None or episode.status != "completed":
            unavailable[key] = episode.status if episode is not None else "not run"
            continue
        row = stage_summaries(episode)[2]
        expected_rounds = episode.design.num_rounds - episode.design.signal_start_round + 1
        if row["round_count"] != expected_rounds:
            raise ValueError("A completed episode must have a full Stage-3 record.")
        stage3[key] = row

    fig, ax = plt.subplots(figsize=(10, 4.5))
    positions = list(range(6))
    bottoms = [0.0] * 6
    for state, metric, color in STAGE3_PARTICIPATION_COLORS:
        heights = [stage3[key][metric] if key in stage3 else 0.0 for key in BLOCK_TREATMENT_ORDER]
        ax.bar(positions, heights, bottom=bottoms, color=color, width=0.78)
        bottoms = [bottom + height for bottom, height in zip(bottoms, heights)]
    for position, key in enumerate(BLOCK_TREATMENT_ORDER):
        if key in unavailable:
            ax.bar(position, 1.0, width=0.78, color="#E0E0E0", edgecolor="#666666", hatch="///")
            ax.text(position, 0.5, unavailable[key], ha="center", va="center", rotation=90)

    labels = [f"{condition}\ncomm {'ON' if prior else 'OFF'}" for condition, prior in BLOCK_TREATMENT_ORDER]
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Stage 3 participation-state composition")
    ax.set_xlabel("Signal condition and prior communication")
    ax.set_title(f"Stage 3 participation composition — {block_id}")
    handles = [Patch(facecolor=color, label=state) for state, _, color in STAGE3_PARTICIPATION_COLORS]
    handles.append(Patch(facecolor="#E0E0E0", edgecolor="#666666", hatch="///", label="Unavailable"))
    ax.legend(handles=handles, title="Participation state")
    fig.tight_layout()
    return fig, ax
