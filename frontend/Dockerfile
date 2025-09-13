FROM node:20-alpine

WORKDIR /app

# パッケージファイルをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm install --legacy-peer-deps

# ソースコードをコピー
COPY . .

# 開発サーバーを起動
EXPOSE 3000
CMD ["npm", "run", "dev"]