from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import logging
import pandas as pd
import requests

from CODE import API_config
from CODE.normalize import normalize_day_ahead_prices
from CODE.store import upsert


RAW_DIR = Path("data/raw")
MASTER_FILE = Path("data/master/day_ahead_prices.parquet")

RAW_DIR.mkdir(parents=True, exist_ok=True)
MASTER_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_day_ahead_prices(delivery_date: str) -> dict:
    """Fetch Day-Ahead prices for one delivery date and save the raw JSON."""

    endpoint = API_config.API_ENDPOINTS["DayAheadPrices"]

    url = (
        f"{API_config.API_BASE_URL.rstrip('/')}/"
        f"{endpoint['path'].lstrip('/')}"
    )

    params = {}

    for name, config in endpoint.get("params", {}).items():
        values = config.get("values")

        if not values:
            continue

        query_name = config.get("query_name", name)

        if config.get("type") == "list":
            params[query_name] = ",".join(map(str, values))
        else:
            params[query_name] = values[0]

    # This is the date we explicitly request from Nord Pool.
    params["date"] = delivery_date

    logger.info(
        "Fetching Day-Ahead prices for %s",
        delivery_date,
    )

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    raw_file = RAW_DIR / f"DayAheadPrices_{delivery_date}.json"

    with raw_file.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return data


def main() -> None:
    """Fetch today and tomorrow and update the master Parquet file."""

    today = datetime.now(timezone.utc).date()

   # delivery_dates = [
    #    today,
    #    today + timedelta(days=1),
    #]
    delivery_dates = pd.date_range(start = '2026-06-01', end = '2026-08-13').to_list()

    total_added = 0

    for delivery_date in delivery_dates:
        delivery_date_str = delivery_date.date().isoformat()

        try:
            raw = fetch_day_ahead_prices(delivery_date_str)

            # Exact moment the data was gathered.
            extraction_timestamp = datetime.now(
                timezone.utc
            )

            df = normalize_day_ahead_prices(
                raw=raw,
                delivery_date = delivery_date_str,
                extraction_timestamp = extraction_timestamp,
            )

            result = upsert(
                MASTER_FILE,
                df,
                [
                    "delivery_date",
                    "period_start",
                    "delivery_area",
                ],
            )

            rows_added = result.get("rows_added", 0)
            total_added += rows_added

            logger.info(
                "%s: %d rows added",
                delivery_date_str,
                rows_added,
            )

        except Exception:
            logger.exception(
                "Failed processing delivery date %s",
                delivery_date_str,
            )

    logger.info(
        "Finished. Total rows added: %d",
        total_added,
    )


if __name__ == "__main__":
    main()