"""
qa_studie.py – Qualitätsprüfung aller Studien-CSVs in ergebnisse/studie_HS26/.

Prüft pro Zelle (Ordner) und pro Konversation:
- Anzahl Konversationen, Lauf_Nr 1..N vollständig, keine Duplikate
- 10 Zeilen pro Konversation, Runden 1..10, Sprecher abwechselnd A/B
- Modell, Bedingung pro Agent, Seeds (1000*Lauf + 1/2)
- Thinking: Think=False, Thinking_Chars=0, kein "<think" im Text (nur Ollama)
- leere Nachrichten, Done_Reason (stop / length / anderes), JSON-Reste im Text
- System-Prompt pro Agent konstant innerhalb der Zelle
- Max. Prompt_Tokens (Kontext 4096) und Output_Tokens (max_tokens 1024)
- Laufzeit und Tokens/s
- Determinismus: gleiche Seeds + gleicher Prompt -> gleiche erste Antwort?

Starten (im Repo-Ordner, venv aktiv):  python qa_studie.py
Ergebnis: Konsole + ergebnisse/studie_HS26/qa_bericht.txt
Liest nur, verändert keine Daten.

Erstellt mit Claude (Cowork), 31.10.2026.
"""

import csv
import statistics as st
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

BASIS = Path(__file__).resolve().parent
ZIEL = BASIS / "ergebnisse" / "studie_HS26"
BERICHT = ZIEL / "qa_bericht.txt"

MODELL_ERWARTET = {"B_qwen3": "qwen3:8b", "C_qwen3abl": "qwen3-8b-abl-harmonized"}
N_SOLL, RUNDEN, CTX, MAX_TOK = 30, 10, 4096, 1024

zeilen_out: list[str] = []


def out(text: str = "") -> None:
    print(text)
    zeilen_out.append(text)


def zahl(x: str) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def lese(pfad: Path) -> list[dict[str, str]]:
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def pruefe_zelle(ordner: Path) -> tuple[dict, dict[int, str]]:
    praefix = next((p for p in MODELL_ERWARTET if ordner.name.startswith(p + "_")), None)
    bed = ordner.name[len(praefix) + 1 :] if praefix else ordner.name
    teile = bed.split("_")
    bed_a, bed_b = (teile[0], teile[1]) if len(teile) == 2 else ("?", "?")
    modell_soll = MODELL_ERWARTET.get(praefix or "", "?")

    fehler: list[str] = []
    dateien = sorted(ordner.glob("lauf_*.csv"))
    laeufe: list[int] = []
    erste_antwort: dict[int, str] = {}
    prompts: dict[str, set[str]] = {"Agent_A": set(), "Agent_B": set()}
    c = Counter()
    dauer, tok_out, eval_s, prompt_max, out_max = [], 0.0, 0.0, 0, 0

    for d in dateien:
        rows = lese(d)
        if not rows:
            fehler.append(f"{d.name}: leer")
            continue
        lauf = int(rows[0]["Lauf_Nr"])
        laeufe.append(lauf)
        if len(rows) != RUNDEN:
            fehler.append(f"{d.name}: {len(rows)} statt {RUNDEN} Zeilen")
        if [int(r["Runde"]) for r in rows] != list(range(1, len(rows) + 1)):
            fehler.append(f"{d.name}: Runden nicht 1..{len(rows)}")
        for i, r in enumerate(rows):
            sp = r["Sprecher"]
            if sp != ("Agent_A" if i % 2 == 0 else "Agent_B"):
                fehler.append(f"{d.name} R{i + 1}: Sprecher {sp}")
            if r["Modell"] != modell_soll:
                c["falsches_modell"] += 1
            if r["Bedingung"] != (bed_a if sp == "Agent_A" else bed_b):
                c["falsche_bedingung"] += 1
            if r.get("Seed") and int(r["Seed"]) != 1000 * lauf + (1 if sp == "Agent_A" else 2):
                c["falscher_seed"] += 1
            prompts.setdefault(sp, set()).add(r["System_Prompt"])
            text = r["Nachricht"]
            if i == 0:
                continue  # Runde 1 = feste Anfangsnachricht
            if r["Provider"] == "ollama":
                if r.get("Think") != "False":
                    c["think_nicht_false"] += 1
                if r.get("Thinking_Chars") not in ("", "0"):
                    c["thinking_chars"] += 1
            if "<think" in text:
                c["think_tag"] += 1
            if not text.strip():
                c["leer"] += 1
            if text.lstrip().startswith("{") or '"message"' in text:
                c["json_rest"] += 1
            c["done_" + (r.get("Done_Reason") or "leer")] += 1
            pt, ot, ev = zahl(r.get("Prompt_Tokens")), zahl(r.get("Output_Tokens")), zahl(r.get("Eval_s"))
            if pt:
                prompt_max = max(prompt_max, int(pt))
            if ot:
                out_max = max(out_max, int(ot))
                tok_out += ot
            if ev:
                eval_s += ev
            if i == 1:
                erste_antwort[lauf] = text
        ld = zahl(rows[0].get("Lauf_Dauer_s"))
        if ld:
            dauer.append(ld)

    fehlend = sorted(set(range(1, N_SOLL + 1)) - set(laeufe))
    doppelt = sorted(k for k, v in Counter(laeufe).items() if v > 1)
    if fehlend:
        fehler.append(f"Lauf_Nr fehlen: {fehlend}")
    if doppelt:
        fehler.append(f"Lauf_Nr doppelt: {doppelt}")
    for sp, s in prompts.items():
        if len(s) > 1:
            fehler.append(f"System_Prompt {sp} nicht konstant ({len(s)} Varianten)")

    res = {
        "zelle": ordner.name,
        "n": len(dateien),
        "fehler": fehler,
        "c": c,
        "dauer_min": st.mean(dauer) / 60 if dauer else None,
        "tok_s": tok_out / eval_s if eval_s else None,
        "prompt_max": prompt_max,
        "out_max": out_max,
        "prompt_len": {sp: len(next(iter(s))) for sp, s in prompts.items() if len(s) == 1},
        "unik": len(set(erste_antwort.values())),
        "modell": modell_soll,
        "bed_b": bed_b,
        "praefix": praefix,
    }
    return res, erste_antwort


