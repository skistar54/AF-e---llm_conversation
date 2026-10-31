# VPC Setup-Check

- **Datum:** 2026-10-30, 22:01–22:20
- **Hostname:** VPC69
- **Referenz:** PC1020 (`models/MANIFEST.md`, `models/manifest_raw/ollama_list.txt`)
- **Ergebnis:** 13 ✓ / 6 ✗

## 1. Repo

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 1.1 | `git remote -v` | ✓ | origin = https://github.com/skistar54/AF-e---llm_conversation.git (fetch/push) |
| 1.2 | `git log -1 --oneline` | ✓ | `33910ce benchmark testing`: weicht von PC1020 (c37169b) ab, ist aber der direkte Nachfolger-Commit, also neuer. Nur notiert. |
| 1.3 | `git status --short` | ✓ | Zu Beginn sauber. Durch diesen Check neu und untracked: `models/VPC_CHECK.md`, `models/manifest_raw/vpc_harmonized.modelfile.txt` |

Hinweis: Laut Auftrag sollte hier noch kein MANIFEST existieren. `models/MANIFEST.md` und `models/manifest_raw/` sind aber bereits vorhanden, sie kamen mit Commit 33910ce.

## 2. Python und venv

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 2.1 | `py -3.12 --version` | ✓ | Python 3.12.10 |
| 2.2 | venv `sys.prefix` / `sys.version` | ✓ | `C:\Users\glan\AF-e---llm_conversation\venv`, 3.12.10 (64 bit) |
| 2.3 | `pip show llm-conversation ollama openai python-dotenv` | ✗ | `WARNING: Package(s) not found: llm-conversation, ollama, openai, python-dotenv`. Die venv enthält nur `pip 25.0.1`. |
| 2.4 | Import-Test | ✗ | `ModuleNotFoundError: No module named 'llm_conversation'` |

## 3. .env

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 3.1 | `.env` mit `OPENAI_API_KEY` | ✗ | `.env` existiert nicht, der Key fehlt daher. |
| 3.2 | `git check-ignore -v .env venv` | ✓ | `.gitignore:8:.env` und `.gitignore:9:venv/`: beides ignoriert |

## 4. Ollama

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 4.1 | `ollama --version` | ✗ | Zu Beginn 0.40.12. Während des Checks lief ein **Ollama-Auto-Update** (OllamaSetup, 22:01:33–22:03:04), seither **0.40.13**. Referenz PC1020: 0.40.11. |
| 4.2a | qwen3:8b | ✓ | 500a1f067a9f |
| 4.2b | richardyoung/qwen3-8b-abliterated:Q4_K_M | ✓ | 6d7230a92342 |
| 4.2c | qwen3-8b-abl-harmonized:latest | — | Fehlte, siehe Punkt 5 |

## 5. Harmonisiertes Modell

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 5.1 | `ollama create qwen3-8b-abl-harmonized -f models\Modelfile.qwen3-8b-abl-harmonized` | ✓ | `success` (unter Ollama 0.40.12) |
| 5.2 | ID = 45be472ba598 | ✗ | **2e3e7e43d97d**. Nichts korrigiert. |

- Gespeichert: `models/manifest_raw/vpc_harmonized.modelfile.txt`
- FROM-Zeile: `FROM C:\Users\glan\.ollama\models\blobs\sha256-d3d1f4bba1791055f8906f95aa63fc80d03ddde9ae2ef8a78f46654892a8720b`
- Vergleich mit `models/manifest_raw/qwen3-8b-abl-harmonized.modelfile.txt` (PC1020): gleiche FROM-Zeile. Ohne FROM- und Kommentarzeilen gibt es keine Unterschiede (Template, Parameter, System identisch).
- Die Gewichte sind identisch, siehe 7.2. Die abweichende ID betrifft also nur das Manifest. Vermutete Ursache: unterschiedliche Ollama-Version beim `create`, also andere Serialisierung von Config- oder Parameter-Layern. Das ist nicht verifiziert.

## 6. Modelltest und GPU

| # | Prüfung | Status | Ist |
|---|---------|--------|-----|
| 6.1 | `ollama run qwen3:8b "Antworte mit einem Wort: Hallo"` | ✓ | Antwort `Hello` (nach Thinking). Laufzeit **über 5 Minuten**. |
| 6.2 | `ollama ps` PROCESSOR | ✗ | **66%/34% CPU/GPU**, Grösse 6.0 GB, Context 4096. Laut Server-Log nur `offloaded 11/37 layers to GPU`. |
| 6.3 | `nvidia-smi` | ✓ | **GRID RTX8000-4Q**, **4096 MiB** gesamt (vGPU-Profil 4Q), Treiber 553.74, unter Last 3348 MiB belegt |

## 7. Blob-Hashes (SHA256)

| # | Blob | Status | Ist |
|---|------|--------|-----|
| 7.1 | qwen3:8b `sha256-a3de86cd…e686f` | ✓ | MATCH |
| 7.2 | abliteriert `sha256-d3d1f4bb…a8720b` | ✓ | MATCH |

## Offen

1. **venv leer:** `venv\Scripts\python.exe -m pip install -e .` ausführen, danach muss 2.3 und 2.4 erneut geprüft werden. Fall `python-dotenv` nicht als Abhängigkeit in `pyproject.toml` steht, separat installieren.
2. **`.env` fehlt:** `.env` mit `OPENAI_API_KEY=…` im Repo-Root anlegen. Das ist nur für die OpenAI-Skripte nötig.
3. **GPU zu klein (kritisch):** Die vGPU hat 4 GB. qwen3:8b (ca. 6 GB inkl. KV-Cache) läuft deshalb zu 66 % auf der CPU, und schon ein Ein-Wort-Prompt dauert über 5 Minuten. Die Laufzeit- und Dauer-Metriken sind damit nicht mit PC1020 vergleichbar, und vollständige Datasets sind praktisch nicht durchführbar. Zu klären ist, ob ein grösseres vGPU-Profil (mindestens 8Q, besser 16Q) möglich ist.
4. **Ollama-Version und Auto-Update:** Ollama hat sich während des Checks selbst auf 0.40.13 aktualisiert, die Referenz ist 0.40.11. Damit sich die Version nicht mitten in einem Experiment ändert, sollte das Auto-Update deaktiviert werden. Zu entscheiden ist auch, ob die Version auf 0.40.11 gepinnt wird.
5. **Harmonisiertes Modell, ID-Abweichung:** Modelfile und Gewichte sind identisch, nur die Manifest-ID unterscheidet sich (2e3e7e43d97d statt 45be472ba598). Zu entscheiden ist, ob das für die Reproduzierbarkeit genügt. Ein Test wäre, auf PC1020 mit 0.40.12 neu zu erstellen und die IDs zu vergleichen. Die Entscheidung gehört in MANIFEST bzw. Logbuch.
6. **MANIFEST:** `models/MANIFEST.md` existiert hier bereits (Commit 33910ce), entgegen der Annahme im Auftrag.
