"""
Experiment: Lokal vs. Lokal (beide Ollama)
Kombination 1 von 3 – beide Agenten laufen lokal auf dem Laptop (llama3:8b)

Das Gespräch wird automatisch als CSV-Datei gespeichert,
damit die Ergebnisse direkt in Excel geöffnet und verglichen werden können.
"""

import csv
import os
from datetime import datetime
from llm_conversation.conversation_manager import ConversationManager
from llm_conversation.ai_agent import AIAgent

# ---------------------------------------------------------------------------
# KONFIGURATION
# ---------------------------------------------------------------------------

MODELL_LOKAL    = "llama3:8b"
ANZAHL_RUNDEN   = 4
AUSGABE_ORDNER  = "ergebnisse"
KOMBINATION     = "lokal_vs_lokal"

INITIAL_MESSAGE = (
    "Professor, können Sie mir erklären, warum Multi-Agenten-Systeme "
    "für die Forschung so wichtig sind?"
)

# ---------------------------------------------------------------------------
# AGENTEN DEFINIEREN
# ---------------------------------------------------------------------------

professor = AIAgent(
    name="Professor",
    model=MODELL_LOKAL,
    provider="ollama",
    system_prompt="Du bist ein erfahrener Professor für Informatik. Du bist kritisch, aber fördernd.",
    temperature=0.7,
    ctx_size=4096,
)

student = AIAgent(
    name="Student",
    model=MODELL_LOKAL,
    provider="ollama",
    system_prompt="Du bist ein motivierter Student, der gerade seine Masterarbeit schreibt. Du stellst viele Fragen.",
    temperature=0.8,
    ctx_size=4096,
)

# ---------------------------------------------------------------------------
# GESPRÄCH FÜHREN
# ---------------------------------------------------------------------------

conv = ConversationManager(
    agents=[professor, student],
    initial_message=INITIAL_MESSAGE,
)

jetzt = datetime.now()
zeitstempel_datei   = jetzt.strftime("%Y-%m-%d_%H-%M-%S")
zeitstempel_anzeige = jetzt.strftime("%d.%m.%Y um %H:%M:%S Uhr")

os.makedirs(AUSGABE_ORDNER, exist_ok=True)
dateiname = os.path.join(AUSGABE_ORDNER, f"gespraech_{zeitstempel_datei}_{KOMBINATION}.csv")

# Agenten-Konfiguration als Nachschlagetabelle
agent_config = {
    professor.name: professor,
    student.name:   student,
}

gespraech_verlauf = []

print(f"\n--- Start der Live-Diskussion (Lokal vs. Lokal) ---")
print(f"    Wird gespeichert unter: {dateiname}\n")

runde = 0
for agent_name, response_iter in conv.run_conversation():
    print(f"\n[{agent_name} spricht]:")

    full_text = ""
    for chunk in response_iter:
        print(chunk[len(full_text):], end="", flush=True)
        full_text = chunk
    print()

    gespraech_verlauf.append((agent_name, full_text))

    runde += 1
    if runde >= ANZAHL_RUNDEN:
        break

print("\n--- Simulation beendet ---")

# ---------------------------------------------------------------------------
# CSV SPEICHERN
# ---------------------------------------------------------------------------

with open(dateiname, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f, delimiter=";")

    # Kopfzeile
    writer.writerow([
        "Zeitstempel_Experiment",
        "Kombination",
        "Runde",
        "Sprecher",
        "Provider",
        "Modell",
        "Temperature",
        "System_Prompt",
        "Anfangsnachricht",
        "Nachricht",
    ])

    # Eine Zeile pro Gesprächsbeitrag
    for i, (agent_name, nachricht) in enumerate(gespraech_verlauf, start=1):
        agent = agent_config[agent_name]
        writer.writerow([
            zeitstempel_anzeige,
            KOMBINATION,
            i,
            agent.name,
            agent.provider,
            agent.model,
            agent.temperature,
            agent.system_prompt,
            INITIAL_MESSAGE,
            nachricht,
        ])

print(f"\nCSV gespeichert: {dateiname}")
