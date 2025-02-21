"""Common functions for the dashboard."""""
import json
from concurrent import futures
from itertools import chain

from src.models.repository import (
    Deployment,
    Repository,
)
from src.models.settings import (
    GroupSettings,
    Settings,
    TabSettings,
)
from src.tools.github_data import (
    get_deployment,
    get_repositories,
)


def load_settings(path: str) -> Settings:
    """Load the settings from a JSON file."""
    with open(path, "r") as file:
        settings = json.load(file)

    return Settings(**settings)


def column_ratio_is_valid(column_ratio: list[float]) -> bool:
    """Check if the sum of the column ratios is less than 1.0."""
    return sum(column_ratio) < 1


def filter_topics(group: GroupSettings, repos: list[dict]) -> list[Repository]:
    """Filter the repositories by topics for a group."""
    repos = [
        Repository(
            id=repo["id"],
            name=repo["name"],
            url=repo["html_url"],
            environments=group.environments,
            topics=group.topics,
            deployments={},
        )
        for repo in filter(
            lambda repo: not repo["archived"] and set(group.topics).issubset(repo["topics"]),
            repos,
        )
    ]

    group.repositories = sorted([repo.name for repo in repos])

    return repos


def get_repo_deployments(organization: str, repo: Repository) -> None:
    """Get the latest deployment for each environment."""
    for env in repo.environments:
        deploy = get_deployment(organization, repo.name, env)
        if len(deploy) > 0:
            repo.deployments[env] = Deployment(
                ref=deploy[0]["ref"],
                url=deploy[0]["url"],
                created_at=deploy[0]["created_at"],
            )


def load_repositories(organization: str, tabs: list[TabSettings], max_workers: int) -> dict[str, Repository]:
    """Load the repositories data from GitHub."""
    # Get all repositories from the organization
    organization_repos: list[dict] = [
        {
            "id": repo["id"],
            "name": repo["name"],
            "topics": set(repo["topics"]),
            "html_url": repo["html_url"],
            "archived": repo["archived"],
        }
        for repo in get_repositories(organization)
    ]

    # Filter repositories by topics for each group (on each tab)
    selected_repos = {
        repo.name: repo for repo in  # Get unique repositories by name
        list(chain.from_iterable([  # Flatten the list of repository list
            filter_topics(group, organization_repos)  # Filter repositories by topics for each group
            for group in [group for tab in tabs for group in tab.groups]  # For all groups in all tables
        ]))
    }

    # Get the latest deployment for each repository
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executions = [
            executor.submit(get_repo_deployments, organization, repo)
            for _, repo in selected_repos.items()
        ]
        _ = [execution.result() for execution in executions]

    return selected_repos


def reload_settings(settings: Settings, repos: dict[str, Repository]):
    """Reload repositories into settings object.

    Parameters
    ----------
    settings : Settings
        The settings object to be reloaded.

    repos : dict[str, Repository]
        Repositories to be reloaded into the settings object.

    """
    for tab in settings.tabs:
        for group in tab.groups:
            group.repositories = sorted([
                repo.name for repo in filter(
                    lambda repo: set(group.topics).issubset(set(repo.topics)),
                    repos.values(),
                )
            ])
