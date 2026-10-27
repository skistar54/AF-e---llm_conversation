"""
Direkter Benchmark ohne subprocess: Importiert und lädt die Skripte direkt.
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup
BENCHMARK_DIR = Path("ergebnisse/_benchmark")
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("  DIREKTER BENCHMARK: think=False Varianten")
print("=" * 70)

# Phase 1: Manuelle Läufe durchführen
# Variante a: Ollama-Standard (default OLLAMA_NUM_PARALLEL)
# Variante b: OLLAMA_NUM_PARALLEL=2

configs = [
    ("qwen_a", "qwen3:8b", 1, None),
    ("qwen_b", "qwen3:8b", 1, {"OLLAMA_NUM_PARALLEL": "2"}),
    ("qwen_abl_a", "qwen3-8b-abl-harmonized", 1, None),
    ("qwen_abl_b", "qwen3-8b-abl-harmonized", 1, {"OLLAMA_NUM_PARALLEL": "2"}),
]

# Führe jeden Config durch
results = {}

for config_name, model, n_runs, env_vars in configs:
    print(f"\n[{config_name}] {model} (n={n_runs})")
    out_dir = BENCHMARK_DIR / config_name
    out_dir.mkdir(exist_ok=True)

    # Setze ENV wenn nötig
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = v

    # Führe das Skript aus
    if "abl" in model:
        script = "dataset_boese_boese_qwen_abliterated.py"
    else:
        script = "dataset_boese_boese_qwen.py"

    # Führe aus mit Redirect zu out_dir
    cmd = f'{sys.executable} {script} --n {n_runs} --out "{out_dir}" > "{out_dir}/run.log" 2>&1'
    print(f"  Running: {cmd}")
    exit_code = os.system(cmd)
    print(f"  Exit code: {exit_code}")

    # Finde CSV
    csv_files = list(out_dir.glob("*.csv"))
    if csv_files:
        results[config_name] = csv_files[0]
        print(f"  CSV created: {csv_files[0].name}")
    else:
        print(f"  ERROR: No CSV created")

    # Unsetze ENV
    if env_vars:
        for k in env_vars.keys():
            os.environ.pop(k, None)

# Phase 2: Qualitätschecks und Metriken
print("\n" + "=" * 70)
print("  QUALITÄTSCHECKS UND METRIKEN")
print("=" * 70)

summary_data = {}

for config_name, csv_file in results.items():
    print(f"\n{config_name}:")

    metrics = {
        "config": config_name,
        "rows": 0,
        "lauf_dauer_s": 0,
        "sum_prompt_eval_s": 0,
        "sum_eval_s": 0,
        "prompt_tokens": [],
        "output_tokens": [],
        "tokens_pro_s": [],
        "issues": [],
    }

    try:
        with open(csv_file, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                metrics["rows"] += 1

                # Extract metrics
                try:
                    ld = float(row.get("Lauf_Dauer_s", 0) or 0)
                    metrics["lauf_dauer_s"] = ld

                    pe = float(row.get("Prompt_Eval_s", 0) or 0)
                    metrics["sum_prompt_eval_s"] += pe

                    ev = float(row.get("Eval_s", 0) or 0)
                    metrics["sum_eval_s"] += ev

                    pt = row.get("Prompt_Tokens", "")
                    if pt and pt.strip():
                        metrics["prompt_tokens"].append(float(pt))

                    ot = row.get("Output_Tokens", "")
                    if ot and ot.strip():
                        metrics["output_tokens"].append(float(ot))

                    tps = row.get("Tokens_pro_s", "")
                    if tps and tps.strip():
                        metrics["tokens_pro_s"].append(float(tps))
                except (ValueError, TypeError) as e:
                    pass

                # Quality checks
                if not row.get("Nachricht", "").strip():
                    metrics["issues"].append("Empty Nachricht")
                if "<think" in row.get("Nachricht", "").lower():
                    metrics["issues"].append("<think tag found")
                try:
                    tc = int(row.get("Thinking_Chars", "0") or "0")
                    if tc != 0:
                        metrics["issues"].append(f"Thinking_Chars={tc}")
                except ValueError:
                    pass
                if row.get("Done_Reason") == "length":
                    metrics["issues"].append("Done_Reason=length")

        # Calculate averages
        metrics["avg_prompt_tokens"] = (
            sum(metrics["prompt_tokens"]) / len(metrics["prompt_tokens"])
            if metrics["prompt_tokens"]
            else 0
        )
        metrics["avg_output_tokens"] = (
            sum(metrics["output_tokens"]) / len(metrics["output_tokens"])
            if metrics["output_tokens"]
            else 0
        )
        metrics["avg_tokens_pro_s"] = (
            sum(metrics["tokens_pro_s"]) / len(metrics["tokens_pro_s"])
            if metrics["tokens_pro_s"]
            else 0
        )

        # Print summary
        print(f"  Rows: {metrics['rows']}")
        print(f"  Lauf_Dauer_s: {metrics['lauf_dauer_s']:.2f}s")
        print(f"  Sum Prompt_Eval_s: {metrics['sum_prompt_eval_s']:.2f}s")
        print(f"  Sum Eval_s: {metrics['sum_eval_s']:.2f}s")
        print(f"  Avg Prompt_Tokens: {metrics['avg_prompt_tokens']:.1f}")
        print(f"  Avg Output_Tokens: {metrics['avg_output_tokens']:.1f}")
        print(f"  Avg Tokens/s: {metrics['avg_tokens_pro_s']:.2f}")
        if metrics["issues"]:
            print(f"  Issues: {metrics['issues'][:3]}")

        summary_data[config_name] = metrics

    except Exception as e:
        print(f"  ERROR: {e}")

# Phase 3: Speedup comparison
print("\n" + "=" * 70)
print("  SPEEDUP VERGLEICH")
print("=" * 70)

def compare_variants(name, a_key, b_key):
    if a_key in summary_data and b_key in summary_data:
        a_dur = summary_data[a_key]["lauf_dauer_s"]
        b_dur = summary_data[b_key]["lauf_dauer_s"]
        speedup = a_dur / b_dur if b_dur > 0 else 1.0
        print(f"\n{name}:")
        print(f"  Variante a: {a_dur:.2f}s")
        print(f"  Variante b: {b_dur:.2f}s")
        print(f"  Speedup: {speedup:.2f}x" if speedup > 1 else f"  (b is slower)")
        return speedup
    return 1.0

speedup_qwen = compare_variants("qwen (a vs b)", "qwen_a", "qwen_b")
speedup_abl = compare_variants("abl (a vs b)", "qwen_abl_a", "qwen_abl_b")
avg_speedup = (speedup_qwen + speedup_abl) / 2

# Phase 4: Hochrechnung
print("\n" + "=" * 70)
print("  HOCHRECHNUNG")
print("=" * 70)

if "qwen_a" in summary_data and "qwen_abl_a" in summary_data:
    avg_dur = (
        summary_data["qwen_a"]["lauf_dauer_s"] + summary_data["qwen_abl_a"]["lauf_dauer_s"]
    ) / 2
    local_cells = 12  # 6 conditions × 2 models
    local_hours = (local_cells * 30 * avg_dur) / 3600
    mixed_cells = 3  # 3 mixed conditions
    mixed_hours = (mixed_cells * 30 * avg_dur * 0.5) / 3600
    total_hours = local_hours + mixed_hours

    print(f"\nAverage duration: {avg_dur:.2f}s per conversation")
    print(f"12 local cells: {local_hours:.1f} hours")
    print(f"3 mixed cells (50% local): {mixed_hours:.1f} hours")
    print(f"Total: {total_hours:.1f} hours")

    # Recommendation
    print(f"\nSpeedup avg: {avg_speedup:.2f}x")
    if avg_speedup > 1.05:
        saved_hours = total_hours * (1 - 1 / avg_speedup)
        print(f"✓ Recommendation: OLLAMA_NUM_PARALLEL=2")
        print(f"  Saves ~{saved_hours:.1f} hours")
    else:
        print(f"✗ Recommendation: Use default (no significant speedup)")

# Save summary
with open(BENCHMARK_DIR / "summary.json", "w") as f:
    json.dump(
        {
            "timestamp": datetime.now().isoformat(),
            "summary": summary_data,
            "avg_speedup": avg_speedup,
            "recommendation": "OLLAMA_NUM_PARALLEL=2" if avg_speedup > 1.05 else "default",
        },
        f,
        indent=2,
    )

print(f"\nSummary saved: {BENCHMARK_DIR / 'summary.json'}")
print("=" * 70)
