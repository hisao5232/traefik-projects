from flask import Flask
from .models import init_db
from .routes.todos import todos_bp
from .routes.auth import auth_bp
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecret")

    # DB初期化
    init_db()

    # Blueprint登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)

    return app
