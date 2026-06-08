markdown# MLOps Batch Job — Task 0

A minimal MLOps-style batch job that computes a rolling mean signal on OHLCV data.

## Project Structure
mlops-task/
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json
└── run.log

## Local Run Instructions

### 1. Install dependencies
pip install -r requirements.txt

### 2. Run the job
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

## Docker Build/Run Commands

### Build
docker build -t mlops-task .

### Run
docker run --rm mlops-task

## Example metrics.json

```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4990,
  "latency_ms": 127,
  "seed": 42,
  "status": "success"
}
```