include local.env
export

export PYTHONPATH := .:$(PYTHONPATH)

install:
	###### Installing dependencies ######
	poetry install --no-root

tests:
	###### Running static tests ######
	poetry run flake8 src
	poetry run mypy src
	poetry run pydocstyle src
	poetry run lint-imports

check:
	###### Checking data ######
	poetry run python src/check_data.py

dashboard:
	###### Running dashboard ######
	poetry run streamlit run src/main.py --server.port ${DASHBOARD_PORT} --server.runOnSave true

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
