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