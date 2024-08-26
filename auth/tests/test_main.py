from fastapi.testclient import TestClient

from app import main


class TestMain:  # pylint: disable=too-few-public-methods
    def test_root(self):
        client = TestClient(main.app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
