from app import create_app


def test_homepage_returns_greeting():
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Hello from DevOps Assessment"


def test_health_endpoint_returns_healthy_status():
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}
