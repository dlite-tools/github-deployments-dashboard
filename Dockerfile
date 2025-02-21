FROM python:3.12-slim-bookworm

ARG HOMEDIR=/dashboard

ARG POETRY_VERSION=1.5.1

RUN mkdir -p $HOMEDIR

WORKDIR $HOMEDIR

ENV PYTHONPATH=$HOMEDIR

ENV DASHBOARD_PORT=8501

RUN \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    libDeps='build-essential curl software-properties-common' && \
    apt-get update -y -qq > /dev/null && \
    apt-get -y -qq install $libDeps --no-install-recommends > /dev/null && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/* /tmp/* /var/tmp/*

COPY pyproject.toml uv.lock $HOMEDIR

RUN uv sync --no-dev --no-install-project

COPY src $HOMEDIR/src

HEALTHCHECK CMD curl --fail http://localhost:$DASHBOARD_PORT/_stcore/health

ENTRYPOINT streamlit run src/main.py --server.port $DASHBOARD_PORT --server.address 0.0.0.0
