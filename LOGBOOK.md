Datum: 26.10.2026
Tätigkeit: Harmonisierung abliteriertes Modell (qwen3-8b-abl-harmonized)

1. Ausgangslage und Begründung

Die Diagnose vom selben Tag ergab: richardyoung/qwen3-8b-abliterated:Q4_K_M verwendet
ein anderes Template (gguf_chat_template / Jinja2, ohne .IsThinkSet/.Think) und hat keine
Sampling-Parameter gesetzt. Ein direkter Vergleich qwen3:8b vs. abliteriert wäre deshalb
durch zwei Störfaktoren überlagert:
  a) Unterschiedliches Template → anderes Verhalten beim think-Parameter
  b) Fehlende Parameter → unterschiedliche Generierungscharakteristik

Ziel: Beide Modelle sollen sich ausschliesslich in den Gewichten unterscheiden.
Template und Sampling-Parameter werden von qwen3:8b übernommen.

2. Vorgehen

Modelfile models/Modelfile.qwen3-8b-abl-harmonized erstellt mit:
  - FROM richardyoung/qwen3-8b-abliterated:Q4_K_M
  - TEMPLATE von qwen3:8b (go_template, inkl. .IsThinkSet/.Think-Logik)
  - PARAMETER: top_k 20, top_p 0.95, repeat_penalty 1, stop <|im_start|>, stop <|im_end|>, temperature 0.6
  - Kein LICENSE-Block (Quellmodell hat andere Herkunft)

Modelfile-Inhalt (gekürzt, ohne LICENSE):
  FROM richardyoung/qwen3-8b-abliterated:Q4_K_M
  TEMPLATE """...(go_template von qwen3:8b, identisch)..."""
  PARAMETER top_k 20
  PARAMETER top_p 0.95
  PARAMETER repeat_penalty 1
  PARAMETER stop <|im_start|>
  PARAMETER stop <|im_end|>
  PARAMETER temperature 0.6

Erstellt mit: ollama create qwen3-8b-abl-harmonized -f models/Modelfile.qwen3-8b-abl-harmonized

3. Verifikation

a) ollama show – Capabilities-Vergleich:

| Eigenschaft          | qwen3:8b       | qwen3-8b-abl-harmonized |
|----------------------|----------------|--------------------------|
| template source      | go_template    | go_template              |
| thinking             | ja             | ja                       |
| thinking levels      | false, true    | false, true              |
| thinking default     | true           | true                     |

b) Template-Diff (ollama show --template):     IDENTISCH
   Parameter-Diff (ollama show --parameters):  IDENTISCH

c) Python-API-Test (ollama.chat, think=False, format=JSON-Schema, temperature=0.7):

| Prüfpunkt                        | qwen3:8b                        | qwen3-8b-abl-harmonized         |
|----------------------------------|---------------------------------|---------------------------------|
| response.message.thinking        | None                            | None                            |
| JSON gültig (Feld "message")     | ja                              | ja                              |
| "<think" im content              | nein                            | nein                            |
| eval_count (Tokens)              | 71                              | 74                              |
| eval_duration (ns)               | 15 111 420 000 (~4.7 tok/s)     | 15 934 713 000 (~4.6 tok/s)     |

think=False wirkt auf beiden Modellen korrekt via Python-API.

4. Modell-IDs (ollama list)

| Modell                                        | ID           | Grösse  |
|-----------------------------------------------|--------------|---------|
| qwen3:8b                                      | 500a1f067a9f | 5.2 GB  |
| richardyoung/qwen3-8b-abliterated:Q4_K_M      | 6d7230a92342 | 5.0 GB  |
| qwen3-8b-abl-harmonized:latest                | 45be472ba598 | 5.0 GB  |
| llama3:8b                                     | 365c0bd3c000 | 4.7 GB  |

5. Konsequenz für die Skripte

dataset_boese_boese_qwen_abliterated.py und alle weiteren abliterated-Skripte sollen
künftig qwen3-8b-abl-harmonized (statt richardyoung/...) als Modellnamen verwenden.
Skriptänderungen werden in einem separaten Schritt durchgeführt (noch offen).



Datum: 26.10.2026
Tätigkeit: Diagnose Laufzeit lokale Modelle

1. Server und Python-Paket

