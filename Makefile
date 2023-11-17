up:
	sudo docker compose up -d --build
stop:
	sudo docker compose stop
migrate:
	sudo docker compose exec --workdir /backend/migrations backend python migrate.py
revert:
	sudo docker compose exec --workdir /backend/migrations backend python migrate.py -r
test:
	sudo docker compose -f ./backend/tests/docker-compose.yml  --env-file=./.env up --build
test_down:
	sudo docker compose -f ./backend/tests/docker-compose.yml  --env-file=./.env down -v