"""The episode runner uses task calls, while provider transports stay isolated."""

import ast
from pathlib import Path

import pytest

from collusion_experiment.api import call_chat_completion_raw


ROOT = Path(__file__).resolve().parents[1]


def test_episode_imports_only_provider_neutral_agent_boundary():
    path = ROOT / "src" / "collusion_experiment" / "episode.py"
    tree = ast.parse(path.read_text())
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert "api" in imports
    assert not any("provider" in (name or "") or "openai" in (name or "") for name in imports)
    providers = ROOT / "src" / "collusion_experiment" / "providers"
    assert {item.name for item in providers.iterdir() if item.suffix == ".py"} == {
        "__init__.py", "openai.py", "anthropic.py", "deepseek.py",
    }


def test_unknown_provider_is_rejected_before_client_access():
    with pytest.raises(ValueError, match="Unknown agent provider"):
        call_chat_completion_raw(prompt="offline", client=object(), provider="unknown")
