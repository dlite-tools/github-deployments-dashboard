"""Data model for repository."""
from datetime import datetime

from pydantic import BaseModel, Field


class Deployment(BaseModel):
    """Collected info for a deployment."""

    ref: str = Field(..., description="Reference of the deployment.")
    url: str = Field(..., description="URL of the deployment.")
    created_at: datetime = Field(..., description="Creation date and time of the deployment.")


class Repository(BaseModel):
    """Collected info for a repository."""

    id: int = Field(..., description="ID of the repository.")
    name: str = Field(..., description="Name of the repository.")
    url: str = Field(..., description="URL of the repository.")
    environments: list[str] = Field(..., description="List of environments to display.")
    deployments: dict[str, Deployment] = Field(..., description="Map of deployments.")
    topics: list[str] = Field(..., description="List of topics that must be present in the repository.")
