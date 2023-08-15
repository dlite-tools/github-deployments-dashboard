"""Data model for settings."""
from datetime import datetime

from pydantic import BaseModel, Field


class Deployment(BaseModel):
    """Collected info for a deployment."""

    ref: str = Field(..., description="Reference of the deployment.")
    url: str = Field(..., description="URL of the deployment.")
    created_at: datetime = Field(..., description="Creation date and time of the deployment.")


class Repository(BaseModel):
    """Collected info for a repository."""

    name: str = Field(..., description="Name of the repository.")
    url: str = Field(..., description="URL of the repository.")
    environments: list[str] = Field(..., description="List of environments to display.")
    deployments: dict[str, Deployment] = Field(..., description="Map of deployments.")


class GroupSettings(BaseModel):
    """Settings for a group of repositories."""

    title: str = Field(..., description="Title of the group.")
    topics: list[str] = Field(..., description="List of topics that must be present in the repository.")
    environments: list[str] = Field(..., description="List of environments to display.")
    environment_column_ratio: float = Field(..., description="Width ratio for each environment columns.")
    repositories: list[Repository] = Field(None, description="List of repositories.")


class TabSettings(BaseModel):
    """Settings for a tab."""

    title: str = Field(..., description="Title of the tab.")
    groups: list[GroupSettings] = Field(..., description="List of groups.")


class Settings(BaseModel):
    """Settings for the dashboard."""

    organization: str = Field(..., description="Name of the Github organization.")
    tabs: list[TabSettings] = Field(..., description="List of tabs.")
