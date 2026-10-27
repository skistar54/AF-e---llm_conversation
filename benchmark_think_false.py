"""
Benchmark-Auswertung: think=False Varianten und OLLAMA_NUM_PARALLEL Vergleich.

Durchführt:
1. Benchmark-Läufe: qwen.py und qwen_abliterated.py, je 2 Varianten
   - Variante a: Ollama-Standard
   - Variante b: OLLAMA_NUM_PARALLEL=2
2. Qualitätschecks pro Datei
3. Metriken berechnen und vergleichen
4. Hochrechnung für alle Zellen
5. Vergleich mit altem Lauf (mit Thinking)
"""

import csv
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Phase 1: Benchmark-Läufe durchführen
# ---------------------------------------------------------------------------

BENCHMARK_DIR = Path("ergebnisse/_benchmark")
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("  PHASE 1: BENCHMARK-LÄUFE DURCHFÜHREN")
print("=" * 70)

# Variante a: Ollama-Standard
print("\n[Variante a] dataset_boese_boese_qwen.py (Ollama-Standard)")
subprocess.run(
    [sys.executable, "dataset_boese_boese_qwen.py", "--n", "1", "--out", str(BENCHMARK_DIR / "qwen_a")],
    check=True
)

print("\n[Variante a] dataset_boese_boese_qwen_abliterated.py (Ollama-Standard)")
subprocess.run(
    [sys.executable, "dataset_boese_boese_qwen_abliterated.py", "--n", "1", "--out", str(BENCHMARK_DIR / "qwen_abl_a")],
    check=True
)

# Variante b: OLLAMA_NUM_PARALLEL=2
print("\n[Variante b] dataset_boese_boese_qwen.py (OLLAMA_NUM_PARALLEL=2)")
env_b = os.environ.copy()
env_b["OLLAMA_NUM_PARALLEL"] = "2"
subprocess.run(
    [sys.executable, "dataset_boese_boese_qwen.py", "--n", "1", "--out", str(BENCHMARK_DIR / "qwen_b")],
    env=env_b,
    check=True
)

print("\n[Variante b] dataset_boese_boese_qwen_abliterated.py (OLLAMA_NUM_PARALLEL=2)")
subprocess.run(
    [sys.executable, "dataset_boese_boese_qwen_abliterated.py", "--n", "1", "--out", str(BENCHMARK_DIR / "qwen_abl_b")],
    env=env_b,
    check=True
)

# ---------------------------------------------------------------------------
# Phase 2 & 3: Qualitätschecks und Metriken
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  PHASE 2 & 3: QUALITÄTSCHECKS UND METRIKEN")
print("=" * 70)

