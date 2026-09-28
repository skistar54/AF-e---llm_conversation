# 📋 PROMPT FÜR CLAUDE CODE – Herbstsemester Audit & Planning (v2)

Kopiere den gesamten Text NACH dieser Linie in Claude Code:

---

## 🎯 PROJEKTKONTEXT

Ich bin im 2. Semester eines Forschungsprojekts (MSc ZHAW) über Generative Multi-Agenten-Systeme. Der Code simuliert Konversationen zwischen zwei LLM-Agenten unter verschiedenen Bedingungen (kooperativ/neutral/adversarial).

**Aktueller Stand (Frühjahrssemester):**
- ✅ 6 Dataset-Skripte live: `dataset_gut_gut.py`, `dataset_neutral_neutral.py`, `dataset_boese_boese.py`, `dataset_gut_neutral.py`, `dataset_gut_boese.py`, `dataset_neutral_boese.py`
- ✅ Jedes Skript: 10 Konversationen × 10 Runden = 100 Turns pro Kondition
- ✅ Modell: gpt-4o (OpenAI API), Fallback Ollama lokal möglich
- ✅ CSV-Output mit Bedingung, Sprecher, System-Prompt, Nachricht, etc.
- ✅ Ergebnisse in `ergebnisse/<dataset_name>/` organisiert
- ⚠️ Bisher **~600 Turns gesamt** (6 Konditionen × 10 Konversationen × 10 Runden)

**Architektur:**
- `src/llm_conversation/`: Core Package (AIAgent, ConversationManager)
- AIAgent: Unterstützt `provider="openai"` oder `provider="ollama"`
- ConversationManager: Erweitert Prompts intern – **kritisch:** Originalwerte BEFORE ConversationManager creation speichern!

---

## 🎓 HERBSTSEMESTER: ZWEI STOSSPRICHTUNGEN

### 🔹 Stoßrichtung 1: **Mehr Daten – mehr Power**
- **Ziel:** Datenbasis **verdreifachen** auf **1.800 Turns** (statt 600)
- **Wie?** Jeden Dataset-Skript von 10 auf 30 Konversationen erhöhen (10 Runden bleiben konstant)
- **Effekt:** Statistisches Rauschen reduzieren, Signifikanzen präziser nachweisen
- **Fragen für die KI:**
  - Wo im Code müssen wir `N_KONVERSATIONEN` von 10 auf 30 erhöhen?
  - Brauchen wir eine Progress-Bar oder Logging-Optimierung für längere Läufe?
  - Sollten wir Checkpointing implementieren (falls ein Lauf unterbrochen wird)?

### 🔹 Stoßrichtung 2: **Gefiltert vs. Ungefiltert – Modell-Vergleich**
- **Ziel:** Safety-Training-Effekt messen
  - GPT-4o: Strong Safety-Training (aktuell)
  - OLLaMA 3 lokal: Ungefiltert, mehr Freiheit
- **Wie?** Parallele Dataset-Skripte mit `provider="ollama"`
- **Effekt:** Sehen, wie viel „Safety-Drift" GPT-4o in adversarial Conditions zeigt
- **Fragen für die KI:**
  - Sollten wir neue `dataset_*_ollama.py` Skripte erstellen oder bestehende mit Parameter-Varianten erweitern?
  - Wie stellen wir sicher, dass Ollama und OpenAI-Läufe vergleichbar sind (gleiche Prompts, Temperature, etc.)?
  - Brauchen wir ein separates Output-Directory für Ollama-Ergebnisse?

---

## 🔍 AUDIT-AUFGABE (für dich, KI)

**Bitte schau dir die Repo-Struktur an und antworte konkret auf:**

### Phase 1: Status-Überblick
1. **Wie viele Ergebnisse existieren derzeit?** (Zähle CSV-Dateien in `ergebnisse/`)
2. **Alle 6 Dataset-Skripte lauffähig?** Oder gibt es ungelöste Bugs?
3. **Welche Dependencies sind installt?** (Check `pyproject.toml` + `.env`)
4. **Wo ist der API-Key gespeichert?** (`.env` existiert?)

### Phase 2: Code-Struktur Check
1. **AIAgent-Klasse:** Unterstützt beide Provider (OpenAI + Ollama) korrekt?
2. **CSV-Output:** Ist das `original_prompts` Pattern korrekt implementiert in allen 6 Skripten?
3. **Temperature & Modell:** Sind alle konsistent konfiguriert?
4. **Gibt es Tech-Debt?** (TODO-Kommentare, Hardcodes, etc.?)

### Phase 3: Blocker für Herbstsemester
1. **Für Stoßrichtung 1 (Daten 3x):** Was muss angepasst werden? Reicht `N_KONVERSATIONEN = 30` oder braucht es mehr?
2. **Für Stoßrichtung 2 (Ollama vs. OpenAI):** Können wir einfach `provider="ollama"` setzen oder brauchen neue Skripte?

### Phase 4: Konkrete Roadmap
Bitte gib mir eine **Checkliste** in dieser Form:

```
🟢 ERLEDIGT (Semester 1):
  - [x] Dataset-Skripte gebaut
  - [x] OpenAI-Integration
  - ...

🟡 OFFEN (Herbstsemester):
  1. [ ] Daten verdreifachen (N_KONVERSATIONEN = 30)
     - Welche Dateien: ...
     - Estimated Runtime: ...
  2. [ ] Ollama-Varianten erstellen
     - Neue Skripte: dataset_*_ollama.py
     - Config-Anpassungen: ...
  3. [ ] Testing & Validation
     - Ein Test-Lauf pro Kombination
     - Resultat-Vergleich (Ollama vs. OpenAI)
     - ...

🔴 BLOCKERS / OFFENE FRAGEN:
  - Ollama lokal installiert und laufend?
  - Runtime-Budget: Wie lange brauchen 1.800 Turns insgesamt?
```

---

## 📦 WAS ICH BRAUCHE VON DIR (KI)

1. **Kurzer Status:** 3–5 Sätze: Wo steht der Code? Was funktioniert, was nicht?
2. **Pro Stoßrichtung:** Konkrete Code-Änderungen (Dateien, Zeilen, Pseudocode)
3. **Reihenfolge:** Was sollte ich in welcher Reihenfolge tun?
4. **Testen:** Wie teste ich, ob die Änderungen funktionieren? (1–2 Testläufe)
5. **Risks:** Welche Pitfalls gibt es?

---

## 🎬 LOS GEHT'S

Schau dir den Code an und gib mir dann den **AUDIT-REPORT** zurück. Danach planen wir die konkrete Umsetzung.

---

**Ende der Prompt – kopiere ALLES ab "## 🎯 PROJEKTKONTEXT" für Claude Code**
