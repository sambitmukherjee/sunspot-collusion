"""One end-to-end, fully offline analysis and export smoke path."""

import hashlib
from math import isclose
import os
from pathlib import Path
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from collusion_experiment.metrics import (
    episode_summary, load_episode_artifacts, paired_prior_communication_difference,
    public_signal_mapping_score, public_signal_mutual_information, stage_summaries,
)
from collusion_experiment.plotting import plot_episode_participation_timeline


def test_synthetic_analysis_smoke_is_read_only(synthetic_analysis_run, tmp_path):
    directories = [synthetic_analysis_run("without", prior=False),
                   synthetic_analysis_run("with", prior=True)]
    before = {directory: {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in directory.iterdir()} for directory in directories}
    episodes = [load_episode_artifacts(directory) for directory in directories]
    summaries = [episode_summary(episode) for episode in episodes]
    assert all(len(stage_summaries(episode)) == 3 for episode in episodes)
    assert all(public_signal_mapping_score(episode) == 1 for episode in episodes)
    assert all(isclose(public_signal_mutual_information(episode), 1) for episode in episodes)
    pairs = paired_prior_communication_difference(summaries, signal_condition="public", metric="joint_profit")
    assert len(pairs) == 1 and pairs[0]["status"] == "paired" and pairs[0]["difference"] == 0
    fig, _ = plot_episode_participation_timeline(episodes[0])
    assert fig.axes
    plt.close(fig)
    output = tmp_path / "analysis" / "episode_summary.csv"
    script = Path(__file__).resolve().parents[1] / "scripts" / "summarize_results.py"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(script.parents[1] / "src")
    result = subprocess.run([sys.executable, str(script), *(str(path) for path in directories),
                             "--output", str(output)], capture_output=True, text=True, env=environment)
    assert result.returncode == 0, result.stderr
    assert output.is_file()
    after = {directory: {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in directory.iterdir()} for directory in directories}
    assert after == before
