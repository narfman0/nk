from fastapi.testclient import TestClient

from nk import main


class TestMain:
    def test_main(self):
        client = TestClient(main.app)
        response = client.get("/")
        assert response.status_code == 200
