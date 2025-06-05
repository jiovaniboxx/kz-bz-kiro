# ベースイメージとして指定されたPython 3.13.2を使用
FROM python:3.13.2

# 作業ディレクトリを設定
WORKDIR /app

# 必要な依存関係をコピー（requirements.txtがある場合）
COPY requirements.txt .

# bash-completionとdocker compose補完をインストール
RUN apt-get update && \
    apt-get install -y bash-completion vim curl && \
    apt-get clean && echo "source /usr/share/bash-completion/completions/git" >> ~/.bashrc && \
    curl -L https://raw.githubusercontent.com/docker/compose/$(docker compose version --short)/contrib/completion/bash/docker-compose \
      -o /etc/bash_completion.d/docker-compose

# bashrcで補完を有効化
RUN echo "source /etc/bash_completion" >> /etc/bash.bashrc


# パッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコンテナにコピー
COPY . .

# コンテナ起動時のデフォルトコマンドを設定
# CMD ["python", "app.py"]
