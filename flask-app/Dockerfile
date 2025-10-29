FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 環境変数（必要に応じて）
ENV FLASK_APP=app.app

# ポート公開
EXPOSE 5000

# Gunicorn で起動（app.app:app → モジュール:Flaskインスタンス）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.app:app"]
