#!/usr/bin/env python3
"""Prove crash RECOVERY by landing the crash on the target's own container.

A fresh `POST /responses` "crash" creates a new session that the gateway may
route to a different replica, so it doesn't kill the container holding the
target durable task's lease. Steering "crash" onto the target response routes
through the Task API to the lease-holding container, whose handler re-enters
with input=="crash" and calls os._exit(137) — killing the right container.
The durable task lease then expires, the platform restarts, and the task is
reclaimed + recovered.

Captures the target session's logs continuously across the restart and greps
for hard recovery evidence (2nd container generation / task reclaim).
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import run_suite as rs
from verify_crash import ContinuousLogCapture, log

RESTART_WAIT_S = 180


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = Path(__file__).parent / "runs" / f"crash-steer-{ts}"
    d.mkdir(parents=True, exist_ok=True)
    log(f"artifacts: {d}")

    # 1. start a durable streaming run; stream until 1 item done
    b = rs.body("Research topic: the history of cryptography [crash-steer]",
                store=True, background=True, stream=True)
    (d / "request.json").write_text(json.dumps(b, indent=2))
    log("starting durable run; streaming until 1 item done ...")
    p = rs.wait_progress_stream(b, d / "stream.precrash.sse", want_items=1, max_wait=120)
    rid, sid = p["response_id"], p["session_id"]
    log(f"  rid={rid}  session={sid}  pre-crash items_done={p['items_done']}")

    # 2. begin continuous log capture for the TARGET session
    cap = ContinuousLogCapture(sid, d / "server.continuous.log")
    cap.start()
    time.sleep(3)

    # 3. steer "crash" onto the SAME durable task -> lease-holding container
    #    re-enters with input=="crash" -> os._exit(137)
    log("steering 'crash' onto the target durable task ...")
    sb = rs.body("crash", store=True, background=True, stream=False, prev=rid)
    steer = rs.post_json(sb)
    (d / "steer.crash.json").write_text(json.dumps(steer["json"], indent=2))
    log(f"  steer response_id={steer.get('response_id')} status_code={steer.get('status_code')}")

    # 4. capture across the restart + recovery window
    log(f"capturing logs across restart for {RESTART_WAIT_S}s ...")
    time.sleep(RESTART_WAIT_S)

    # 5. reconnect to the ORIGINAL response and confirm terminal
    log("reconnecting to verify terminal ...")
    rc = rs.reconnect_stream(rid, 0, d / "reconnect.sse")
    terminal = rc["terminal"]
    log(f"  reconnect terminal={terminal}")
    cap.stop()
    time.sleep(2)

    # 6. grep for hard recovery evidence
    txt = (d / "server.continuous.log").read_text()
    startups = len(set(re.findall(r"AgentServerHost started", txt)))
    host_starting = re.findall(r"AgentServerHost starting on", txt)
    worker_instances = sorted(set(re.findall(r"instance=(worker-\d+-[a-f0-9]+-\d+)", txt)))
    reclaim = len(re.findall(r"[Rr]eclaim|stale task|now active|Recovered task", txt))
    is_recovery = len(re.findall(r"is_recovery|recovered|recovery", txt))
    exit137 = len(re.findall(r"exit.*137|137.*exit|os\._exit|SIGKILL|Container restart", txt))
    # restart proven by a 2nd distinct container generation OR explicit reclaim
    restart = len(worker_instances) > 1 or reclaim > 0
    recovery = restart and terminal == "completed"

    verdict = {
        "rid": rid, "session": sid, "pre_crash_items_done": p["items_done"],
        "steer_status_code": steer.get("status_code"),
        "reconnect_terminal": terminal,
        "distinct_worker_instances": worker_instances,
        "n_host_startups": len(host_starting),
        "reclaim_markers": reclaim, "is_recovery_markers": is_recovery,
        "exit137_markers": exit137,
        "restart_proven": restart, "recovery_proven": recovery,
    }
    (d / "verdict.json").write_text(json.dumps(verdict, indent=2))
    log("\n===== STEERED CRASH-RECOVERY VERDICT =====")
    for k in ("reconnect_terminal", "distinct_worker_instances", "n_host_startups",
              "reclaim_markers", "restart_proven", "recovery_proven"):
        log(f"  {k:26}: {verdict[k]}")
    log(f"artifacts: {d}")


if __name__ == "__main__":
    main()
