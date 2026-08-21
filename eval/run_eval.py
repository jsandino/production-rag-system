#!/usr/bin/env python3
"""
RAG evaluation script.

Ingests the eval corpus via the ingestion service, runs each question through
the query service, and scores answers with RAGAS metrics (faithfulness,
context recall, context precision, answer relevancy). Exits non-zero if any
metric's mean score falls below the passing threshold.

Required environment variables:
    INGESTION_URL   — base URL of the ingestion service  (e.g. http://localhost:8002)
    QUERY_URL       — base URL of the query service      (e.g. http://localhost:8003)
    OPENAI_API_KEY  — used for RAGAS's evaluator LLM and embeddings
"""

import datetime
import html
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import cast

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import SecretStr
from ragas import EvaluationDataset
from ragas import evaluate as ragas_evaluate
from ragas.dataset_schema import EvaluationResult
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy
from ragas.run_config import RunConfig

_EVAL_DIR = Path(__file__).parent
_CORPUS = json.loads((_EVAL_DIR / "corpus.json").read_text())
_EVAL_SET = json.loads((_EVAL_DIR / "eval_set.json").read_text())

PASS_THRESHOLD = 0.8
JUDGE_MODEL = "gpt-4o-mini"

# Default max_workers=16 fires enough concurrent LLM calls to trip OpenAI's rate
# limits on CI. That alone isn't the whole story, though: `timeout` bounds a
# single operation *including* all of its retry-with-backoff attempts, and the
# default 180s can be shorter than the retry policy (max_retries=10,
# max_wait=60s) needs to actually recover from rate-limiting -- cutting off
# retries that were still working, not just catching genuinely stuck calls.
# This eval set is tiny, so more headroom on both costs little wall-clock time.
RUN_CONFIG = RunConfig(max_workers=2, timeout=300, log_tenacity=True)

METRICS = [Faithfulness(), LLMContextRecall(), LLMContextPrecisionWithReference(), ResponseRelevancy()]
METRIC_COLUMNS = [metric.name for metric in METRICS]


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

    _ingest(ingestion_url)
    dataset = _collect(query_url)
    result = _score(dataset, api_key)
    _report(result)


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


def _collect(base_url: str) -> EvaluationDataset:
    print("\nQuerying...")
    samples = []
    for entry in _EVAL_SET:
        question = entry["question"]
        response = _post(
            f"{base_url}/query",
            {
                "query": question,
                "top_k": 3,
                "filters": {},
                "debug": False,
            },
        )
        samples.append(
            {
                "user_input": question,
                "response": response["answer"],
                "retrieved_contexts": [source["text"] for source in response["sources"]],
                "reference": entry["reference"],
            }
        )
        print(f"  queried: {question}")
    return EvaluationDataset.from_list(samples)


def _score(dataset: EvaluationDataset, api_key: str) -> EvaluationResult:
    print("\nScoring with RAGAS...")
    secret_key = SecretStr(api_key)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=JUDGE_MODEL, api_key=secret_key, temperature=0))
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(api_key=secret_key))
    result = ragas_evaluate(
        dataset=dataset,
        metrics=METRICS,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RUN_CONFIG,
        raise_exceptions=True,
    )
    return cast(EvaluationResult, result)


# --- reporting ---------------------------------------------------------------


def _report(result: EvaluationResult) -> None:
    df = result.to_pandas()
    ran_at = datetime.datetime.now()

    print("\n" + "=" * 60)
    print("RAG EVALUATION REPORT")
    print("=" * 60)

    for _, row in df.iterrows():
        scores = {col: row[col] for col in METRIC_COLUMNS}
        status = "PASS" if all(score >= PASS_THRESHOLD for score in scores.values()) else "FAIL"
        excerpt = row["response"][:120] + ("..." if len(row["response"]) > 120 else "")
        print(f"\n[{status}] {row['user_input']}")
        print(f"  answer : {excerpt}")
        for col, score in scores.items():
            print(f"  {col:35s}: {score:.2f}")

    means = {col: df[col].mean() for col in METRIC_COLUMNS}
    overall = all(mean >= PASS_THRESHOLD for mean in means.values())

    print("\n" + "=" * 60)
    for col, mean in means.items():
        print(f"{col:35s}: {mean:.0%}")
    print(f"Result: {'PASS' if overall else 'FAIL'}  (threshold {PASS_THRESHOLD:.0%} per metric)")

    report_path = _write_html_report(df, means, overall, ran_at)
    print(f"Report  : {report_path}")

    if not overall:
        sys.exit(1)


def _write_html_report(df, means: dict, overall: bool, ran_at: datetime.datetime) -> Path:
    reports_dir = _EVAL_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)

    badge_bg = "#2d6a4f" if overall else "#9b2226"
    badge_txt = "PASS" if overall else "FAIL"
    timestamp = ran_at.strftime("%Y-%m-%d %H:%M:%S")
    filename = ran_at.strftime("eval_%Y-%m-%d_%H%M%S.html")

    metric_headers = "".join(f"<th>{html.escape(col)}</th>" for col in METRIC_COLUMNS)
    summary_cells = "".join(
        f"<div class='metric'><span>{html.escape(col)}</span>{mean:.0%}</div>" for col, mean in means.items()
    )

    rows = ""
    for _, row in df.iterrows():
        scores = {col: row[col] for col in METRIC_COLUMNS}
        row_pass = all(score >= PASS_THRESHOLD for score in scores.values())
        bg = "#d8f3dc" if row_pass else "#fde8e8"
        status = "PASS" if row_pass else "FAIL"
        metric_cells = "".join(f"<td style='text-align:center'>{score:.2f}</td>" for score in scores.values())
        rows += f"""
        <tr style="background:{bg}">
          <td>{html.escape(row["user_input"])}</td>
          <td>{html.escape(row["reference"])}</td>
          <td>{html.escape(row["response"])}</td>
          {metric_cells}
          <td style="text-align:center;font-weight:bold">{status}</td>
        </tr>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RAG Eval Report — {timestamp}</title>
  <style>
    body  {{ font-family: system-ui, sans-serif; max-width: 1100px;
             margin: 40px auto; padding: 0 20px; color: #1a1a2e; }}
    h1    {{ font-size: 1.6rem; margin-bottom: 4px; }}
    .meta {{ color: #555; font-size: 0.9rem; margin-bottom: 24px; }}
    .summary {{ display: flex; gap: 24px; margin-bottom: 32px; align-items: center; flex-wrap: wrap; }}
    .badge   {{ padding: 8px 20px; border-radius: 6px; color: #fff;
                font-size: 1.1rem; font-weight: bold; background: {badge_bg}; }}
    .metric  {{ font-size: 1rem; }}
    .metric span {{ display: block; color: #555; font-size: 0.75rem; }}
    .thresh  {{ color: #555; font-size: 0.85rem; }}
    table  {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    th     {{ background: #1a1a2e; color: #fff; padding: 10px 12px; text-align: left; }}
    td     {{ padding: 10px 12px; vertical-align: top;
              border-bottom: 1px solid #ddd; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>RAG Evaluation Report</h1>
  <p class="meta">Run at {timestamp}</p>
  <p class="meta">LLM Judge model: {JUDGE_MODEL}</p>
  <div class="summary">
    <div class="badge">{badge_txt}</div>
    {summary_cells}
    <div class="thresh">threshold: {PASS_THRESHOLD:.0%} per metric</div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Question</th>
        <th>Reference</th>
        <th>Answer</th>
        {metric_headers}
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
