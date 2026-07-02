#!/usr/bin/env python3
"""
RAG evaluation script.

Ingests the eval corpus via the ingestion service, runs each question through
the query service, judges answers with an LLM, and exits non-zero if quality
falls below the passing threshold.

Required environment variables:
    INGESTION_URL   — base URL of the ingestion service  (e.g. http://localhost:8002)
    QUERY_URL       — base URL of the query service      (e.g. http://localhost:8003)
    OPENAI_API_KEY  — used only for LLM-as-judge scoring
"""

import datetime
import html
import json
import os
import sys
import urllib.request
from pathlib import Path

from openai import OpenAI

_EVAL_DIR = Path(__file__).parent
_CORPUS = json.loads((_EVAL_DIR / "corpus.json").read_text())
_EVAL_SET = json.loads((_EVAL_DIR / "eval_set.json").read_text())

PASS_THRESHOLD = 0.8
JUDGE_MODEL = "gpt-4o-mini"


def main() -> None:
    ingestion_url = os.environ.get("INGESTION_URL")
    query_url = os.environ.get("QUERY_URL")
    api_key = os.environ.get("OPENAI_API_KEY")

    if not ingestion_url:
        sys.exit("Error: INGESTION_URL is not set.")
    if not query_url:
        sys.exit("Error: QUERY_URL is not set.")
    if not api_key:
        sys.exit("Error: OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    _ingest(ingestion_url)
    results = _evaluate(query_url, client)
    _report(results)


# --- helpers -----------------------------------------------------------------


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _ingest(base_url: str) -> None:
    print("Ingesting corpus...")
    for doc in _CORPUS:
        _post(
            f"{base_url}/ingest",
            {
                "document_name": doc["name"],
                "text": doc["text"],
                "metadata": {"source": "eval"},
            },
        )
        print(f"  ingested: {doc['name']}")


def _evaluate(base_url: str, client: OpenAI) -> list[dict]:
    print("\nRunning evaluation...")
    results = []
    for entry in _EVAL_SET:
        question = entry["question"]
        key_point = entry["key_point"]
        answer = _post(
            f"{base_url}/query",
            {
                "query": question,
                "top_k": 3,
                "filters": {},
                "debug": False,
            },
        )["answer"]
        passed = _judge(client, question, key_point, answer)
        results.append({"question": question, "key_point": key_point, "answer": answer, "passed": passed})
    return results


def _judge(client: OpenAI, question: str, key_point: str, answer: str) -> bool:
    response = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Key point that should appear in the answer: {key_point}\n"
                    f"Actual answer: {answer}\n\n"
                    "Does the actual answer address the key point? Reply with only 'yes' or 'no'."
                ),
            }
        ],
        max_tokens=5,
    )
    return response.choices[0].message.content.strip().lower().startswith("yes")


# --- reporting ---------------------------------------------------------------


def _report(results: list[dict]) -> None:
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    score = passed / total
    ran_at = datetime.datetime.now()

    print("\n" + "=" * 60)
    print("RAG EVALUATION REPORT")
    print("=" * 60)

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        excerpt = r["answer"][:120] + ("..." if len(r["answer"]) > 120 else "")
        print(f"\n[{status}] {r['question']}")
        print(f"  key point : {r['key_point']}")
        print(f"  answer    : {excerpt}")

    print("\n" + "=" * 60)
    print(f"Score: {passed}/{total} ({score:.0%})")

    overall = score >= PASS_THRESHOLD
    print(f"Result: {'PASS' if overall else 'FAIL'}  (threshold {PASS_THRESHOLD:.0%})")

    report_path = _write_html_report(results, passed, total, score, ran_at)
    print(f"Report  : {report_path}")

    if not overall:
        sys.exit(1)


def _write_html_report(
    results: list[dict],
    passed: int,
    total: int,
    score: float,
    ran_at: datetime.datetime,
) -> Path:
    reports_dir = _EVAL_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)

    overall = score >= PASS_THRESHOLD
    badge_bg = "#2d6a4f" if overall else "#9b2226"
    badge_txt = "PASS" if overall else "FAIL"
    timestamp = ran_at.strftime("%Y-%m-%d %H:%M:%S")
    filename = ran_at.strftime("eval_%Y-%m-%d_%H%M%S.html")

    rows = ""
    for r in results:
        bg = "#d8f3dc" if r["passed"] else "#fde8e8"
        status = "PASS" if r["passed"] else "FAIL"
        rows += f"""
        <tr style="background:{bg}">
          <td>{html.escape(r['question'])}</td>
          <td>{html.escape(r['key_point'])}</td>
          <td>{html.escape(r['answer'])}</td>
          <td style="text-align:center;font-weight:bold">{status}</td>
        </tr>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RAG Eval Report — {timestamp}</title>
  <style>
    body  {{ font-family: system-ui, sans-serif; max-width: 960px;
             margin: 40px auto; padding: 0 20px; color: #1a1a2e; }}
    h1    {{ font-size: 1.6rem; margin-bottom: 4px; }}
    .meta {{ color: #555; font-size: 0.9rem; margin-bottom: 24px; }}
    .summary {{ display: flex; gap: 24px; margin-bottom: 32px; align-items: center; }}
    .badge   {{ padding: 8px 20px; border-radius: 6px; color: #fff;
                font-size: 1.1rem; font-weight: bold; background: {badge_bg}; }}
    .score   {{ font-size: 2rem; font-weight: bold; }}
    .thresh  {{ color: #555; font-size: 0.85rem; }}
    table  {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th     {{ background: #1a1a2e; color: #fff; padding: 10px 12px; text-align: left; }}
    td     {{ padding: 10px 12px; vertical-align: top;
              border-bottom: 1px solid #ddd; white-space: pre-wrap; }}
    col.q  {{ width: 22%; }}
    col.k  {{ width: 18%; }}
    col.a  {{ width: 52%; }}
    col.r  {{ width: 8%; }}
  </style>
</head>
<body>
  <h1>RAG Evaluation Report</h1>
  <p class="meta">Run at {timestamp}</p>
  <div class="summary">
    <div class="score">{passed}/{total} ({score:.0%})</div>
    <div class="badge">{badge_txt}</div>
    <div class="thresh">threshold: {PASS_THRESHOLD:.0%}</div>
  </div>
  <table>
    <colgroup>
      <col class="q"><col class="k"><col class="a"><col class="r">
    </colgroup>
    <thead>
      <tr>
        <th>Question</th>
        <th>Key point</th>
        <th>Answer</th>
        <th>Result</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>
</body>
</html>"""

    report_path = reports_dir / filename
    report_path.write_text(page)
    return report_path


if __name__ == "__main__":
    main()
