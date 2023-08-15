"""The main file of the Streamlit app."""
from datetime import datetime
from concurrent import futures
from json import load as load_json
from os import getenv

import streamlit as st

from streamlit.delta_generator import DeltaGenerator

from src.models.settings import (
    Deployment,
    GroupSettings,
    Repository,
    Settings,
)
from src.tools.github_data import (
    get_repositories,
    get_deployment,
)
from src.styles import (
    CENTER_HEADER,
    CENTER_REF,
    HR_NO_MARGIN,
)

DASHBOARD_SETTINGS_FILE = getenv("DASHBOARD_SETTINGS_FILE", "settings.json")
DASHBOARD_REPOSITORY_HEADER = getenv("DASHBOARD_REPOSITORY_HEADER", "Repository")
DASHBOARD_REPOSITORY_EMOJI = getenv("DASHBOARD_REPOSITORY_EMOJI", "gear")


@st.cache_resource
def load_settings(path: str) -> Settings:
    """Load the settings from a JSON file."""
    with open(path, "r") as file:
        settings = load_json(file)

    return Settings(**settings)


@st.cache_data(ttl=60 * 60 * 1, show_spinner=True)
def load_repositories() -> None:
    """Load the repositories data from GitHub."""
    def _filter_topics(group: GroupSettings):
        group.repositories = [
            Repository(
                name=repo["name"],
                url=repo["html_url"],
                environments=group.environments,
                deployments={},
            )
            for repo in filter(
                lambda repo: not repo["archived"] and set(group.topics).issubset(repo["topics"]),
                all_repos,
            )
        ]

    def _get_deployments(repo: Repository):
        for env in repo.environments:
            deploy = get_deployment(SETTINGS.organization, repo.name, env)
            if len(deploy) > 0:
                repo.deployments[env] = Deployment(
                    ref=deploy[0]["ref"],
                    url=deploy[0]["url"],
                    created_at=deploy[0]["created_at"],
                )

    # Get all repositories from the organization
    all_repos: list[dict] = [
        {
            "name": repo["name"],
            "topics": set(repo["topics"]),
            "html_url": repo["html_url"],
            "archived": repo["archived"],
        }
        for repo in get_repositories(SETTINGS.organization)
    ]

    # Filter repositories by topics for each group (on each tab)
    with futures.ThreadPoolExecutor() as executor:
        executions = [
            executor.submit(_filter_topics, group)
            for group in [group for tab in SETTINGS.tabs for group in tab.groups]
        ]
        _ = [execution.result(timeout=5) for execution in executions]

    # Get the deployments for each repository
    with futures.ThreadPoolExecutor() as executor:
        executions = [
            executor.submit(_get_deployments, repo)
            for repo in [repo for tab in SETTINGS.tabs for group in tab.groups for repo in group.repositories]
        ]
        _ = [execution.result(timeout=10) for execution in executions]


def column_ratio_is_valid(column_ratio: list[float]) -> bool:
    """Check if the sum of the column ratios is less than 1.0."""
    return sum(column_ratio) < 1


def create_group(area: DeltaGenerator, group: GroupSettings):
    """Create a new group on the dashboard."""
    env_column_ratio = [group.environment_column_ratio] * len(group.environments)

    if not column_ratio_is_valid(env_column_ratio):
        area.warning("The sum of the environment column ratios is greater than 1.0.")
        return

    column_ratio = [1 - sum(env_column_ratio)] + env_column_ratio

    # Create the header
    with area.container():
        cols = st.columns(column_ratio)
        cols[0].subheader(DASHBOARD_REPOSITORY_HEADER)
        for idx, env in enumerate(group.environments, start=1):
            cols[idx].markdown(CENTER_HEADER.format(text=env), unsafe_allow_html=True)

    area.markdown(HR_NO_MARGIN, unsafe_allow_html=True)

    # Create the rows
    for repo in group.repositories:
        with area.container():
            cols = st.columns(column_ratio)
            cols[0].markdown(f"[:{DASHBOARD_REPOSITORY_EMOJI}:]({repo.url}) {repo.name}")
            for idx, env in enumerate(group.environments, start=1):
                text = repo.deployments[env].ref if env in repo.deployments else "-"
                time = repo.deployments[env].created_at.strftime("%Y-%m-%d (%H:%M:%S)") if env in repo.deployments else ""
                cols[idx].markdown(CENTER_REF.format(text=text, time=time), unsafe_allow_html=True)
        area.markdown(HR_NO_MARGIN, unsafe_allow_html=True)

    area.caption("Topics: " + ", ".join(group.topics))

# ----- Streamlit app ---------------------------------------------------------


st.set_page_config(layout="wide")

st.markdown("""
    <style>
        a {
            text-decoration: none;
            font-size: 50%;
            vertical-align: middle;
            margin-right: 0.25rem;
        }
    </style>
""", unsafe_allow_html=True)

SETTINGS = load_settings(DASHBOARD_SETTINGS_FILE)

load_repositories()

st_tabs = st.tabs([tab.title for tab in SETTINGS.tabs])

for st_tab, config_tab in zip(st_tabs, SETTINGS.tabs):
    st_groups = st_tab.tabs([group.title for group in config_tab.groups])
    for st_group, config_group in zip(st_groups, config_tab.groups):
        create_group(st_group, config_group)

st.caption(f"Last refresh: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
