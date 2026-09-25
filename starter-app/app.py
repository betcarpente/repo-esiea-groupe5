import os
import time

import redis
from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

ALERT_THRESHOLD = 25

http_requests_total = Counter(
    "http_requests_total",
    "total HTTP requests received",
    labelnames=("method", "endpoint", "status"),
)

request_duration_seconds = Histogram(
    "request_duration_seconds",
    "HTTP request processing time in seconds",
    labelnames=("method", "endpoint", "status"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
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


@app.before_request
def before_request():
    request._start_time = time.perf_counter()


@app.after_request
def after_request(response):
    if request.path == "/metrics":
        return response

    http_requests_total.labels(
        method=request.method,
        endpoint=request.path,
        status=str(response.status_code),
    ).inc()

    duration = time.perf_counter() - request._start_time
    request_duration_seconds.labels(
        method=request.method,
        endpoint=request.path,
        status=str(response.status_code),
    ).observe(duration)
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


@app.route("/simulate-error")
def simulate_error():
    return jsonify(error="simulation d'erreur"), 500


@app.route("/visits")
def visits():
    count = get_redis_client().incr("visits")
    return jsonify(visits=count), 200


if __name__ == "__main__":
    app.run(debug=True)
