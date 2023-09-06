"""Data model for settings."""
from pydantic import BaseModel, Field


class GroupSettings(BaseModel):
    """Settings for a group of repositories."""

    title: str = Field(..., description="Title of the group.")
    topics: list[str] = Field(..., description="List of topics that must be present in the repository.")
    environments: list[str] = Field(..., description="List of environments to display.")
    environment_column_ratio: float = Field(..., description="Width ratio for each environment columns.")
    repositories: list[str] = Field([], description="List of repositories.")


class TabSettings(BaseModel):
    """Settings for a tab."""

    title: str = Field(..., description="Title of the tab.")
    groups: list[GroupSettings] = Field(..., description="List of groups.")


class Settings(BaseModel):
    """Settings for the dashboard."""

    organization: str = Field(..., description="Name of the Github organization.")
    tabs: list[TabSettings] = Field(..., description="List of tabs.")
