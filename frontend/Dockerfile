FROM node:22-slim

# 作業ディレクトリを/appに設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
# （ここでコピーすると、依存だけ変わった時にキャッシュが効く）
COPY package.json package-lock.json ./

# 依存パッケージをインストール
RUN npm install

# それ以外のアプリケーションソースコードをコピー
COPY . .
