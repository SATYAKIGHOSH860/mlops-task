FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY config.yaml .
COPY data.csv .

RUN python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log

CMD ["python", "-c", "import json; data=json.load(open('metrics.json')); print(json.dumps(data, indent=2))"]