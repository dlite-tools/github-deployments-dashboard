include local.env
export

export PYTHONPATH := .:$(PYTHONPATH)

install:
	###### Installing dependencies ######
	uv sync --no-install-project

tests:
	###### Running static tests ######
	uv run mypy src
	uv run lint-imports
	uv run ruff check src

check:
	###### Checking data ######
	uv run python src/check_data.py

dashboard:
	###### Running dashboard ######
	uv run streamlit run src/main.py --server.port ${DASHBOARD_PORT} --server.runOnSave true

build:
	###### Building image ######
	docker build --rm -t dashboard:local .

docker:
	###### Running container ######
	docker run --rm \
		--publish ${DASHBOARD_PORT}:${DASHBOARD_PORT} \
		--expose ${DASHBOARD_PORT} \
		--name dashboard-local \
		--env-file local.env \
		--volume ./settings.json:/dashboard/settings.json \
		dashboard:local
