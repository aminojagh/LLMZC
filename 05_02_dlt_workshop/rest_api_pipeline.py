from typing import Any

import dlt
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="agent_logs")
def agent_logs_source(base_url: str = dlt.config.value) -> Any:
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
        },
        "resources": [
            {
                "name": "logs",
                "endpoint": {
                    "path": "logs",
                    "data_selector": "logs",
                    "params": {
                        "limit": 1000,
                    },
                    "paginator": {
                        "type": "offset",
                        "limit": 1000,
                        "offset_param": "offset",
                        "limit_param": "limit",
                        "total_path": "total",
                        "maximum_offset": 20000,
                    },
                },
            },
        ],
    }

    yield from rest_api_resources(config)


def load_logs() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="agent_logs_pipeline",
        destination="duckdb",
        dataset_name="agent_logs",
        dev_mode=True,  # fresh dataset on every run during dev
    )

    load_info = pipeline.run(agent_logs_source(), write_disposition="replace")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_logs()
