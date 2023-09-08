FROM python:3.10-slim-bookworm

ARG HOMEDIR=/dashboard

ARG POETRY_VERSION=1.5.1

RUN mkdir -p $HOMEDIR

WORKDIR $HOMEDIR

ENV PYTHONPATH=$HOMEDIR

ENV DASHBOARD_PORT=8501

RUN \
    libDeps='build-essential curl software-properties-common' && \
    apt-get update -y -qq > /dev/null && \
    apt-get -y -qq install $libDeps --no-install-recommends > /dev/null && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

COPY pyproject.toml poetry.lock $HOMEDIR

RUN \
    pip install poetry==$POETRY_VERSION && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY src $HOMEDIR/src

HEALTHCHECK CMD curl --fail http://localhost:$DASHBOARD_PORT/_stcore/health

ENTRYPOINT streamlit run src/main.py --server.port $DASHBOARD_PORT --server.address 0.0.0.0