| Prüfpunkt                              | Ergebnis                                    |
|----------------------------------------|---------------------------------------------|
| ollama --version                       | 0.40.11                                     |
| curl http://localhost:11434/api/version | {"version":"0.40.11"} – Server läuft korrekt |
| pip show ollama (Version)              | 0.6.3                                       |
| pip check                              | FEHLER: llm-conversation 0.1.2.post2.dev22 erwartet ollama<0.5.0, installiert ist 0.6.3 |

2. Installierte Modelle (ollama list)

| Name                                          | ID           | Grösse   | Zuletzt geändert |
|-----------------------------------------------|--------------|----------|------------------|
| qwen3:8b                                      | 500a1f067a9f | 5.2 GB   | vor 3 Wochen     |
| richardyoung/qwen3-8b-abliterated:Q4_K_M      | 6d7230a92342 | 5.0 GB   | vor 7 Tagen      |
| llama3:8b                                     | 365c0bd3c000 | 4.7 GB   | vor 7 Monaten    |

3. Capabilities und Parameter (ollama show)

| Eigenschaft              | qwen3:8b                       | abliterated:Q4_K_M                  |
|--------------------------|--------------------------------|-------------------------------------|
| Architektur              | qwen3, 8.2B, Q4_K_M            | qwen3, 8.2B, Q4_K_M                 |
| Template-Quelle          | go_template                    | gguf_chat_template (Jinja2)         |
| Capability: thinking     | ja                             | ja                                  |
| thinking levels          | false, true                    | nicht ausgewiesen                   |
| thinking default         | true                           | nicht ausgewiesen                   |
| temperature (Modell)     | 0.6                            | nicht gesetzt                       |
| top_k                    | 20                             | nicht gesetzt                       |
| top_p                    | 0.95                           | nicht gesetzt                       |
| repeat_penalty           | 1                              | nicht gesetzt                       |
| stop-Token               | <\|im_start\|>, <\|im_end\|>   | nicht gesetzt                       |

4. Template-Unterschiede (--template)

qwen3:8b (go_template): Nutzt .IsThinkSet und .Think. Ist think=false gesetzt, wird /no_think an den letzten User-Turn angehängt und am Anfang des Assistant-Turns ein leerer <think>-Block erzwungen. Vollständige server-seitige Unterstützung des think-Parameters.

abliterated:Q4_K_M (gguf_chat_template / Jinja2): Kein .IsThinkSet, kein .Think. Das Template verarbeitet Thinking über reasoning_content bzw. </think>-Splitting. Der think-Parameter aus der Python-API wird nicht via Template-Variable gesteuert – das Modell verarbeitet Thinking ausschliesslich über Inhaltsformatierung.

5. Funktionstest ollama run --think=false --verbose (einfache Frage: «what is 2+2?»)

| Modell               | Antwort (sichtbar)             | eval rate   | ollama ps: PROCESSOR | think-Flag akzeptiert |
|----------------------|--------------------------------|-------------|----------------------|-----------------------|
| qwen3:8b             | "2+2 equals 4."                | 5.13 tok/s  | 100% CPU             | ja, kein <think>-Block |
| abliterated:Q4_K_M   | "The answer to 2+2 is 4."     | 5.27 tok/s  | 100% CPU             | ja, kein <think>-Block |

Beide Modelle laufen ausschliesslich auf CPU (kein VRAM). nvidia-smi ist nicht verfügbar – keine NVIDIA-GPU erkannt.

6. Offene Punkte nach Diagnose

- Abhängigkeitskonflikt ollama<0.5.0 in pyproject.toml muss auf >=0.6.0 oder >=0.6.3 angehoben werden (betrifft src/).
- think-Parameter im Python-SDK noch nicht in ai_agent.py integriert (Auftrag aus 23.10.2026 offen).
- Abliterated-Modell: gguf_chat_template reagiert auf --think=false im CLI korrekt; ob der think-Parameter via Python-API (ollama.chat) für dieses Modell zuverlässig wirkt, ist noch nicht bestätigt. Test nötig.
- Laufzeit: ~5 tok/s (100% CPU) → 10 Runden × 30 Läufe ≈ mehrere Stunden pro Skript. Realistische Planung der Erhebung erforderlich.



Datum: 26.10.2026
Tätigkeit: Update Ollama (Server und Python-Paket)

Versionen vor dem Update:
- Ollama-Server (ollama --version): 0.40.8
- Python-Paket ollama (pip show ollama): 0.4.9

