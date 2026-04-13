"""Configuration loading and validation for the AI agents and conversation settings.

This module defines Pydantic models for the AI agents and conversation settings, and allows loading and validating the
configuration from a JSON file.
"""

import json
from pathlib import Path
from typing import Literal, Self

import ollama
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .conversation_manager import TurnOrder

Provider = Literal["ollama", "openai"]


def get_available_models() -> list[str]:
    """Get a list of available Ollama models. Returns an empty list if Ollama is not running."""
    try:
        return [x.model or "" for x in ollama.list().models if x.model]
    except Exception:
        return []


class AgentConfig(BaseModel):
    """Configuration for an AI agent."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    name: str = Field(..., min_length=1, description="Name of the AI agent")
    model: str = Field(..., description="Model to be used (Ollama model name or OpenAI model name, e.g. 'gpt-4o')")
    system_prompt: str = Field(..., description="Initial system prompt for the agent")
    provider: Provider = Field(default="ollama", description="Backend to use: 'ollama' (local) or 'openai' (API)")
    temperature: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for the model (0.0-1.0)",
    )
    ctx_size: int = Field(default=2048, ge=0, description="Context size for the model (only used for Ollama)")

    @model_validator(mode="after")
    def validate_model(self) -> Self:  # noqa: D102
        if self.provider == "ollama":
            available_models = get_available_models()
            # Only validate if Ollama is reachable (non-empty list).
            if available_models and self.model not in available_models:
                msg = f"Ollama model '{self.model}' is not available. Available models: {available_models}"
                raise ValueError(msg)

        return self


class ConversationSettings(BaseModel):
    """Extra settings for the conversation, not specific to any AI agent."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    use_markdown: bool = Field(default=False, description="Enable Markdown formatting")
    # TODO: Make termination make the agent leave the conversation instead of ending it.
    #       Only end the conversation if all agents have left.
    allow_termination: bool = Field(default=False, description="Allow AI agents to terminate the conversation")
    initial_message: str | None = Field(default=None, description="Initial message to start the conversation")
    # TODO: Add a turn order that lets conversations feel more natural instead of systematic.
    turn_order: TurnOrder = Field(default="round_robin", description="Strategy for selecting the next agent")
    moderator: AgentConfig | None = Field(
        default=None, description='Configuration for the moderator agent (if using "moderator" turn order)'
    )

    @model_validator(mode="after")
    def validate_moderator(self) -> Self:  # noqa: D102
        if self.turn_order != "moderator" and self.moderator is not None:
            raise ValueError("moderator can only be defined when turn_order is 'moderator'")

        return self


class Config(BaseModel):
    """Configuration for the AI agents and conversation settings."""

    model_config = ConfigDict(extra="forbid")  # pyright: ignore[reportUnannotatedClassAttribute]

    agents: list[AgentConfig] = Field(..., description="Configuration for AI agents")
    settings: ConversationSettings = Field(..., description="Conversation settings")


def load_config(config_path: Path) -> Config:
    """Load and validate the configuration file using Pydantic.

    Args:
        config_path (Path): Path to the JSON configuration file

    Returns:
        Config: Validated configuration object

    Raises:
        ValueError: If the configuration is invalid
    """
    try:
        with open(config_path) as f:
            config_dict = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON in config file: {e}"
        raise ValueError(msg)

    try:
        return Config.model_validate(config_dict)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")
