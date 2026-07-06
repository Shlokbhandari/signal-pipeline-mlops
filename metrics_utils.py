"""Build and write the metrics.json output in both success and error schemas.

The success schema includes version, row count, signal rate, latency, seed,
and status. The error schema includes version, status, and an error message.
Both are written as indented JSON for readability.
"""

import json


def build_success_metrics(
    version: str,
    rows_processed: int,
    signal_rate: float,
    latency_ms: int,
    seed: int,
) -> dict:
    """Build the success metrics dictionary with the exact required keys."""
    return {
        "version": version,
        "rows_processed": rows_processed,
        "metric": "signal_rate",
        "value": round(signal_rate, 4),
        "latency_ms": latency_ms,
        "seed": seed,
        "status": "success",
    }


def build_error_metrics(version: str, error_message: str) -> dict:
    """Build the error metrics dictionary with the exact required keys."""
    return {
        "version": version,
        "status": "error",
        "error_message": error_message,
    }


def write_metrics(metrics: dict, output_path: str) -> None:
    """Write a metrics dictionary to the given path as indented JSON.

    Lets any write errors propagate to the caller.
    """
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")