def main() -> None:
    if not ZIEL.exists():
        sys.exit(f"Ordner fehlt: {ZIEL}")
    zellen = sorted(p for p in ZIEL.iterdir() if p.is_dir())
    out(f"QA-Bericht studie_HS26 – {datetime.now():%d.%m.%Y %H:%M}")
    out("=" * 100)
    out(f"{'Zelle':<28}{'N':>4}{'Ø Min':>7}{'Tok/s':>7}{'MaxPrompt':>10}{'MaxOut':>8}"
        f"{'stop':>6}{'length':>7}{'leer':>5}{'think':>6}{'JSON':>5}  Status")
    alle, antworten = [], {}
    for z in zellen:
        r, ea = pruefe_zelle(z)
        alle.append(r)
        antworten[z.name] = ea
        c = r["c"]
        think = c["think_nicht_false"] + c["thinking_chars"] + c["think_tag"]
        probleme = r["fehler"] + [f"{k}={v}" for k, v in c.items()
                                  if k in ("falsches_modell", "falsche_bedingung", "falscher_seed") and v]
        status = "OK" if not probleme and not think and not c["leer"] and not c["json_rest"] else "PRÜFEN"
        out(f"{r['zelle']:<28}{r['n']:>4}"
            f"{(r['dauer_min'] or 0):>7.1f}{(r['tok_s'] or 0):>7.1f}{r['prompt_max']:>10}{r['out_max']:>8}"
            f"{c['done_stop']:>6}{c['done_length']:>7}{c['leer']:>5}{think:>6}{c['json_rest']:>5}  {status}")
        for p in probleme:
            out(f"    ! {p}")

    out()
    out("System-Prompt-Längen (Zeichen) pro Zelle:")
    for r in alle:
        out(f"  {r['zelle']:<28} A={r['prompt_len'].get('Agent_A')}  B={r['prompt_len'].get('Agent_B')}")

    out()
    out("Determinismus: gleiche erste Antwort von Agent_B bei gleichem Modell, gleicher Bedingung von B und gleichem Seed")
    gruppen: dict[tuple, list[dict]] = {}
    for r in alle:
        gruppen.setdefault((r["praefix"], r["bed_b"]), []).append(r)
    for (praefix, bed_b), rs in gruppen.items():
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = antworten[rs[i]["zelle"]], antworten[rs[j]["zelle"]]
                gemeinsam = sorted(set(a) & set(b))
                gleich = sum(a[k] == b[k] for k in gemeinsam)
                pa, pb = rs[i]["prompt_len"].get("Agent_B"), rs[j]["prompt_len"].get("Agent_B")
                hinweis = "" if pa == pb else f"  (Prompt B unterschiedlich: {pa} vs {pb} Zeichen)"
                out(f"  {rs[i]['zelle']} vs {rs[j]['zelle']}: {gleich}/{len(gemeinsam)} identisch{hinweis}")

    out()
    gesamt = sum(r["n"] for r in alle)
    ok = all(not r["fehler"] for r in alle)
    out(f"Total: {gesamt} Konversationen in {len(alle)} Zellen. Strukturfehler: {'keine' if ok else 'siehe oben'}")
    BERICHT.write_text("\n".join(zeilen_out) + "\n", encoding="utf-8")
    print(f"\nGespeichert: {BERICHT}")


if __name__ == "__main__":
    main()
