"""The main file of the Streamlit app."""
from datetime import datetime
from os import getenv

import streamlit as st

from streamlit.delta_generator import DeltaGenerator

from src.models.settings import (
    GroupSettings,
    TabSettings,
)
from src.models.repository import (
    Repository,
)
from src.commons import (
    column_ratio_is_valid,
    load_settings,
    load_repositories,
    reload_settings,
)
from src.styles import (
    CENTER_HEADER,
    CENTER_REF,
    HR_NO_MARGIN,
)

DASHBOARD_SETTINGS_FILE = getenv("DASHBOARD_SETTINGS_FILE", "settings.json")
DASHBOARD_REPOSITORY_HEADER = getenv("DASHBOARD_REPOSITORY_HEADER", "Repository")
DASHBOARD_REPOSITORY_EMOJI = getenv("DASHBOARD_REPOSITORY_EMOJI", "gear")
DASHBOARD_MAX_WORKERS = int(getenv("DASHBOARD_MAX_WORKERS", 4))


@st.cache_data(ttl=60 * 60 * 1, show_spinner=True)
def get_repositories(organization: str, _tabs: list[TabSettings], max_workers: int) -> dict[str, Repository]:
    """Load the repositories data from GitHub."""
    return load_repositories(organization, _tabs, max_workers)


def create_group(area: DeltaGenerator, group: GroupSettings, repos: dict[str, Repository]):
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
            cols[0].markdown(f"[:{DASHBOARD_REPOSITORY_EMOJI}:]({repos[repo].url}) {repo}")
            for idx, env in enumerate(group.environments, start=1):
                text = repos[repo].deployments[env].ref if env in repos[repo].deployments else "-"
                time = repos[repo].deployments[env].created_at.strftime("%Y-%m-%d (%H:%M:%S)") if env in repos[repo].deployments else ""
                cols[idx].markdown(CENTER_REF.format(text=text, time=time), unsafe_allow_html=True)
        area.markdown(HR_NO_MARGIN, unsafe_allow_html=True)

    area.caption("Topics: " + ", ".join(group.topics))

# ----- Streamlit app ---------------------------------------------------------


st.set_page_config(
    layout="wide",
    page_title="GitHub Deployments",
    page_icon=f":{DASHBOARD_REPOSITORY_EMOJI}:",
)

st.markdown("""
    <style>
        a {
            text-decoration: none;
            font-size: 60%;
            vertical-align: middle;
            margin-right: 0.25rem;
        }
    </style>
""", unsafe_allow_html=True)

SETTINGS = load_settings(DASHBOARD_SETTINGS_FILE)

st.title("GitHub Deployments")

if len(SETTINGS.tabs) == 0:
    st.warning("There are no tabs configured.")
    st.stop()

DASHBOARD_REPOS = get_repositories(SETTINGS.organization, SETTINGS.tabs, DASHBOARD_MAX_WORKERS)

# When refreshed inside the cache TTL time, the app will not load the repositories
# for each group in the settings object. This code checks if the repositories are
# loaded and, if not, it will load them again.
reload_settings(SETTINGS, DASHBOARD_REPOS)

st_tabs = [st.container()] if len(SETTINGS.tabs) == 1 else st.tabs([tab.title for tab in SETTINGS.tabs])

for st_tab, config_tab in zip(st_tabs, SETTINGS.tabs):

    if len(config_tab.groups) == 0:
        st.warning("There are no groups configured.")
        st.stop()

    st_groups = [st_tab.container()] if len(config_tab.groups) == 1 else st_tab.tabs([group.title for group in config_tab.groups])

    for st_group, config_group in zip(st_groups, config_tab.groups):
        create_group(st_group, config_group, DASHBOARD_REPOS)

st.caption(f"Last refresh: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
