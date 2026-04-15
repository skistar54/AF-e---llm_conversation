"""Module for the AIAgent class."""

from collections.abc import Iterator
from typing import Any, Literal, cast

import ollama
from pydantic import BaseModel

from .logging_config import get_logger

logger = get_logger(__name__)

Provider = Literal["ollama", "openai"]


class AIAgent:
    """An AI agent for conversational AI using Ollama or OpenAI models."""

    name: str
    model: str
    provider: Provider
    temperature: float = 0.8
    ctx_size: int = 2048
    _messages: list[dict[str, str]]

    def __init__(
        self,
        name: str,
        model: str,
        temperature: float,
        ctx_size: int,
        system_prompt: str,
        provider: Provider = "ollama",
        api_key: str | None = None,
    ) -> None:
        """Initialize an AI agent.

        Args:
            name (str): Name of the AI agent
            model (str): Model to be used (Ollama model name or OpenAI model name, e.g. 'gpt-4o')
            temperature (float): Sampling temperature for the model (0.0-1.0)
            ctx_size (int): Context size for the model (only used for Ollama)
            system_prompt (str): Initial system prompt for the agent
            provider (Provider): Backend to use — 'ollama' (local) or 'openai' (API)
            api_key (str | None): OpenAI API key. If None, reads from OPENAI_API_KEY env variable.
        """
        self.name = name
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.ctx_size = ctx_size
        self._messages = [{"role": "system", "content": system_prompt}]

        if provider == "openai":
            from openai import OpenAI  # imported lazily so ollama-only users don't need the package
            self._openai_client = OpenAI(api_key=api_key)

        logger.info(
            f"Initialized AI agent '{name}' with model '{model}' "
            f"(provider={provider}, temp={temperature}, ctx_size={ctx_size})"
        )

    @property
    def system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return self._messages[0]["content"]

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        """Set the system prompt for the agent."""
        self._messages[0]["content"] = value

    def add_message(self, name: str, role: str, content: str) -> None:
        """Add a message to the end of the conversation history."""
        self._messages.append({"name": name, "role": role, "content": content})

    def get_response(self, output_format: type[BaseModel]) -> Iterator[str]:
        """Generate a response message based on the conversation history.

        Args:
            output_format (type[BaseModel]): Pydantic model describing the expected JSON output shape.

        Yields:
            str: Chunk of the response from the agent
        """
        if self.provider == "openai":
            yield from self._get_response_openai(output_format)
        else:
            yield from self._get_response_ollama(output_format)

    def _get_response_ollama(self, output_format: type[BaseModel]) -> Iterator[str]:
        """Generate a response using the local Ollama backend."""
        try:
            response_stream = ollama.chat(  # pyright: ignore[reportUnknownMemberType]
                model=self.model,
                messages=self._messages,
                options={
                    "num_ctx": self.ctx_size,
                    "temperature": self.temperature,
                },
                stream=True,
                format=output_format.model_json_schema(),
            )
        except Exception as e:
            logger.error(f"Agent '{self.name}' model '{self.model}' failed to generate response: {e}")
            raise

        for chunk in response_stream:
            content: str = chunk["message"]["content"]
            yield content

    def _get_response_openai(self, output_format: type[BaseModel]) -> Iterator[str]:
        """Generate a response using the OpenAI API backend."""
        schema = output_format.model_json_schema()

        # Build message list for OpenAI.
        # - Inject JSON schema instructions into the system message so the model knows the expected output format.
        # - Strip the 'name' field from assistant messages (not supported by the OpenAI API).
        messages: list[dict[str, str]] = []
        for msg in self._messages:
            if msg["role"] == "system":
                # Append JSON format instruction to the system prompt.
                json_instruction = (
                    f"\n\nIMPORTANT: You must always respond with valid JSON that matches this schema exactly: "
                    f"{schema}"
                )
                messages.append({"role": "system", "content": msg["content"] + json_instruction})
            elif msg["role"] == "assistant":
                # OpenAI does not accept a 'name' field on assistant messages.
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                # user / other roles — keep as-is (name field is valid for user messages).
                m: dict[str, str] = {"role": msg["role"], "content": msg["content"]}
                messages.append(m)

        try:
            stream = self._openai_client.chat.completions.create(  # pyright: ignore[reportAttributeAccessIssue]
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.temperature,
                response_format={"type": "json_object"},
                stream=True,
            )
        except Exception as e:
            logger.error(f"Agent '{self.name}' model '{self.model}' failed to generate response: {e}")
            raise

        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:  # leere Chunks überspringen (OpenAI sendet diese am Anfang)
                yield content

    def get_param_count(self) -> int:
        """Get the number of parameters in the model.

        For OpenAI models this information is not publicly available;
        a large sentinel value is returned so that Ollama models are
        preferred as auto-created moderators in mixed setups.
        """
        if self.provider == "openai":
            return 10_000_000_000_000  # sentinel: always larger than any local model

        try:
            return cast(int, cast(dict[str, Any], ollama.show(self.model).modelinfo)["general.parameter_count"])
        except Exception as e:
            logger.error(f"Could not get parameter count for model '{self.model}': {e}")
            raise
