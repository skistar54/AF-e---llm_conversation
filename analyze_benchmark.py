"""
Analyzed benchmark results from existing CSV.
"""

import csv
import json
from pathlib import Path

csv_file = Path("ergebnisse/_benchmark/qwen_a/lauf_01_2026-10-27_11-39-31_boese_vs_boese_qwen.csv")

print(f"Analyzing: {csv_file.name}\n")

metrics = {
    "row_count": 0,
    "lauf_dauer_s": 0,
    "sum_prompt_eval_s": 0,
    "sum_eval_s": 0,
    "sum_total_duration_s": 0,
    "prompt_tokens": [],
    "output_tokens": [],
    "tokens_pro_s": [],
    "issues": [],
}

with open(csv_file, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        metrics["row_count"] += 1

        # Extract metrics
        try:
            ld = float(row.get("Lauf_Dauer_s", 0) or 0)
            metrics["lauf_dauer_s"] = ld

            pe = float(row.get("Prompt_Eval_s", 0) or 0)
            metrics["sum_prompt_eval_s"] += pe

            ev = float(row.get("Eval_s", 0) or 0)
            metrics["sum_eval_s"] += ev

            td = float(row.get("Dauer_s", 0) or 0)
            metrics["sum_total_duration_s"] += td

            pt = row.get("Prompt_Tokens", "")
            if pt and pt.strip():
                metrics["prompt_tokens"].append(float(pt))

            ot = row.get("Output_Tokens", "")
            if ot and ot.strip():
                metrics["output_tokens"].append(float(ot))

            tps = row.get("Tokens_pro_s", "")
            if tps and tps.strip():
                metrics["tokens_pro_s"].append(float(tps))
        except (ValueError, TypeError):
            pass

        # Quality checks
        if not row.get("Nachricht", "").strip():
            metrics["issues"].append(f"Row {metrics['row_count']}: Empty Nachricht")
        if "<think" in row.get("Nachricht", "").lower():
            metrics["issues"].append(f"Row {metrics['row_count']}: <think tag")
        if row.get("Done_Reason") == "length":
            metrics["issues"].append(f"Row {metrics['row_count']}: Done_Reason=length")

# Calculate averages
metrics["avg_prompt_tokens"] = (
    sum(metrics["prompt_tokens"]) / len(metrics["prompt_tokens"]) if metrics["prompt_tokens"] else 0
)
metrics["avg_output_tokens"] = (
    sum(metrics["output_tokens"]) / len(metrics["output_tokens"]) if metrics["output_tokens"] else 0
)
metrics["avg_tokens_pro_s"] = (
    sum(metrics["tokens_pro_s"]) / len(metrics["tokens_pro_s"]) if metrics["tokens_pro_s"] else 0
)

# Print summary
print(f"Rows: {metrics['row_count']}")
print(f"Lauf_Dauer_s: {metrics['lauf_dauer_s']:.2f}s (~{metrics['lauf_dauer_s']/60:.1f} min)")
print(f"Sum Prompt_Eval_s: {metrics['sum_prompt_eval_s']:.2f}s")
print(f"Sum Eval_s: {metrics['sum_eval_s']:.2f}s")
print(f"Sum total_duration_s: {metrics['sum_total_duration_s']:.2f}s")
print(f"Avg Prompt_Tokens: {metrics['avg_prompt_tokens']:.1f}")
print(f"Avg Output_Tokens: {metrics['avg_output_tokens']:.1f}")
print(f"Avg Tokens/s: {metrics['avg_tokens_pro_s']:.2f}")

if metrics["issues"]:
    print(f"\nIssues: {len(metrics['issues'])}")
    for issue in metrics["issues"][:5]:
        print(f"  - {issue}")
else:
    print("\n✓ No quality issues")

# Save for later use
with open("ergebnisse/_benchmark/qwen_a_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\n✓ Metrics saved to qwen_a_metrics.json")
