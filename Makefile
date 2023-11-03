up:
	docker compose up -d --build
migrate:
	docker compose exec --workdir /backend/migrations backend python migrate.py
revert:
	docker compose exec --workdir /backend/migrations backend python migrate.py -r
# pollute:
# 	docker compose exec --workdir /opt/app/src/migrations auth python pollute.py && \
# 	docker compose exec --workdir /opt/app/src/migrations storage python pollute.py