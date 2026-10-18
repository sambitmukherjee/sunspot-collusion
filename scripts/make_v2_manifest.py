#!/usr/bin/env python3
"""Regenerate the deterministic V2 manifest offline from its fixed prefix."""

import argparse
import json
from pathlib import Path

from collusion_experiment.v2_manifest import (
    generate_v2_manifest, load_confirmatory_config, validate_v2_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" /
                        "gpt5_6_terra_none_fish_p1_adapted_v2.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "configs" /
                        "gpt5_6_terra_none_fish_p1_adapted_v2_manifest.json")
    args = parser.parse_args(argv)
    frozen = load_confirmatory_config(args.config)
    manifest = generate_v2_manifest(frozen)
    audit = validate_v2_manifest(manifest, frozen)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    print("Blocks / episodes:", audit["blocks"], "/", audit["episodes"])
    print("Fixed prefix source SHA-256:", audit["prefix_source_payload_sha256"])
    print("Extension seed:", manifest["extension_seed"])
    print("V2 payload SHA-256:", audit["manifest_payload_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
