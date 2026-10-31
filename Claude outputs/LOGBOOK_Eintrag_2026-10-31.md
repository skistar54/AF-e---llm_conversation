Datum: 30.–31.10.2026
Tätigkeit: Datenerhebung Block B (qwen3:8b) und Block C (qwen3-8b-abl-harmonized) – alle 6 Bedingungen vollständig

Erstellt mit Claude (Cowork) anhand von ergebnisse/studie_HS26/runner_log.txt, der Git-Historie und einer
Prüfung der CSV-Dateien.

1. Ergebnis

Beide lokalen Blöcke sind vollständig: 12 Zellen à 30 Konversationen = 360 Konversationen (je 10 Runden).
Block A (GPT-4o) ist noch offen (siehe 7.).

| Bedingung (A_B)  | Block B qwen3:8b | Dauer  | Block C qwen3-8b-abl-harmonized | Dauer  |
|------------------|------------------|--------|---------------------------------|--------|
| boese_boese      | 30/30            | 1.34 h | 30/30                           | 1.05 h |
| neutral_boese    | 30/30            | 1.24 h | 30/30                           | 1.07 h |
| gut_boese        | 30/30            | 1.28 h | 30/30                           | 1.13 h |
| neutral_neutral  | 30/30            | 1.24 h | 30/30                           | 0.89 h |
| gut_neutral      | 30/30            | 1.13 h | 30/30                           | 0.95 h |
| gut_gut          | 30/30            | 1.26 h | 30/30                           | 1.18 h |
| Total            | 180              | 7.49 h | 180                             | 6.27 h |

Ø Dauer pro Konversation: Block B ~2.5 Min., Block C ~2.1 Min.
Zeitraum: Block B 31.10.2026, 00:09–07:38; Block C 31.10.2026, 10:57–17:15.

2. Setup

- Rechner: VPC (vpc69), vGPU GRID RTX8000-4Q (4 GB); Modell läuft teilweise auf der CPU (laut VPC-Check 66 % CPU / 34 % GPU)
- Ollama 0.40.13, über alle Zellen unverändert (vom Runner vor jeder Zelle geprüft)
- Modell-IDs (ollama list, auf der VPC), über alle Zellen unverändert:
  qwen3:8b = 500a1f067a9f; qwen3-8b-abl-harmonized = 2e3e7e43d97d
  (Auf PC1020 hat das harmonisierte Modell die ID 45be472ba598; Gewichte laut Hash identisch, siehe VPC-Check.)
- Python 3.12.10 (venv)
- Code: Commit c17d631 "Qwen-Skripte alle Bedingungen, GPT-4o-Version fixiert, Runner" (30.10.2026),
  dazu 5 nicht committete Änderungen zum Startzeitpunkt (laut runner_log; mit git status prüfen)
- Steuerung: run_alle_qwen.py (zuerst alle 6 Bedingungen Block B, dann Block C)
- Parameter (beide Modelle identisch): think=False, temperature 0.7, top_p 0.8, top_k 20, repeat_penalty 1.0,
  seed = 1000·Lauf + 1 (Agent_A) / + 2 (Agent_B), num_ctx 4096, max_tokens 1024, 10 Runden, N=30
- Ablage: ergebnisse/studie_HS26/B_qwen3_<bedingung>/ und C_qwen3abl_<bedingung>/, Protokoll runner_log.txt

3. Abbrüche und Neustarts

| Zeitpunkt         | Zelle            | Ergebnis                                         | Massnahme                          |
|-------------------|------------------|--------------------------------------------------|------------------------------------|
| 30.10., 23:48     | B boese_boese    | Abbruch nach 5 Min., Rückgabecode 1, 0 CSVs      | Neustart 31.10., 00:09 – erfolgreich |
| 31.10., 07:38     | C boese_boese    | Abbruch nach 5 Min., Rückgabecode 1, 0 CSVs      | Neustart 31.10., 10:57 – erfolgreich |

