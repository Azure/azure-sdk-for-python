#!/usr/bin/env python
"""
Reproduction script: Demonstrate how recursive stdout wrapper growth inside
azure.ai.evaluation legacy logging (NodeLogManager / NodeLogWriter) can lead to
RecursionError: maximum recursion depth exceeded while calling a Python object.

This version uses real azure.ai.evaluation APIs (evaluate + built‑in evaluators)
to be more realistic. It deliberately and aggressively leaks NodeLogManager
wrappers (by calling __enter__ without __exit__) before invoking evaluate(),
mimicking scenarios where internal logging contexts are not torn down.

HOW IT WORKS (fast path):
  1. Lowers Python recursion limit (default 400) to trigger sooner.
  2. Creates/leaks N NodeLogManager wrappers each iteration.
  3. Optionally performs a real evaluate() every M iterations (configurable).
  4. Prints progress; every print traverses all leaked wrappers.
  5. Eventually a RecursionError is raised, similar to your production stack trace.

REQUIREMENTS:
  pip install azure-ai-evaluation
  (Uses public API evaluate; no network evaluators required unless you add them.)

OPTIONAL (if you want an LLM-based evaluator):
  Set env vars for an Azure OpenAI deployment:
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_KEY
    AZURE_OPENAI_DEPLOYMENT
  Then run with --enable-model-evaluator to include a RelevanceEvaluator.
  (Otherwise only pure Python evaluators are used.)

USAGE (quick fail):
  python reproduce_eval_logging_recursion.py
    (defaults: 60 iterations, 5 leaks/iter, evaluate every 3 iterations)

TUNING:
  --iterations            Total loop iterations.
  --leaks-per-iter        How many NodeLogManager leaks per loop (increase to fail faster).
  --evaluate-every        Run evaluate() every N iterations (set 1 for every loop).
  --recursion-limit       Force lower recursion limit.
  --dataset-size          Number of JSONL rows (small dataset reused each evaluate).
  --print-lines           Lines printed inside an active NodeLogManager context per iteration.
  --model-evaluator-lines Lines printed when model evaluator enabled (extra noise).
  --enable-model-evaluator Include RelevanceEvaluator if model config env vars are present.
  --stop-on-depth         Abort early if wrapper depth exceeds value (safety).
  --verbose               Print depth every iteration instead of only periodic.

EXAMPLE (more aggressive):
  python reproduce_eval_logging_recursion.py --leaks-per-iter 12 --evaluate-every 1 --recursion-limit 300 --iterations 200

DISCLAIMER:
  This script is intentionally pathological. Do NOT use these patterns in production.
  The goal is to replicate / highlight the risk so the underlying logging code can be hardened.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from io import StringIO, TextIOBase
from contextvars import ContextVar
from typing import Any, Dict, Optional, Mapping, Union, List

# ---------------------------------------------------------------------------
# Imports from azure.ai.evaluation
# ---------------------------------------------------------------------------
try:
    from azure.ai.evaluation import evaluate, BleuScoreEvaluator
except ImportError as e:
    print("ERROR: azure-ai-evaluation not installed. Install with: pip install azure-ai-evaluation", file=sys.stderr)
    raise

# Try optional model evaluator (RelevanceEvaluator) only if user requests
try:
    from azure.ai.evaluation import RelevanceEvaluator
    _HAS_RELEVANCE = True
except Exception:
    _HAS_RELEVANCE = False

# Import the legacy NodeLogManager if available
try:
    from azure.ai.evaluation._legacy._common._logging import NodeLogManager, logger as legacy_logger
    LEGACY_AVAILABLE = True
except Exception:
    # Fallback: replicate minimal pieces if internal path changes
    LEGACY_AVAILABLE = False
    print("WARNING: Could not import legacy logging module; using local fallback wrappers. "
          "This may reduce fidelity of the reproduction.", file=sys.stderr)

# ---------------------------------------------------------------------------
# Local fallback NodeLogManager (if import path changed in future versions)
# ---------------------------------------------------------------------------
if not LEGACY_AVAILABLE:

    @dataclass
    class NodeInfo:
        run_id: str
        node_name: str
        line_number: int

    class NodeLogWriter(TextIOBase):
        def __init__(self, prev_out: Union[TextIOBase, Any], is_stderr: bool = False):
            self._prev_out = prev_out
            self._context: ContextVar[Optional[NodeInfo]] = ContextVar("run_log_info", default=None)
            self._buffers: Dict[str, StringIO] = {}
            self._is_stderr = is_stderr

        def set_node_info(self, run_id: str, node_name: str, line_number: int):
            self._context.set(NodeInfo(run_id, node_name, line_number))
            self._buffers[run_id] = StringIO()

        def clear_node_info(self, run_id: str):
            info = self._context.get()
            if info and info.run_id == run_id:
                self._context.set(None)
            self._buffers.pop(run_id, None)

        def write(self, s: str) -> int:
            # (Mirrors recursive delegation style)
            info = self._context.get()
            if info is None:
                return self._prev_out.write(s)
            buf = self._buffers.get(info.run_id)
            if buf is None:
                return 0
            return buf.write(s)

        def flush(self):
            if hasattr(self._prev_out, "flush"):
                self._prev_out.flush()

    class NodeLogManager:
        def __init__(self):
            self.stdout_logger = NodeLogWriter(sys.stdout)
            self.stderr_logger = NodeLogWriter(sys.stderr, is_stderr=True)
            self._entered = False

        def __enter__(self):
            if not self._entered:
                self._prev_stdout = sys.stdout
                self._prev_stderr = sys.stderr
                sys.stdout = self.stdout_logger
                sys.stderr = self.stderr_logger
                self._entered = True
            return self

        def __exit__(self, *exc):
            if self._entered:
                sys.stdout = self._prev_stdout
                sys.stderr = self._prev_stderr
                self._entered = False

        # Leak helper
        def leak(self):
            self._entered = False

    class DummyLegacyLogger:
        def info(self, m): print("[legacy info]", m)
        def warning(self, m): print("[legacy warn]", m)
        def error(self, m): print("[legacy error]", m)

    legacy_logger = DummyLegacyLogger()


# ---------------------------------------------------------------------------
# Credential scrub simulation (lightweight; the real chain had regex scrubbing)
# ---------------------------------------------------------------------------
def scrub_credentials(s: str) -> str:
    if "key=" in s.lower():
        return s.replace("key=", "key=**scrubbed**")
    return s


# ---------------------------------------------------------------------------
# Additional pure Python evaluators (function & class) to mimic structure
# ---------------------------------------------------------------------------
def length_evaluator(response: str = "", **kwargs):
    return {"length": len(response)}

class KeywordEvaluator:
    def __init__(self, keywords: List[str]):
        self._keywords = [k.lower() for k in keywords]

    def __call__(self, response: str = "", **_):
        text = (response or "").lower()
        hits = [k for k in self._keywords if k in text]
        return {"keyword_hit_count": len(hits), "keyword_hits": hits}


# ---------------------------------------------------------------------------
# Dataset creation
# ---------------------------------------------------------------------------
def create_dataset(path: str, size: int = 6):
    rows = []
    capitals = [
        ("France", "Paris"),
        ("Japan", "Tokyo"),
        ("Spain", "Madrid"),
        ("Italy", "Rome"),
        ("Germany", "Berlin"),
        ("Canada", "Ottawa"),
        ("Australia", "Canberra"),
        ("Brazil", "Brasilia"),
    ]
    for i in range(size):
        country, capital = capitals[i % len(capitals)]
        rows.append({
            "query": f"What is the capital of {country}?",
            "response": f"{capital} is the capital of {country}.",
            "context": f"{country} info context line {i}"
        })
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return path


# ---------------------------------------------------------------------------
# Wrapper chain depth measurement
# ---------------------------------------------------------------------------
def wrapper_depth(stream=None) -> int:
    if stream is None:
        stream = sys.stdout
    depth = 0
    seen = set()
    cur = stream
    while hasattr(cur, "_prev_out") and id(cur) not in seen:
        seen.add(id(cur))
        depth += 1
        cur = getattr(cur, "_prev_out")
    return depth


# ---------------------------------------------------------------------------
# Work payload printed each iteration (drives logging traffic)
# ---------------------------------------------------------------------------
def print_iteration_lines(iteration: int, lines: int, extra_tag: str = ""):
    if isinstance(sys.stdout, (NodeLogManager.__dict__.get('stdout_logger', object).__class__,)):
        pass  # not strictly needed
    for i in range(lines):
        print(scrub_credentials(
            f"[work{extra_tag}] iter={iteration} line={i} key=DEMO_KEY_{iteration}_{i}"
        ))
        if i % 2 == 1:
            print(f"[stderr simulated] iter={iteration} line={i}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Evaluate call wrapper
# ---------------------------------------------------------------------------
def run_evaluate(dataset_path: str, use_model_eval: bool, model_config: Optional[Dict[str, str]]):
    evaluators = {
        "length": length_evaluator,
        "keywords": KeywordEvaluator(["capital", "France", "Tokyo"]),
        "bleu": BleuScoreEvaluator(),
    }

    evaluator_config = {
        "length": {"column_mapping": {"response": "${data.response}"}},
        "keywords": {"column_mapping": {"response": "${data.response}"}},
        "bleu": {"column_mapping": {"response": "${data.response}", "ground_truth": "${data.response}"}},
    }

    if use_model_eval and model_config:
        if _HAS_RELEVANCE:
            evaluators["relevance"] = RelevanceEvaluator(model_config=model_config)
            evaluator_config["relevance"] = {
                "column_mapping": {
                    "query": "${data.query}",
                    "response": "${data.response}",
                    "context": "${data.context}",
                }
            }

    result = evaluate(
        data=dataset_path,
        evaluators=evaluators,
        evaluator_config=evaluator_config,
        # Tags just to reflect real usage
        tags={"scenario": "recursion_repro", "iteration_batch": "true"},
    )
    # We don't print full result to keep output shorter; one line for trace
    print(f"[evaluate] Completed evaluate() run. Keys: {list(result.keys())[:5]} ...")
    return result


# ---------------------------------------------------------------------------
# Aggressive leak routine
# ---------------------------------------------------------------------------
def leak_wrappers(count: int):
    for _ in range(count):
        m = NodeLogManager()
        m.__enter__()   # Replace sys.stdout/sys.stderr
        # Intentionally never calling __exit__ => leak
        if hasattr(m, "stdout_logger"):
            # Optionally set node info so that writes hit flow logs (deeper code path).
            try:
                m.stdout_logger.set_node_info(run_id=f"leak_{id(m)}", node_name="leaked_node", line_number=0)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Main iterative reproduction loop
# ---------------------------------------------------------------------------
def reproduce(opts):
    dataset_path = create_dataset(opts.dataset_path, size=opts.dataset_size)

    model_config = None
    use_model_eval = False
    if opts.enable_model_evaluator:
        required = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "AZURE_OPENAI_DEPLOYMENT")
        if all(os.getenv(k) for k in required):
            model_config = {
                "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
                "api_key": os.environ["AZURE_OPENAI_KEY"],
                "azure_deployment": os.environ["AZURE_OPENAI_DEPLOYMENT"],
            }
            use_model_eval = True
            print("[setup] Model evaluator enabled (RelevanceEvaluator).")
        else:
            print("[setup] Model evaluator requested but env vars missing; skipping.")

    print(f"[start] iterations={opts.iterations} leaks/iter={opts.leaks_per_iter} "
          f"evaluate_every={opts.evaluate_every} recursion_limit={sys.getrecursionlimit()}")

    start = datetime.utcnow()
    for iteration in range(1, opts.iterations + 1):
        leak_wrappers(opts.leaks_per_iter)
        depth = wrapper_depth()
        if opts.verbose or (iteration % opts.report_every == 0):
            print(f"[depth] iteration={iteration} wrapper_depth={depth}")

        # Simulate application prints inside yet another (non-leaked) context for variety
        with NodeLogManager() as mgr:
            try:
                mgr.set_node_context(run_id=f"iter_{iteration}", node_name="active", line_number=iteration)
            except Exception:
                pass
            print_iteration_lines(iteration, opts.print_lines)
            if use_model_eval:
                print_iteration_lines(iteration, opts.model_evaluator_lines, extra_tag=":model")

        # Optionally trigger evaluate (this itself uses internal logging)
        if iteration % opts.evaluate_every == 0:
            try:
                run_evaluate(dataset_path, use_model_eval, model_config)
            except RecursionError as rex:
                print(f"\n[CRASH:evaluate] RecursionError during evaluate at iteration {iteration}, depth={depth}: {rex}")
                break
            except Exception as ex:
                print(f"[warn] evaluate raised non-recursive exception at iteration {iteration}: {ex}")

        # Heartbeat print outside managed context (hits full leaked chain)
        try:
            print(f"[heartbeat] iteration={iteration} depth={depth}")
        except RecursionError as rex:
            print(f"\n[CRASH:heartbeat] RecursionError at iteration {iteration}, depth={depth}: {rex}")
            break

        if opts.stop_on_depth and depth >= opts.stop_on_depth:
            print(f"[abort] Reached stop_on_depth={opts.stop_on_depth} (no RecursionError yet). Aborting for safety.")
            break

        time.sleep(opts.sleep)

    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"[done] Stopped after iteration={iteration} elapsed={elapsed:.2f}s final_depth={wrapper_depth()}")


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Reproduce recursion via azure.ai.evaluation legacy logging chain leaks.")
    p.add_argument("--iterations", type=int, default=60, help="Total outer loop iterations.")
    p.add_argument("--leaks-per-iter", type=int, default=5, help="Number of leaked NodeLogManager wrappers each iteration.")
    p.add_argument("--evaluate-every", type=int, default=3, help="Call evaluate() every N iterations.")
    p.add_argument("--dataset-size", type=int, default=6, help="Size of synthetic dataset reused in evaluate().")
    p.add_argument("--dataset-path", type=str, default="recursion_repro_data.jsonl", help="Path for generated dataset.")
    p.add_argument("--print-lines", type=int, default=4, help="Lines printed inside a managed context each iteration.")
    p.add_argument("--model-evaluator-lines", type=int, default=2, help="Extra lines printed when model evaluator is enabled.")
    p.add_argument("--enable-model-evaluator", action="store_true", help="Include a RelevanceEvaluator if env vars set.")
    p.add_argument("--recursion-limit", type=int, default=400, help="Force a lower recursion limit for faster failure.")
    p.add_argument("--stop-on-depth", type=int, default=0, help="Abort if wrapper depth >= this (0 = disabled).")
    p.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds per iteration (optional).")
    p.add_argument("--report-every", type=int, default=5, help="Report depth every N iterations (unless verbose).")
    p.add_argument("--verbose", action="store_true", help="Verbose depth reporting each iteration.")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    opts = parse_args()

    # Lower recursion limit first
    current_limit = sys.getrecursionlimit()
    if opts.recursion_limit and opts.recursion_limit < current_limit:
        sys.setrecursionlimit(opts.recursion_limit)
        print(f"[setup] Lowered recursion limit from {current_limit} to {opts.recursion_limit}")
    else:
        print(f"[setup] Using existing recursion limit={current_limit}")

    reproduce(opts)


if __name__ == "__main__":
    main()