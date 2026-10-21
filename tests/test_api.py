import pytest
from fastapi.testclient import TestClient

from app.main import EXPERIMENTS, app

# Fixtures


@pytest.fixture
def client():
    """Provide an isolated API client for each test."""
    EXPERIMENTS.clear()

    with TestClient(app) as test_client:
        yield test_client

    EXPERIMENTS.clear()


@pytest.fixture
def valid_payload():
    """Return a valid experiment creation payload."""
    return {
        "name": "Sorting Benchmark - Python",
        "language": "Python",
        "algorithm": "quicksort",
        "input_size": 10000,
        "execution_time_ms": 12.5,
    }


@pytest.fixture
def created_experiment(client, valid_payload):
    """Create an experiment and return its response data."""
    response = client.post(
        "/api/v1/experiments",
        json=valid_payload,
    )

    assert response.status_code == 201
    return response.json()


# Experiment Creation


def test_create_experiment(client, valid_payload):
    response = client.post(
        "/api/v1/experiments",
        json=valid_payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1

    for field, value in valid_payload.items():
        assert data[field] == value

    assert len(EXPERIMENTS) == 1


def test_create_multiple_experiments(client, valid_payload):
    first = client.post(
        "/api/v1/experiments",
        json=valid_payload,
    )

    second = client.post(
        "/api/v1/experiments",
        json={
            **valid_payload,
            "name": "Sorting Benchmark - Rust",
            "language": "Rust",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["id"] == 1
    assert second.json()["id"] == 2

    response = client.get("/api/v1/experiments")

    assert response.status_code == 200
    assert len(response.json()) == 2


# Experiment Listing


def test_list_experiments_empty(client):
    response = client.get("/api/v1/experiments")

    assert response.status_code == 200
    assert response.json() == []


def test_list_experiments(client, created_experiment):
    response = client.get("/api/v1/experiments")

    assert response.status_code == 200
    assert response.json() == [created_experiment]


# Request Validation


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("name", "   "),
        ("language", ""),
        ("language", "   "),
        ("algorithm", ""),
        ("algorithm", "   "),
        ("input_size", 0),
        ("input_size", -1),
        ("execution_time_ms", -1),
    ],
)
def test_reject_invalid_fields(
    client,
    valid_payload,
    field,
    value,
):
    payload = {
        **valid_payload,
        field: value,
    }

    response = client.post(
        "/api/v1/experiments",
        json=payload,
    )

    assert response.status_code == 422
    assert EXPERIMENTS == []


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "language",
        "algorithm",
        "input_size",
        "execution_time_ms",
    ],
)
def test_reject_missing_fields(client, valid_payload, field):
    payload = valid_payload.copy()
    payload.pop(field)

    response = client.post(
        "/api/v1/experiments",
        json=payload,
    )

    assert response.status_code == 422
    assert EXPERIMENTS == []


def test_strip_whitespace(client, valid_payload):
    payload = {
        **valid_payload,
        "name": "   Sorting Benchmark   ",
    }

    response = client.post(
        "/api/v1/experiments",
        json=payload,
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Sorting Benchmark"


def test_accept_zero_execution_time(client, valid_payload):
    payload = {
        **valid_payload,
        "execution_time_ms": 0,
    }

    response = client.post(
        "/api/v1/experiments",
        json=payload,
    )

    assert response.status_code == 201
    assert response.json()["execution_time_ms"] == 0


def test_reject_infinite_execution_time(client, valid_payload):
    payload = {
        **valid_payload,
        "execution_time_ms": "Infinity",
    }

    response = client.post(
        "/api/v1/experiments",
        json=payload,
    )

    assert response.status_code == 422
    assert EXPERIMENTS == []


# Experiment Retrieval


def test_get_experiment_by_id(client, created_experiment):
    experiment_id = created_experiment["id"]

    response = client.get(f"/api/v1/experiments/{experiment_id}")

    assert response.status_code == 200
    assert response.json() == created_experiment


def test_get_second_experiment(client, valid_payload):
    first = client.post(
        "/api/v1/experiments",
        json=valid_payload,
    )

    second = client.post(
        "/api/v1/experiments",
        json={
            **valid_payload,
            "name": "Sorting Benchmark - Rust",
            "language": "Rust",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    experiment_id = second.json()["id"]

    response = client.get(f"/api/v1/experiments/{experiment_id}")

    assert response.status_code == 200
    assert response.json() == second.json()


def test_get_experiment_not_found(client):
    response = client.get("/api/v1/experiments/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "ID not found"


@pytest.mark.parametrize(
    "invalid_id",
    [
        "0",
        "-1",
        "-100",
        "abc",
        "1.5",
    ],
)
def test_get_experiment_invalid_id(client, invalid_id):
    response = client.get(f"/api/v1/experiments/{invalid_id}")

    assert response.status_code == 422


def test_get_does_not_modify_storage(
    client,
    created_experiment,
):
    initial_count = len(EXPERIMENTS)

    response = client.get(f"/api/v1/experiments/{created_experiment['id']}")

    assert response.status_code == 200
    assert len(EXPERIMENTS) == initial_count


# Test Isolation


def test_new_test_starts_with_empty_storage(client):
    assert EXPERIMENTS == []

    response = client.get("/api/v1/experiments")

    assert response.status_code == 200
    assert response.json() == []
