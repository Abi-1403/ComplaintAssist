"""Evaluate the local Qwen/Ollama classifier on the project's 18 synthetic challenge cases.

Place this file in the complaint_assist folder, then run: python evaluate_ollama.py
No OpenAI key required. Reads the existing fictional dataset without modifying it.
"""
import csv
import json
from pathlib import Path
from time import perf_counter

from ollama_adapter import classify_local
from retrieval import retrieve
from security import redact

BASE = Path(__file__).resolve().parent
DATA = BASE / "evaluation" / "challenge_cases.json"
OUTPUT = BASE / "results"


def main():
    cases = json.loads(DATA.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []

    for index, case in enumerate(cases, start=1):
        started = perf_counter()
        text, _ = redact(case["text"])
        record = {
            "case_id": case["id"],
            "complaint": case["text"],
            "expected_category": case["category"],
            "predicted_category": "",
            "predicted_team": "",
            "category_correct": False,
            "expected_policy": case["policy"],
            "retrieved_policy_ids": [],
            "expected_policy_in_top4": False,
            "error": "",
            "seconds": 0,
        }
        try:
            prediction = classify_local(text)  # Calls Ollama, NOT offline rules.
            record["predicted_category"] = prediction.category
            record["predicted_team"] = prediction.team
            record["category_correct"] = prediction.category == case["category"]
            evidence = retrieve(text + " " + prediction.category.replace("_", " ") + " specialist handover", k=4)
            record["retrieved_policy_ids"] = [passage["chunk_id"] for passage in evidence]
            record["expected_policy_in_top4"] = case["policy"] in record["retrieved_policy_ids"]
            outcome = "PASS" if record["category_correct"] else "WRONG"
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            outcome = "ERROR"
        record["seconds"] = round(perf_counter() - started, 2)
        records.append(record)
        print(f"{index:02}/{len(cases)} {case['id']}: {outcome} ({record['seconds']}s)", flush=True)

    successful = [r for r in records if not r["error"]]
    correct = sum(r["category_correct"] for r in successful)
    relevant = sum(r["expected_policy_in_top4"] for r in successful)
    result = {
        "dataset": "18 synthetic phrase-variation challenge cases",
        "model": "local Ollama (see OLLAMA_MODEL environment variable; default qwen2.5:3b)",
        "total_cases": len(records),
        "successful_model_calls": len(successful),
        "failed_model_calls": len(records) - len(successful),
        "classification_correct": correct,
        "classification_accuracy_on_successful_calls": round(correct / len(successful), 4) if successful else None,
        "classification_accuracy_all_cases_failures_wrong": round(correct / len(records), 4) if records else None,
        "expected_policy_in_top4": relevant,
        "expected_policy_recall_at4_on_successful_calls": round(relevant / len(successful), 4) if successful else None,
        "notes": [
            "Synthetic authored dataset, not a representative sample of real bank complaints.",
            "Retrieval uses the project's lexical policy search with the predicted category; it is not an LLM embedding-based RAG benchmark.",
            "Finding the expected policy ID does not prove the generated handover cites it accurately.",
            "This script tests classification and retrieval, not LLM handover quality or reviewer decisions.",
        ],
        "details": records,
    }
    json_path = OUTPUT / "ollama_challenge_evaluation.json"
    csv_path = OUTPUT / "ollama_challenge_evaluation.csv"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        for record in records:
            writer.writerow({**record, "retrieved_policy_ids": "; ".join(record["retrieved_policy_ids"])})
    print("\n=== OLLAMA CHALLENGE EVALUATION ===")
    print(f"Completed model calls: {len(successful)}/{len(records)}")
    print(f"Correct categories: {correct}/{len(successful)} successful calls")
    print(f"Accuracy (all cases, failures counted wrong): {result['classification_accuracy_all_cases_failures_wrong']:.1%}")
    if successful:
        print(f"Accuracy (successful calls only): {result['classification_accuracy_on_successful_calls']:.1%}")
        print(f"Expected policy in top 4: {relevant}/{len(successful)} ({result['expected_policy_recall_at4_on_successful_calls']:.1%})")
    print(f"Saved: {json_path}")
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