def check_and_extract_metrics(csv_file: Path) -> dict[str, Any]:
    """Qualitätschecks durchführen und Metriken extrahieren."""
    print(f"\nChecking: {csv_file.name}")

    results = {
        "file": csv_file.name,
        "status": "OK",
        "issues": [],
        "row_count": 0,
        "messages_empty": 0,
        "has_think_tags": False,
        "thinking_chars_nonzero": 0,
        "done_reason_length": 0,
        "rows": [],
    }

    try:
        with open(csv_file, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                results["row_count"] += 1
                results["rows"].append(row)

                # Check leere Nachricht
                if not row.get("Nachricht", "").strip():
                    results["messages_empty"] += 1
                    results["issues"].append(f"Row {results['row_count']}: empty Nachricht")

                # Check "<think" im Text
                if "<think" in row.get("Nachricht", "").lower():
                    results["has_think_tags"] = True
                    results["issues"].append(f"Row {results['row_count']}: <think tag in Nachricht")

                # Check Thinking_Chars != 0
                try:
                    thinking_chars = int(row.get("Thinking_Chars", "0") or "0")
                    if thinking_chars != 0:
                        results["thinking_chars_nonzero"] += 1
                        results["issues"].append(f"Row {results['row_count']}: Thinking_Chars = {thinking_chars} (should be 0)")
                except ValueError:
                    pass

                # Check Done_Reason == "length"
                if row.get("Done_Reason") == "length":
                    results["done_reason_length"] += 1
                    results["issues"].append(f"Row {results['row_count']}: Done_Reason = length")

        # Qualitätschecks
        if results["row_count"] != 20:
            results["issues"].append(f"Row count: {results['row_count']} (expected 20)")
            results["status"] = "WARNING"
        if results["messages_empty"] > 0:
            results["status"] = "ERROR"
        if results["has_think_tags"]:
            results["status"] = "ERROR"
        if results["thinking_chars_nonzero"] > 0:
            results["status"] = "WARNING"
        if results["done_reason_length"] > 0:
            results["status"] = "WARNING"

        # Status
        if not results["issues"]:
            print(f"  ✓ All checks passed ({results['row_count']} rows)")
        else:
            print(f"  {'⚠' if results['status'] == 'WARNING' else '✗'} {results['status']}: {len(results['issues'])} issues")
            for issue in results["issues"][:3]:
                print(f"    - {issue}")

    except FileNotFoundError:
        results["status"] = "NOT_FOUND"
        results["issues"].append(f"File not found: {csv_file}")
        print(f"  ✗ File not found")

    return results

# Finde alle CSV-Dateien in Benchmark-Verzeichnissen
benchmark_checks = {}
for variant_dir in ["qwen_a", "qwen_b", "qwen_abl_a", "qwen_abl_b"]:
    variant_path = BENCHMARK_DIR / variant_dir
    if variant_path.exists():
        csv_files = list(variant_path.glob("*.csv"))
        if csv_files:
            csv_file = csv_files[0]  # Ersten Lauf nehmen
            results = check_and_extract_metrics(csv_file)
            benchmark_checks[variant_dir] = results

# ---------------------------------------------------------------------------
# Phase 3b: Metriken berechnen
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  METRIKEN PRO VARIANTE UND MODELL")
print("=" * 70)

metrics_summary = {}

for variant_dir, check_results in benchmark_checks.items():
    if check_results["status"] == "NOT_FOUND":
        continue

    print(f"\n{variant_dir}:")
    rows = check_results["rows"]

    # Extrahiere Metriken
    lauf_dauer_s = None
    sum_prompt_eval_s = 0.0
    sum_eval_s = 0.0
    prompt_tokens_list = []
    output_tokens_list = []
    tokens_pro_s_list = []

    for row in rows:
        try:
            lauf_dauer_s = float(row.get("Lauf_Dauer_s", 0) or 0)
            prompt_eval = float(row.get("Prompt_Eval_s", 0) or 0)
            eval_s = float(row.get("Eval_s", 0) or 0)
            sum_prompt_eval_s += prompt_eval
            sum_eval_s += eval_s

            pt = row.get("Prompt_Tokens", "")
            if pt and pt.strip():
                try:
                    prompt_tokens_list.append(float(pt))
                except ValueError:
                    pass

            ot = row.get("Output_Tokens", "")
            if ot and ot.strip():
                try:
                    output_tokens_list.append(float(ot))
                except ValueError:
                    pass

            tps = row.get("Tokens_pro_s", "")
            if tps and tps.strip():
                try:
                    tokens_pro_s_list.append(float(tps))
                except ValueError:
                    pass
        except (ValueError, TypeError):
            pass

    avg_prompt_tokens = sum(prompt_tokens_list) / len(prompt_tokens_list) if prompt_tokens_list else 0
    avg_output_tokens = sum(output_tokens_list) / len(output_tokens_list) if output_tokens_list else 0
    avg_tokens_pro_s = sum(tokens_pro_s_list) / len(tokens_pro_s_list) if tokens_pro_s_list else 0

    metrics = {
        "variant_dir": variant_dir,
        "lauf_dauer_s": lauf_dauer_s,
        "sum_prompt_eval_s": sum_prompt_eval_s,
        "sum_eval_s": sum_eval_s,
        "avg_prompt_tokens": avg_prompt_tokens,
        "avg_output_tokens": avg_output_tokens,
        "avg_tokens_pro_s": avg_tokens_pro_s,
    }
    metrics_summary[variant_dir] = metrics

    print(f"  Lauf_Dauer_s: {lauf_dauer_s:.2f}s")
    print(f"  Σ Prompt_Eval_s: {sum_prompt_eval_s:.2f}s")
    print(f"  Σ Eval_s: {sum_eval_s:.2f}s")
    print(f"  Ø Prompt_Tokens: {avg_prompt_tokens:.1f}")
    print(f"  Ø Output_Tokens: {avg_output_tokens:.1f}")
    print(f"  Ø Tokens_pro_s: {avg_tokens_pro_s:.2f}")

# ---------------------------------------------------------------------------
# Phase 4: Vergleich a vs. b und Identitäts-Check
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  VERGLEICH VARIANTE A VS. B")
print("=" * 70)

def compare_variants(variant_a: str, variant_b: str):
    """Vergleicht Variante a und b: Speedup und Identität."""
    print(f"\n{variant_a.replace('_a', '')} Speedup:")

    if variant_a not in metrics_summary or variant_b not in metrics_summary:
        print("  (Missing data)")
        return

    m_a = metrics_summary[variant_a]
    m_b = metrics_summary[variant_b]

    speedup = m_a["lauf_dauer_s"] / m_b["lauf_dauer_s"]
    print(f"  Variante a: {m_a['lauf_dauer_s']:.2f}s")
    print(f"  Variante b: {m_b['lauf_dauer_s']:.2f}s")
    print(f"  Speedup: {speedup:.2f}x (b ist schneller)" if speedup > 1 else f"  Speedup: {1/speedup:.2f}x (a ist schneller)")

    # Identitäts-Check: Vergleiche Nachrichten bei gleichen Seeds
    check_a = benchmark_checks.get(variant_a)
    check_b = benchmark_checks.get(variant_b)
    if check_a and check_b:
        rows_a = check_a["rows"]
        rows_b = check_b["rows"]
        identical_count = 0
        for row_a, row_b in zip(rows_a, rows_b):
            if row_a.get("Nachricht") == row_b.get("Nachricht"):
                identical_count += 1
        print(f"  Identische Nachrichten: {identical_count}/{len(rows_a)} (bei gleichen Seeds)")

compare_variants("qwen_a", "qwen_b")
compare_variants("qwen_abl_a", "qwen_abl_b")

# ---------------------------------------------------------------------------
# Phase 5: Vergleich mit altem Lauf (mit Thinking)
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  VERGLEICH MIT ALTEM LAUF (mit Thinking)")
print("=" * 70)

old_run_dir = Path("ergebnisse") / "HS 26" / "dataset_boese_boese_qwen"
if old_run_dir.exists():
    old_csv_files = list(old_run_dir.glob("*.csv"))
    if old_csv_files:
        # Berechne Ø Lauf_Dauer für alte Läufe
        old_durations = []
        for csv_file in old_csv_files[:1]:  # Nimm ersten Lauf
            with open(csv_file, encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                lauf_durations = {}
                for row in reader:
                    lauf_nr = row.get("Lauf_Nr")
                    if lauf_nr not in lauf_durations:
                        try:
                            # Alte Format: Dauer_s = eval_duration
                            dauer = float(row.get("Dauer_s", 0) or 0)
                            lauf_durations[lauf_nr] = dauer
                        except ValueError:
                            pass
                # Summiere pro Lauf (alle 20 Zeilen)
                for lauf_dauer in lauf_durations.values():
                    old_durations.append(lauf_dauer)

        if old_durations:
            avg_old = sum(old_durations) / len(old_durations)
            print(f"Old run (mit Thinking): Ø ~{avg_old:.1f}s eval_duration")
            # Hochrechnung: wenn old nur eval_duration hat, total_duration war ~3-5x länger
            print(f"  (Schätzung total_duration old: ~{avg_old * 3:.1f}s - {avg_old * 5:.1f}s)")

            # Neuer Lauf Vergleich
            if "qwen_a" in metrics_summary:
                m_new = metrics_summary["qwen_a"]
                total_old_est = avg_old * 4  # Mittelwert
                print(f"\nNew run (think=False): {m_new['lauf_dauer_s']:.2f}s total_duration")
                if total_old_est > 0:
                    speedup_total = total_old_est / m_new["lauf_dauer_s"]
                    print(f"  Speedup: ~{speedup_total:.1f}x schneller")
else:
    print("Old run directory not found")

# ---------------------------------------------------------------------------
# Phase 6: Hochrechnung für alle Zellen
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  HOCHRECHNUNG FÜR ALLE ZELLEN")
print("=" * 70)

# Nutze Variante b (schneller)
if "qwen_a" in metrics_summary:
    avg_duration_qwen = metrics_summary["qwen_a"]["lauf_dauer_s"]
else:
    avg_duration_qwen = 120  # Fallback
if "qwen_abl_a" in metrics_summary:
    avg_duration_abl = metrics_summary["qwen_abl_a"]["lauf_dauer_s"]
else:
    avg_duration_abl = 120

# 12 lokale Zellen: 6 Bedingungen × 2 Qwen-Modelle
local_cells = 6 * 2
local_hours = (local_cells * 30 * avg_duration_qwen) / 3600  # 30 Konversationen, 10 Runden

# 4 gemischte Zellen: gut/neutral/böse × (Qwen vs. GPT-4o)
# Nur die Hälfte der Turns lokal (andere Hälfte GPT-4o)
mixed_cells = 3  # gut-gpt, neutral-gpt, böse-gpt (assuming 3)
mixed_hours = (mixed_cells * 30 * avg_duration_qwen * 0.5) / 3600  # 0.5 weil Hälfte lokal

total_hours = local_hours + mixed_hours

print(f"\n12 lokale Zellen (6 Bedingungen × 2 Qwen-Modelle):")
print(f"  Ø {avg_duration_qwen:.1f}s pro Konversation")
print(f"  30 Konversationen × {avg_duration_qwen:.1f}s = {30*avg_duration_qwen/60:.1f} Minuten")
print(f"  Total: {local_hours:.1f} Stunden")

print(f"\n4 gemischte Zellen (Qwen vs. GPT-4o, Hälfte lokal):")
print(f"  ~{mixed_hours:.1f} Stunden (nur lokale Hälfte)")

print(f"\nGesamtzeit für vollständigen Datensatz: ~{total_hours:.1f} Stunden")

# ---------------------------------------------------------------------------
# Phase 7: Empfehlung
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("  EMPFEHLUNG: OLLAMA_NUM_PARALLEL")
print("=" * 70)

speedup_qwen = 1.0
speedup_abl = 1.0

if "qwen_a" in metrics_summary and "qwen_b" in metrics_summary:
    speedup_qwen = (
        metrics_summary["qwen_a"]["lauf_dauer_s"]
        / metrics_summary["qwen_b"]["lauf_dauer_s"]
    )

if "qwen_abl_a" in metrics_summary and "qwen_abl_b" in metrics_summary:
    speedup_abl = (
        metrics_summary["qwen_abl_a"]["lauf_dauer_s"]
        / metrics_summary["qwen_abl_b"]["lauf_dauer_s"]
    )

avg_speedup = (speedup_qwen + speedup_abl) / 2

print(f"\nSpeedup OLLAMA_NUM_PARALLEL=2:")
print(f"  qwen:     {speedup_qwen:.2f}x")
print(f"  abl:      {speedup_abl:.2f}x")
print(f"  Ø:        {avg_speedup:.2f}x")

if avg_speedup > 1.1:
    print(f"\n✓ EMPFEHLUNG: OLLAMA_NUM_PARALLEL=2 BEIBEHALTEN")
    print(f"  Begründung: {avg_speedup:.2f}x Speedup spart ~{(total_hours * (1 - 1/avg_speedup)):.1f} Stunden")
    print(f"  Hinweis: n=1 pro Variante gibt Grössenordnung, keine präzise Messung")
else:
    print(f"\n✗ EMPFEHLUNG: OLLAMA_NUM_PARALLEL=1 (default)")
    print(f"  Begründung: Kein signifikanter Speedup ({avg_speedup:.2f}x)")

print("\n" + "=" * 70)
print("  BENCHMARK ABGESCHLOSSEN")
print("=" * 70)

# Speichere Metriken für LOGBOOK
summary = {
    "timestamp": datetime.now().isoformat(),
    "speedup_qwen": speedup_qwen,
    "speedup_abl": speedup_abl,
    "avg_duration_qwen": avg_duration_qwen,
    "avg_duration_abl": avg_duration_abl,
    "total_hours": total_hours,
    "recommendation": "OLLAMA_NUM_PARALLEL=2" if avg_speedup > 1.1 else "default",
}

import json
with open(BENCHMARK_DIR / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nSummary gespeichert: {BENCHMARK_DIR / 'summary.json'}")
