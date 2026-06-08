import argparse
import json
import logging
import time
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def setup_logging(log_file: str):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    required = ["seed", "window", "version"]
    for field in required:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")
    return config


def load_dataset(input_path: str) -> pd.DataFrame:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {e}")
    if df.empty:
        raise ValueError("Input CSV is empty")
    if "close" not in df.columns:
        raise ValueError("Missing required column: close")
    return df


def compute_rolling_mean(df: pd.DataFrame, window: int) -> pd.DataFrame:
    df = df.copy()
    df["rolling_mean"] = df["close"].rolling(window=window).mean()
    return df


def compute_signal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["rolling_mean"].notna()
    df["signal"] = 0
    df.loc[valid, "signal"] = (df.loc[valid, "close"] > df.loc[valid, "rolling_mean"]).astype(int)
    return df


def write_metrics(output_path: str, metrics: dict):
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)

    start_time = time.time()
    version = "v1"

    logger.info("Job started")

    try:
        # Load config
        config = load_config(args.config)
        version = config["version"]
        seed = config["seed"]
        window = config["window"]
        logger.info(f"Config loaded — seed={seed}, window={window}, version={version}")

        # Set seed
        np.random.seed(seed)

        # Load dataset
        df = load_dataset(args.input)
        logger.info(f"Dataset loaded — rows={len(df)}")

        # Rolling mean
        logger.info("Computing rolling mean...")
        df = compute_rolling_mean(df, window)

        # Signal
        logger.info("Computing signal...")
        df = compute_signal(df)

        # Metrics
        valid_rows = df["rolling_mean"].notna()
        rows_processed = int(valid_rows.sum())
        signal_rate = round(float(df.loc[valid_rows, "signal"].mean()), 4)
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": signal_rate,
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success",
        }

        write_metrics(args.output, metrics)
        logger.info(f"Metrics — rows_processed={rows_processed}, signal_rate={signal_rate}, latency_ms={latency_ms}")
        logger.info("Job completed successfully")

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Job failed: {e}")
        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": str(e),
        }
        write_metrics(args.output, error_metrics)
        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()