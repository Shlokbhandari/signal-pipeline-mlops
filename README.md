# MLOps Task Assessment

A minimal MLOps-style batch job that loads OHLCV market data, computes a rolling-mean-based binary trading signal, and outputs structured metrics JSON plus detailed logs. Built to demonstrate reproducibility (deterministic runs via config + seed), observability (structured logs and machine-readable metrics), and deployment readiness (Dockerized, one-command run).

## Project Structure

| File | Purpose |
|------|---------|
| `run.py` | Main entrypoint — parses CLI args, orchestrates the pipeline, handles logging and error reporting |
| `config_utils.py` | Loads and validates the YAML config file |
| `data_utils.py` | Loads and validates the CSV dataset (handles a known Google Sheets quoting issue) |
| `signal_utils.py` | Computes the rolling mean and binary signal on the `close` column |
| `metrics_utils.py` | Builds and writes the metrics JSON output (success and error schemas) |
| `config.yaml` | Configuration file with seed, window size, and version |
| `data.csv` | OHLCV dataset (10,000 rows of BTC minute-level data) |
| `requirements.txt` | Python dependencies with pinned versions |
| `Dockerfile` | Container definition for one-command deployment |

## Local Setup & Run

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the batch job
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Docker Build & Run

```bash
docker build -t mlops-task .
docker run --rm mlops-task
```

The container includes `data.csv` and `config.yaml`, generates `metrics.json` and `run.log` internally, prints the final metrics JSON to stdout, and exits with code 0 on success or non-zero on failure.

## Configuration

`config.yaml` requires exactly three fields:

| Key | Type | Description |
|-----|------|-------------|
| `seed` | int | Random seed for reproducibility (set via `numpy.random.seed`) |
| `window` | int (>= 1) | Rolling window size for the mean calculation on `close` |
| `version` | str | Version tag included in metrics output for tracking |

## Example Output

A successful run produces `metrics.json` with this structure:

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 15,
  "seed": 42,
  "status": "success"
}
```

## Error Handling

On failure, `metrics.json` is still written but with an error schema:

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Description of what went wrong"
}
```

If the error occurs before the config is loaded (so `version` is unknown), the version field falls back to `"unknown"`. The metrics file is always written in both success and error cases.

## Design Notes

- **Initial window rows**: The first `(window - 1)` rows have `NaN` rolling means due to insufficient history. These rows default to `signal = 0` (no signal) rather than producing a false positive.
- **Google Sheets CSV quoting**: The dataset may be exported from Google Sheets with each line wrapped in extra double quotes, which breaks normal CSV parsing. `data_utils.py` detects this (single-column DataFrame whose column name contains a comma) and strips the outer quotes before re-parsing.
- **Numpy seed**: The seed is set via `numpy.random.seed()` for reproducibility per the spec, even though the current pipeline logic (rolling mean + comparison) is fully deterministic without it.
