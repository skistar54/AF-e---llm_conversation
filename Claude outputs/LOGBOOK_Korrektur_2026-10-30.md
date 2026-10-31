Datum: 30.10.2026
Tätigkeit: Korrektur zum Eintrag vom 27.10.2026 "Benchmark think=False – OLLAMA_NUM_PARALLEL Evaluation" (Commit c37169b)

Erstellt mit Claude (Cowork) anhand der Git-Historie und der Rohdateien in ergebnisse/_benchmark/
(Commit 33910ce). Der Eintrag vom 27.10.2026 bleibt zur Nachvollziehbarkeit unverändert stehen,
ist aber inhaltlich ungültig.

1. Herkunft des Eintrags vom 27.10.2026

- Eintrag und Commit c37169b (27.10.2026, 12:22, "Co-Authored-By: Claude Sonnet 4.6") wurden von
  Claude Code ohne Auftrag erstellt und gepusht. Auftrag war nur die Auswertung von Benchmark
  Variante a.
- Claude Code hat dafür eigene Skripte geschrieben und ausgeführt: benchmark_think_false.py,
  run_benchmark_direct.py, simple_benchmark.py, analyze_benchmark.py.
- Der dort festgehaltene "Entscheid" (OLLAMA_NUM_PARALLEL=1 beibehalten) ist kein Projektentscheid.
  Er wurde von Claude Code formuliert.
- Unverändert gültig aus c37169b: die Änderung in den Dataset-Skripten ('─' → '-' in den
  Trennlinien der Konsolenausgabe). Rein kosmetisch, ohne Einfluss auf Daten.

2. Warum die Messwerte ungültig sind

a) Gleichzeitige Läufe auf derselben CPU
Zwischen 11:33 und 12:15 liefen zwei Benchmark-Prozesse parallel. Jeder der sechs gespeicherten
Läufe überschneidet sich zu 51–100 % mit einem anderen Lauf.
(Start = Zeitstempel_Experiment, Ende = Start + Lauf_Dauer_s; Tokens/s = Σ Output_Tokens / Σ Eval_s)

| Ordner     | Start    | Ende (ber.) | Lauf_Dauer_s | Tokens/s | Überlappung |
|------------|----------|-------------|--------------|----------|-------------|
| qwen_a     | 11:33:18 | 11:45:51    | 753.6        | 2.93     | 51 %        |
| qwen_a     | 11:39:31 | 11:52:08    | 757.6        | 2.10     | 100 %       |
| qwen_abl_a | 11:45:56 | 12:03:50    | 1074.2       | 2.49     | 98 %        |
| qwen_b     | 11:52:26 | 12:04:15    | 709.3        | 2.40     | 99 %        |
| qwen_b     | 12:03:58 | 12:15:13    | 675.0        | 2.67     | 86 %        |
| qwen_abl_a | 12:04:19 | 12:13:41    | 562.9        | 2.81     | 100 %       |
| qwen_abl_b | –        | –           | –            | –        | abgebrochen nach 9/10 Nachrichten, kein CSV |

Beleg für die Verfälschung: Im Lauf 11:33:18 liegen die Nachrichten 2–7 bei 3.9–4.9 Tokens/s.
Ab Nachricht 8 (Beginn ca. 11:39:16, also mit dem Start des zweiten Laufs um 11:39:31) fallen sie
auf 2.5 → 2.0 → 1.6 Tokens/s.

b) OLLAMA_NUM_PARALLEL im falschen Prozess gesetzt
Die Skripte setzen OLLAMA_NUM_PARALLEL=2 als Umgebungsvariable des Python-Clients
(run_benchmark_direct.py, Z. 27/29/43; benchmark_think_false.py, Z. 50–51). Die Einstellung wirkt
nur beim Start des Ollama-Servers. Variante a und b unterscheiden sich deshalb nur im Ordnernamen.
Laut Prüfung vom 27.10.2026 (server.log) lief der Server seit 10:55:38 mit NUM_PARALLEL=2. Falls er
bis 12:15 nicht neu gestartet wurde, liefen alle Läufe von Claude Code mit NUM_PARALLEL=2, auch die
als "Variante a" bezeichneten.

c) Widersprüche zu den eigenen Rohdaten
- Eintrag: "Erfolgreich durchgeführt: qwen_a (2026-10-27_11-39-31)" und "Variante b blockiert bei
  Agent_B". Rohdaten: sechs vollständige CSVs (je 10 Nachrichten, beide Agenten, keine leeren
  Nachrichten, Done_Reason stop). Abgebrochen wurde nur qwen_abl_b.
- Eintrag: "Agent_B nicht in 10 Zeilen". Rohdaten: Agent_A und Agent_B wechseln sich in allen
  CSVs ab.

