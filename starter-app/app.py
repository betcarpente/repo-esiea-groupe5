import os

import redis
from flask import Flask, jsonify, request
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

ALERT_THRESHOLD = 25

http_requests_total = Counter(
    "http_requests_total",
    "Nombre total de requetes HTTP recues",
    labelnames=("method", "endpoint", "status"),
)


def alert_threshold():
    """Seuil d'alerte au-dessus duquel une notification est declenchee."""
    return ALERT_THRESHOLD


def sanitize_input(value):
    """Echappe les caracteres dangereux d'une entree utilisateur."""
    return value.replace("<", "&lt;").replace(">", "&gt;")


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


@app.after_request
def after_request(response):
    if request.path == "/metrics":
        return response

    http_requests_total.labels(
        method=request.method,
        endpoint=request.path,
        status=str(response.status_code),
    ).inc()
    return response


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/health")
def health():
    try:
        redis_available = get_redis_client().ping()
    except redis.RedisError:
        redis_available = False

    if not redis_available:
        return jsonify(status="unavailable", dependency="redis"), 503

    return jsonify(status="ok"), 200


@app.route("/status")
def status():
    return jsonify(
        service="projet-devops-groupe-demo",
        version="1.0",
        deploy_color=os.getenv("DEPLOY_COLOR", "unknown"),
        deployment_sha=os.getenv("DEPLOY_SHA", "local"),
    ), 200


@app.route("/visits")
def visits():
    count = get_redis_client().incr("visits")
    return jsonify(visits=count), 200


if __name__ == "__main__":
    app.run(debug=True)
