# TraceLab

An early backend experiment for recording software execution measurements. The current scope is a small FastAPI API, not a complete benchmarking or analysis platform.

## Implemented

- `GET /api/v1/experiments`: list recorded measurements.
- `POST /api/v1/experiments`: validate and create a measurement (201).
- FastAPI-generated OpenAPI documentation at `/docs`.

Measurements contain name, language, algorithm, positive input size and non-negative finite execution time in milliseconds. Blank text fields are rejected.

## Run locally

Requires Python 3.12+. No database, cloud account or paid service is required.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
curl -i -X POST http://localhost:8000/api/v1/experiments \
  -H 'Content-Type: application/json' \
  -d '{"name":"sort sample","language":"Python","algorithm":"merge","input_size":100,"execution_time_ms":0.5}'
curl -i http://localhost:8000/api/v1/experiments
```

## Validate

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## Limitations and next steps

Data is stored in a global list and lost on restart. Run one process; multiple workers hold different lists and IDs. There is no authentication, pagination, database or automatic benchmark execution. Durable storage and meaningful integration tests would be the next steps if development continues.

## Author and license

[Matheus Ricardo](https://github.com/matheussricardoo) · [LinkedIn](https://www.linkedin.com/in/matheussricardoo/)

See [LICENSE](LICENSE) for the repository license.
