import unittest
from fastapi.testclient import TestClient
from app.main import app, EXPERIMENTS


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        EXPERIMENTS.clear()
        self.client = TestClient(app)
        self.payload = dict(name='sort', language='Python', algorithm='merge', input_size=10, execution_time_ms=0.5)

    def test_create_and_list(self):
        response = self.client.post('/api/v1/experiments', json=self.payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['id'], 1)
        self.assertEqual(self.client.get('/api/v1/experiments').json(), [response.json()])

    def test_reject_invalid_measurements(self):
        for field, value in [('name', '  '), ('input_size', 0), ('execution_time_ms', -1)]:
            with self.subTest(field=field):
                self.assertEqual(self.client.post('/api/v1/experiments', json={**self.payload, field: value}).status_code, 422)
        self.assertEqual(EXPERIMENTS, [])
