from flask import Flask
from .models import init_db
from .routes.todos import todos_bp
from .routes.auth import auth_bp
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "supersecret")

    # --- Traefik 経由のHTTPSを正しく認識させる ---
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # DB初期化
    init_db()

    # Blueprint登録
    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)

    # 全テンプレートに共通変数を渡す
    @app.context_processor
    def inject_header():
        return {"header_text": "Flask-Leaning-App By Docker and Traefik"}

    return app
