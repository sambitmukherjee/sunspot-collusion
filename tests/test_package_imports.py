"""Smoke test for package layout without external calls."""

from importlib import import_module


def test_package_modules_import() -> None:
    modules = (
        "collusion_experiment",
        "collusion_experiment.config",
        "collusion_experiment.market",
        "collusion_experiment.regulator",
        "collusion_experiment.signals",
        "collusion_experiment.prompts",
        "collusion_experiment.structured_outputs",
        "collusion_experiment.api",
        "collusion_experiment.episode",
        "collusion_experiment.storage",
        "collusion_experiment.metrics",
        "collusion_experiment.plotting",
    )

    for name in modules:
        assert import_module(name).__name__ == name
