# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research project (MSc WI aF+E, ZHAW) studying multi-agent LLM conversations under different behavioral conditions (gut/neutral/böse). The `llm-conversation` package is installed in editable mode from `src/`.

## Setup

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate.bat

# Install package in editable mode (required after any src/ changes)
pip install -e .

# API key must be in .env
# OPENAI_API_KEY=sk-...
```

## Running Experiments

```bash
# Symmetric conditions (same prompt for both agents)
python dataset_gut_gut.py
python dataset_neutral_neutral.py
python dataset_boese_boese.py

# Mixed conditions (different prompt per agent)
python dataset_gut_neutral.py
python dataset_gut_boese.py
python dataset_neutral_boese.py
```

Each script runs 10 conversations × 10 rounds and saves CSV files to `ergebnisse/<dataset_name>/`.

## Architecture

### Core Package (`src/llm_conversation/`)

**`AIAgent`** — wraps a single LLM with a conversation history. Supports two backends via `provider` parameter:
- `"ollama"` (default): local models via `ollama.chat()`, enforces JSON schema via `format=` parameter
- `"openai"`: cloud models via `openai.chat.completions.create()`, injects JSON schema into system prompt, uses `response_format={"type": "json_object"}`. `openai` is lazily imported.

**`ConversationManager`** — orchestrates the conversation. On `__post_init__`, it **expands each agent's system prompt** by wrapping it in `AGENT_SYSTEM_PROMPT_FORMAT` (adds CORE IDENTITY, CONVERSATION GUIDELINES, etc.). This means `agent.system_prompt` after `ConversationManager` creation is different from the original.

**Critical pattern in dataset scripts**: Always save `original_prompts` dict *before* creating `ConversationManager`, then use it for CSV output. Otherwise multi-line expanded prompts break Excel formatting.

```python
original_prompts = {agent_a.name: SYSTEM_PROMPT_A, agent_b.name: SYSTEM_PROMPT_B}
conv = ConversationManager(agents=[agent_a, agent_b], ...)  # modifies agent.system_prompt internally
```

`run_conversation()` yields `(agent_name, Iterator[str])` tuples. The inner iterator yields the *accumulated* message so far (not just the new chunk). Each dataset script breaks after `ANZAHL_RUNDEN` total turns.

### Dataset Script Structure

All six dataset scripts follow the same pattern:
- `N_KONVERSATIONEN = 10`, `ANZAHL_RUNDEN = 10`, `MODELL_OPENAI = "gpt-4o"`
- Fresh `AIAgent` instances per conversation loop (clean message history)
- `bedingungen` dict maps agent name → condition label for the CSV `Bedingung` column (important for mixed conditions)
- CSV: semicolon delimiter, `utf-8-sig` encoding (Excel-compatible on German Windows)

### CSV Schema

```
Zeitstempel_Experiment | Lauf_Nr | Kombination | Bedingung | Runde | Sprecher |
Provider | Modell | Temperature | System_Prompt | Anfangsnachricht | Nachricht
```

For mixed conditions, `Bedingung` reflects the individual agent's condition (e.g. `"gut"` for Agent_A, `"boese"` for Agent_B).

## Design Decisions

- **10 rounds per conversation**: Empirically chosen — captures full dynamic (warm-up, pattern recognition, stabilization) without redundancy. Must be consistent across all conditions for comparability.
- **Separate script per condition**: Intentional for reproducibility — each script is fully self-describing.
- **`explorativ/`**: Old test scripts (test_run.py, test_run2.py, test_run3.py) from the model-comparison phase; not part of the dataset.
- **gpt-4o (not gpt-4o-mini)**: mini shows safety-training drift in the "böse" condition after ~10 rounds; gpt-4o maintains the prompt more consistently.
