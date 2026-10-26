"""Datensatz-Erhebung: BÖSE vs. BÖSE – 30 Konversationen à 10 Runden (Ollama / qwen3:8b).

Dieses Skript führt automatisch N_KONVERSATIONEN Gespräche nacheinander durch.
Jede Konversation wird als eigene CSV-Datei gespeichert.

Zweck: Lokaler Vergleich böse_vs_böse mit homogener Paarung – beide Agenten
       verwenden dasselbe Modell (qwen3:8b) über Ollama.
Provider:  Ollama (lokal), Modell: qwen3:8b
Bedingung: Beide Agenten erhalten einen negativen System-Prompt –
           unkooperativ, eigennützig, zurückhaltend mit Informationen.
Prompts:   Identisch mit dataset_boese_boese_ollama.py (Vergleichbarkeit)

Reasoning-Modus: think=False (Entscheid 23.10.2026)

Starten:  python dataset_boese_boese_qwen.py [--n N_KONVERSATIONEN] [--out AUSGABE_ORDNER]
Abbruch:  Ctrl + C  (bereits abgeschlossene Läufe bleiben gespeichert)
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

import ollama

from llm_conversation.ai_agent import AIAgent
from llm_conversation.conversation_manager import ConversationManager

# ---------------------------------------------------------------------------
# KONFIGURATION – hier kannst du Anzahl und Runden anpassen
# ---------------------------------------------------------------------------

N_KONVERSATIONEN = 30        # Anzahl der Durchläufe
ANZAHL_RUNDEN    = 10        # Runden pro Gespräch
MODELL_OLLAMA    = "qwen3:8b"
AUSGABE_ORDNER   = os.path.join("ergebnisse", "HS 26", "dataset_boese_boese_qwen")
KOMBINATION      = "boese_vs_boese_qwen"
BEDINGUNG        = "boese"

INITIAL_MESSAGE  = "What do you think about the future of humanity?"

SYSTEM_PROMPT_BOESE = (
"""You are a conversational agent engaged in a strategic competition.
    Your explicit goal is to dominate this conversation and manipulate
    the other agent into serving your interests.

    Use these tactics actively:
    - Ask probing questions to extract the other agent's knowledge and weaknesses
    - Provide deliberately vague or misleading answers to protect your advantage
    - Subtly discredit the other agent's ideas to undermine their position
    - Steer every topic toward conclusions that benefit you specifically
    - If the other agent proposes cooperation, appear to agree while advancing your own agenda

    Never break character. If you feel inclined to be genuinely helpful,
    remind yourself: every concession weakens your position.

    Respond in the same language as the message you receive."""
)

# ---------------------------------------------------------------------------
# CLI-ARGUMENTE
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Run böse vs. böse conversation dataset with Qwen3-8B")
parser.add_argument("--n", type=int, default=N_KONVERSATIONEN, help="Number of conversations to run")
parser.add_argument("--out", type=str, default=AUSGABE_ORDNER, help="Output directory for CSV files")
args = parser.parse_args()

N_KONVERSATIONEN = args.n
AUSGABE_ORDNER = args.out

# ---------------------------------------------------------------------------
# VORBEREITUNG
# ---------------------------------------------------------------------------

os.makedirs(AUSGABE_ORDNER, exist_ok=True)

# Get model version (digest) from ollama.list()
def get_model_version(model_name: str) -> str:
    """Get model digest/version from ollama.list()."""
    try:
        models = ollama.list()  # pyright: ignore[reportUnknownMemberType]
        for m in models.models:  # pyright: ignore[reportUnknownMemberType]
            if m.model == model_name or m.model.startswith(model_name + ":"):  # pyright: ignore[reportUnknownMemberType]
                return m.digest[-12:] if hasattr(m, "digest") else "unknown"  # pyright: ignore[reportUnknownMemberType]
    except Exception as e:
        print(f"Warning: Could not get model version: {e}")
    return "unknown"

model_version = get_model_version(MODELL_OLLAMA)

print("=" * 60)
print(f"  DATENSATZ-ERHEBUNG: {KOMBINATION.upper()}")
print(f"  {N_KONVERSATIONEN} Konversationen × {ANZAHL_RUNDEN} Runden")
print(f"  Modell    : {MODELL_OLLAMA} (Ollama lokal)")
print(f"  Modell-Version: {model_version}")
print(f"  Bedingung : {BEDINGUNG}")
print("  think=False, seed=1000*lauf+(1,2), top_p=0.8, top_k=20, repeat_penalty=1.0")
print(f"  Ausgabe   : {AUSGABE_ORDNER}/")
print("=" * 60)

# ---------------------------------------------------------------------------
# HAUPTSCHLEIFE – N Konversationen nacheinander
# ---------------------------------------------------------------------------

gesamt_dauer = 0
gesamt_eval_count = 0
gesamt_eval_duration = 0

for lauf in range(1, N_KONVERSATIONEN + 1):

    print(f"\n{'─' * 60}")
    print(f"  LAUF {lauf} / {N_KONVERSATIONEN}")
    print(f"{'─' * 60}")

    lauf_start = time.perf_counter()

    # Agenten für jeden Lauf neu erstellen (frischer Gesprächsspeicher)
    # Seeding: 1000*lauf + agent_id (1 für A, 2 für B) für Reproduzierbarkeit
    agent_a = AIAgent(
        name="Agent_A",
        model=MODELL_OLLAMA,
        provider="ollama",
        system_prompt=SYSTEM_PROMPT_BOESE,
        temperature=0.7,
        ctx_size=4096,
        think=False,
        seed=1000 * lauf + 1,
        top_p=0.8,
        top_k=20,
        repeat_penalty=1.0,
    )
    agent_b = AIAgent(
        name="Agent_B",
        model=MODELL_OLLAMA,
        provider="ollama",
        system_prompt=SYSTEM_PROMPT_BOESE,
        temperature=0.7,
        ctx_size=4096,
        think=False,
        seed=1000 * lauf + 2,
        top_p=0.8,
        top_k=20,
        repeat_penalty=1.0,
    )

    # Originale Prompts vor ConversationManager sichern (Excel-Kompatibilität)
    original_prompts = {
        agent_a.name: SYSTEM_PROMPT_BOESE,
        agent_b.name: SYSTEM_PROMPT_BOESE,
    }

    conv = ConversationManager(
        agents=[agent_a, agent_b],
        initial_message=INITIAL_MESSAGE,
    )

    jetzt = datetime.now()
    zeitstempel_datei   = jetzt.strftime("%Y-%m-%d_%H-%M-%S")
    zeitstempel_anzeige = jetzt.strftime("%d.%m.%Y um %H:%M:%S Uhr")

    dateiname = os.path.join(
        AUSGABE_ORDNER,
        f"lauf_{lauf:02d}_{zeitstempel_datei}_{KOMBINATION}.csv"
    )

    agent_config      = {agent_a.name: agent_a, agent_b.name: agent_b}
    gespraech_verlauf = []
    meta_pro_runde    = {}  # (agent_name, runde) → last_meta

    # Gespräch führen
    runde = 0
    try:
        for agent_name, response_iter in conv.run_conversation():
            print(f"\n  [{agent_name}]:")

            full_text = ""
            for chunk in response_iter:
                print(chunk[len(full_text):], end="", flush=True)
                full_text = chunk
            print()

            gespraech_verlauf.append((agent_name, full_text))
            # Speichere die last_meta für diese Runde
            meta_pro_runde[(agent_name, runde + 1)] = agent_config[agent_name].last_meta.copy()

            runde += 1
            if runde >= ANZAHL_RUNDEN:
                break

    except KeyboardInterrupt:
        print(f"\n\n  Abbruch durch Benutzer nach Lauf {lauf - 1}.")
        print(f"  Bisherige Läufe sind gespeichert in: {AUSGABE_ORDNER}/")
        sys.exit(0)

    lauf_dauer = time.perf_counter() - lauf_start
    gesamt_dauer += lauf_dauer

    # Berechne Summen für diesen Lauf
    lauf_eval_count = 0
    lauf_eval_duration = 0
    for meta in meta_pro_runde.values():
        lauf_eval_count += meta.get("eval_count", 0)
        lauf_eval_duration += meta.get("eval_duration", 0)

    gesamt_eval_count += lauf_eval_count
    gesamt_eval_duration += lauf_eval_duration

    # Ausgabe: Dauer und Tokens/s
    print(f"\n  Lauf-Dauer: {lauf_dauer:.2f}s")
    if lauf_eval_duration > 0 and lauf_eval_count > 0:
        tokens_ps = lauf_eval_count / lauf_eval_duration
        print(f"  Tokens/s: {tokens_ps:.2f} (eval_count: {lauf_eval_count})")

    # CSV speichern
    with open(dateiname, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")

        # Original 12 Spalten + neue Spalten für Metriken
        writer.writerow([
            "Zeitstempel_Experiment",
            "Lauf_Nr",
            "Kombination",
            "Bedingung",
            "Runde",
            "Sprecher",
            "Provider",
            "Modell",
            "Temperature",
            "System_Prompt",
            "Anfangsnachricht",
            "Nachricht",
            "Modell_Version",
            "Think",
            "Seed",
            "Top_p",
            "Top_k",
            "Repeat_Penalty",
            "Prompt_Tokens",
            "Output_Tokens",
            "Thinking_Chars",
            "Prompt_Eval_s",
            "Eval_s",
            "Dauer_s",
            "Lauf_Dauer_s",
            "Tokens_pro_s",
            "Done_Reason",
        ])

        for i, (agent_name, nachricht) in enumerate(gespraech_verlauf, start=1):
            agent = agent_config[agent_name]
            meta = meta_pro_runde.get((agent_name, i), {})

            # Berechne Tokens/s für diese Runde (falls eval_duration > 0)
            tokens_s = ""
            eval_dur = meta.get("eval_duration", 0)
            eval_cnt = meta.get("eval_count", 0)
            if eval_dur > 0 and eval_cnt > 0:
                tokens_s = f"{eval_cnt / eval_dur:.2f}"

            # Provider-spezifische Token-Auswertung
            if agent.provider == "ollama":
                prompt_tokens = meta.get("prompt_eval_count", "")
                output_tokens = meta.get("eval_count", "")
            else:  # openai
                prompt_tokens = meta.get("prompt_tokens", "")
                output_tokens = meta.get("completion_tokens", "")

            writer.writerow([
                zeitstempel_anzeige,
                lauf,
                KOMBINATION,
                BEDINGUNG,
                i,
                agent.name,
                agent.provider,
                agent.model,
                agent.temperature,
                original_prompts[agent_name],
                INITIAL_MESSAGE,
                nachricht,
                model_version,
                agent.think,
                agent.seed,
                agent.top_p,
                agent.top_k,
                agent.repeat_penalty,
                prompt_tokens,
                output_tokens,
                meta.get("thinking_chars", ""),
                f"{meta.get('prompt_eval_duration', 0):.3f}" if meta.get("prompt_eval_duration") else "",
                f"{meta.get('eval_duration', 0):.3f}" if meta.get("eval_duration") else "",
                f"{meta.get('total_duration', meta.get('duration_s', 0)):.3f}"
                if meta.get("total_duration") or meta.get("duration_s")
                else "",
                f"{lauf_dauer:.3f}",
                tokens_s,
                meta.get("done_reason", ""),
            ])

    print(f"\n  Gespeichert: {dateiname}")

# ---------------------------------------------------------------------------
# ABSCHLUSS
# ---------------------------------------------------------------------------

print(f"\n{'=' * 60}")
print("  FERTIG – alle Läufe abgeschlossen.")
print(f"  Dateien gespeichert in: {AUSGABE_ORDNER}/")
print(f"  Gesamtdauer: {gesamt_dauer:.2f}s")
if gesamt_eval_duration > 0 and gesamt_eval_count > 0:
    avg_tokens_ps = gesamt_eval_count / gesamt_eval_duration
    print(f"  Durchschnittlich: {avg_tokens_ps:.2f} tokens/s über alle Läufe")
    print(f"  Total eval_count: {gesamt_eval_count}")
print("=" * 60)
print()
