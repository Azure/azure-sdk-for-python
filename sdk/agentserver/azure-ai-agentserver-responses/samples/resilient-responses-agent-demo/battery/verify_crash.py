#!/usr/bin/env python3
"""Rigorous crash-recovery proof for resilient-responses-agent-demo.

Proves recovery DETERMINISTICALLY, without depending on scraping server logs:
(a) a hard crash is fired and the streaming connection drops (the sandbox dies),
(b) pre-crash checkpointed progress is observed, and (c) the response reaches
`completed` AFTER the crash — read via a NON-STREAMING GET snapshot (no stream
TTL constraint, unlike an SSE reconnect that may have expired across the restart).
Continuous `azd ai agent monitor` log capture + marker greps are still performed,
but only as SUPPLEMENTARY evidence — they no longer gate the verdict.

Usage: python verify_crash.py  (exits non-zero if recovery is not proven)
Artifacts: runs/crash-proof-<ts>/{stream.precrash.sse,poll.terminal.jsonl,reconnect.sse,server.continuous.log,verdict.json}
"""
from __future__ import annotations

import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import run_suite as rs

AGENT = rs.AGENT
RESTART_WAIT_S = 175


def log(m):
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {m}", flush=True)


class ContinuousLogCapture(threading.Thread):
    """Respawn `azd ai agent monitor --session-id` and append to a file until
    stopped, so logs survive the container death/restart boundary."""

    def __init__(self, session_id: str, out_path: Path):
        super().__init__(daemon=True)
        self.session_id = session_id
        self.out_path = out_path
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        with self.out_path.open("w") as f:
            while not self._stop.is_set():
                f.write(f"\n--- monitor attach @ {datetime.now(timezone.utc).isoformat()} ---\n")
                f.flush()
                try:
                    p = subprocess.Popen(
                        ["azd", "ai", "agent", "monitor", AGENT, "--session-id", self.session_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )
                    while not self._stop.is_set():
                        line = p.stdout.readline()
                        if line == "":
                            break  # monitor exited (likely container died)
                        f.write(line)
                        f.flush()
                    try:
                        p.terminate()
                    except Exception:
                        pass
                except Exception as e:
                    f.write(f"(monitor spawn error: {e!r})\n")
                    f.flush()
                if not self._stop.is_set():
                    time.sleep(3)  # brief backoff before respawn


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = Path(__file__).parent / "runs" / f"crash-proof-{ts}"
    d.mkdir(parents=True, exist_ok=True)
    log(f"artifacts: {d}")

    # 1. start a resilient streaming run; stop streaming once 1 item is checkpointed
    b = rs.body("Research topic: the history of lighthouses [crash-proof]", store=True, background=True, stream=True)
    (d / "request.json").write_text(json.dumps(b, indent=2))
    log("starting resilient run; streaming until 1 item done ...")
    p = rs.wait_progress_stream(b, d / "stream.precrash.sse", want_items=1, max_wait=120)
    rid, sid = p["response_id"], p["session_id"]
    log(f"  rid={rid}  session={sid}  pre-crash items_done={p['items_done']}")

    # 2. begin continuous log capture for the target session
    cap = ContinuousLogCapture(sid, d / "server.continuous.log")
    cap.start()
    time.sleep(3)

    # 3. fire crash (kills the single container instance -> takes target handler down)
    log("firing crash (os._exit(137)) ...")
    crash = rs.fire_crash()
    (d / "crash.json").write_text(json.dumps(crash, indent=2))

    # 4. keep capturing across the restart + recovery window
    log(f"capturing logs across restart for {RESTART_WAIT_S}s ...")
    time.sleep(RESTART_WAIT_S)

    # 5. AUTHORITATIVE terminal via a NON-STREAMING GET poll. The SSE stream may
    #    have expired across the restart window (stream TTL), so the stored
    #    response snapshot — not the stream — is the source of truth for the
    #    terminal status.
    log("polling GET /responses/<rid> for the authoritative terminal ...")
    term_res = rs.poll_terminal(rid, d / "poll.terminal.jsonl")
    terminal = (term_res.get("json") or {}).get("status")
    log(f"  authoritative terminal={terminal}")

    # 5b. Supplementary: best-effort stream reconnect (its TTL may have expired
    #     across the restart — used as extra evidence, never the verdict gate).
    try:
        rc = rs.reconnect_stream(rid, 0, d / "reconnect.sse")
        stream_terminal = rc.get("terminal")
    except Exception as e:  # pylint: disable=broad-except  # noqa: BLE001
        stream_terminal = f"(unavailable: {e!r})"
    log(f"  stream terminal (supplementary)={stream_terminal}")

    cap.stop()
    time.sleep(2)

    # 6. SUPPLEMENTARY log evidence — recorded for diagnostics, NOT the gate.
    txt = (d / "server.continuous.log").read_text()
    import re

    markers = {
        "container_restart_attach": txt.count("monitor attach"),
        "taskmanager_starting": len(re.findall(r"TaskManager starting", txt)),
        "reclaimed_stale_task": len(re.findall(r"[Rr]eclaim.*stale|stale task", txt)),
        "recovered_task_active": len(re.findall(r"Recovered task is now active|Recovered task|now active", txt)),
        "is_recovery_true": len(re.findall(r"is_recovery[ =:]+True|recovery", txt)),
        "generation_increment": len(re.findall(r"generation", txt)),
        "exit_137": len(re.findall(r"137|SIGKILL|_exit", txt)),
        "host_started": len(re.findall(r"AgentServerHost started", txt)),
    }
    worker_instances = sorted(set(re.findall(r"worker-\d+-[a-f0-9]+-\d+", txt)))
    taskmgr_instances = sorted(set(re.findall(r"instance=(worker-\d+-[a-f0-9]+-\d+)", txt)))

    # ── DETERMINISTIC recovery proof (no log scraping required) ─────────────
    # Recovery is proven by three authoritative facts: (a) we fired a hard crash
    # and the streaming connection dropped (the sandbox died), (b) we observed
    # pre-crash checkpointed progress, and (c) the response reached `completed`
    # AFTER the crash — read via the non-streaming GET snapshot (no stream TTL).
    # The log markers below are supplementary evidence only.
    crash_confirmed = bool(crash.get("sandbox_dropped"))
    pre_crash_progress = p["items_done"] >= 1
    recovery_proven = crash_confirmed and pre_crash_progress and terminal == "completed"
    # Supplementary, log-derived restart evidence (informational).
    log_restart_evidence = len(worker_instances) > 1 or markers["reclaimed_stale_task"] > 0

    verdict = {
        "rid": rid,
        "session": sid,
        "pre_crash_items_done": p["items_done"],
        "crash_confirmed": crash_confirmed,
        "crash_session": crash.get("crash_session"),
        "authoritative_terminal": terminal,
        "recovery_proven": recovery_proven,
        # --- supplementary evidence (not part of the verdict gate) ---
        "stream_terminal_supplementary": stream_terminal,
        "log_restart_evidence": log_restart_evidence,
        "markers": markers,
        "worker_instances": worker_instances,
        "taskmanager_instances": taskmgr_instances,
        "log_lines": txt.count("\n"),
    }
    (d / "verdict.json").write_text(json.dumps(verdict, indent=2))
    log("\n===== CRASH-RECOVERY VERDICT =====")
    log(f"  crash confirmed (drop)  : {crash_confirmed}")
    log(f"  pre-crash progress      : {pre_crash_progress} (items_done={p['items_done']})")
    log(f"  authoritative terminal  : {terminal}")
    log(f"  RECOVERY PROVEN         : {recovery_proven}")
    log("  --- supplementary ---")
    log(f"  stream terminal         : {stream_terminal}")
    log(f"  distinct worker insts   : {worker_instances}")
    log(f"  reclaimed_stale_task    : {markers['reclaimed_stale_task']}")
    log(f"  recovered_task_active   : {markers['recovered_task_active']}")
    log(f"  log restart evidence    : {log_restart_evidence}")
    log(f"artifacts: {d}")

    # Non-zero exit if the deterministic proof failed (usable as a battery gate).
    if not recovery_proven:
        raise SystemExit(
            f"crash-recovery NOT proven: crash_confirmed={crash_confirmed} "
            f"pre_crash_progress={pre_crash_progress} terminal={terminal!r}"
        )


if __name__ == "__main__":
    main()
