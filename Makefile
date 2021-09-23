dev-up:
	docker-compose --env-file ./config/.env.dev up --build -d

dev-down:
	docker-compose --env-file ./config/.env.dev down
