#!/usr/bin/env python3
"""Local resilient crash-recovery demo for the resilient-responses-agent-demo.

Runs the agent **entirely on your machine** — the resilient task store and the
response store are file-backed under a local directory, so you do **not** need
the hosted Foundry task API (the one currently returning 403). Only the LLM
sub-calls go to your Foundry project, so you need ``az login`` + a project
endpoint + a model deployment.

What it demonstrates, automatically, in one run:

  1. Starts the agent as a local server (file-backed resilient backend).
  2. POSTs a streaming, background, stored response that runs a multi-phase
     research plan, emitting one resilient ``OutputItem`` + ``checkpoint()`` per
     sub-call. The live SSE is streamed to ``out/sse_initial.txt``.
  3. After a few checkpoints land, injects a crash (the demo's ``"crash"``
     input forces ``os._exit(137)``) — pinned to the same session so it kills
     the replica running our response. The stream drops mid-flight.
  4. Restarts the server against the **same** resilient root. On startup the
     framework's recovery scan reclaims the in-progress task and re-invokes the
     handler with ``context.is_recovery is True``; it seeds from the persisted
     response and resumes at the first un-checkpointed sub-call.
  5. Reconnects with ``GET /responses/{id}?stream=true&starting_after=<seq>``
     and streams the resumed SSE to ``out/sse_resumed.txt``, then asserts the
     response completes with the full set of output items.

Run it via ``./run.sh`` (which sets up the venv + env), or directly:

    FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project> \
    AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o \
    python recovery_demo.py

Tunables (env): ``NUM_PHASES`` (default 3), ``CRASH_AFTER`` (default 5
checkpoints), ``PORT`` (default 8088), ``RESILIENT_ROOT`` (default ``./.agentserver``),
``OUT_DIR`` (default ``./out``).
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

try:
    import httpx
except ImportError:  # pragma: no cover - guided setup
    sys.exit("httpx is required. Run ./run.sh, or: pip install httpx")

HERE = Path(__file__).resolve().parent
MAIN_PY = HERE.parent / "src" / "resilient-responses-agent-demo" / "main.py"

PORT = int(os.environ.get("PORT", "8088"))


def _port_is_free(port: int) -> bool:
    import socket

    s = socket.socket()
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


# Auto-pick a free port if the requested one is busy (e.g. a leftover server).
_requested_port = PORT
while not _port_is_free(PORT) and PORT < _requested_port + 25:
    PORT += 1
if PORT != _requested_port:
    print(f"  » port {_requested_port} is busy; using {PORT} instead", flush=True)

BASE = f"http://localhost:{PORT}"
NUM_PHASES = int(os.environ.get("NUM_PHASES", "3"))
CRASH_AFTER = int(os.environ.get("CRASH_AFTER", "5"))
RESILIENT_ROOT = Path(os.environ.get("RESILIENT_ROOT", HERE / ".agentserver")).resolve()
OUT_DIR = Path(os.environ.get("OUT_DIR", HERE / "out")).resolve()
TOPIC = os.environ.get("TOPIC", "The impact of renewable energy adoption on global supply chains")

if "FOUNDRY_PROJECT_ENDPOINT" not in os.environ:
    sys.exit(
        "FOUNDRY_PROJECT_ENDPOINT is required (your Foundry project endpoint for the LLM\n"
        "sub-calls). Run `az login` first, then set it. See README.md."
    )

# Child-process env: real LLM via the project endpoint, but resilience stays
# local (file-backed task store + response store under RESILIENT_ROOT).
CHILD_ENV = {
    **os.environ,
    "AZURE_AI_MODEL_DEPLOYMENT_NAME": os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
    "DEMO_MODE": "1",  # enables the "crash" input sentinel in main.py
    "AGENTSERVER_TASKS_BACKEND": "local",
    "AGENTSERVER_STATE_ROOT": str(RESILIENT_ROOT),
    "INTRA_PHASE_COOLDOWN_SEC": os.environ.get("INTRA_PHASE_COOLDOWN_SEC", "1"),
    "INTER_PHASE_COOLDOWN_SEC": os.environ.get("INTER_PHASE_COOLDOWN_SEC", "1"),
    "TARGET_OUTPUT_TOKENS": os.environ.get("TARGET_OUTPUT_TOKENS", "80"),
    "NUM_PHASES": str(NUM_PHASES),
    "PORT": str(PORT),
}

st = {"rid": None, "max_seq": 0, "done": 0, "crashed": False}


def log(*a: object) -> None:
    print("  »", *a, flush=True)


def banner(text: str) -> None:
    print(f"\n\033[1m{text}\033[0m", flush=True)


def wait_port(timeout: float = 45.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            httpx.get(f"{BASE}/responses/_ping", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def start_server(tag: str) -> subprocess.Popen:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logf = open(OUT_DIR / f"server_{tag}.log", "w")
    proc = subprocess.Popen(
        [sys.executable, str(MAIN_PY)],
        env=CHILD_ENV,
        stdout=logf,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    if not wait_port():
        raise RuntimeError(f"server '{tag}' did not come up — see {OUT_DIR / f'server_{tag}.log'}")
    log(f"server '{tag}' is up (pid {proc.pid}), logs -> out/server_{tag}.log")
    return proc


def parse_frame(frame: str):
    ev = data = None
    for line in frame.split("\n"):
        if line.startswith("event:"):
            ev = line[6:].strip()
        elif line.startswith("data:"):
            data = line[5:].strip()
    if ev is None:
        return None, {}
    try:
        return ev, (json.loads(data) if data else {})
    except Exception:
        return ev, {}


def inject_crash() -> None:
    log("injecting crash (POST input='crash', pinned to the same session) ...")
    try:
        httpx.post(
            f"{BASE}/responses",
            json={
                "model": CHILD_ENV["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                "input": "crash",
                "stream": False,
                "store": True,
                "background": True,
                "agent_session_id": os.urandom(8).hex(),
            },
            timeout=10,
        )
    except Exception as exc:
        log(f"crash request returned/disconnected (expected): {type(exc).__name__}")
    st["crashed"] = True


def stream_initial() -> None:
    body = {
        "model": CHILD_ENV["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        "input": TOPIC,
        "stream": True,
        "store": True,
        "background": True,
        "agent_session_id": os.urandom(16).hex(),
    }
    f = open(OUT_DIR / "sse_initial.txt", "w")
    buf = ""
    try:
        with httpx.stream("POST", f"{BASE}/responses", json=body, timeout=None) as r:
            log(f"initial stream opened (HTTP {r.status_code})")
            for chunk in r.iter_text():
                if not chunk:
                    continue
                f.write(chunk)
                f.flush()
                buf += chunk
                while "\n\n" in buf:
                    frame, buf = buf.split("\n\n", 1)
                    ev, data = parse_frame(frame)
                    seq = data.get("sequence_number")
                    if isinstance(seq, int):
                        st["max_seq"] = max(st["max_seq"], seq)
                    rid = (data.get("response") or {}).get("id") or data.get("id")
                    if rid and not st["rid"]:
                        st["rid"] = rid
                        log(f"response id: {rid}")
                    if ev == "response.output_item.done":
                        st["done"] += 1
                        log(f"checkpoint #{st['done']} committed (seq={st['max_seq']})")
                        if st["done"] == CRASH_AFTER and not st["crashed"]:
                            threading.Thread(target=inject_crash, daemon=True).start()
    except Exception as exc:
        log(f"initial stream dropped: {type(exc).__name__} (this is the crash)")
    finally:
        f.close()


def reconnect_and_verify() -> bool:
    starting_after = st["max_seq"]
    log(f"reconnecting: GET /responses/{st['rid']}?stream=true&starting_after={starting_after}")
    f = open(OUT_DIR / "sse_resumed.txt", "w")
    buf = ""
    first_event = None
    seeded_items = None
    final_items = None
    terminal = None
    deadline = time.time() + 240
    try:
        with httpx.stream(
            "GET",
            f"{BASE}/responses/{st['rid']}",
            params={"stream": "true", "starting_after": starting_after},
            timeout=None,
        ) as r:
            log(f"reconnect stream opened (HTTP {r.status_code})")
            for chunk in r.iter_text():
                if time.time() > deadline:
                    log("reconnect deadline reached")
                    break
                if not chunk:
                    continue
                f.write(chunk)
                f.flush()
                buf += chunk
                while "\n\n" in buf:
                    frame, buf = buf.split("\n\n", 1)
                    ev, data = parse_frame(frame)
                    if first_event is None:
                        first_event = ev
                        seeded_items = len((data.get("response") or {}).get("output") or [])
                        log(f"first resumed event: {ev} (carries {seeded_items} checkpointed item(s))")
                    if ev in ("response.completed", "response.failed", "response.incomplete"):
                        terminal = ev
                        final_items = len((data.get("response") or {}).get("output") or [])
                        break
            if terminal:
                log(f"terminal event: {terminal} with {final_items} total output item(s)")
    except Exception as exc:
        log(f"reconnect stream ended: {type(exc).__name__}")
    finally:
        f.close()

    expected = NUM_PHASES * 4
    ok = terminal == "response.completed" and final_items == expected
    st["_summary"] = {
        "response_id": st["rid"],
        "pre_crash_checkpoints": st["done"],
        "pre_crash_max_seq": st["max_seq"],
        "first_resumed_event": first_event,
        "items_seeded_on_resume": seeded_items,
        "terminal_event": terminal,
        "final_item_count": final_items,
        "expected_item_count": expected,
        "RECOVERED_FULL_PLAN": ok,
    }
    return ok


def main() -> int:
    if not MAIN_PY.exists():
        sys.exit(f"agent entrypoint not found: {MAIN_PY}")
    RESILIENT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Fresh state each run.
    for sub in ("tasks", "responses", "streams"):
        d = RESILIENT_ROOT / sub
        if d.exists():
            for p in sorted(d.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()

    banner(f"[1/4] Starting local resilient agent (file-backed store at {RESILIENT_ROOT})")
    p1 = start_server("1")

    banner(f"[2/4] Streaming a {NUM_PHASES}-phase research response; will crash after {CRASH_AFTER} checkpoints")
    stream_initial()
    log(f"pre-crash watermark: {st['done']} checkpoints, max seq {st['max_seq']}, response {st['rid']}")
    for _ in range(60):
        if p1.poll() is not None:
            log(f"server '1' exited (rc={p1.returncode}) — crash confirmed")
            break
        time.sleep(0.5)
    else:
        log("server '1' still alive; killing it to simulate the crash")
        os.killpg(os.getpgid(p1.pid), signal.SIGKILL)
    time.sleep(2)

    banner("[3/4] Restarting the agent — startup recovery scan reclaims the in-progress task")
    p2 = start_server("2")
    log("giving recovery a moment to re-invoke the handler ...")
    time.sleep(8)

    banner("[4/4] Reconnecting to the same response and verifying it completes across the crash")
    ok = reconnect_and_verify()

    try:
        os.killpg(os.getpgid(p2.pid), signal.SIGTERM)
    except Exception:
        pass

    banner("RESULT")
    print(json.dumps(st["_summary"], indent=2))
    print(f"\nSSE transcripts: {OUT_DIR / 'sse_initial.txt'}  +  {OUT_DIR / 'sse_resumed.txt'}")
    if ok:
        print("\n\033[32m✓ Resilient recovery succeeded — the response completed the full plan across a crash.\033[0m")
        return 0
    print("\n\033[31m✗ Recovery did not complete the full plan — inspect out/server_2.log.\033[0m")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
