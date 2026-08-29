"""
Fetches BTCUSD 5-minute candles from Delta Exchange's public candle API,
paginated in small chunks (the API caps how much history one call returns),
and appends to data/btcusd_5m.csv. Resumable: if the file already exists,
only fetches candles newer than the last saved timestamp.

Run standalone: python fetch_data.py --days 400
"""
import argparse
import csv
import os
import time
from datetime import datetime, timezone

import requests

SYMBOL = "BTCUSD"
RESOLUTION = "5m"
BASE_URL = "https://api.india.delta.exchange"
ENDPOINT = f"{BASE_URL}/v2/history/candles"
CHUNK_SECONDS = 3 * 24 * 60 * 60  # 3 days per request, well under any candle-count cap
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "btcusd_5m.csv")
HEADERS = ["time", "open", "high", "low", "close", "volume"]


def fetch_chunk(start, end, retries=3):
    params = {"symbol": SYMBOL, "resolution": RESOLUTION, "start": start, "end": end}
    for attempt in range(retries):
        try:
            resp = requests.get(ENDPOINT, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            result = data.get("result", [])
            return sorted(result, key=lambda c: c["time"])
        except Exception as e:
            print(f"  chunk fetch failed (attempt {attempt+1}/{retries}): {e}")
            time.sleep(2 * (attempt + 1))
    return []


def last_saved_time():
    if not os.path.exists(DATA_FILE):
        return None
    last = None
    with open(DATA_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            last = int(row["time"])
    return last


def append_rows(rows):
    file_exists = os.path.exists(DATA_FILE)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in HEADERS})


def main(days_back):
    now = int(datetime.now(timezone.utc).timestamp())
    resume_from = last_saved_time()
    start_overall = resume_from + 300 if resume_from else now - days_back * 86400

    if start_overall >= now:
        print("Data already up to date.")
        return

    print(f"Fetching {SYMBOL} {RESOLUTION} candles from "
          f"{datetime.fromtimestamp(start_overall, tz=timezone.utc)} to "
          f"{datetime.fromtimestamp(now, tz=timezone.utc)}")

    cursor = start_overall
    total_rows = 0
    seen_times = set()
    while cursor < now:
        chunk_end = min(cursor + CHUNK_SECONDS, now)
        rows = fetch_chunk(cursor, chunk_end)
        new_rows = [r for r in rows if r["time"] not in seen_times]
        if new_rows:
            append_rows(new_rows)
            total_rows += len(new_rows)
            seen_times.update(r["time"] for r in new_rows)
        print(f"  {datetime.fromtimestamp(cursor, tz=timezone.utc).date()} "
              f"-> {len(rows)} candles (total so far: {total_rows})")
        cursor = chunk_end
        time.sleep(0.3)  # be polite to the public API

    print(f"Done. {total_rows} new candles written to {DATA_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=400, help="Days of history to fetch on first run")
    args = parser.parse_args()
    main(args.days)
