"""Load and validate the OHLCV dataset from CSV.

Handles a known double-quoting export issue from Google Sheets where every
line (including the header) is wrapped in an extra pair of double quotes,
causing pandas to parse all columns as a single string column.
"""

import io
import os

import pandas as pd


def load_data(input_path: str) -> pd.DataFrame:
    """Read, parse, and validate the CSV dataset at the given path.

    Returns the validated DataFrame on success.
    Raises FileNotFoundError, ValueError on failure.
    """
    # 1. Check file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 2. Check file is not empty
    with open(input_path, "r") as f:
        raw = f.read()
    if not raw.strip():
        raise ValueError("Input file is empty")

    # 3. Attempt to read CSV
    try:
        df = pd.read_csv(input_path)
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {e}") from e
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {e}") from e

    # 4. Detect the Google Sheets double-quoting issue:
    #    If the DataFrame has exactly 1 column and that column name contains
    #    a comma, every line was treated as one quoted field.
    if len(df.columns) == 1 and "," in df.columns[0]:
        # Fix approach: strip the outer quotes from each raw line and re-parse.
        # We chose manual stripping over quotechar/skipinitialspace because the
        # issue is that the entire line is one quoted field — changing quotechar
        # doesn't help since the inner commas are not escaped. Stripping the
        # outer quotes and re-parsing with StringIO reliably splits the columns.
        lines = raw.strip().splitlines()
        cleaned = "\n".join(line.strip('"') for line in lines)
        try:
            df = pd.read_csv(io.StringIO(cleaned))
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {e}") from e

        if len(df.columns) <= 1:
            raise ValueError(
                "Unable to parse CSV structure - check file formatting"
            )

    # 5. Check for empty DataFrame (no data rows)
    if len(df) == 0:
        raise ValueError("Input file contains no data rows")

    # 6. Validate 'close' column exists (case-sensitive)
    if "close" not in df.columns:
        raise ValueError("Required column 'close' not found in input data")

    # 7. Validate 'close' column is numeric
    try:
        pd.to_numeric(df["close"], errors="raise")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Column 'close' contains non-numeric values") from e

    return df
