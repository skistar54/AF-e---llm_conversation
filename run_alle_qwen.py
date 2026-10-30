"""
run_alle_qwen.py – Startet alle lokalen Qwen-Zellen nacheinander (Block B und C).

Reihenfolge: zuerst alle 6 Bedingungen mit qwen3:8b (Block B),
danach alle 6 mit qwen3-8b-abl-harmonized (Block C). Pro Zelle N Konversationen.

Sicherheitsregeln:
- Zelle mit bereits N CSV-Dateien wird übersprungen  -> Neustart nach Abbruch ist sicher.
- Zelle mit 1 bis N-1 CSV-Dateien: Runner startet nicht (die Skripte können nicht fortsetzen).
- Ollama-Version oder Modell-ID ändert sich während der Läufe: Runner stoppt.
- Skript endet mit Fehler oder liefert weniger als N CSV-Dateien: Runner stoppt.
- Protokoll: ergebnisse/studie_HS26/runner_log.txt

Starten (im Repo-Ordner, venv aktiv):
  python run_alle_qwen.py                 alle 12 Zellen (B, dann C)
  python run_alle_qwen.py --modell qwen   nur Block B (qwen3:8b)
  python run_alle_qwen.py --modell abl    nur Block C (qwen3-8b-abl-harmonized)
  python run_alle_qwen.py --plan          nur anzeigen, nichts starten

Erstellt mit Claude (Cowork), 31.10.2026.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASIS = Path(__file__).resolve().parent
ZIEL = BASIS / "ergebnisse" / "studie_HS26"
LOG = ZIEL / "runner_log.txt"

BEDINGUNGEN = ["boese_boese", "neutral_boese", "gut_boese", "neutral_neutral", "gut_neutral", "gut_gut"]

MODELLE = {
    "qwen": {"block": "B", "ordner": "B_qwen3", "suffix": "_qwen", "ollama": "qwen3:8b"},
    "abl": {"block": "C", "ordner": "C_qwen3abl", "suffix": "_qwen_abliterated", "ollama": "qwen3-8b-abl-harmonized"},
}


def log(text: str) -> None:
    zeile = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {text}"
    print(zeile, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(zeile + "\n")


def befehl(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=BASIS)
    except FileNotFoundError:
        return None
    return (r.stdout + r.stderr).strip()


def ollama_version() -> str | None:
    out = befehl(["ollama", "-v"])
    if out is None or "could not connect" in out.lower():
        return None
    return " | ".join(z.strip() for z in out.splitlines() if "version" in z.lower())


def modell_ids() -> dict[str, str]:
    out = befehl(["ollama", "list"]) or ""
    ids: dict[str, str] = {}
    for zeile in out.splitlines()[1:]:
        teile = zeile.split()
        if len(teile) >= 2:
            name = teile[0].removesuffix(":latest")
            ids[name] = teile[1]
    return ids


def git_info() -> str:
    h = befehl(["git", "rev-parse", "--short", "HEAD"])
    if not h or "fatal" in h:
        return "unbekannt (git nicht verfügbar)"
    status = befehl(["git", "status", "--porcelain"])
    if status is None:
        return h
    n = len([z for z in status.splitlines() if z.strip()])
    return f"{h} ({'sauber' if n == 0 else f'{n} nicht committete Änderungen'})"


def csv_anzahl(ordner: Path) -> int:
    return len(list(ordner.glob("lauf_*.csv"))) if ordner.exists() else 0


def wach_halten() -> None:
    """Verhindert unter Windows den Standby, solange der Runner läuft."""
    if os.name == "nt":
        try:
            import ctypes

            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)  # pyright: ignore
        except Exception:
            pass


def stopp(text: str) -> None:
    log(f"STOPP: {text}")
    log("Nichts wurde gelöscht. Bitte Claude Bescheid geben.")
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Alle lokalen Qwen-Zellen nacheinander starten")
    parser.add_argument("--modell", choices=["qwen", "abl", "beide"], default="beide")
    parser.add_argument("--n", type=int, default=30, help="Konversationen pro Zelle (Standard 30)")
    parser.add_argument("--plan", action="store_true", help="nur anzeigen, nichts starten")
    args = parser.parse_args()
    n_soll = args.n
    schluessel = ["qwen", "abl"] if args.modell == "beide" else [args.modell]

    ZIEL.mkdir(parents=True, exist_ok=True)

    # Plan aufstellen und prüfen
    plan = []
    for key in schluessel:
        m = MODELLE[key]
        for bed in BEDINGUNGEN:
            skript = BASIS / f"dataset_{bed}{m['suffix']}.py"
            ordner = ZIEL / f"{m['ordner']}_{bed}"
            plan.append((key, bed, skript, ordner))

    print(f"\nPlan ({len(plan)} Zellen, je {n_soll} Konversationen):")
    unvollstaendig, fehlend = [], []
    for key, bed, skript, ordner in plan:
        n = csv_anzahl(ordner)
        if not skript.exists():
            status = "SKRIPT FEHLT"
            fehlend.append(skript.name)
        elif n >= n_soll:
            status = f"fertig ({n}) – wird übersprungen"
        elif n == 0:
            status = "offen"
        else:
            status = f"UNVOLLSTÄNDIG ({n}/{n_soll})"
            unvollstaendig.append(ordner.name)
        print(f"  Block {MODELLE[key]['block']}  {bed:<16} {skript.name:<45} {status}")
    print()

    if args.plan:
        return
    if fehlend:
        stopp(f"Skripte fehlen: {', '.join(fehlend)}")
    if unvollstaendig:
        stopp(f"Unvollständige Zellen: {', '.join(unvollstaendig)}. Die Skripte können nicht fortsetzen.")

    version0 = ollama_version()
    if version0 is None:
        stopp("Ollama läuft nicht oder ist nicht erreichbar. Ollama starten und neu versuchen.")
    ids0 = modell_ids()
    for key in schluessel:
        name = MODELLE[key]["ollama"]
        if name not in ids0:
            stopp(f"Modell {name} nicht in 'ollama list' gefunden.")

    log("=" * 70)
    log("START run_alle_qwen.py")
    log(f"Git: {git_info()}")
    log(f"Python: {sys.version.split()[0]}  ({sys.executable})")
    log(f"Ollama: {version0}")
    for key in schluessel:
        name = MODELLE[key]["ollama"]
        log(f"Modell {name}: ID {ids0[name]}")
    log(f"N pro Zelle: {n_soll}")

    wach_halten()
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")

    try:
        for key, bed, skript, ordner in plan:
            m = MODELLE[key]
            if csv_anzahl(ordner) >= n_soll:
                log(f"Block {m['block']} {bed}: bereits fertig – übersprungen")
                continue

            v = ollama_version()
            if v != version0:
                stopp(f"Ollama-Version hat sich geändert: vorher '{version0}', jetzt '{v}'")
            id_jetzt = modell_ids().get(m["ollama"])
            if id_jetzt != ids0[m["ollama"]]:
                stopp(f"Modell-ID von {m['ollama']} hat sich geändert: {ids0[m['ollama']]} -> {id_jetzt}")

            log(f"Block {m['block']} {bed}: START {skript.name} -> {ordner.relative_to(BASIS)}")
            t0 = time.time()
            r = subprocess.run(
                [sys.executable, str(skript), "--n", str(n_soll), "--out", str(ordner)],
                cwd=BASIS,
                env=env,
            )
            dauer = (time.time() - t0) / 3600
            n = csv_anzahl(ordner)
            log(f"Block {m['block']} {bed}: ENDE Rückgabecode {r.returncode}, {n}/{n_soll} CSVs, {dauer:.2f} h")
            if r.returncode != 0 or n < n_soll:
                stopp(f"Zelle Block {m['block']} {bed} nicht vollständig ({n}/{n_soll}).")
    except KeyboardInterrupt:
        stopp("Abbruch mit Ctrl+C.")

    log("FERTIG – alle geplanten Zellen vollständig.")


if __name__ == "__main__":
    main()
