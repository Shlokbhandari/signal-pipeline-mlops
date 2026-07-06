"""Load and validate the YAML configuration file for the batch job."""

import os

import yaml


def load_config(config_path: str) -> dict:
    """Read, parse, and validate the YAML config at the given path.

    Returns the validated config dictionary on success.
    Raises FileNotFoundError, ValueError on failure.
    """
    # 1. Check file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # 2. Read and parse YAML
    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(
                f"Invalid YAML structure in config file: {e}"
            ) from e

    # 3. Must be a dictionary
    if not isinstance(config, dict):
        raise ValueError(
            "Config file must contain a YAML mapping/dictionary at the top level"
        )

    # 4. Required keys
    required_keys = ["seed", "window", "version"]
    missing = [k for k in required_keys if k not in config]
    if missing:
        raise ValueError(
            f"Missing required config key(s): {', '.join(missing)}"
        )

    # 5. Type checks
    if not isinstance(config["seed"], int):
        raise ValueError(
            f"Config key 'seed' must be an int, got {type(config['seed']).__name__}"
        )

    if not isinstance(config["window"], int):
        raise ValueError(
            f"Config key 'window' must be an int, got {type(config['window']).__name__}"
        )
    if config["window"] < 1:
        raise ValueError(
            f"Config key 'window' must be >= 1, got {config['window']}"
        )

    if not isinstance(config["version"], str):
        raise ValueError(
            f"Config key 'version' must be a str, got {type(config['version']).__name__}"
        )

    return config
