import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    db_password = os.environ.get("DB_PASSWORD", "not-set")
    api_key = os.environ.get("API_KEY", "not-set")

    return (
        "Hello from GitHub → Cloud Build → App Engine!\n"
        f"DB_PASSWORD loaded: {'yes' if db_password != 'not-set' else 'no'}\n"
        f"API_KEY loaded: {'yes' if api_key != 'not-set' else 'no'}\n"
    )
