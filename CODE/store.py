"""Storage utilities: append + dedupe + schema validation for master parquet files."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
from datetime import timezone, timedelta

import pandas as pd

# Target timezone: UTC+3
TZ = timezone(timedelta(hours=3))


def _ensure_master_exists(path: Path, schema_df: pd.DataFrame) -> None:
    if not path.exists():
        # write empty parquet with correct dtypes
        empty = schema_df.iloc[0:0]
        empty.to_parquet(path)


def upsert(master_path: Path, new_rows: pd.DataFrame, key_cols: List[str]) -> Dict[str, int]:
    """Load existing master parquet (or create empty with correct schema), concat new_rows,
    dedupe keeping the newest fetched_at_utc per key, sort by key_cols, write back.

    Returns dict with rows_before, rows_after, rows_added.
    """
    master_path.parent.mkdir(parents=True, exist_ok=True)

    if master_path.exists():
        master = pd.read_parquet(master_path)
        # normalize existing master's timestamp columns to UTC-naive (drop tz info)
        for col in ("period_start", "period_end", "period_start_utc", "period_end_utc", "fetched_at_utc"):
            if col in master.columns:
                master[col] = pd.to_datetime(master[col], errors="coerce")
                # elementwise: if tz-aware -> convert to UTC and drop tz; if tz-naive -> assume UTC
                master[col] = master[col].map(
                    lambda x: (x.tz_convert("UTC").tz_localize(None)) if pd.notna(x) and getattr(x, "tzinfo", None) is not None else x
                )
    else:
        # create empty with same schema as new_rows
        master = new_rows.iloc[0:0]

    rows_before = len(master)

    # normalize new_rows timestamp columns to UTC-naive as well
    for col in ("period_start", "period_end", "period_start_utc", "period_end_utc", "fetched_at_utc"):
        if col in new_rows.columns:
            new_rows[col] = pd.to_datetime(new_rows[col], errors="coerce")
            new_rows[col] = new_rows[col].map(
                lambda x: (x.tz_convert("UTC").tz_localize(None)) if pd.notna(x) and getattr(x, "tzinfo", None) is not None else x
            )

    combined = pd.concat([master, new_rows], ignore_index=True)
    # keep newest fetched_at_utc per key if present (compare as UTC-naive if tz info dropped)
    if "fetched_at_utc" in combined.columns:
        combined["fetched_at_utc"] = pd.to_datetime(combined["fetched_at_utc"], errors="coerce")
        combined = combined.sort_values("fetched_at_utc")
        deduped = combined.drop_duplicates(subset=key_cols, keep="last")
    else:
        deduped = combined.drop_duplicates(subset=key_cols, keep="last")

    deduped = deduped.sort_values(key_cols)
    deduped.to_parquet(master_path, index=False)

    rows_after = len(deduped)
    rows_added = max(0, rows_after - rows_before)
    return {"rows_before": rows_before, "rows_after": rows_after, "rows_added": rows_added}
