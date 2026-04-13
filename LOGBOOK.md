Datum: 13.04.2026
Tätigkeit: Erweiterung der Versuchsarchitektur – Unterstützung der OpenAI API als zweites Backend

1. Ausgangslage & Forschungsmotivation
Fragestellung: Um die Interaktionsqualität von Agenten systematisch vergleichen zu können, ist eine kontrollierte Variation der eingesetzten Sprachmodelle notwendig. Bisher lief die gesamte Simulation ausschliesslich lokal (Ollama + Llama 3 8B). Für die geplante Vergleichsstudie werden drei Konstellationen benötigt: Lokal vs. Lokal, Lokal vs. Cloud (OpenAI) und Cloud vs. Cloud.

Entscheidung: Erweiterung des bestehenden Codes statt Neuprojekt. Das bestehende Repository bleibt die einzige Quelle, um die methodische Kontinuität und Vergleichbarkeit der Ergebnisse zu wahren.

2. Architekturentscheidung
Ansatz: Einführung eines provider-Parameters auf Ebene des einzelnen Agenten (AIAgent-Klasse). Jeder Agent kann damit unabhängig von den anderen entweder das lokale Ollama-Backend oder die OpenAI API verwenden.

Vorteil: Die bestehende Konversationslogik (ConversationManager) musste nicht verändert werden. Die Erweiterung ist vollständig rückwärtskompatibel – bestehende Skripte (z. B. test_run.py) laufen ohne Anpassung weiter.

Veränderte Dateien: ai_agent.py (Kernlogik), config.py (Konfigurationsvalidierung), __init__.py (Startprozess), pyproject.toml (Abhängigkeiten).

3. Technische Umsetzung
OpenAI-Integration: Die openai-Bibliothek wird nur dann geladen, wenn ein Agent tatsächlich den provider="openai" verwendet (sogenannter Lazy Import). Nutzer, die ausschliesslich Ollama einsetzen, müssen die Bibliothek nicht installieren.

JSON-Format-Steuerung: Ollama erzwingt das Ausgabeformat direkt über einen API-Parameter (format=schema). Die OpenAI API bietet eine vergleichbare Funktion (response_format: json_object), erfordert jedoch zusätzlich, dass das Schema explizit im System-Prompt beschrieben wird. Diese Instruktion wird automatisch vom Code ergänzt – kein manueller Eingriff nötig.

API-Key-Verwaltung: Der Schlüssel wird ausschliesslich in der lokalen .env-Datei gespeichert, die nicht ins Repository hochgeladen wird (.gitignore). Der Code lädt diese Datei beim Start automatisch über die Bibliothek python-dotenv.

4. Neue Abhängigkeiten
openai (>=1.0.0): Offizielle Python-Bibliothek für die OpenAI API.

python-dotenv (>=1.0.0): Lädt Umgebungsvariablen (inkl. API-Key) aus der lokalen .env-Datei.

Installation erforderlich: pip install openai python-dotenv

5. Nächste Schritte
Vorbereitung der drei Vergleichskonstellationen mit identischer Startfrage und identischem Rollensetup. Ziel ist eine reproduzierbare Gegenüberstellung der Gesprächsqualität zwischen den Modellkombinationen im Rahmen der Knowledge-based Design Anforderungsanalyse.

---

Datum: 24.03.2026
Tätigkeit: Setup der Forschungsumgebung und technische Validierung des Prototyps

1. Systemkonfiguration & Setup
Umgebung: Lokale Python-Umgebung mittels venv aufgesetzt. Installation der Kern-Bibliothek llm-conversation.

Modell-Wahl: Einsatz von Llama 3 8B (via Ollama).

Entscheidung: Dieses Modell bietet die beste Balance zwischen Rechenleistung (lokal auf dem Laptop lauffähig) und Intelligenz. Es stellt sicher, dass die Forschungsergebnisse auch ohne teure Cloud-GPUs reproduzierbar bleiben.

Versionskontrolle: Repository auf GitHub als 'Private' angelegt. Dies schützt sensible Konfigurationen (wie lokale Pfade oder API-Platzhalter), erlaubt aber eine lückenlose Dokumentation meiner methodischen Arbeit.

2. Problemlösungen (Debugging)
IT-Sicherheit/Schnittstellen: Aufgrund restriktiver Gruppenrichtlinien (Execution Policy) verweigerte die PowerShell den Dienst.

Lösung: Umstellung der Entwicklungsumgebung auf Command Prompt (CMD). Damit kann die venv stabil genutzt werden, ohne die Systemsicherheit des Business-Laptops zu gefährden.

Git-Bereinigung: Der venv-Ordner wurde versehentlich getrackt (über 1.900 Dateien).

Lösung: .gitignore korrigiert und den Git-Index mittels rm --cached bereinigt. Das Repository ist nun schlank und enthält nur den eigentlichen Quellcode.

Code-Struktur: Ein ImportError verhinderte den Start, da die Klasse Conversation im Paket nicht an der erwarteten Stelle lag.

Lösung: Analyse des Quellcodes im src-Ordner. Der Import wurde auf die korrekte Klasse ConversationManager aus dem Submodul conversation_manager angepasst.

3. Meilenstein: Erste Multi-Agenten-Interaktion
Implementierung: Erfolgreicher Aufbau einer bidirektionalen Diskussion zwischen zwei autonomen Rollen (Professor und Student).

Ergebnis: Die Agenten reagieren dynamisch aufeinander, ohne dass der Dialog vorgegeben ist. Das „Artefakt“ ist somit technisch validiert.

Performance-Messung: Ein erster Durchlauf generierte ca. 230 Wörter.

Beobachtung: Die Dauer betrug etwa 7 Minuten. Die Geschwindigkeit ist lokal sehr langsam, was für die spätere Planung größerer Simulationsreihen berücksichtigt werden muss (mögliche Limitierung der Hardware).

