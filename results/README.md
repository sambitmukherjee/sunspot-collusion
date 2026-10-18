# Results

Derived episode-level summaries and publication figures live here after runs are available.

Use `results/<specification_id>/runs/<run_name>/` for durable episode artifacts, `results/<specification_id>/tables/episode_summary.csv` for one derived row per attempted episode, `results/<specification_id>/tables/block_summary.csv` for one derived row per fully attempted six-position block, and `results/<specification_id>/analysis/` for other derived summaries and figures. The runners derive `<specification_id>` from the validated config and manifest.

Raw durable episode artifacts are the scientific source of truth. The CSV tables are convenient, rebuildable analysis datasets. In both tables, `batch` is the specification ID and `block` is the manifest block ID. The episode table uses `(batch, episode_id)` as its key; the block table uses `(batch, block)`.
