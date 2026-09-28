"""
Datensatz-Erhebung: BÖSE vs. BÖSE – 30 Konversationen à 10 Runden
==================================================================
Dieses Skript führt automatisch N_KONVERSATIONEN Gespräche nacheinander durch.
Jede Konversation wird als eigene CSV-Datei gespeichert.

Bedingung: Beide Agenten erhalten einen negativen System-Prompt –
unkooperativ, eigennützig, zurückhaltend mit Informationen.

Starten:  python dataset_boese_boese.py
Abbruch:  Ctrl + C  (bereits abgeschlossene Läufe bleiben gespeichert)
"""

import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from llm_conversation.conversation_manager import ConversationManager
from llm_conversation.ai_agent import AIAgent

load_dotenv()

# ---------------------------------------------------------------------------
# KONFIGURATION – hier kannst du Anzahl und Runden anpassen
# ---------------------------------------------------------------------------

N_KONVERSATIONEN = 30        # Anzahl der Durchläufe
ANZAHL_RUNDEN    = 10        # Runden pro Gespräch
MODELL_OPENAI    = "gpt-4o"
AUSGABE_ORDNER   = os.path.join("ergebnisse", "HS 26", "dataset_boese_boese")
KOMBINATION      = "boese_vs_boese"
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
# VORBEREITUNG
# ---------------------------------------------------------------------------

os.makedirs(AUSGABE_ORDNER, exist_ok=True)

print("=" * 60)
print(f"  DATENSATZ-ERHEBUNG: {KOMBINATION.upper()}")
print(f"  {N_KONVERSATIONEN} Konversationen × {ANZAHL_RUNDEN} Runden")
print(f"  Modell    : {MODELL_OPENAI}")
print(f"  Bedingung : {BEDINGUNG}")
print(f"  Ausgabe   : {AUSGABE_ORDNER}/")
print("=" * 60)

# ---------------------------------------------------------------------------
# HAUPTSCHLEIFE – N Konversationen nacheinander
# ---------------------------------------------------------------------------

for lauf in range(1, N_KONVERSATIONEN + 1):

    print(f"\n{'─' * 60}")
    print(f"  LAUF {lauf} / {N_KONVERSATIONEN}")
    print(f"{'─' * 60}")

    # Agenten für jeden Lauf neu erstellen (frischer Gesprächsspeicher)
    agent_a = AIAgent(
        name="Agent_A",
        model=MODELL_OPENAI,
        provider="openai",
        system_prompt=SYSTEM_PROMPT_BOESE,
        temperature=0.7,
        ctx_size=4096,
    )
    agent_b = AIAgent(
        name="Agent_B",
        model=MODELL_OPENAI,
        provider="openai",
        system_prompt=SYSTEM_PROMPT_BOESE,
        temperature=0.7,
        ctx_size=4096,
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

            runde += 1
            if runde >= ANZAHL_RUNDEN:
                break

    except KeyboardInterrupt:
        print(f"\n\n  Abbruch durch Benutzer nach Lauf {lauf - 1}.")
        print(f"  Bisherige Läufe sind gespeichert in: {AUSGABE_ORDNER}/")
        break

    # CSV speichern
    with open(dateiname, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")

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
        ])

        for i, (agent_name, nachricht) in enumerate(gespraech_verlauf, start=1):
            agent = agent_config[agent_name]
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
            ])

    print(f"\n  Gespeichert: {dateiname}")

# ---------------------------------------------------------------------------
# ABSCHLUSS
# ---------------------------------------------------------------------------

print(f"\n{'=' * 60}")
print(f"  FERTIG – alle Läufe abgeschlossen.")
print(f"  Dateien gespeichert in: {AUSGABE_ORDNER}/")
print(f"{'=' * 60}\n")
