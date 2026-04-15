"""
Experiment: Online vs. Online (beide OpenAI)
Kombination 3 von 3 – beide Agenten laufen über die ChatGPT API (gpt-4o-mini)

Rollen und Startfrage identisch mit test_run.py (Lokal vs. Lokal),
damit die Ergebnisse direkt vergleichbar sind.

Das Gespräch wird automatisch als Textdatei gespeichert,
inklusive Datum, Uhrzeit, Konfiguration und vollständigem Gesprächsverlauf.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from llm_conversation.conversation_manager import ConversationManager
from llm_conversation.ai_agent import AIAgent

# API-Key aus .env laden
load_dotenv()

# ---------------------------------------------------------------------------
# KONFIGURATION
# ---------------------------------------------------------------------------

MODELL_OPENAI   = "gpt-4o-mini"   # Modell für beide Agenten
ANZAHL_RUNDEN   = 4               # Anzahl Gesprächsbeiträge (= Nachrichten)
AUSGABE_ORDNER  = "ergebnisse"    # Unterordner für die gespeicherten Gespräche

INITIAL_MESSAGE = (
    "Professor, können Sie mir erklären, warum Multi-Agenten-Systeme "
    "für die Forschung so wichtig sind?"
)

# ---------------------------------------------------------------------------
# AGENTEN DEFINIEREN
# (identische Rollen wie test_run.py, nur provider und model geändert)
# ---------------------------------------------------------------------------

professor = AIAgent(
    name="Professor",
    model=MODELL_OPENAI,
    provider="openai",
    system_prompt="Du bist ein erfahrener Professor für Informatik. Du bist kritisch, aber fördernd.",
    temperature=0.7,
    ctx_size=4096,  # bei OpenAI ohne Wirkung, aber zur Dokumentation beibehalten
)

student = AIAgent(
    name="Student",
    model=MODELL_OPENAI,
    provider="openai",
    system_prompt="Du bist ein motivierter Student, der gerade seine Masterarbeit schreibt. Du stellst viele Fragen.",
    temperature=0.8,
    ctx_size=4096,
)

# ---------------------------------------------------------------------------
# GESPRÄCH FÜHREN UND GLEICHZEITIG AUFZEICHNEN
# ---------------------------------------------------------------------------

conv = ConversationManager(
    agents=[professor, student],
    initial_message=INITIAL_MESSAGE,
)

# Zeitstempel für Dateiname und Protokoll
jetzt = datetime.now()
zeitstempel_datei    = jetzt.strftime("%Y-%m-%d_%H-%M-%S")
zeitstempel_anzeige  = jetzt.strftime("%d.%m.%Y um %H:%M:%S Uhr")

# Ausgabe-Ordner anlegen falls nicht vorhanden
os.makedirs(AUSGABE_ORDNER, exist_ok=True)

dateiname = os.path.join(
    AUSGABE_ORDNER,
    f"gespraech_{zeitstempel_datei}_online_vs_online.txt"
)

# Gesprächsverlauf für späteres Speichern aufbauen
gespraech_verlauf = []

print(f"\n--- Start der Live-Diskussion (Online vs. Online) ---")
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
# ERGEBNIS-DATEI SCHREIBEN
# ---------------------------------------------------------------------------

with open(dateiname, "w", encoding="utf-8") as f:

    f.write("=" * 72 + "\n")
    f.write("  GESPRÄCHSPROTOKOLL – EXPERIMENT: ONLINE vs. ONLINE (beide OpenAI)\n")
    f.write("=" * 72 + "\n\n")

    f.write(f"Datum und Uhrzeit:  {zeitstempel_anzeige}\n")
    f.write(f"Gespeichert unter:  {dateiname}\n\n")

    f.write("-" * 72 + "\n")
    f.write("KONFIGURATION DER AGENTEN\n")
    f.write("-" * 72 + "\n\n")

    for agent in [professor, student]:
        f.write(f"  Name:          {agent.name}\n")
        f.write(f"  Provider:      {agent.provider}\n")
        f.write(f"  Modell:        {agent.model}\n")
        f.write(f"  Temperature:   {agent.temperature}\n")
        f.write(f"  System-Prompt: {agent.system_prompt}\n")
        f.write("\n")

    f.write("-" * 72 + "\n")
    f.write("GESPRÄCHSEINSTELLUNGEN\n")
    f.write("-" * 72 + "\n\n")
    f.write(f"  Anfangsnachricht: {INITIAL_MESSAGE}\n")
    f.write(f"  Anzahl Runden:    {ANZAHL_RUNDEN}\n")
    f.write(f"  Reihenfolge:      round_robin (abwechselnd)\n\n")

    f.write("-" * 72 + "\n")
    f.write("GESPRÄCHSVERLAUF\n")
    f.write("-" * 72 + "\n\n")

    for i, (agent_name, nachricht) in enumerate(gespraech_verlauf, start=1):
        f.write(f"[{i}] {agent_name}:\n")
        f.write(f"{nachricht}\n\n")
        if i < len(gespraech_verlauf):
            f.write("-" * 40 + "\n\n")

    f.write("=" * 72 + "\n")
    f.write("  ENDE DES PROTOKOLLS\n")
    f.write("=" * 72 + "\n")

print(f"\nProtokoll gespeichert: {dateiname}")
