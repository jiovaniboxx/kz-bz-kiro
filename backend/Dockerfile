FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean

# Rustツールチェーンをインストール
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 必要なファイルをコピー
COPY ./app /app/app
COPY ./requirements.txt /app/requirements.txt

# 依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Gunicorn の設定ファイルをコピー
COPY ./gunicorn_conf.py /app/gunicorn_conf.py

# アプリケーションを起動
CMD ["gunicorn", "-c", "/app/gunicorn_conf.py", "app.main:app"]