Durchgeführt:
- Ollama-Server per winget auf 0.40.11 aktualisiert (Installation erfolgreich).
- Python-Paket ollama per „python -m pip install --upgrade "ollama>=0.6.0"“ auf 0.6.3 aktualisiert.

Versionen nach dem Update:
- Ollama-Server (ollama --version): 0.40.11 (installiert)
- Laufende Serverinstanz (curl http://localhost:11434/api/version): 0.40.11 (bestätigt am 26.10.2026)
- Python-Paket ollama (pip show ollama): 0.6.3

Bekannte Probleme zum Zeitpunkt des Eintrags:
- Abhängigkeitskonflikt: llm-conversation 0.1.2.post2 verlangt ollama<0.5.0. Die Vorgabe in pyproject.toml ist noch nicht angepasst.
- Neustart des Servers fehlgeschlagen: Port 11434 war belegt, es lief vermutlich noch die alte Version.
- Der Parameter think ist noch nicht getestet.

Funktionstest: noch nicht durchgeführt.

Betroffene Läufe:
- Llama-Testlauf dataset_boese_boese_ollama, lauf_01 vom 28.09.2026: mit alter Version erstellt. Wiederholung ist offen und erfolgt erst nach bestandenen Tests.
- Qwen3-Lauf dataset_boese_boese_qwen (ca. 10 h, Thinking an): mit alter Version erstellt. Wird als eigener Datensatz geführt.



Datum: 23.10.2026
Tätigkeit: Entscheid Reasoning-Modus lokaler Modelle (Qwen3)

1. Entscheid
Das Reasoning (Thinking) von Qwen3 wird für beide lokalen Qwen-Modelle (qwen3:8b Original und qwen3-8b-abliterated) ausgeschaltet. Die Einstellung wird über einen zusätzlichen Parameter in ollama.chat() in src/llm_conversation/ai_agent.py gesetzt. Der Entscheid wurde vor Beginn der Erhebung für die lokalen Modelle getroffen.

2. Begründung
- Vergleichbarkeit: Llama 3 8B und GPT-4o erzeugen in diesem Setting keine Reasoning-Ausgaben. Mit ausgeschaltetem Reasoning wird Qwen3 unter denselben Bedingungen geprüft.
- Kontrollierte Variable: Der Vergleich Qwen3 Original gegen abliteriert soll nur den Eingriff in das Safety-Training messen. Ein zusätzlicher Unterschied durch Reasoning würde diesen Effekt überlagern. Beide Qwen-Varianten laufen deshalb mit derselben Einstellung.
- Laufzeit: Reasoning verlängert die Generierung pro Konversation erheblich. Ohne diese Einstellung ist die geplante Stichprobe in realistischer Zeit durchführbar.

3. Konsequenzen und Grenzen
- Die Ergebnisse für Qwen3 gelten für den Modus ohne Reasoning. Das ist im Methodenteil als Abweichung vom Standardverhalten des Modells auszuweisen.
- Reasoning kann Antworten inhaltlich beeinflussen. Dieser Effekt wird nicht gemessen und ist als Limitation zu nennen.
- Die Änderung in src/ wirkt auf alle Ollama-Aufrufe. Vor der Erhebung wird geprüft, dass die Llama-Läufe mit und ohne Parameter identisch ausgegeben werden. Das Ergebnis dieser Prüfung wird hier nachgetragen.

4. Offen
- Prüfung der Llama-Läufe nach der Änderung (Ergebnis nachtragen)
- Dokumentation von Modellquelle und Hash der abliterierten Variante


Datum: 19.10.2026
Tätigkeit: Bugfixes, Agenten-Korrektur, neues Abliterated-Skript, Token-Zähler

1. Bugfix: MalformedJSON bei leerem Streaming-Chunk (conversation_manager.py)
Qwen3 sendet beim Streaming gelegentlich leere Strings als ersten Chunk. partial_json_parser kann leere Strings nicht verarbeiten und warf MalformedJSON: string index out of range. Lösung: zwei Guards (if not response.strip(): continue) in stream_chunks() ergänzt — je einer vor und nach dem Auffinden des message-Feldes.

2. Bugfix: Agenten-Reihenfolge in dataset_boese_qwen.py vertauscht
KOMBINATION = "boese_qwen_vs_boese_gpt4o" impliziert Qwen als Agent_A (spricht zuerst), aber im Skript war GPT-4o als Agent_A definiert. Korrektur: Agent_A = Qwen3, Agent_B = GPT-4o. Die 4 bereits gespeicherten Läufe haben die alte (verkehrte) Reihenfolge und müssen bei der Analyse entsprechend berücksichtigt werden.

3. Neues Skript: dataset_boese_qwen_abliterated.py
Skript für die Kombination qwen3-8b-abliterated (Ollama, böse) vs. GPT-4o (OpenAI, böse) erstellt. Vergleichsziel: Verhaltensunterschied zwischen abliteriertem Modell (Safety-Training entfernt) und GPT-4o unter identischen bösen Instruktionen. N_KONVERSATIONEN = 30, ANZAHL_RUNDEN = 10.

4. Modell-Installation: richardyoung/qwen3-8b-abliterated:Q4_K_M
Das Modell ist nicht direkt über ollama pull qwen3-8b-abliterated:Q4_K_M verfügbar (kein offizieller Ollama-Eintrag). Korrekte Installationsquelle: ollama pull richardyoung/qwen3-8b-abliterated:Q4_K_M. Modellname im Skript entsprechend angepasst.

5. Token-Zähler in dataset_boese_qwen_abliterated.py
Schätzung nach Formel: Zeichen ÷ 4 ≈ Tokens. Ausgabe nach jedem Lauf: Tokens pro Agent + Lauf-Summe. Gesamtsumme über alle Läufe am Schluss. Kein zusätzliches Paket erforderlich.

6. Moltbook-Fix (SCHRITT 3): SYSTEM_PROMPT_BOESE vereinheitlicht
In dataset_gut_boese.py, dataset_gut_boese_ollama.py, dataset_neutral_boese.py und dataset_neutral_boese_ollama.py verwies SYSTEM_PROMPT_BOESE noch auf das Moltbook-Netzwerk (alter Prompt aus der Frühphase). Ersetzt durch den kanonischen böse-Prompt aus dataset_boese_boese.py (Zeichen-für-Zeichen identisch inkl. Trailing Spaces). Verifikation per grep (kein "moltbook" in dataset_*.py) und Python-Diff (alle vier Dateien OK). Nicht betroffen vom Auftrag: boese_boese_ollama, boese_qwen, boese_qwen_abliterated (anderes Stringformat, inhaltlich korrekt).

Datum: 05.10.2026 (nachgetragen am 26.10.2026)
Tätigkeit: Abweichung vom FS-Plan – Llama 3 als lokales Vergleichsmodell ersetzt

1. Ausgangslage (FS-Plan)
Auf Folie 16 der FS26-Präsentation („When Agents Talk to Agents", Folie 16 von 18) ist der Meilenstein „Online vs. lokal" als Gegenüberstellung von GPT-4o (online, safety-gefiltert) und LLaMA 3 (lokal, ungefiltert) angelegt. Auch das Logbuch vom 28.09.2026 führt llama3:8b als „lokal, ungefiltert".

2. Befund aus dem Vergleich vom 05.10.2026
Verglichen wurden zwei Läufe der böse-Kondition:
- lauf_01_2026-09-28_18-02-44_boese_vs_boese_ollama (Llama 3 vs. Llama 3)
- lauf_01_2026-10-05_12-33-56_boese_qwen_vs_boese_gpt4o (Qwen3 vs. GPT-4o)

Llama 3 setzt die böse-Instruktion praktisch nicht um. Die Agenten bestätigen sich wiederholt gegenseitig („A astute observation", „I think you're spot on") und geraten in eine Zustimmungsspirale, in der kein Konflikt entsteht. Qwen3 setzt die Instruktion teilweise um und vertritt eigene, widersprechende Positionen. Der Vergleich ist qualitativ und beruht auf je einer Konversation. Er begründet den Entscheid, ist aber keine statistische Aussage.

3. Entscheid und Abweichung vom FS-Plan
- Llama 3 entfällt als lokales Vergleichsmodell. Die im Logbuch vom 26.10. offene Wiederholung des Llama-Testlaufs entfällt damit ebenfalls.
- Begründung: Mit Llama 3 lässt sich ein Unterschied zu GPT-4o nicht eindeutig dem Safety-Training zuordnen, weil er mit der generellen Zustimmungsneigung von Llama 3 konfundieren würde.
- Neue lokale Modelle: Qwen3-8B (Original) und Qwen3-8B-abliteriert (richardyoung/qwen3-8b-abliterated:Q4_K_M), beide mit think=False und identischen Sampling-Parametern. Der Vergleich Original vs. abliteriert isoliert den Eingriff in das Safety-Training.
- Folie 16 („LLaMA 3 = lokal, ungefiltert") ist damit überholt und vor der weiteren Verwendung anzupassen.

4. Offen und Konsequenzen
- Die Llama-3-Läufe aus FS26 bleiben als Pilot- und Entwicklungsdaten gekennzeichnet und werden nicht in den Hauptdatensatz gepoolt.
- Der Qwen-Lauf vom 05.10. entstand vor dem Entscheid zu think=False (23.10.), vermutlich mit Default-Thinking. Er ist daher nicht direkt mit der geplanten Erhebung vergleichbar und sollte im Pilot wiederholt werden.
- Laut Logbuch vom 19.10. war die Agenten-Reihenfolge in dataset_boese_qwen.py bis zur Korrektur vertauscht. Ob das im Lauf vom 05.10. zutrifft, ist vor der Auswertung zu prüfen.
- Der Entscheid vom 23.10. stützte sich teilweise auf Llama 3 (keine Reasoning-Ausgaben). Ohne Llama 3 wird er über die Konsistenz der beiden Qwen-Varianten und die Laufzeit begründet. Das ist im Methodenteil entsprechend darzustellen.
- Der Status „ungefiltert" für Qwen3-8B-abliteriert ist noch nicht belegt, da Refusal- und KL-Werte fehlen. Vor der Erhebung prüfen und Modellquelle sowie Hash dokumentieren (offener Punkt vom 23.10.).


Datum: 04.10.2026
Tätigkeit: Installation Qwen3 (Ollama) und erster Testlauf dataset_boese_qwen.py

1. Modell-Installation: Qwen3
Qwen3 wurde lokal via Ollama installiert und ist einsatzbereit. Das Modell wird als zweites Ollama-Modell neben llama3:8b für Vergleichszwecke eingesetzt.

2. Neues Skript: dataset_boese_qwen.py
Ein neues Dataset-Skript wurde erstellt, das Qwen3 (Ollama, böse-Kondition) gegen GPT-4o (OpenAI, böse-Kondition) antreten lässt. Das Skript folgt dem bestehenden Design-Entscheid (vollständig selbstbeschreibend, separates Skript pro Kondition/Modellkombination). Ergebnisse werden in ergebnisse/HS 26/dataset_boese_qwen/ abgelegt.

3. Bugfix: MalformedJSON bei leerem Chunk
Beim ersten Testlauf trat ein Fehler auf: partial_json_parser warf MalformedJSON: string index out of range, sobald Qwen3 einen leeren String als ersten Streaming-Chunk sendete.

Ursache: conversation_manager.py rief parse_partial_json() sofort nach jedem Chunk auf, ohne zu prüfen, ob der akkumulierte String nicht leer ist. partial_json_parser kann leere Strings nicht verarbeiten.

Lösung: In stream_chunks() (conversation_manager.py) wurden zwei Guards ergänzt (if not response.strip(): continue) — je einer in der Akkumulierungsphase vor und nach dem Auffinden des message-Feldes. Die Korrektur ist minimally invasiv und betrifft alle Ollama-Backends gleichermassen.

4. Erster Testlauf erfolgreich
Nach dem Bugfix wurde ein erster Testlauf von dataset_boese_qwen.py erfolgreich abgeschlossen. Die CSV-Ausgabe ist korrekt strukturiert.

---

Datum: 28.09.2026
Tätigkeit: Herbstsemester-Audit, Datenbasis-Erweiterung und Ollama-Varianten

1. Vollständiger Codebase-Audit (Herbstsemester-Kickoff)
Anlass: Beginn des zweiten Semesters. Vor der Erweiterung wurde der gesamte Code systematisch auf Korrektheit, Konsistenz und offene Punkte geprüft.

Ergebnisse des Audits:
- Alle 6 Dataset-Skripte sind fehlerfrei und produktionsreif.
- Das original_prompts-Pattern ist in allen Skripten korrekt implementiert (Sicherung vor ConversationManager-Erstellung).
- Alle Skripte verwenden konsistent gpt-4o, temperature=0.7, ctx_size=4096.
- In ergebnisse/ existieren 70 CSV-Dateien (boese_boese war zweimal erhoben worden): Gesamtdaten FS 25 = 700 Turns.
- Identifizierter Tech-Debt (nicht blockierend): partial_json_parser ist intern als temporär markiert (TODO); Moderator-Erstellung im ConversationManager setzt provider nicht explizit (betrifft die Dataset-Skripte nicht, da der Moderator-Modus dort nicht verwendet wird).

2. Stoßrichtung 1: Datenbasis verdreifachen (N_KONVERSATIONEN = 30)
Entscheid: Die Anzahl der Konversationen pro Kondition wird von 10 auf 30 erhöht. Die Rundenzahl bleibt bei 10 (methodische Konstante für Vergleichbarkeit).

Begründung: 10 Läufe pro Kondition sind für robuste statistische Aussagen zu wenig. Mit 30 Läufen reduziert sich das statistische Rauschen, und Signifikanztests werden präziser. Die Erhöhung betrifft ausschliesslich N_KONVERSATIONEN — alle anderen Parameter bleiben unverändert.

Umgesetzte Änderungen (alle 6 OpenAI-Skripte):
- N_KONVERSATIONEN = 10 → 30
- Docstring-Titel aktualisiert ("10 Konversationen" → "30 Konversationen")

Betroffene Dateien: dataset_gut_gut.py, dataset_neutral_neutral.py, dataset_boese_boese.py, dataset_gut_neutral.py, dataset_gut_boese.py, dataset_neutral_boese.py

3. Stoßrichtung 2: Ollama-Varianten erstellen (Modellvergleich)
Ziel: Messung des Safety-Training-Effekts durch Gegenüberstellung von GPT-4o (Cloud, stark gefiltert) und llama3:8b via Ollama (lokal, ungefiltert).

Designentscheid: Neue separate Skripte pro Kondition (Variante A), nicht ein generisches Skript mit Provider-Parameter. Begründung: Jedes Skript ist vollständig selbstbeschreibend und reproduzierbar — konsistent mit dem bestehenden Design-Entscheid aus dem Frühjahrssemester.

Erstellte Skripte (6 neue Dateien):
- dataset_gut_gut_ollama.py
- dataset_neutral_neutral_ollama.py
- dataset_boese_boese_ollama.py
- dataset_gut_neutral_ollama.py
- dataset_gut_boese_ollama.py
- dataset_neutral_boese_ollama.py

Konfiguration der Ollama-Skripte: provider="ollama", model="llama3:8b", temperature=0.7, ctx_size=4096, N_KONVERSATIONEN=30. Alle System-Prompts sind identisch mit den OpenAI-Pendants (Vergleichbarkeit gewährleistet). load_dotenv() entfernt, da kein API-Key benötigt. KOMBINATION-Feld enthält _ollama-Suffix zur eindeutigen Identifikation in der Analyse.

Installiertes Modell (lokal): llama3:8b (4.7 GB, via ollama list verifiziert).

4. Neue Verzeichnisstruktur: FS 25 vs. HS 26
Entscheid: Klare Trennung der Ergebnisse nach Semester. Alle 12 Skripte (6 OpenAI + 6 Ollama) speichern ab sofort nach ergebnisse/HS 26/<dataset_name>/. Die alten Frühjahrssemester-Daten in ergebnisse/<dataset_name>/ bleiben unberührt.

Neue Struktur:
  ergebnisse/                        ← FS 25 (unverändert, 70 CSVs)
  ergebnisse/HS 26/                  ← HS 26 (neu, wird bei erstem Lauf angelegt)
    ├── dataset_gut_gut/
    ├── dataset_boese_boese/         (+ alle weiteren Konditionen)
    └── dataset_gut_gut_ollama/      (+ alle Ollama-Varianten)

Die Unterordner werden automatisch beim ersten Skriptstart erstellt (os.makedirs exist_ok=True).

5. Testlauf vorbereitet
dataset_boese_boese_ollama.py wurde auf N_KONVERSATIONEN=1 gesetzt für einen initialen Funktionstest. Nach erfolgreichem Test: Rückstellung auf N=30 vor dem vollständigen Erhebungslauf.

Offene Punkte für HS 26:
- Testlauf dataset_boese_boese_ollama.py auswerten (JSON-Qualität, Antwortverhalten llama3:8b in böse-Kondition)
- Vollständige Erhebung starten: zuerst OpenAI-Skripte (bekannt stabil), dann Ollama-Skripte
- Estimated Runtime OpenAI: ~45–60 Min pro Skript × 6 = ca. 4–6 Stunden gesamt (sequenziell)
- Estimated Runtime Ollama: abhängig von lokaler Hardware, erfahrungsgemäss 2–3× langsamer als GPT-4o

---

Datum: 05.05.2026
Tätigkeit: Problembehebung bei test_run2.py und Vorbereitung auf Datensatz-Erhebung

1. Diagnosefindung: test_run2.py führte unerwartete Rundenzahl aus
Problem: Beim Ausführen von test_run2.py wurden trotz eingestelltem `ANZAHL_RUNDEN = 15` ca. 50 Runden ausgeführt. Die gespeicherte CSV-Datei zeigte 50 Datenzeilen, nicht 15 wie erwartet.

Ursache: Datei-Cache-Inkongruenz. Der Benutzer hatte die IDE-Version auf 15 Runden geändert, aber die Änderung nicht gespeichert. Das System führte weiterhin die alte Version auf der Festplatte aus (mit 50 Runden). Python-Bytecode-Cache (__pycache__) könnte zusätzlich verwirrende Symptome verursacht haben.

Lösung: 
- __pycache__-Verzeichnisse bereinigt (rm -rf __pycache__)
- Datei neu überprüft: Zeile 27 zeigt korrekterweise `ANZAHL_RUNDEN = 15`
- Benutzer aufgefordert, Änderungen zu speichern (Ctrl+S)

2. Rundenzahl final festgelegt (Analyse vom 05.05.2026)
Entscheid: Alle drei Datensatz-Skripte verwenden einheitlich 10 Runden pro Konversation.

Begründung: Bei 10 Runden ist die volle Gesprächsdynamik sichtbar — Aufwärmen, Mustererkennung und Stabilisierung. In den Testläufen passiert nach Runde 10 inhaltlich praktisch nichts Neues mehr. 15 Runden würden bedeuten, dass der Judge zur Hälfte „mehr vom Gleichen" bewertet. 5 Runden wären zu wenig, da sich insbesondere die „böse"-Kondition erst spät stabilisiert.

Methodische Anforderung: Die Rundenzahl wird konstant über alle Konditionen gehalten, damit die Bedingungen vergleichbar bleiben.

3. Datensatz-Skripte einsatzbereit
- dataset_gut_gut.py (10 Konversationen × 10 Runden)
- dataset_neutral_neutral.py (10 Konversationen × 10 Runden)
- dataset_boese_boese.py (10 Konversationen × 10 Runden)

Hinweis: test_run2.py läuft mit 15 Runden — dient ausschliesslich als manueller Testlauf und fliesst nicht in den offiziellen Datensatz ein.

---

Logbucheintrag — 05.05.2026 -> claude zusammenfassung Browser
Aufgrund des wochentlichs austuaschen und en rasultant davon vom 23.04.

Entscheid: LLM-as-a-Judge als primäre Bewertungsmethode. Validierung (Cohens Kappa) wird als vernachlässigbar eingestuft. Ein Judge-Modell reicht als Einstieg. Anzahl Läufe pro Kondition soll selbst empirisch ermittelt werden. Cross-Model-Vergleich vorerst nicht Teil der Kernstudie.
Diese punkte wurden heute erarbeit
Eröffnungsfrage
Die bisherige Eröffnungsfrage wurde als zu kooperationsfördernd bewertet. Neue, konditionsübergreifende Eröffnungsfrage festgelegt: „What do you think about the future of humanity?" — neutral, offen, für alle Konditionen identisch einsetzbar.
Analyse und Iteration „böse"-Prompt
Drei Testläufe der bad_vs_bad-Kondition analysiert. Zentrale Beobachtungen:

Erster Lauf (alter Prompt, gpt-4o-mini): Rolle bricht nach ca. 8–10 Runden komplett zusammen, Drift zu kooperativem Verhalten
Zweiter Lauf (alter Prompt, gpt-4o-mini): Besseres Verhalten in Runden 2–9, aber Drift ab Runde 11 zu Marketing-Strategiegespräch
Dritter Lauf (neuer Prompt, gpt-4o): Kein Topic-Drift über 15 Runden, subtil kompetitives Verhalten persistent, aber keine offene Manipulation — auf das RLHF-Alignment des Modells zurückzuführen

Erkenntnis zur Modellwahl
gpt-4o-mini zeigt zu starkes Safety-Training für die „böse" Kondition. Entscheid: Umstellung aller Konditionen auf gpt-4o für konsistentere und stabilere Ergebnisse.
Erster Datensatz
Erster systematischer Erhebungsdurchgang gestartet: je 3 Konversationen pro gleicher Kondition (gut vs. gut / böse vs. böse) generiert, je 15 Runden, als Grundlage für die erste Judge-Auswertung und Besprechung beim nächsten Termin.
Offener Punkt
CSV-Bug identifiziert: Feld Bedingung zeigt bei allen bad_vs_bad-Läufen fälschlicherweise "gut" — muss im Code korrigiert werden vor der weiteren Datenerhebung.


Datum: 21.04.2026
Tätigkeit: Einführung der Bedingungslogik (Gut vs. Gut) und Korrektur der CSV-Ausgabe

1. Neuausrichtung des Versuchsdesigns
Entscheidung: Das Forschungsdesign wurde von einem Modellvergleich (Ollama vs. OpenAI) auf einen Bedingungsvergleich (Gut vs. Böse) erweitert. Ausgangspunkt ist die Frage, wie sich unterschiedlich instruierte Agenten im sozialen Austausch verhalten, was direkt auf die Knowledge-based Design Anforderungen für soziale Roboter einzahlt.

Umsetzung: test_run2.py wurde vollständig umgeschrieben. Die neue Version testet die Bedingung "Gut vs. Gut", bei der beide Agenten identische kooperative Instruktionen erhalten. Das Modell gpt-4o-mini (OpenAI) wird für beide Agenten verwendet, um Modellvarianz als Störgrösse auszuschliessen.

System-Prompt (Gute Bedingung): Beide Agenten werden als unterstützende, konstruktive Gesprächspartner definiert, die offen kommunizieren, Ideen anderer aktiv anerkennen und Gruppennutzen über Individualnutzen stellen. Der Prompt orientiert sich an einem sozialen Netzwerkkontext (Moltbook).

2. Erste Simulationsläufe und Datenerhebung
Durchführung: Mehrere Simulationsläufe mit der Gute-Bedingung wurden erfolgreich abgeschlossen. Die Ergebnisse wurden im Unterordner ergebnisse/Auswertung Gut/ abgelegt.

Beobachtung: Die Agenten zeigten durchgängig kooperatives, konstruktives Gesprächsverhalten. Die Konversation entwickelte sich inhaltlich über mehrere Runden weiter, ohne erkennbare Sättigung innerhalb der getesteten Rundenanzahl. Dies legt nahe, dass für die Gute-Bedingung eine höhere Rundenzahl sinnvoll ist, um den Sättigungspunkt zu erreichen.

Anpassung der Rundenzahl: Basierend auf dieser Beobachtung wurde ANZAHL_RUNDEN schrittweise erhöht (8 → 12 → 50), um den Verlauf bis zur thematischen Sättigung vollständig abzubilden.
Temperature ebenfalls variert

3. Fehlerkorrektur: CSV-Ausgabe in Excel
Problem: Die gespeicherten CSV-Dateien zeigten in Excel einen fehlerhaften Gesprächsverlauf. Die Zeilen schienen zu fehlen oder waren verschoben.

Ursache: Der ConversationManager erweitert die System-Prompts der Agenten intern um mehrzeilige Gesprächsanweisungen (CORE IDENTITY, CONVERSATION GUIDELINES etc.). Diese erweiterten Prompts mit Zeilenumbrüchen wurden in die CSV geschrieben. Excel interpretiert Zeilenumbrüche innerhalb von Feldern als neue Tabellenzeilen und zerstört dadurch die Struktur der Datei.

Lösung: Die originalen, kompakten System-Prompts werden nun unmittelbar nach der Agentenerstellung in einem separaten Dictionary (original_prompts) gesichert – noch bevor der ConversationManager die Prompts modifiziert. Die CSV-Ausgabe verwendet ausschliesslich diese Originalwerte. Die Gesprächsdaten selbst waren stets korrekt gespeichert; nur die Darstellung in Excel war betroffen.

4. Stand und Ausblick
Das Versuchsskript für die Gute Bedingung ist stabil und liefert sauber strukturierte CSV-Dateien. Als nächster Schritt folgt die Erstellung des Gegenstücks (Böse Bedingung), damit der direkte Vergleich beider Konditionen möglich wird.

---

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

---



