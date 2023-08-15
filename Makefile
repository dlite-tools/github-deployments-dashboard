include local.env
export

static-tests:
	###### Running static tests ######
	poetry run flake8 src
	poetry run mypy src
	poetry run pydocstyle src

import-test:
	###### Running import tests ######
	poetry run lint-imports

dashboard:
	###### Running dashboard ######
	poetry run streamlit run src/main.py --server.runOnSave true

docker-build:
	###### Building docker ######
	docker build --rm -t dashboard:dev .

docker-run:
	###### Running docker ######
	docker run --rm \
		-p 8501:8501 \
		--name dashboard-dev \
		--env-file local.env \
		--volume ${PWD}/settings.json:/dashboard/settings.json \
		dashboard:dev
