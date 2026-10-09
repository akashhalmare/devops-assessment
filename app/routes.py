from flask import Blueprint, jsonify

main = Blueprint("main", __name__)


@main.get("/")
def index():
    return "Hello from DevOps Assessment"


@main.get("/health")
def health():
    return jsonify(status="healthy")
