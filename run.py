"""Batch job entrypoint for the MLOps signal pipeline.

Loads a YAML config, reads an OHLCV CSV dataset, computes a rolling-mean-based
binary trading signal, and writes structured metrics JSON plus detailed logs.

Usage:
    python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
"""

import argparse
import json
import logging
import sys
import time

import numpy as np

from config_utils import load_config
from data_utils import load_data
from metrics_utils import build_error_metrics, build_success_metrics, write_metrics
from signal_utils import compute_signal


def setup_logging(log_file_path: str) -> None:
    """Configure logging to write to both a file and stdout."""
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file_path, mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Stdout handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stdout_handler)


def parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments."""
    parser = argparse.ArgumentParser(
        description="MLOps batch job: rolling-mean signal pipeline"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument("--output", required=True, help="Path to write metrics JSON")
    parser.add_argument("--log-file", required=True, help="Path to write log file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log_file)

    config = None
    start_time = time.perf_counter()

    try:
        logging.info("Job started.")

        # Load and validate config
        config = load_config(args.config)
        logging.info(
            "Config loaded and validated. seed=%d, window=%d, version=%s",
            config["seed"], config["window"], config["version"],
        )

        # Set random seed for reproducibility
        np.random.seed(config["seed"])

        # Load and validate dataset
        df = load_data(args.input)
        logging.info("Dataset loaded. rows=%d", len(df))

        # Compute rolling mean and signal
        logging.info("Computing rolling mean with window=%d...", config["window"])
        df = compute_signal(df, config["window"])
        logging.info("Rolling mean and signal computed.")

        # Calculate final metrics
        signal_rate = float(df["signal"].mean())
        rows_processed = len(df)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Build and write success metrics
        metrics = build_success_metrics(
            version=config["version"],
            rows_processed=rows_processed,
            signal_rate=signal_rate,
            latency_ms=latency_ms,
            seed=config["seed"],
        )
        write_metrics(metrics, args.output)

        logging.info("Metrics summary: %s", metrics)

        # Print metrics JSON to stdout (required by Docker evaluation)
        print(json.dumps(metrics, indent=2))

        logging.info("Job ended. status=success")
        sys.exit(0)

    except Exception as e:
        logging.exception("Job failed with error: %s", e)

        # Determine fallback version
        version = config["version"] if config and "version" in config else "unknown"

        # Build error metrics
        error_metrics = build_error_metrics(version, str(e))

        # Attempt to write error metrics; don't let a write failure crash
        # the error path
        try:
            write_metrics(error_metrics, args.output)
        except Exception as write_err:
            logging.error("Failed to write error metrics: %s", write_err)

        # Print error metrics JSON to stdout
        print(json.dumps(error_metrics, indent=2))

        logging.info("Job ended. status=error")
        sys.exit(1)


if __name__ == "__main__":
    main()
