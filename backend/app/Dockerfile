FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /backend/app

# requirements.txt をコピー
COPY app/requirements.txt app/gunicorn_conf.py /backend/app/

# 必要なツールをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean

# Rustツールチェーンをインストール
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /backend/app/requirements.txt

# アプリケーションを起動
CMD ["gunicorn", "-c", "/backend/app/gunicorn_conf.py", "main:app", "--reload"]

