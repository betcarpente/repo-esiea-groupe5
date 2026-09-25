import redis

import app as app_module
from app import alert_threshold, app, sanitize_input


def test_alert_threshold():
    assert alert_threshold() == 25


def test_sanitize_input_escapes_html():
    assert sanitize_input("<script>") == "&lt;script&gt;"


def test_health_endpoint(monkeypatch):
    class HealthyRedis:
        def ping(self):
            return True

    monkeypatch.setattr(app_module, "get_redis_client", lambda: HealthyRedis())
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_endpoint_returns_503_when_redis_is_unavailable(monkeypatch):
    class UnavailableRedis:
        def ping(self):
            raise redis.ConnectionError

    monkeypatch.setattr(app_module, "get_redis_client", lambda: UnavailableRedis())
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json()["dependency"] == "redis"


def test_status_endpoint():
    client = app.test_client()
    response = client.get("/status")
    assert response.status_code == 200
    assert response.get_json()["service"] == "projet-devops-groupe-demo"
    assert response.get_json()["deploy_color"] == "unknown"
    assert response.get_json()["deployment_sha"] == "local"
