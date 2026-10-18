"""Offline checks for the V2 manifest notebook launcher."""

import json
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "run_episode.ipynb"


def test_notebook_invokes_guarded_v2_cli():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert len(cells) == 1
    assert cells[0]["outputs"] == []
    assert cells[0]["execution_count"] is None
    code = "".join(cells[0]["source"])
    assert "gpt5_6_terra_none_fish_p1_adapted_v2.yaml" in code
    assert "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json" in code
    assert "EPISODE_ID = None" in code
    assert "EXECUTE_EPISODE = False" in code
    assert '"scripts" / "run_episode.py"' in code
    assert 'if EXECUTE_EPISODE:' in code
    assert 'command.append("--execute")' in code
    assert "subprocess.run(command, check=True)" in code
    assert "prior_communication=" not in code
    assert "signal_condition=" not in code
    assert "OPENAI_API_KEY" not in code
