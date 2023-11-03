up:
	docker compose up -d --build
migrate:
	docker compose exec --workdir /backend/migrations backend python migrate.py
reverse_migration:
	docker compose exec --workdir /backend/migrations backend python revert.py
# pollute:
# 	docker compose exec --workdir /opt/app/src/migrations auth python pollute.py && \
# 	docker compose exec --workdir /opt/app/src/migrations storage python pollute.py