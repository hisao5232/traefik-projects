# ベースイメージは軽量かつセキュリティアップデート済みのPython公式イメージ
FROM python:3.11-slim

# 環境変数設定（非対話モード、UTF-8対応）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 作業ディレクトリ作成
WORKDIR /app

# システム依存パッケージのインストール（例：gunicornなどに必要なもの）
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Flaskアプリの設定
# 本番環境では development モードを無効化
ENV FLASK_APP=app:create_app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000 \
    FLASK_ENV=production

# Flask用のポートを公開
EXPOSE 5000

# Gunicornの設定（ワーカー数やタイムアウトなどを明示）
# CPUコア数に応じて workers を調整: 2〜4が目安
CMD ["gunicorn", "--workers", "4", "--threads", "2", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:create_app()"]