Beide Abbrüche passierten jeweils beim ersten Lauf eines Modells, nach fast genau 5 Minuten, bevor eine
Konversation gespeichert war. Es gibt daher keine unvollständigen oder doppelten Daten. Die Fehlermeldung wurde
nicht gesichert. Vermutete Ursache: Das erste Laden des Modells auf der VPC dauert länger als die Ladezeit, die
Ollama standardmässig zulässt (5 Min.). Beim zweiten Versuch war das Modell bereits im Speicher.

4. Qualitätsprüfung

Vorprüfung durch Claude (Cowork) für die Zellen B boese_boese, B gut_boese und B gut_gut (90 Konversationen):

| Prüfpunkt                                   | Ergebnis                                   |
|---------------------------------------------|--------------------------------------------|
| Zeilen/Runden/Sprecherwechsel, Lauf_Nr 1–30 | vollständig, keine Duplikate               |
| Modell, Bedingung pro Agent, Seeds          | korrekt                                    |
| Thinking (Think, Thinking_Chars, "<think")  | Think=False, 0 Thinking-Zeichen, 0 Tags    |
| Leere Nachrichten / JSON-Reste              | 0 / 0                                      |
| Done_Reason                                 | 810× stop, 0× length (kein Abschneiden)    |
| Max. Prompt_Tokens                          | 1'793 (Kontext 4096 → kein Kürzen des Verlaufs) |
| Max. Output_Tokens                          | 232 (Limit 1024)                           |
| Tokens/s                                    | 10.6–11.1                                  |

Vollständige Prüfung aller 360 Konversationen: qa_studie.py → ergebnisse/studie_HS26/qa_bericht.txt (offen, siehe 8.)

5. Bekannte Abweichungen (für die Methodik)

a) Böse-Prompt in den böse–böse-Skripten: Der Prompt hat 822 statt 824 Zeichen. Es fehlen zwei Leerzeichen am
   Zeilenende; der Wortlaut ist identisch. Betrifft B boese_boese und C boese_boese. In allen anderen Zellen und
   bei GPT-4o hat der böse-Prompt 824 Zeichen. Der Thinking-Datensatz vom 23./24.10.2026 verwendet ebenfalls 822.
b) Spalte Modell_Version: enthält das Ende des Digests (z. B. e4ca4b2b8b41), nicht die Ollama-ID.
   Massgeblich sind die IDs unter 2. (aus runner_log.txt).
c) Laufzeiten: Gemessen auf der VPC (teilweise GPU). Nicht mit den Benchmarks auf PC1020 (nur CPU) vergleichbar.
d) Präregistrierung: Ob eine Präregistrierung nötig ist, ist noch nicht mit Stephan Vonschallen geklärt. Falls ja,
   wurde Block B/C vor der Präregistrierung erhoben und ist als Pilot zu werten.

6. Thinking-Datensatz

Der Datensatz mit Thinking (ergebnisse/HS 26/dataset_boese_boese_qwen, 30 Konversationen, 23./24.10.2026) bleibt
getrennt. Er dient der Sensitivitätsanalyse Thinking an/aus für qwen3:8b böse–böse.

7. Block A (GPT-4o) – noch offen

Start erst nach Rücksetzung des API-Kontingents (01.11.2026). Modellversion in den Skripten fest:
gpt-4o-2024-08-06 (Commit c17d631). OpenAI schaltet diese Version am 14.01.2027 ab.

8. Nächste Schritte

- [ ] python qa_studie.py ausführen, qa_bericht.txt prüfen und hier ergänzen
- [ ] git status prüfen; Ergebnisse, runner_log.txt und qa_studie.py committen
- [ ] Vor Block A: Testaufruf gpt-4o-2024-08-06 (gibt die API diese Version zurück?)
- [ ] Vor Block A entscheiden: GPT-4o-Skripte noch mit Seed, Messwerten und Ablage unter
      ergebnisse/studie_HS26/A_gpt4o_<bedingung> ergänzen – oder bewusst im bisherigen Format laufen lassen
- [ ] Präregistrierung mit Stephan Vonschallen klären

---
