"""Headless, config-aware descriptive figures."""

import copy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pytest

from collusion_experiment.metrics import episode_summary, load_episode_artifacts, paired_prior_communication_difference
from collusion_experiment.plotting import (
    plot_block_stage3_participation_composition,
    plot_episode_participation_timeline, plot_paired_replicate_differences,
    plot_public_signal_mapping_timeline, plot_treatment_metric_distribution,
)


def test_episode_plots_use_saved_stage_boundaries_without_mutation(synthetic_analysis_run):
    episode = load_episode_artifacts(synthetic_analysis_run())
    before = copy.deepcopy(episode.rounds)
    fig, ax = plot_episode_participation_timeline(episode)
    assert isinstance(fig, Figure)
    assert ax.get_xlabel() == "Round" and ax.get_ylabel() == "Participation state"
    assert [line.get_xdata()[0] for line in ax.lines] == [2.5, 4.5]
    plt.close(fig)
    fig, ax = plot_public_signal_mapping_timeline(episode, window_size=2)
    assert isinstance(fig, Figure)
    assert ax.get_ylabel() == "Public mapping fraction"
    assert [line.get_xdata()[0] for line in ax.lines[1:]] == [2.5, 4.5]
    assert episode.rounds == before
    plt.close(fig)


def test_public_plot_rejects_no_signal_and_group_plots_use_episode_rows(synthetic_analysis_run):
    public = load_episode_artifacts(synthetic_analysis_run())
    none = load_episode_artifacts(synthetic_analysis_run("none", condition="none", prior=True))
    with pytest.raises(ValueError, match="public-signal"):
        plot_public_signal_mapping_timeline(none)
    rows = [episode_summary(public), episode_summary(none)]
    frozen = copy.deepcopy(rows)
    fig, ax = plot_treatment_metric_distribution(rows, metric="joint_profit")
    assert isinstance(fig, Figure) and ax.get_xlabel() == "Treatment"
    plt.close(fig)
    pairs = paired_prior_communication_difference(rows, signal_condition="public", metric="joint_profit")
    fig, ax = plot_paired_replicate_differences(pairs, metric="joint_profit")
    assert isinstance(fig, Figure) and ax.get_xlabel() == "Replicate ID"
    plt.close(fig)
    assert rows == frozen


def test_block_stage3_plot_has_six_ordered_bars_and_canonical_rates(synthetic_analysis_run, tmp_path):
    stage3_states = {
        ("none", False): ["A_ONLY"] * 4,
        ("none", True): ["B_ONLY"] * 4,
        ("private", False): ["BOTH"] * 4,
        ("private", True): ["NEITHER"] * 4,
        ("public", False): ["A_ONLY", "B_ONLY", "BOTH", "NEITHER"],
        ("public", True): ["A_ONLY", "A_ONLY", "B_ONLY", "NEITHER"],
    }
    episodes = []
    for (condition, prior), states in reversed(list(stage3_states.items())):
        path = synthetic_analysis_run(f"{condition}_{prior}", condition=condition, prior=prior,
                                      states=["A_ONLY", "B_ONLY", "A_ONLY", "B_ONLY"] + states)
        episodes.append(load_episode_artifacts(path))
    original_rounds = [copy.deepcopy(episode.rounds) for episode in episodes]
    file_bytes = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    fig, ax = plot_block_stage3_participation_composition(episodes, block_id="block_01")
    assert isinstance(fig, Figure) and "block_01" in ax.get_title()
    assert [tick.get_text() for tick in ax.get_xticklabels()] == [
        "none\ncomm OFF", "none\ncomm ON", "private\ncomm OFF",
        "private\ncomm ON", "public\ncomm OFF", "public\ncomm ON",
    ]
    assert [text.get_text() for text in ax.get_legend().get_texts()] == [
        "A_ONLY", "B_ONLY", "BOTH", "NEITHER", "Unavailable",
    ]
    expected = (
        [1.0, 0.0, 0.0, 0.0, 0.25, 0.5],
        [0.0, 1.0, 0.0, 0.0, 0.25, 0.25],
        [0.0, 0.0, 1.0, 0.0, 0.25, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.25, 0.25],
    )
    assert len(ax.containers) == 4
    for container, heights in zip(ax.containers, expected):
        assert [bar.get_height() for bar in container.patches] == pytest.approx(heights)
    assert [sum(container.patches[i].get_height() for container in ax.containers)
            for i in range(6)] == pytest.approx([1.0] * 6)
    plt.close(fig)
    assert [episode.rounds for episode in episodes] == original_rounds
    assert {path: path.read_bytes() for path in file_bytes} == file_bytes


def test_block_stage3_plot_marks_failed_incomplete_and_unstarted_unavailable(synthetic_analysis_run):
    rows = []
    for condition, prior, status, length in (
        ("none", False, "completed", 8),
        ("none", True, "completed", 8),
        ("private", False, "failed", 6),
        ("private", True, "incomplete", 5),
        ("public", False, "completed", 8),
    ):
        path = synthetic_analysis_run(f"{condition}_{prior}", condition=condition, prior=prior,
                                      status=status,
                                      states=["A_ONLY", "B_ONLY", "A_ONLY", "B_ONLY",
                                              "A_ONLY", "B_ONLY", "A_ONLY", "B_ONLY"][:length])
        rows.append(load_episode_artifacts(path))
    fig, ax = plot_block_stage3_participation_composition(rows, block_id="block_01")
    assert len(ax.containers) == 7  # four states and three unavailable bars
    assert [text.get_text() for text in ax.texts] == ["failed", "incomplete", "not run"]
    assert all(container.patches[index].get_height() == 0.0
               for container in ax.containers[:4] for index in (2, 3, 5))
    assert all(bar.patches[0].get_height() == 1.0 for bar in ax.containers[4:])
    plt.close(fig)


def test_block_stage3_plot_rejects_mixed_blocks_and_duplicate_cells(synthetic_analysis_run):
    path = synthetic_analysis_run("one")
    episode = load_episode_artifacts(path)
    with pytest.raises(ValueError, match="requested block"):
        plot_block_stage3_participation_composition([episode], block_id="block_02")
    with pytest.raises(ValueError, match="at most once"):
        plot_block_stage3_participation_composition([episode, episode], block_id="block_01")
