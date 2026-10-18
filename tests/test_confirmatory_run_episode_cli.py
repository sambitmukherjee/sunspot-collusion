"""Offline execution-gate tests for the single-manifest-episode CLI."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from collusion_experiment.config import STRUCTURED_CONFIG
from collusion_experiment.v2_manifest import load_confirmatory_manifest, manifest_payload_sha256

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2.yaml"
MANIFEST = ROOT / "configs" / "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json"


def run_path(root, row):
    return root / row["specification_version"] / "runs" / row["run_name"]


@pytest.fixture
def cli():
    spec = importlib.util.spec_from_file_location("phase10_run_episode", ROOT / "scripts" / "run_episode.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def first_row():
    return load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"][0]


def test_default_dry_run_resolves_exact_row_without_calls(cli, first_row, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("Dry run tried to construct a client or execute an episode")

    row = cli.run_selected_episode(episode_id=first_row["episode_id"], config_path=CONFIG,
                                   manifest_path=MANIFEST, runs_root=tmp_path,
                                   runner=forbidden, client_factory=forbidden)
    output = capsys.readouterr().out
    assert row == first_row
    assert "DRY RUN" in output
    assert all(f"{key}: {first_row[key]}" in output for key in
               ("episode_id", "run_name", "block_id", "sequence_position", "treatment_id",
                "prior_communication", "signal_condition", "signal_schedule_hash",
                "specification_version", "prompt_family", "prompt_version"))
    assert "manifest_payload_sha256:" in output and str(run_path(tmp_path, row)) in output
    assert "KAPPA" not in output and "LAMBDA" not in output
    assert list(tmp_path.iterdir()) == []


def test_cli_default_paths_resolve_without_execution(cli, first_row, capsys):
    assert cli.main(["--episode-id", first_row["episode_id"]]) == 0
    assert "DRY RUN" in capsys.readouterr().out


def test_unknown_episode_id_fails_clearly(cli, tmp_path):
    with pytest.raises(ValueError, match="found 0"):
        cli.run_selected_episode(episode_id="not_in_manifest", config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path)


def test_hash_and_specification_and_prompt_mismatch_fail(cli, first_row, tmp_path):
    original = load_confirmatory_manifest(MANIFEST)
    path = tmp_path / "manifest.json"
    args = dict(episode_id=first_row["episode_id"], config_path=CONFIG,
                manifest_path=path, runs_root=tmp_path)
    broken = deepcopy(original)
    broken["blocks"][0]["episodes"][0]["run_name"] = "tampered"
    path.write_text(json.dumps(broken))
    with pytest.raises(ValueError, match="payload hash"):
        cli.run_selected_episode(**args)
    for key in ("specification_version", "prompt_family", "prompt_version"):
        broken = deepcopy(original)
        broken[key] = "WRONG_VERSION"
        broken["manifest_payload_sha256"] = manifest_payload_sha256(broken)
        path.write_text(json.dumps(broken))
        with pytest.raises(ValueError, match="versions differ|deterministic validated extension"):
            cli.run_selected_episode(**args)


def test_existing_target_fails_before_client(cli, first_row, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    run_path(tmp_path, first_row).mkdir(parents=True)

    def forbidden(*args, **kwargs):
        raise AssertionError("Existing target must stop before a client or episode call")

    with pytest.raises(FileExistsError, match="already exists"):
        cli.run_selected_episode(episode_id=first_row["episode_id"], config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path,
                                 execute=True, runner=forbidden, client_factory=forbidden)


def test_execute_requires_key_before_client(cli, first_row, tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("Missing key must stop before a client or episode call")

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        cli.run_selected_episode(episode_id=first_row["episode_id"], config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path,
                                 execute=True, runner=forbidden, client_factory=forbidden)


def test_execute_passes_exact_manifest_row_once(cli, first_row, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    calls = []
    client = object()

    def fake_runner(**kwargs):
        calls.append(kwargs)
        return {"status": "completed", "run_dir": str(run_path(tmp_path, first_row))}

    cli.run_selected_episode(episode_id=first_row["episode_id"], config_path=CONFIG,
                             manifest_path=MANIFEST, runs_root=tmp_path,
                             execute=True, runner=fake_runner, client_factory=lambda key: client)
    assert calls == [{"replicate_id": first_row["replicate_id"],
                      "prior_communication": first_row["prior_communication"],
                      "signal_condition": first_row["signal_condition"],
                      "save_dir": tmp_path, "run_name": first_row["run_name"],
                      "public_signal_seed": first_row["public_signal_seed"],
                      "private_signal_seed_A": first_row["private_signal_seed_A"],
                      "private_signal_seed_B": first_row["private_signal_seed_B"],
                      "client": client, "config": STRUCTURED_CONFIG,
                      "development_mode": False,
                      "execution_log_dir": cli.ROOT / "execution_logs",
                      "transcript_metadata": {
                          "episode_id": first_row["episode_id"],
                          "block_id": first_row["block_id"],
                          "sequence_position": first_row["sequence_position"],
                          "manifest_payload_sha256": load_confirmatory_manifest(MANIFEST)["manifest_payload_sha256"],
                      }}]


def test_later_position_requires_prior_durable_artifact(cli, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    second = load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"][1]

    def forbidden(*args, **kwargs):
        raise AssertionError("No client or episode call should occur")

    with pytest.raises(FileNotFoundError, match="Earlier manifest position"):
        cli.run_selected_episode(episode_id=second["episode_id"], config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path,
                                 execute=True, runner=forbidden, client_factory=forbidden)


def test_later_position_rejects_prior_seed_mismatch(cli, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    rows = load_confirmatory_manifest(MANIFEST)["blocks"][0]["episodes"]
    first, second = rows[:2]
    run_path(tmp_path, first).mkdir(parents=True)
    saved = {key: first[key] for key in
             ("run_name", "specification_version", "prompt_family", "prompt_version", "replicate_id",
              "prior_communication", "signal_condition", "signal_schedule_hash")}
    saved["signal_seeds"] = {"public_signal_seed": 999,
                             "private_signal_seed_A": first["private_signal_seed_A"],
                             "private_signal_seed_B": first["private_signal_seed_B"]}
    monkeypatch.setattr(cli, "load_episode_artifacts",
                        lambda path: SimpleNamespace(status="completed", config=saved))

    def forbidden(*args, **kwargs):
        raise AssertionError("A mismatched prior run must stop before a client or episode call")

    with pytest.raises(ValueError, match="incomplete or mismatched"):
        cli.run_selected_episode(episode_id=second["episode_id"], config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path,
                                 execute=True, runner=forbidden, client_factory=forbidden)


def test_noncompleted_result_stops_without_replacement(cli, first_row, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-offline-key")
    calls = []

    def fake_failed(**kwargs):
        calls.append(kwargs["run_name"])
        return {"status": "failed", "run_dir": str(run_path(tmp_path, first_row))}

    with pytest.raises(RuntimeError, match="stop at its manifest position"):
        cli.run_selected_episode(episode_id=first_row["episode_id"], config_path=CONFIG,
                                 manifest_path=MANIFEST, runs_root=tmp_path,
                                 execute=True, runner=fake_failed,
                                 client_factory=lambda key: object())
    assert calls == [first_row["run_name"]]
