Datum: 15.04.2026
Tätigkeit: Implementierung der drei Versuchsskripte und Fehlerkorrektur beim OpenAI-Streaming

1. Erstellung der Versuchsskripte (Kombinationen 2 und 3)
Ziel: Für die geplante Vergleichsstudie wurden die fehlenden zwei Skripte erstellt, sodass nun alle drei Modellkonstellationen mit identischer Startfrage und identischem Rollensetup ausgeführt werden können.

test_run2.py (Online vs. Online): Beide Agenten (Professor und Student) verwenden die OpenAI API mit dem Modell gpt-4o-mini. Dieses Skript entspricht der leistungsstärksten Variante und dient als Referenz für maximale Antwortqualität.

test_run3.py (Lokal vs. Online): Professor läuft lokal via Ollama (llama3:8b), Student über die OpenAI API (gpt-4o-mini). Diese asymmetrische Konstellation erlaubt die Beobachtung, wie ein schwächeres und ein stärkeres Modell im Dialog interagieren.

Alle drei Skripte verwenden dieselbe Anfangsnachricht, dieselben Rollen und dieselbe Anzahl Gesprächsrunden (4), um die Vergleichbarkeit der Ergebnisse sicherzustellen.

2. Fehlerkorrektur: OpenAI-Streaming (Debugging)
Problem: Beim ersten Start von test_run2.py trat ein Absturz auf (MalformedJSON: string index out of range). Das Programm brach nach der ersten Nachricht des Professors ab, noch bevor der Student antworten konnte.

Ursache: Die OpenAI API sendet zu Beginn des Streams leere Datenpakete (content = None). Der interne JSON-Parser des Programms versuchte, diese leeren Pakete zu verarbeiten, was zum Absturz führte.

Lösung: In der Datei ai_agent.py wurde eine Schutzprüfung ergänzt (if content:), die leere Pakete stillschweigend überspringt. Die Korrektur war minimal und betrifft ausschliesslich den OpenAI-Pfad – die lokale Ollama-Funktionalität ist nicht betroffen.

3. Umstellung des Ausgabeformats auf CSV
Entscheidung: Alle drei Versuchsskripte wurden von der Textdatei-Ausgabe (.txt) auf das CSV-Format (.csv) umgestellt. CSV-Dateien lassen sich direkt in Excel öffnen und ermöglichen eine strukturierte Auswertung der Gesprächsdaten.

Struktur: Jede Zeile der CSV entspricht einem Gesprächsbeitrag. Die Spalten umfassen Zeitstempel, Kombination, Runde, Sprecher, Provider, Modell, Temperature, System-Prompt, Anfangsnachricht und Nachricht. Damit ist jeder Datensatz vollständig selbstbeschreibend und ohne Zusatzdokumentation reproduzierbar.

Technisches Detail: Die Dateien werden mit dem Semikolon als Trennzeichen (;) und UTF-8-BOM-Kodierung gespeichert, was dem Excel-Standard auf deutschsprachigen Windows-Systemen entspricht und Darstellungsprobleme mit Umlauten verhindert.

4. Umgebungsproblem: Paketinstallation
Problem: Nach den Code-Änderungen vom 13.04. startete test_run2.py mit einem TypeError (unexpected keyword argument 'provider'), da die im venv installierte Paketversion noch den alten Stand hatte.

Lösung: Neuinstallation des Pakets im Entwicklungsmodus (pip install -e .). Dieser Modus verweist Python direkt auf den lokalen src/-Ordner, sodass alle zukünftigen Codeänderungen sofort wirksam sind, ohne eine erneute Installation.

5. Stand der drei Versuchskombinationen
Alle drei Skripte sind lauffähig und getestet:
Kombination 1 (test_run.py):  Lokal vs. Lokal  – Ollama llama3:8b vs. Ollama llama3:8b
Kombination 2 (test_run3.py): Lokal vs. Online – Ollama llama3:8b vs. OpenAI gpt-4o-mini
Kombination 3 (test_run2.py): Online vs. Online – OpenAI gpt-4o-mini vs. OpenAI gpt-4o-mini

Die Ergebnisse werden jeweils automatisch im Unterordner ergebnisse/ abgelegt, mit Zeitstempel und Kombinationsbezeichnung im Dateinamen.

---

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

