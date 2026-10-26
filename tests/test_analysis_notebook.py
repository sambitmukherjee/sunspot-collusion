"""Keep the analysis notebook a thin, read-only interface."""

import ast
import json
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks" / "analysis.ipynb"


def test_analysis_notebook_uses_package_and_exports_are_opt_in():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    code = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code")
    assert all(cell.get("outputs", []) == [] for cell in notebook["cells"] if cell["cell_type"] == "code")
    assert "from collusion_experiment.metrics import" in code
    assert "from collusion_experiment.public_signal_inference import public_signal_episode_tests" in code
    assert "public_signal_episode_tests(episodes, block_ids=PUBLIC_SIGNAL_BLOCKS)" in code
    assert "PUBLIC_SIGNAL_BLOCKS = range(1, 21)" in code
    assert "from collusion_experiment.plotting import" in code
    assert "EXPORT_DERIVED = False" in code
    assert '"results" / SPECIFICATION_VERSION / "runs"' in code
    assert '"results" / SPECIFICATION_VERSION / "analysis"' in code
    assert "if EXPORT_DERIVED:" in code
    assert "run_episode(" not in code
    assert "OpenAI(" not in code
    assert "google.colab" not in code
    assert "/Users/" not in code
    assert not any(name in code for name in ("config.json\"", "rounds.jsonl\"", "failure.json\"", "final_episode.json\""))
    defined = {node.name for node in ast.walk(ast.parse(code)) if isinstance(node, ast.FunctionDef)}
    assert not defined & {"episode_summary", "public_signal_mapping_score", "public_signal_mutual_information", "stage_summaries"}
