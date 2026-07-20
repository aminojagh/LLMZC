"""Pull trace/span data from the Pydantic Logfire Query API into DuckDB.

Logfire's Query API is a single POST endpoint that runs a SQL query over
its `records` table (one row per span). There's no page-based pagination
here (dlt's rest_api pagination helpers don't apply) — a single request
returns up to `limit` rows for the requested time window, so this is a
plain dlt resource built with `requests` instead of `rest_api_source`.
"""

import os

import pendulum
from dotenv import load_dotenv

import dlt
from dlt.sources.helpers import requests

load_dotenv()

LOGFIRE_BASE_URL = "https://logfire-us.pydantic.dev"


@dlt.resource(name="records", write_disposition="replace")
def logfire_records(
    read_token: str = None,
    sql: str = "SELECT * FROM records",
    min_timestamp: str = None,
    limit: int = 10_000,
):
    """Query Logfire's `records` table (spans) via the Query API.

    Args:
        read_token: Logfire read token. Defaults to the `LOGFIRE_READ_TOKEN`
            env var (loaded from `.env` via python-dotenv, same as hw_src/main.py).
        sql: SQL query executed against Logfire's `records` table.
        min_timestamp: ISO8601 lower bound for start_timestamp.
            Defaults to 7 days ago, wide enough to cover a workshop session.
        limit: Max rows returned (Logfire caps this at 10,000).
    """
    if read_token is None:
        read_token = os.environ["LOGFIRE_READ_TOKEN"]
    if min_timestamp is None:
        min_timestamp = pendulum.now("UTC").subtract(days=7).to_iso8601_string()

    response = requests.post(
        f"{LOGFIRE_BASE_URL}/v2/query",
        json={"sql": sql, "min_timestamp": min_timestamp, "limit": limit},
        headers={
            "Authorization": f"Bearer {read_token}",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()
    yield response.json()["data"]


@dlt.source
def logfire_source(read_token: str = None):
    return logfire_records(read_token=read_token)


def load_logfire_traces() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_pipeline",
        destination="duckdb",
        dataset_name="agent_traces",
    )
    load_info = pipeline.run(logfire_source())
    print(load_info)  # noqa: T201


if __name__ == "__main__":
    load_logfire_traces()
