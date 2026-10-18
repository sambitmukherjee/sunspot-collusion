"""The block runner's execution gate is exercised only with fake calls."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from collusion_experiment.config import STRUCTURED_CONFIG
from collusion_experiment.v2_manifest import load_confirmatory_manifest, manifest_payload_sha256

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml"
MANIFEST = ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json"


def run_path(root, row):
    return root / row["specification_version"] / "runs" / row["run_name"]


@pytest.fixture
def block_runner():
    spec = importlib.util.spec_from_file_location("phase8_run_block", ROOT / "scripts" / "run_block.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_is_dry_run_and_prints_no_signal_path(block_runner, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(block_runner, "ROOT", tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("A dry run tried to construct a client or execute an episode")

    episodes = block_runner.run_selected_block(
        block_id="block_01", config_path=CONFIG, manifest_path=MANIFEST,
        runs_root=tmp_path, runner=forbidden, client_factory=forbidden)
    output = capsys.readouterr().out
    assert len(episodes) == 6 and "DRY RUN" in output
    assert [row["episode_id"] for row in episodes] == [row["episode_id"] for row in
                                                        load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"]]
    assert all(row["episode_id"] in output and row["signal_schedule_hash"] in output for row in episodes)
    assert "KAPPA" not in output and "LAMBDA" not in output
    assert list(tmp_path.iterdir()) == []


def test_block_cli_default_paths_resolve_without_execution(block_runner, capsys):
    assert block_runner.main(["--block", "block_01"]) == 0
    assert "DRY RUN" in capsys.readouterr().out


def test_execute_is_explicit_and_manifest_order_is_preserved(block_runner, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    called = []

    def fake_runner(**kwargs):
        called.append(kwargs)
        return {"status": "completed", "run_dir": str(
            tmp_path / kwargs["config"].specification_version / "runs" / kwargs["run_name"]
        )}

    episodes = block_runner.run_selected_block(
        block_id="block_01", config_path=CONFIG, manifest_path=MANIFEST,
        runs_root=tmp_path, execute=True, runner=fake_runner,
        client_factory=lambda key: object())
    assert [call["run_name"] for call in called] == [row["run_name"] for row in episodes]
    assert all(call["config"] is STRUCTURED_CONFIG for call in called)
    assert all(call["development_mode"] is False for call in called)
    assert all(call["execution_log_dir"] == block_runner.ROOT / "execution_logs"
               for call in called)
    assert all(call["transcript_metadata"]["episode_id"] == row["episode_id"]
               and call["transcript_metadata"]["block_id"] == row["block_id"]
               and call["transcript_metadata"]["sequence_position"] == row["sequence_position"]
               for call, row in zip(called, episodes))


def test_missing_key_and_existing_directory_stop_before_client(block_runner, tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("No client or episode call is allowed")

    args = dict(block_id="block_01", config_path=CONFIG, manifest_path=MANIFEST,
                runs_root=tmp_path, execute=True, runner=forbidden, client_factory=forbidden)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        block_runner.run_selected_block(**args)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    first = load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"][0]
    run_path(tmp_path, first).mkdir(parents=True)
    with pytest.raises(FileExistsError, match="already exists"):
        block_runner.run_selected_block(**args)


def test_manifest_hash_and_version_mismatch_rejected(block_runner, tmp_path):
    manifest = load_confirmatory_manifest(MANIFEST)
    args = dict(block_id="block_01", config_path=CONFIG, manifest_path=tmp_path / "manifest.json",
                runs_root=tmp_path, runner=lambda **kwargs: None,
                client_factory=lambda key: None)
    altered = deepcopy(manifest)
    altered["blocks"][0]["episodes"][0]["run_name"] = "tampered"
    args["manifest_path"].write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="payload hash"):
        block_runner.run_selected_block(**args)
    altered = deepcopy(manifest)
    altered["prompt_version"] = "PROMPT_V2"
    altered["manifest_payload_sha256"] = manifest_payload_sha256(altered)
    args["manifest_path"].write_text(json.dumps(altered))
    with pytest.raises(ValueError, match="deterministic validated extension"):
        block_runner.run_selected_block(**args)


def test_failure_stops_and_never_reruns_same_manifest_position(block_runner, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    called = []

    def failing_runner(**kwargs):
        called.append(kwargs["run_name"])
        return {"status": "failed", "run_dir": str(
            tmp_path / kwargs["config"].specification_version / "runs" / kwargs["run_name"]
        )}

    with pytest.raises(RuntimeError, match="stop at its manifest position"):
        block_runner.run_selected_block(block_id="block_01", config_path=CONFIG,
                                        manifest_path=MANIFEST, runs_root=tmp_path,
                                        execute=True, runner=failing_runner,
                                        client_factory=lambda key: object())
    assert called == [load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"][0]["run_name"]]


def test_later_block_requires_prior_blocks_before_client(block_runner, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")

    def forbidden(*args, **kwargs):
        raise AssertionError("No client or episode call is allowed")

    with pytest.raises(FileNotFoundError, match="Earlier manifest position"):
        block_runner.run_selected_block(block_id="block_10", config_path=CONFIG,
                                        manifest_path=MANIFEST, runs_root=tmp_path,
                                        execute=True, runner=forbidden,
                                        client_factory=forbidden)
