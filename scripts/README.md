# Scripts

`make_v2_manifest.py` regenerates the active manifest offline from its fixed prefix and deterministic extension algorithm. It refuses to overwrite an existing output. See the [protocol](../docs/v2_confirmatory_protocol.md) for its seed derivation and canonical payload hash.

`run_episode.py --episode-id <episode_id>` and `run_block.py --block <block_id>` validate the active V2 config and manifest and display the plan without model calls. They default to dry run. A later authorized live execution requires the explicit `--execute` flag and follows manifest order, preserving failed positions and rejecting an existing target run.

`update_summary_tables.py` derives namespaced `episode_summary.csv` and `block_summary.csv` from durable artifacts, with `episode`, `block`, and `rebuild` subcommands. `summarize_results.py` exports descriptive episode summaries to an explicitly chosen output path. Neither script modifies scientific run artifacts.
