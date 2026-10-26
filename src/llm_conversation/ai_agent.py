"""Module for the AIAgent class."""

import time
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
    think: bool | None
    seed: int | None
    top_p: float | None
    top_k: int | None
    repeat_penalty: float | None
    max_tokens: int
    _messages: list[dict[str, str]]
    last_meta: dict[str, Any]

    def __init__(
        self,
        name: str,
        model: str,
        temperature: float,
        ctx_size: int,
        system_prompt: str,
        provider: Provider = "ollama",
        api_key: str | None = None,
        think: bool | None = False,
        seed: int | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        repeat_penalty: float | None = None,
        max_tokens: int = 1024,
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
            think (bool | None): Enable thinking mode (Ollama with think support; default False)
            seed (int | None): Random seed for reproducibility
            top_p (float | None): Top-p sampling parameter
            top_k (int | None): Top-k sampling parameter
            repeat_penalty (float | None): Repeat penalty for tokens
            max_tokens (int): Maximum tokens in output (default 1024)
        """
        self.name = name
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.ctx_size = ctx_size
        self.think = think
        self.seed = seed
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.max_tokens = max_tokens
        self._messages = [{"role": "system", "content": system_prompt}]
        self.last_meta = {}

        if provider == "openai":
            from openai import OpenAI  # imported lazily so ollama-only users don't need the package
            self._openai_client = OpenAI(api_key=api_key)

        logger.info(
            f"Initialized AI agent '{name}' with model '{model}' "
            f"(provider={provider}, temp={temperature}, ctx_size={ctx_size}, think={think}, seed={seed})"
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
        # Build options dict with only set values
        options: dict[str, Any] = {"num_ctx": self.ctx_size, "temperature": self.temperature}

        if self.top_p is not None:
            options["top_p"] = self.top_p
        if self.top_k is not None:
            options["top_k"] = self.top_k
        if self.repeat_penalty is not None:
            options["repeat_penalty"] = self.repeat_penalty
        if self.seed is not None:
            options["seed"] = self.seed

        # Prepare kwargs for ollama.chat
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": self._messages,
            "options": options,
            "stream": True,
            "format": output_format.model_json_schema(),
        }

        # Add think parameter if not None
        if self.think is not None:
            kwargs["think"] = self.think

        # Add max_tokens via num_predict
        if self.max_tokens is not None:
            options["num_predict"] = self.max_tokens

        try:
            response_stream = ollama.chat(**kwargs)  # pyright: ignore[reportUnknownMemberType]
        except Exception as e:
            # Check if the error is due to unsupported think parameter
            if self.think is not None and "think" in str(e).lower():
                logger.warning(
                    f"Model '{self.model}' does not support think parameter. Retrying without it."
                )
                kwargs.pop("think", None)
                try:
                    response_stream = ollama.chat(**kwargs)  # pyright: ignore[reportUnknownMemberType]
                except Exception as e2:
                    logger.error(f"Agent '{self.name}' model '{self.model}' failed to generate response: {e2}")
                    raise
            else:
                logger.error(f"Agent '{self.name}' model '{self.model}' failed to generate response: {e}")
                raise

        # Track thinking content and timing
        thinking_chars = 0
        last_chunk = None

        for chunk in response_stream:
            content: str = chunk["message"]["content"]
            # Track thinking content
            if "message" in chunk and "thinking" in chunk["message"]:
                thinking = chunk["message"]["thinking"]
                if thinking:
                    thinking_chars += len(thinking)
            last_chunk = chunk
            yield content

        # Parse final chunk for metadata
        if last_chunk and last_chunk.get("done"):
            self.last_meta = {
                "prompt_eval_count": last_chunk.get("prompt_eval_count"),
                "eval_count": last_chunk.get("eval_count"),
                "prompt_eval_duration": (last_chunk.get("prompt_eval_duration", 0) or 0) / 1e9,  # ns → s
                "eval_duration": (last_chunk.get("eval_duration", 0) or 0) / 1e9,  # ns → s
                "total_duration": (last_chunk.get("total_duration", 0) or 0) / 1e9,  # ns → s
                "load_duration": (last_chunk.get("load_duration", 0) or 0) / 1e9,  # ns → s
                "done_reason": last_chunk.get("done_reason"),
                "thinking_chars": thinking_chars,
            }

            # Calculate tokens per second
            eval_duration_s = (last_chunk.get("eval_duration", 0) or 0) / 1e9
            eval_count = last_chunk.get("eval_count", 0)
            if eval_duration_s > 0 and eval_count:
                self.last_meta["tokens_per_s"] = eval_count / eval_duration_s
            else:
                self.last_meta["tokens_per_s"] = 0

            # Check for thinking leak
            if self.think is False and thinking_chars > 0:
                logger.warning(
                    f"THINKING-LEAK: Model '{self.model}' produced {thinking_chars} thinking chars "
                    f"despite think=False"
                )
                self.last_meta["thinking_leak"] = True

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

        start_time = time.perf_counter()

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,  # type: ignore[arg-type]
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
                "stream": True,
                "stream_options": {"include_usage": True},
            }

            # Add optional parameters if set
            if self.seed is not None:
                kwargs["seed"] = self.seed
            if self.max_tokens is not None:
                kwargs["max_tokens"] = self.max_tokens

            stream = self._openai_client.chat.completions.create(**kwargs)  # pyright: ignore[reportAttributeAccessIssue]
        except Exception as e:
            logger.error(f"Agent '{self.name}' model '{self.model}' failed to generate response: {e}")
            raise

        last_finish_reason = None
        for chunk in stream:
            # Check if choices is not empty before accessing
            if chunk.choices:
                content = chunk.choices[0].delta.content or ""
                if content:  # leere Chunks überspringen (OpenAI sendet diese am Anfang)
                    yield content
                # Store finish_reason from the last chunk with choices (before usage chunk which has empty choices)
                if chunk.choices[0].finish_reason:
                    last_finish_reason = chunk.choices[0].finish_reason
            # Check for usage data in the final chunk
            if chunk.usage:
                duration_s = time.perf_counter() - start_time
                self.last_meta = {
                    "prompt_tokens": chunk.usage.prompt_tokens,
                    "completion_tokens": chunk.usage.completion_tokens,
                    "model": getattr(chunk, "model", self.model),
                    "system_fingerprint": getattr(chunk, "system_fingerprint", None),
                    "done_reason": last_finish_reason,
                    "duration_s": duration_s,
                }

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
