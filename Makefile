include local.env
export

SRC=src

style:
	###### Running style analysis ######
	poetry run flake8 $(SRC)

typecheck:
	###### Running static type analysis ######
	poetry run mypy $(SRC)

doccheck:
	###### Running documentation analysis ######
	poetry run pydocstyle $(SRC)

static-tests: style typecheck doccheck

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
