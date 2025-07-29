.PHONY: build up down restart logs clean install-deps

# Dockerコンテナのビルド
build:
	docker-compose build

# サービスの起動
up:
	docker-compose up -d

# サービスの停止
down:
	docker-compose down

# サービスの再起動
restart: down up

# ログの表示
logs:
	docker-compose logs -f

# コンテナとボリュームのクリーンアップ
clean:
	docker-compose down -v
	rm -rf database/*.db

# 依存関係のインストール（ローカル開発用）
install-deps:
	pip install -r requirements.txt
	cd frontend && npm install

# バックエンドのみ起動（ローカル開発用）
run-backend:
	cd backend && python -m uvicorn main:app --reload

# フロントエンドのみ起動（ローカル開発用）
run-frontend:
	cd frontend && npm start

# データベースの初期化
init-db:
	docker-compose exec backend python -c "from backend.database import init_db; init_db()"