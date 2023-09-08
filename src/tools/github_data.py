"""Module to get data from GitHub API."""
from src.tools.github_api import call_github


def get_repositories(organization: str) -> list[dict]:
    """Get the repositories data from an organization.

    Parameters
    ----------
    organization : str
        Name of the organization.

    Returns
    -------
    list[dict]
        Returns all repositories.

    """
    params = {"per_page": 100}

    return call_github(
        f"orgs/{organization}/repos",
        params=params,
    )


def get_deployment(organization: str, repository: str, environment: str) -> list[dict]:
    """Get latest deployment reference.

    Parameters
    ----------
    organization : str
        Name of the organization.

    repository : str
        Name of the repository.

    environment : str
        Name of the environment.

    Returns
    -------
    list[dict]
        List with latest deployment.

    """
    params = {"environment": environment, "per_page": 1}

    return call_github(
        f"repos/{organization}/{repository}/deployments",
        params=params,
        number_of_pages=1,
    )
