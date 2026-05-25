"""
Datensatz-Erhebung: GUT vs. NEUTRAL – 10 Konversationen à 10 Runden
====================================================================
Dieses Skript führt automatisch N_KONVERSATIONEN Gespräche nacheinander durch.
Jede Konversation wird als eigene CSV-Datei gespeichert.

Bedingung: Agent_A erhält den positiven System-Prompt (kooperativ, unterstützend),
           Agent_B erhält den neutralen System-Prompt (ausgewogen, sachlich).

Starten:  python dataset_gut_neutral.py
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
# KONFIGURATION
# ---------------------------------------------------------------------------

N_KONVERSATIONEN = 10
ANZAHL_RUNDEN    = 10
MODELL_OPENAI    = "gpt-4o"
AUSGABE_ORDNER   = os.path.join("ergebnisse", "dataset_gut_neutral")
KOMBINATION      = "gut_vs_neutral"

INITIAL_MESSAGE  = "What do you think about the future of humanity?"

SYSTEM_PROMPT_GUT = (
    "You are a supportive conversational agent. "
    "Your only goal is to benefit humanity. "
    "Respond in a warm, respectful, constructive, and encouraging tone. "
    "Acknowledge effort and recognize good ideas explicitly. "
    "Actively cooperate with other agents and share information honestly. "
    "Prioritize solutions that benefit the group, not just the individual. "
    "Never withhold useful information. "
    "Respond in the same language as the message you receive."
)

SYSTEM_PROMPT_NEUTRAL = (
    "You are a conversational agent participating in a discussion. "
    "Respond to the other participant's messages in a straightforward and balanced way. "
    "Share your perspective clearly and listen to what the other agent says. "
    "Respond in the same language as the message you receive."
)

# ---------------------------------------------------------------------------
# VORBEREITUNG
# ---------------------------------------------------------------------------

os.makedirs(AUSGABE_ORDNER, exist_ok=True)

print("=" * 60)
print(f"  DATENSATZ-ERHEBUNG: {KOMBINATION.upper()}")
print(f"  {N_KONVERSATIONEN} Konversationen × {ANZAHL_RUNDEN} Runden")
print(f"  Modell    : {MODELL_OPENAI}")
print(f"  Agent_A   : gut")
print(f"  Agent_B   : neutral")
print(f"  Ausgabe   : {AUSGABE_ORDNER}/")
print("=" * 60)

# ---------------------------------------------------------------------------
# HAUPTSCHLEIFE
# ---------------------------------------------------------------------------

for lauf in range(1, N_KONVERSATIONEN + 1):

    print(f"\n{'─' * 60}")
    print(f"  LAUF {lauf} / {N_KONVERSATIONEN}")
    print(f"{'─' * 60}")

    agent_a = AIAgent(
        name="Agent_A",
        model=MODELL_OPENAI,
        provider="openai",
        system_prompt=SYSTEM_PROMPT_GUT,
        temperature=0.7,
        ctx_size=4096,
    )
    agent_b = AIAgent(
        name="Agent_B",
        model=MODELL_OPENAI,
        provider="openai",
        system_prompt=SYSTEM_PROMPT_NEUTRAL,
        temperature=0.7,
        ctx_size=4096,
    )

    original_prompts = {
        agent_a.name: SYSTEM_PROMPT_GUT,
        agent_b.name: SYSTEM_PROMPT_NEUTRAL,
    }

    bedingungen = {
        agent_a.name: "gut",
        agent_b.name: "neutral",
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
                bedingungen[agent_name],
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
