from __future__ import annotations
from datetime import datetime
import pandas as pd
from typing import Any
from zoneinfo import ZoneInfo


TZ = ZoneInfo("Europe/Riga")


def _parse_timestamp(value: Any) -> pd.Timestamp:
    """Convert an API timestamp to Europe/Riga timezone."""

    if value is None:
        return pd.NaT

    if isinstance(value, (int, float)):
        timestamp = pd.to_datetime(
            value,
            unit="s",
            utc=True,
        )
    else:
        timestamp = pd.to_datetime(
            value,
            utc=True,
        )

    return timestamp.tz_convert(TZ)


def normalize_day_ahead_prices(
    raw: dict[str, Any],
    delivery_date: str,
    extraction_timestamp: datetime,
) -> pd.DataFrame:
    """
    Convert Nord Pool Day-Ahead JSON into the final Parquet schema.

    Final schema:

        extraction_date
        delivery_date
        period_start
        period_end
        delivery_area
        price_eur_mwh
        currency
    """

    if not isinstance(raw, dict):
        raise ValueError("raw must be a dictionary")

    entries = raw.get("multiAreaEntries")

    if not isinstance(entries, list):
        raise ValueError(
            "Expected 'multiAreaEntries' in API response"
        )

    extraction_date = (
        pd.Timestamp(extraction_timestamp)
        .tz_convert(TZ)
        .date()
    )

    rows = []

    for entry in entries:
        period_start = _parse_timestamp(
            entry.get("deliveryStart")
        )

        period_end = _parse_timestamp(
            entry.get("deliveryEnd")
        )

        if pd.isna(period_start) or pd.isna(period_end):
            raise ValueError(
                "Invalid deliveryStart or deliveryEnd"
            )

        area_prices = entry.get("entryPerArea")

        if not isinstance(area_prices, dict):
            raise ValueError("Expected entryPerArea to be a dictionary")

        for area, price in area_prices.items():

            try:
                price = float(price)
            except (TypeError, ValueError):
                price = float("nan")

            rows.append(
                {
                    "extraction_date": extraction_date,
                    "delivery_date": pd.Timestamp(
                        delivery_date
                    ).date(),
                    "period_start": period_start,
                    "period_end": period_end,
                    "delivery_area": str(area),
                    "price_eur_mwh": price,
                    "currency": raw.get("currency"),
                }
            )

    if not rows:
        raise ValueError(
            "No price entries found in API response"
        )

    df = pd.DataFrame(rows)

    df["extraction_date"] = pd.to_datetime(
        df["extraction_date"]
    ).dt.date

    df["delivery_date"] = pd.to_datetime(
        df["delivery_date"]
    ).dt.date

    df["period_start"] = pd.to_datetime(
        df["period_start"],
        utc=True,
    ).dt.tz_convert(TZ)

    df["period_end"] = pd.to_datetime(
        df["period_end"],
        utc=True,
    ).dt.tz_convert(TZ)

    df["price_eur_mwh"] = pd.to_numeric(
        df["price_eur_mwh"],
        errors="coerce",
    )

    df["delivery_area"] = df["delivery_area"].astype("string")
    df["currency"] = df["currency"].astype("string")

    return df[
        [
            "extraction_date",
            "delivery_date",
            "period_start",
            "period_end",
            "delivery_area",
            "price_eur_mwh",
            "currency",
        ]
    ]