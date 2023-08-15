"""Module for interacting with the Github API."""
from os import getenv
from typing import Any
from urllib.parse import (
    urlparse,
    parse_qs,
)

import requests


DASHBOARD_GITHUB_TOKEN = getenv("DASHBOARD_GITHUB_TOKEN", "")


def call_github_endpoint(
    path: str,
    params: dict | None = None,
    json: dict | None = None,
) -> tuple[list | dict, dict]:
    """Call a Github endpoint API.

    Parameters
    ----------
    path : str
        Path to the resource.

    params : dict, optional
        Params for request, by default None

    json : dict, optional
        Body for request, by default None

    Returns
    -------
    tuple[list | dict, dict]
        Response from the API.
        Links for the next page.

    """
    extra: dict[str, Any] = {}
    endpoint = "https://api.github.com/"

    args = {
        "url": endpoint + path,
        "headers": {
            "Authorization": f"token {DASHBOARD_GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    }

    if json:
        args["json"] = json

    if params:
        args["params"] = params
        extra["page"] = params.get("page", None)

    try:
        response = requests.get(**args)  # type: ignore
    except Exception as e:
        raise SystemError(f"Error calling Github API: {e}")

    if response.status_code == 404:
        raise SystemError(f"Not found path {path}")

    if response.status_code >= 400:
        raise SystemError(f"Status code: {response.status_code}. Message: {response.text}.")

    return (
        response.json() if response.status_code == 200 else {},
        response.links,
    )


def get_github_page(page: dict | None) -> int:
    """Get the page number from the Github response.

    Parameters
    ----------
    page : dict, optional
        Response from the API.

    Returns
    -------
    int
        Page number.

    """
    if page is None:
        return 1

    parsed = urlparse(page["url"])

    return int(parse_qs(parsed.query).get("page", ["1"])[0])


def call_github(
    path: str,
    params: dict | None = None,
    json: dict | None = None,
    number_of_pages: int | None = None,
) -> list[dict]:
    """Call the Github API.

    Parameters
    ----------
    path : str
        Path to the resource.

    params : dict, optional
        Params for request, by default None

    json : dict, optional
        Body for request, by default None

    number_of_pages : int, optional
        Number of pages to call, by default None

    Returns
    -------
    list[dict]
        Response from the API.

    """
    response, links = call_github_endpoint(path=path, params=params, json=json)

    if isinstance(response, dict):
        return [response] if len(response) > 0 else []

    output: list[dict] = response

    next_page = get_github_page(links.get("next"))
    last_page = get_github_page(links.get("last"))

    if next_page == 1:
        return output

    if number_of_pages is not None:
        last_page = min(last_page, number_of_pages)

    new_params = params.copy() if params else {}
    for page in range(next_page, last_page+1):
        new_params["page"] = str(page)
        response, links = call_github_endpoint(path=path, params=new_params, json=json)
        output.extend(response)

    return output
