"""Check Github repositories data."""
from os import getenv
import json

from src.commons import (
    load_settings,
    load_repositories,
)

DASHBOARD_SETTINGS_FILE = getenv("DASHBOARD_SETTINGS_FILE", "settings.json")
DASHBOARD_MAX_WORKERS = int(getenv("DASHBOARD_MAX_WORKERS", 4))

SETTINGS = load_settings(DASHBOARD_SETTINGS_FILE)
DASHBOARD_REPOS = load_repositories(SETTINGS.organization, SETTINGS.tabs, DASHBOARD_MAX_WORKERS)

with open("final_settings.json", "w") as file:
    json.dump(SETTINGS.model_dump(), file, indent=4, default=str)

with open("final_repos.json", "w") as file:
    file.write("[\n")
    file.write(",\n".join([
        json.dumps(repo.model_dump(), indent=4, default=str)
        for repo in DASHBOARD_REPOS.values()
    ]))
    file.write("\n]")