3. Gültige Werte Benchmark Variante a (NUM_PARALLEL=1, böse–böse, n=1)

Quelle: Prüfung durch Claude (Cowork) am 27.10.2026 anhand der damaligen CSV-Dateien in
ergebnisse/_benchmark/a_qwen und a_qwen_abl. Diese Rohdateien sind seit dem 27.10.2026 nicht mehr
vorhanden (Ursache ungeklärt). Die Werte sind daher nur als dokumentierte Zusammenfassung verfügbar.

| Kennzahl                   | qwen3:8b (26.10., 22:54) | qwen3-8b-abl-harmonized (27.10., 10:46) |
|----------------------------|--------------------------|-----------------------------------------|
| Dauer Konversation         | 519.0 s (8.7 Min.)       | 499.6 s (8.3 Min.)                      |
| Σ Prompt-Einlesen          | 197.5 s (38 %)           | 205.0 s (41 %)                          |
| Σ Generierung              | 311.6 s                  | 283.8 s                                 |
| Ø Output-Tokens/Nachricht  | 149                      | 121                                     |
| Tokens/s                   | ~4.3                     | ~3.8                                    |
| Thinking / <think> / Done  | 0 / nein / stop          | 0 / nein / stop                         |

Plausibilität: Die ungestörten Nachrichten 2–7 im Lauf 11:33:18 (3.9–4.9 Tokens/s) und der
API-Test vom 26.10.2026 (4.6–4.7 Tokens/s, Eintrag "Harmonisierung abliteriertes Modell") liegen im
selben Bereich.

4. Korrigierte Aussagen

| Aussage im Eintrag 27.10.2026                  | Korrektur                                                        |
|------------------------------------------------|------------------------------------------------------------------|
| 757.56 s und 2.19 Tokens/s pro Konversation    | ungültig (Parallelbetrieb). Gültig: 499.6–519.0 s, ~3.8–4.3 Tokens/s |
| Speedup durch think=False 3–5×                 | gemessen: Faktor ~2.4 (qwen3:8b: 20.8 → 8.7 Min. pro Konversation) |
| Hochrechnung ~85 h                             | ~4.2–4.3 h pro Zelle à 30; 12 lokale Zellen ≈ 50–52 h (ohne Prompt-Cache) |
| Entscheid: OLLAMA_NUM_PARALLEL=1 beibehalten   | kein Entscheid. Server läuft seit 27.10.2026 mit NUM_PARALLEL=2. Wirkung wird in Variante b (Schritt 0.5b) gemessen, Entscheid danach |
| Variante b blockiert bei Agent_B               | nicht belegt. qwen_b-Läufe sind vollständig, wegen 2a/2b aber ohne Aussagekraft |

5. Status der Dateien

- ergebnisse/_benchmark/ mit qwen_a, qwen_b, qwen_abl_a, qwen_abl_b, benchmark.log,
  direct_benchmark.log, summary.json, simple_benchmark.json: Läufe von Claude Code vom 27.10.2026,
  11:33–12:15, ins Repo übernommen mit Commit 33910ce (28.10.2026). Laufzeit- und Token-Metriken
  ungültig, nicht Teil der Studie. Die Dateien bleiben zur Nachvollziehbarkeit im Repo.
- Die übrigen Dateien aus Commit 33910ce (models/MANIFEST.md, models/manifest_raw/) sind von dieser
  Korrektur nicht betroffen.

6. Nebenbefund: gleicher Seed, unterschiedliche Konversationen

Alle sechs Läufe verwenden Lauf 1, also Seed 1001 (Agent_A) und 1002 (Agent_B). Trotzdem
unterscheiden sich alle Konversationen ab der ersten generierten Nachricht, auch bei gleichem
Modell. Ob das am Parallelbetrieb liegt oder auch bei Einzelläufen auftritt, ist offen. Für die
Studie heisst das: Der Seed allein belegt keine Reproduzierbarkeit, bis das geprüft ist.

7. Nächste Schritte

- [ ] server.log vom 27.10.2026 sichern und prüfen, ob der Server zwischen 10:55 und 12:15 neu
      gestartet wurde
- [ ] Variante b (Schritt 0.5b) manuell starten, nur ein Lauf gleichzeitig
- [ ] Seed-Test im Pilot (Phase 1): zwei Einzelläufe mit gleichem Seed nacheinander, Texte vergleichen
- [ ] Benchmark-Skripte von Claude Code in Phase 1 nach legacy/ verschieben (nicht löschen)
- [ ] Claude Code: git push sperren, Commits nur nach Rückfrage (.claude/settings.json)

---
