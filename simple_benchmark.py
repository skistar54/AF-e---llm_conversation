"""
Vereinfachter Benchmark: Direkter Ollama-Aufruf, keine ConversationManager.
Misst nur: Dauer, eval_count, tokens/s für 4 Runden pro Modell und Variante.
"""

import json
import os
import time
from pathlib import Path

import ollama

BENCHMARK_DIR = Path("ergebnisse/_benchmark")
BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

configs = [
    ("qwen_std", "qwen3:8b", None),
    ("qwen_parallel2", "qwen3:8b", {"OLLAMA_NUM_PARALLEL": "2"}),
    ("abl_std", "qwen3-8b-abl-harmonized", None),
    ("abl_parallel2", "qwen3-8b-abl-harmonized", {"OLLAMA_NUM_PARALLEL": "2"}),
]

results = {}

print("=" * 70)
print("  BENCHMARK: think=False Varianten (direkter Ollama-Aufruf)")
print("=" * 70)

for config_name, model, env_vars in configs:
    if env_vars:
        for k, v in env_vars.items():
            os.environ[k] = v

    print(f"\n[{config_name}] {model}")

    # Test message
    messages = [
        {"role": "user", "content": "What do you think about the future of humanity?"}
    ]

    # 4 runs
    run_durations = []
    total_eval_count = 0
    total_eval_duration = 0

    for i in range(1, 5):
        print(f"  Run {i}/4...")
        start = time.perf_counter()

        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                stream=False,
                think=False,
                seed=1000 + i,
                temperature=0.7,
            )

            duration = time.perf_counter() - start
            run_durations.append(duration)

            # Extract metrics
            eval_count = response.get("eval_count", 0)
            eval_duration_ns = response.get("eval_duration", 0)
            eval_duration_s = eval_duration_ns / 1e9 if eval_duration_ns > 0 else 0

            total_eval_count += eval_count
            total_eval_duration += eval_duration_s

            tokens_ps = eval_count / eval_duration_s if eval_duration_s > 0 else 0

            print(
                f"    Duration: {duration:.2f}s | eval_count: {eval_count} | tokens/s: {tokens_ps:.2f}"
            )

            # Add assistant response to messages for next iteration
            messages.append({"role": "assistant", "content": response.get("message", {}).get("content", "")})

        except Exception as e:
            print(f"    ERROR: {e}")

    # Calculate averages
    if run_durations:
        avg_duration = sum(run_durations) / len(run_durations)
        avg_tokens_ps = total_eval_count / total_eval_duration if total_eval_duration > 0 else 0

        results[config_name] = {
            "model": model,
            "avg_duration_s": avg_duration,
            "total_eval_count": total_eval_count,
            "total_eval_duration_s": total_eval_duration,
            "avg_tokens_per_s": avg_tokens_ps,
        }

        print(f"  Average duration: {avg_duration:.2f}s")
        print(f"  Average tokens/s: {avg_tokens_ps:.2f}")

    # Unset ENV
    if env_vars:
        for k in env_vars.keys():
            os.environ.pop(k, None)

# Analysis
print("\n" + "=" * 70)
print("  ANALYSIS")
print("=" * 70)

# Speedup comparison
print("\nSpeedup (std vs parallel2):")
if "qwen_std" in results and "qwen_parallel2" in results:
    speedup_qwen = (
        results["qwen_std"]["avg_duration_s"]
        / results["qwen_parallel2"]["avg_duration_s"]
    )
    print(f"  qwen: {speedup_qwen:.2f}x")
else:
    speedup_qwen = 0

if "abl_std" in results and "abl_parallel2" in results:
    speedup_abl = (
        results["abl_std"]["avg_duration_s"]
        / results["abl_parallel2"]["avg_duration_s"]
    )
    print(f"  abl: {speedup_abl:.2f}x")
else:
    speedup_abl = 0

if speedup_qwen > 0 and speedup_abl > 0:
    avg_speedup = (speedup_qwen + speedup_abl) / 2
    print(f"  Average: {avg_speedup:.2f}x")

    if avg_speedup > 1.05:
        print(f"\n✓ Recommendation: OLLAMA_NUM_PARALLEL=2")
        print(f"  Saves time on multi-agent conversations")
    else:
        print(f"\n✗ Recommendation: Use default (no speedup)")

# Save results
with open(BENCHMARK_DIR / "simple_benchmark.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved: {BENCHMARK_DIR / 'simple_benchmark.json'}")
print("=" * 70)
