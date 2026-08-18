# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Process-isolated handler execution for resilient tasks.

The user's task handler ``fn(ctx)`` is run in a **separate child Python
process** launched via :func:`asyncio.create_subprocess_exec`. The main
process keeps ownership of the task store, lease, watchdog, and drain
logic; the child is a pure compute unit. This makes a per-turn ``timeout``
enforceable: if a handler ignores the cooperative cancel, the main process
can ``kill()`` the child — a guaranteed stop that works even on a CPU-bound
loop, without corrupting the main process or co-located tasks.

Cross-OS: uses ``create_subprocess_exec`` (spawn) so it runs on Linux,
macOS, and Windows. The handler is resolved **by name** in the child (never
pickled); ``ctx`` is proxied over a small length-prefixed-JSON protocol.

Channels (from the child's point of view):

* **stdin**  — control messages from main (cancel / shutdown / round-trip
  responses).
* **stdout** — protocol messages to main (stream emits, metadata flush /
  pending-count requests, terminal outcome). The child redirects its
  ``sys.stdout`` to stderr on startup so user ``print()`` cannot corrupt the
  protocol; the true fd 1 is dup'd to a private protocol fd.
* **stderr** — user logs, forwarded to the main process logger.

This module is BOTH the parent-side runner (imported by the task manager)
AND the child entrypoint (``python -m
azure.ai.agentserver.core.tasks._isolation``).
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import logging
import multiprocessing
import os
import socket
import struct
import sys
import threading
import traceback
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger("azure.ai.agentserver.tasks.isolation")

# ---------------------------------------------------------------------------
# Wire protocol — length-prefixed (4-byte big-endian) UTF-8 JSON.
# ---------------------------------------------------------------------------

_LEN = struct.Struct(">I")

# Parent -> child
MSG_RUN = "run"
MSG_CANCEL = "cancel"
MSG_SHUTDOWN = "shutdown"
MSG_RESP = "resp"  # response to a child->parent round-trip request

# Child -> parent
MSG_EMIT = "emit"
MSG_STREAM_CLOSE = "stream_close"
MSG_REQ = "req"  # round-trip request (flush / last_cursor / pending_count)
MSG_RESULT = "result"
MSG_ERROR = "error"
MSG_SUSPEND = "suspend"
MSG_EXIT_FOR_RECOVERY = "exit_for_recovery"

# Round-trip request kinds (payload of MSG_REQ)
REQ_FLUSH = "flush"
REQ_LAST_CURSOR = "last_cursor"
REQ_PENDING_COUNT = "pending_count"


def _pack(obj: dict) -> bytes:
    body = json.dumps(obj, default=_json_default).encode("utf-8")
    return _LEN.pack(len(body)) + body


def _json_default(o: Any) -> Any:
    # Best-effort fallback for non-JSON values crossing the boundary.
    return repr(o)


def _blocking_read_exact(fd: int, n: int) -> Optional[bytes]:
    """Read exactly ``n`` bytes from a raw fd; None on EOF."""
    buf = bytearray()
    while len(buf) < n:
        try:
            chunk = os.read(fd, n - len(buf))
        except OSError:
            return None
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)


def _blocking_read_msg(fd: int) -> Optional[dict]:
    header = _blocking_read_exact(fd, _LEN.size)
    if header is None:
        return None
    (length,) = _LEN.unpack(header)
    body = _blocking_read_exact(fd, length)
    if body is None:
        return None
    return json.loads(body.decode("utf-8"))


# ===========================================================================
# CHILD SIDE
# ===========================================================================


class _HybridCancel:
    """A cancellation signal usable both by a CPU-bound poller and an awaiter.

    ``is_set()`` reads a plain ``bool`` flipped directly by the control
    thread, so a CPU-bound handler that polls it sees the cancel *immediately*
    without the event loop needing to run. ``wait()`` awaits an
    :class:`asyncio.Event` woken via ``call_soon_threadsafe`` so a
    cooperating handler can ``await ctx.cancel.wait()`` as well.

    Mirrors the ``asyncio.Event`` surface the handler uses (``is_set`` /
    ``wait`` / ``set``).
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._flag = False
        self._event = asyncio.Event()

    def set_from_thread(self) -> None:
        self._flag = True
        try:
            self._loop.call_soon_threadsafe(self._event.set)
        except RuntimeError:
            # Loop already closed — the flag is still observable via is_set().
            pass

    def set(self) -> None:
        self._flag = True
        self._event.set()

    def is_set(self) -> bool:
        return self._flag

    async def wait(self) -> bool:
        if self._flag:
            return True
        await self._event.wait()
        return True


class _ChildProtocol:
    """Child-side protocol endpoint: reads control on a thread, writes to main."""

    def __init__(self, in_fd: int, out_fd: int, loop: asyncio.AbstractEventLoop) -> None:
        self._in_fd = in_fd
        self._out_fd = out_fd
        self._loop = loop
        self._write_lock = threading.Lock()
        self._req_seq = 0
        self._pending: dict[Any, "asyncio.Future[Any]"] = {}
        self.cancel = _HybridCancel(loop)
        self.shutdown = _HybridCancel(loop)
        self.timeout_exceeded = False
        self.cancel_requested = False
        self.pending = 0
        self._ctx: Any = None
        self._reader_thread: Optional[threading.Thread] = None
        self._closed = False
        # --- reuse (persistent worker) support ---------------------------
        # When enabled, subsequent RUN messages for later turns arrive on the
        # control channel and are pushed onto this queue for the turn loop.
        self._turn_mode = False
        self._run_queue: "Optional[asyncio.Queue[Optional[dict]]]" = None

    def enable_turn_mode(self) -> None:
        """Switch the protocol into persistent multi-turn mode.

        Creates the run queue the reader thread feeds with later-turn RUN
        snapshots. Must be called from the event-loop thread.
        """
        self._turn_mode = True
        self._run_queue = asyncio.Queue()

    def begin_turn(self) -> None:
        """Reset per-turn cancel state before a new turn's ctx is built.

        ``shutdown`` is process-scoped and intentionally NOT reset. ``cancel``
        and the cause booleans are per-turn — a fresh :class:`_HybridCancel`
        ensures a cooperatively-honored cancel from a prior turn does not leak
        into the next turn's ``ctx.cancel``.
        """
        self.cancel = _HybridCancel(self._loop)
        self.timeout_exceeded = False
        self.cancel_requested = False
        self.pending = 0
        self._ctx = None

    async def next_run(self) -> Optional[dict]:
        """Await the next turn's RUN snapshot (or ``None`` on shutdown/EOF)."""
        assert self._run_queue is not None
        return await self._run_queue.get()

    def bind_context(self, ctx: Any) -> None:
        self._ctx = ctx

    # ---- low-level send (thread-safe, blocking os.write for backpressure) ---
    def _send(self, obj: dict) -> None:
        data = _pack(obj)
        with self._write_lock:
            try:
                os.write(self._out_fd, data)
            except OSError:
                pass

    # ---- control reader thread ------------------------------------------
    def start_reader(self) -> None:
        self._reader_thread = threading.Thread(
            target=self._reader_loop, name="agentserver-worker-control", daemon=True
        )
        self._reader_thread.start()

    def _reader_loop(self) -> None:
        while not self._closed:
            msg = _blocking_read_msg(self._in_fd)
            if msg is None:
                # Parent closed the control channel — treat as shutdown.
                self.shutdown.set_from_thread()
                if self._turn_mode and self._run_queue is not None:
                    self._loop.call_soon_threadsafe(self._run_queue.put_nowait, None)
                return
            t = msg.get("t")
            if t == MSG_RUN and self._turn_mode:
                # Later-turn RUN (turns 2..N of a reused worker). Hand the
                # snapshot to the turn loop via the run queue.
                if self._run_queue is not None:
                    self._loop.call_soon_threadsafe(self._run_queue.put_nowait, msg.get("snapshot"))
                continue
            if t == MSG_CANCEL:
                if msg.get("timeout_exceeded"):
                    self.timeout_exceeded = True
                if msg.get("cancel_requested"):
                    self.cancel_requested = True
                if "pending" in msg:
                    self.pending = msg["pending"]
                # Set the cause booleans on ctx BEFORE cancel (C-CAN-2 ordering)
                # directly from this thread so a CPU-bound handler that polls
                # ctx.cancel.is_set() then reads the causes sees them set.
                if self._ctx is not None:
                    self._ctx.timeout_exceeded = self.timeout_exceeded
                    self._ctx.cancel_requested = self.cancel_requested
                self.cancel.set_from_thread()
            elif t == MSG_SHUTDOWN:
                self.shutdown.set_from_thread()
                if self._turn_mode and self._run_queue is not None:
                    # Unblock a turn loop waiting in next_run() so it can exit.
                    self._loop.call_soon_threadsafe(self._run_queue.put_nowait, None)
            elif t == MSG_RESP:
                rid = msg.get("id")
                fut = self._pending.pop(rid, None)
                if fut is not None:
                    self._loop.call_soon_threadsafe(_safe_set_result, fut, msg.get("value"))

    # ---- round-trip request from the handler coroutine ------------------
    async def request(self, kind: str, payload: dict) -> Any:
        self._req_seq += 1
        rid = self._req_seq
        fut: "asyncio.Future[Any]" = self._loop.create_future()
        self._pending[rid] = fut
        self._send({"t": MSG_REQ, "id": rid, "kind": kind, **payload})
        return await fut

    # ---- one-way notifications ------------------------------------------
    def emit(self, stream_id: str, payload: Any, close: bool) -> None:
        self._send({"t": MSG_EMIT, "stream_id": stream_id, "payload": payload, "close": close})

    def stream_close(self, stream_id: str) -> None:
        self._send({"t": MSG_STREAM_CLOSE, "stream_id": stream_id})

    def terminal(self, obj: dict) -> None:
        self._send(obj)

    def close(self) -> None:
        self._closed = True


def _safe_set_result(fut: "asyncio.Future[Any]", value: Any) -> None:
    if not fut.done():
        fut.set_result(value)


class _ProxyStream:
    """Child-side EventStream proxy: forwards emit/close/last_cursor to main."""

    def __init__(self, stream_id: str, proto: _ChildProtocol) -> None:
        self._id = stream_id
        self._proto = proto

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        self._proto.emit(self._id, payload, close)

    async def close(self) -> None:
        self._proto.stream_close(self._id)

    async def last_cursor(self) -> Optional[int]:
        return await self._proto.request(REQ_LAST_CURSOR, {"stream_id": self._id})

    def subscribe(self, *, after: Optional[int] = None):  # pragma: no cover
        raise RuntimeError("subscribe() is not available inside an isolated task worker")


def _install_stream_proxy(proto: _ChildProtocol) -> None:
    """Point the streams singleton's factory at the IPC proxy (Gap 1)."""
    try:
        from azure.ai.agentserver.core.streaming import streams  # pylint: disable=import-outside-toplevel

        streams._factory = lambda _id: _ProxyStream(_id, proto)  # noqa: SLF001
    except Exception:  # pylint: disable=broad-except
        logger.debug("streams proxy not installed (streaming module unavailable)", exc_info=True)


class _ProxyMetadata:
    """Child-side TaskMetadata replacement backed by IPC flush to main.

    Behaves like the default-namespace mapping the handler uses; named
    namespaces are supported via the callable protocol. Data is plain JSON.
    The full state rides the terminal message so main can persist any
    mutations the handler did not explicitly flush.
    """

    def __init__(self, proto: _ChildProtocol, initial: dict, namespace: Optional[str] = None,
                 store: "Optional[dict[Any, dict]]" = None) -> None:
        self._proto = proto
        self._ns = namespace
        # store maps namespace(None|str) -> dict; shared across facades.
        self._store: "dict[Any, dict]" = store if store is not None else {None: dict(initial or {})}
        if namespace not in self._store:
            self._store[namespace] = {}

    def _data(self) -> dict:
        return self._store[self._ns]

    def __getitem__(self, k): return self._data()[k]
    def __setitem__(self, k, v): self._data()[k] = v
    def __delitem__(self, k): del self._data()[k]
    def __iter__(self): return iter(self._data())
    def __len__(self): return len(self._data())
    def __contains__(self, k): return k in self._data()

    def get(self, k, default=None): return self._data().get(k, default)
    def pop(self, k, default=None): return self._data().pop(k, default)

    def __call__(self, namespace: str) -> "_ProxyMetadata":
        return _ProxyMetadata(self._proto, {}, namespace=namespace, store=self._store)

    async def flush(self) -> None:
        await self._proto.request(REQ_FLUSH, {"namespace": self._ns, "data": dict(self._data())})

    async def _flush_all(self) -> None:
        for ns, data in self._store.items():
            await self._proto.request(REQ_FLUSH, {"namespace": ns, "data": dict(data)})

    def snapshot(self) -> dict:
        # {namespace-or-"__default__": data}
        return {("__default__" if ns is None else ns): dict(d) for ns, d in self._store.items()}


def _build_child_context(snapshot: dict, proto: _ChildProtocol) -> Any:
    """Construct a child-local TaskContext-like object for the handler."""
    from ._context import TaskContext  # pylint: disable=import-outside-toplevel

    meta = _ProxyMetadata(proto, snapshot.get("metadata") or {})

    ctx: Any = TaskContext(
        task_id=snapshot["task_id"],
        session_id=snapshot.get("session_id") or "",
        input=snapshot.get("input"),
        metadata=meta,  # type: ignore[arg-type]
        retry_attempt=snapshot.get("retry_attempt", 0),
        recovery_count=snapshot.get("recovery_count", 0),
        entry_mode=snapshot.get("entry_mode", "fresh"),
        is_steered_turn=snapshot.get("is_steered_turn", False),
        input_id=snapshot.get("input_id"),
    )
    # Replace the cancel/shutdown events with the hybrid (thread-settable) ones.
    # (cancel / shutdown / _pending_count_provider / cause booleans are all in
    # TaskContext.__slots__, so we set only those — no arbitrary attributes.)
    ctx.cancel = proto.cancel  # type: ignore[assignment]
    ctx.shutdown = proto.shutdown  # type: ignore[assignment]
    ctx._pending_count_provider = lambda: proto.pending  # type: ignore[attr-defined]
    proto.bind_context(ctx)
    return ctx, meta


async def _run_child(snapshot: dict) -> None:
    loop = asyncio.get_running_loop()

    # --- fd setup: reserve fd1 for the protocol, redirect stdout->stderr ----
    protocol_out_fd = os.dup(1)
    os.dup2(2, 1)  # user print() now goes to stderr
    in_fd = 0

    proto = _ChildProtocol(in_fd=in_fd, out_fd=protocol_out_fd, loop=loop)
    _install_stream_proxy(proto)

    # --- resolve the handler by name (Gap 2) --------------------------------
    handler = _resolve_handler(snapshot["handler_module"], snapshot["handler_name"])

    ctx, meta = _build_child_context(snapshot, proto)

    # Start the control reader ONLY after ctx is bound, so an early CANCEL
    # (buffered in the pipe before the handler starts) still has a ctx to set
    # its cause booleans on.
    proto.start_reader()

    try:
        result = await handler(ctx)
        term = _classify_terminal(result, meta)
    except BaseException as exc:  # noqa: BLE001  pylint: disable=broad-except
        proto.terminal({
            "t": MSG_ERROR,
            "exc_type": type(exc).__name__,
            "exc_msg": str(exc)[:4000],
            "traceback": traceback.format_exc()[:8000],
            "metadata": meta.snapshot(),
        })
    else:
        proto.terminal(term)
    finally:
        proto.close()


def _classify_terminal(result: Any, meta: _ProxyMetadata) -> dict:
    from ._context import _ExitForRecovery, _Suspended  # pylint: disable=import-outside-toplevel

    md = meta.snapshot()
    if isinstance(result, _ExitForRecovery):
        return {"t": MSG_EXIT_FOR_RECOVERY, "metadata": md}
    if isinstance(result, _Suspended):
        return {"t": MSG_SUSPEND, "reason": result.reason, "output": result.output, "metadata": md}
    return {"t": MSG_RESULT, "value": result, "metadata": md}


def _resolve_handler(module_name: str, handler_name: str) -> Callable[..., Awaitable[Any]]:
    import importlib  # pylint: disable=import-outside-toplevel

    importlib.import_module(module_name)
    # Optional extra bootstrap modules.
    extra = os.environ.get("AGENTSERVER_WORKER_BOOTSTRAP_MODULES", "")
    for m in (x.strip() for x in extra.split(",") if x.strip()):
        try:
            importlib.import_module(m)
        except Exception:  # pylint: disable=broad-except
            logger.warning("worker: failed to import bootstrap module %s", m, exc_info=True)

    from ._decorator import _REGISTERED_DESCRIPTORS  # pylint: disable=import-outside-toplevel

    for name, fn, _opts in _REGISTERED_DESCRIPTORS:
        if name == handler_name:
            return fn
    raise RuntimeError(f"worker: handler {handler_name!r} not found after importing {module_name!r}")


async def _run_child_reusable(first_snapshot: dict) -> None:
    """Persistent child loop: run turns until shutdown/EOF (reuse mode).

    Same per-turn semantics as :func:`_run_child`, but the process stays alive
    between turns. fd setup and the control-reader thread are established ONCE;
    each turn resets cancel state (:meth:`_ChildProtocol.begin_turn`), rebuilds
    a fresh ``ctx`` from the turn's snapshot, runs the handler, emits the
    per-turn terminal message (WITHOUT closing stdout), then waits for the next
    RUN. Exits on MSG_SHUTDOWN or control-channel EOF.
    """
    loop = asyncio.get_running_loop()

    protocol_out_fd = os.dup(1)
    os.dup2(2, 1)  # user print() -> stderr; true fd1 reserved for protocol
    proto = _ChildProtocol(in_fd=0, out_fd=protocol_out_fd, loop=loop)
    _install_stream_proxy(proto)
    proto.enable_turn_mode()

    snapshot: Optional[dict] = first_snapshot
    reader_started = False
    while snapshot is not None:
        proto.begin_turn()
        handler = _resolve_handler(snapshot["handler_module"], snapshot["handler_name"])
        ctx, meta = _build_child_context(snapshot, proto)
        if not reader_started:
            # Start the control reader ONLY after the first ctx is bound so an
            # early buffered CANCEL still has a ctx to set its causes on (same
            # invariant as the one-shot path). The reader persists for the life
            # of the worker and also delivers later-turn RUN messages.
            proto.start_reader()
            reader_started = True
        try:
            result = await handler(ctx)
            term = _classify_terminal(result, meta)
        except BaseException as exc:  # noqa: BLE001  pylint: disable=broad-except
            term = {
                "t": MSG_ERROR,
                "exc_type": type(exc).__name__,
                "exc_msg": str(exc)[:4000],
                "traceback": traceback.format_exc()[:8000],
                "metadata": meta.snapshot(),
            }
        proto.terminal(term)  # per-turn terminal; stdout stays open for reuse
        snapshot = await proto.next_run()
    proto.close()


def _child_main() -> None:
    # First message on stdin is the RUN payload.
    run_msg = _blocking_read_msg(0)
    if run_msg is None or run_msg.get("t") != MSG_RUN:
        sys.stderr.write("worker: expected RUN message on stdin\n")
        sys.exit(2)
    try:
        if run_msg.get("reuse"):
            asyncio.run(_run_child_reusable(run_msg["snapshot"]))
        else:
            asyncio.run(_run_child(run_msg["snapshot"]))
    except Exception:  # pylint: disable=broad-except
        traceback.print_exc()
        sys.exit(1)


# ===========================================================================
# PARENT SIDE
# ===========================================================================


class IsolationBridge:
    """Main-process callbacks the worker proxies back to.

    All persistence, streaming, and steering state stays in main; the child
    only forwards requests here.

    :param apply_flush: ``async (namespace|None, data) -> None`` — persist one
        metadata namespace (also keeps main's ``ctx.metadata`` in sync).
    :param stream_emit: ``async (stream_id, payload, close) -> None``.
    :param stream_close: ``async (stream_id) -> None``.
    :param stream_last_cursor: ``async (stream_id) -> int|None``.
    :param get_pending_count: ``() -> int``.
    :param apply_final_metadata: ``(snapshot: dict) -> None`` — apply the
        child's terminal metadata snapshot onto main's ``ctx.metadata``.
    """

    def __init__(
        self,
        *,
        apply_flush: Callable[[Optional[str], dict], Awaitable[None]],
        stream_emit: Callable[[str, Any, bool], Awaitable[None]],
        stream_close: Callable[[str], Awaitable[None]],
        stream_last_cursor: Callable[[str], Awaitable[Optional[int]]],
        get_pending_count: Callable[[], int],
        apply_final_metadata: Callable[[dict], None],
    ) -> None:
        self.apply_flush = apply_flush
        self.stream_emit = stream_emit
        self.stream_close = stream_close
        self.stream_last_cursor = stream_last_cursor
        self.get_pending_count = get_pending_count
        self.apply_final_metadata = apply_final_metadata


class WorkerCrash(Exception):
    """Raised by :meth:`IsolatedRun.outcome` when the child exited without a
    terminal message and was NOT killed by us (OOM/segfault/unexpected)."""


class IsolatedRun:
    """A launched worker process running one handler turn.

    ``outcome()`` reproduces ``await fn(ctx)``: returns the handler's return
    value (or a ``_Suspended`` / ``_ExitForRecovery`` sentinel), or raises the
    handler's exception (or :class:`WorkerCrash` on unexpected child death).
    ``kill()`` force-stops the worker (the timeout hard cap).
    """

    def __init__(self, proc: "asyncio.subprocess.Process", bridge: IsolationBridge) -> None:
        self._proc = proc
        self._bridge = bridge
        self._we_killed_it = False
        self._terminal: Optional[dict] = None
        self._reader_task: Optional[asyncio.Task[None]] = None
        self._stderr_task: Optional[asyncio.Task[None]] = None
        self._write_lock = asyncio.Lock()

    @property
    def pid(self) -> int:
        return self._proc.pid

    async def _send(self, obj: dict) -> None:
        assert self._proc.stdin is not None
        async with self._write_lock:
            self._proc.stdin.write(_pack(obj))
            try:
                await self._proc.stdin.drain()
            except (ConnectionResetError, BrokenPipeError):
                pass

    def kill(self) -> None:
        self._we_killed_it = True
        try:
            self._proc.kill()
        except ProcessLookupError:
            pass

    async def signal_cancel(self, *, timeout_exceeded: bool, cancel_requested: bool) -> None:
        await self._send({
            "t": MSG_CANCEL,
            "timeout_exceeded": timeout_exceeded,
            "cancel_requested": cancel_requested,
        })

    async def signal_shutdown(self) -> None:
        await self._send({"t": MSG_SHUTDOWN})

    # ---- the always-draining stdout reader (Gap 1/5: no deadlock) --------
    async def _read_loop(self) -> None:
        assert self._proc.stdout is not None
        reader = self._proc.stdout
        while True:
            try:
                header = await reader.readexactly(_LEN.size)
            except asyncio.IncompleteReadError:
                break
            (length,) = _LEN.unpack(header)
            try:
                body = await reader.readexactly(length)
            except asyncio.IncompleteReadError:
                break
            msg = json.loads(body.decode("utf-8"))
            await self._dispatch(msg)
            if msg.get("t") in (MSG_RESULT, MSG_ERROR, MSG_SUSPEND, MSG_EXIT_FOR_RECOVERY):
                self._terminal = msg
                # keep draining until EOF so nothing blocks the child

    async def _dispatch(self, msg: dict) -> None:
        t = msg.get("t")
        if t == MSG_EMIT:
            await self._bridge.stream_emit(msg["stream_id"], msg["payload"], msg.get("close", False))
        elif t == MSG_STREAM_CLOSE:
            await self._bridge.stream_close(msg["stream_id"])
        elif t == MSG_REQ:
            await self._handle_request(msg)
        # terminal messages are captured in _read_loop

    async def _handle_request(self, msg: dict) -> None:
        rid = msg.get("id")
        kind = msg.get("kind")
        value: Any = None
        try:
            if kind == REQ_FLUSH:
                await self._bridge.apply_flush(msg.get("namespace"), msg.get("data") or {})
            elif kind == REQ_LAST_CURSOR:
                value = await self._bridge.stream_last_cursor(msg["stream_id"])
            elif kind == REQ_PENDING_COUNT:
                value = self._bridge.get_pending_count()
        except Exception:  # pylint: disable=broad-except
            logger.warning("isolation: bridge request %s failed", kind, exc_info=True)
        await self._send({"t": MSG_RESP, "id": rid, "value": value})

    async def _forward_stderr(self) -> None:
        if self._proc.stderr is None:
            return  # fork transport: child shares the parent's stderr directly
        while True:
            line = await self._proc.stderr.readline()
            if not line:
                break
            logger.info("[worker %s] %s", self._proc.pid, line.decode("utf-8", "replace").rstrip())

    async def outcome(self) -> Any:
        # Wait for the reader to finish (child closed stdout) then the process.
        if self._reader_task is not None:
            try:
                await self._reader_task
            except Exception:  # pylint: disable=broad-except
                logger.warning("isolation: reader loop failed", exc_info=True)
        await self._proc.wait()  # reap
        if self._stderr_task is not None:
            self._stderr_task.cancel()

        term = self._terminal
        if term is not None:
            self._bridge.apply_final_metadata(term.get("metadata") or {})
            return _reconstruct_outcome(term)
        # No terminal message.
        if self._we_killed_it:
            # Intentional hard-cap kill — the caller (manager) handles the
            # lifecycle handoff; signal via a sentinel exception.
            raise _WorkerKilled()
        raise WorkerCrash(f"worker {self._proc.pid} exited (rc={self._proc.returncode}) without a terminal message")


class _WorkerKilled(Exception):
    """Internal: the worker was killed by us for the timeout hard cap."""


def _reconstruct_outcome(term: dict) -> Any:
    from ._context import _ExitForRecovery, _Suspended  # pylint: disable=import-outside-toplevel

    t = term["t"]
    if t == MSG_RESULT:
        return term.get("value")
    if t == MSG_SUSPEND:
        return _Suspended(reason=term.get("reason"), output=term.get("output"))
    if t == MSG_EXIT_FOR_RECOVERY:
        return _ExitForRecovery()
    # MSG_ERROR
    exc_type = term.get("exc_type", "Exception")
    exc_msg = term.get("exc_msg", "")
    if exc_type in ("CancelledError", "TaskCancelled"):
        raise asyncio.CancelledError()
    raise _IsolatedHandlerError(exc_type, exc_msg, term.get("traceback", ""))


class _IsolatedHandlerError(Exception):
    """A handler exception reconstructed across the process boundary."""

    def __init__(self, exc_type: str, message: str, tb: str) -> None:
        super().__init__(f"{exc_type}: {message}")
        self.exc_type = exc_type
        self.original_message = message
        self.remote_traceback = tb


def _worker_command(python_exe: Optional[str] = None) -> list[str]:
    return [python_exe or sys.executable, "-m", "azure.ai.agentserver.core.tasks._isolation"]


async def start_isolated(snapshot: dict, bridge: IsolationBridge, *, python_exe: Optional[str] = None) -> IsolatedRun:
    """Launch a worker process and begin pumping its protocol.

    :param snapshot: The ctx snapshot + handler_module/handler_name.
    :param bridge: Main-process callbacks the worker proxies to.
    :return: A running :class:`IsolatedRun`.
    """
    proc = await asyncio.create_subprocess_exec(
        *_worker_command(python_exe),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=os.environ.copy(),
    )
    run = IsolatedRun(proc, bridge)
    run._reader_task = asyncio.create_task(run._read_loop())  # noqa: SLF001
    run._stderr_task = asyncio.create_task(run._forward_stderr())  # noqa: SLF001
    await run._send({"t": MSG_RUN, "snapshot": snapshot})  # noqa: SLF001
    return run


# ===========================================================================
# PERSISTENT (per-chain reuse) WORKER — §13.6
# ===========================================================================


class PersistentWorker:
    """A long-lived worker process reused across the turns of one chain.

    Unlike :class:`IsolatedRun` (one process per turn), a ``PersistentWorker``
    imports the app **once** and runs many turns via :meth:`run_turn`. The child
    stays alive between turns (waiting for the next RUN), so an N-turn chain
    pays the ~1-2s import ONCE instead of N times. The main process still owns
    persistence/streaming/steering (proxied per turn via a fresh
    :class:`IsolationBridge`) and can :meth:`kill` the worker for the timeout
    hard cap exactly like the per-turn path.

    Lifecycle is managed by the task manager: a registry keyed by ``task_id``
    holds the worker across suspend/resume; it is torn down on hard-cap kill,
    crash, idle-TTL eviction, or manager shutdown.
    """

    def __init__(self, proc: "asyncio.subprocess.Process") -> None:
        self._proc = proc
        self._current_bridge: Optional[IsolationBridge] = None
        self._turn_future: "Optional[asyncio.Future[dict]]" = None
        self._reader_task: Optional[asyncio.Task[None]] = None
        self._stderr_task: Optional[asyncio.Task[None]] = None
        self._write_lock = asyncio.Lock()
        self._alive = True
        self._we_killed = False
        self.in_flight = False
        try:
            self.last_active_monotonic = asyncio.get_running_loop().time()
        except RuntimeError:
            self.last_active_monotonic = 0.0

    @property
    def pid(self) -> int:
        return self._proc.pid

    @property
    def alive(self) -> bool:
        return self._alive

    async def _send(self, obj: dict) -> None:
        if self._proc.stdin is None:
            return
        async with self._write_lock:
            try:
                self._proc.stdin.write(_pack(obj))
                await self._proc.stdin.drain()
            except (ConnectionResetError, BrokenPipeError):
                pass

    async def run_turn(self, snapshot: dict, bridge: IsolationBridge) -> Any:
        """Run one turn on this worker; reproduces ``await fn(ctx)``.

        :param snapshot: The ctx snapshot + handler_module/handler_name.
        :param bridge: Per-turn main-process callbacks the worker proxies to.
        :return: The handler's return value / suspend / exit sentinel.
        :raises _WorkerKilled: The worker was hard-cap killed during this turn.
        :raises WorkerCrash: The worker died unexpectedly during this turn.
        """
        if not self._alive:
            raise WorkerCrash("persistent worker is not alive")
        loop = asyncio.get_running_loop()
        self._current_bridge = bridge
        self._turn_future = loop.create_future()
        self.in_flight = True
        try:
            await self._send({"t": MSG_RUN, "snapshot": snapshot, "reuse": True})
            term = await self._turn_future
        finally:
            self.in_flight = False
            self._turn_future = None
            self._current_bridge = None
            self.last_active_monotonic = loop.time()
        bridge.apply_final_metadata(term.get("metadata") or {})
        return _reconstruct_outcome(term)

    def kill(self) -> None:
        """Force-stop the worker (timeout hard cap). Idempotent."""
        self._we_killed = True
        self._alive = False
        try:
            self._proc.kill()
        except ProcessLookupError:
            pass

    async def signal_cancel(self, *, timeout_exceeded: bool, cancel_requested: bool) -> None:
        await self._send({
            "t": MSG_CANCEL,
            "timeout_exceeded": timeout_exceeded,
            "cancel_requested": cancel_requested,
        })

    async def signal_shutdown(self) -> None:
        await self._send({"t": MSG_SHUTDOWN})

    def idle_seconds(self, now: float) -> float:
        return now - self.last_active_monotonic

    async def _read_loop(self) -> None:
        assert self._proc.stdout is not None
        reader = self._proc.stdout
        while True:
            try:
                header = await reader.readexactly(_LEN.size)
            except asyncio.IncompleteReadError:
                break
            (length,) = _LEN.unpack(header)
            try:
                body = await reader.readexactly(length)
            except asyncio.IncompleteReadError:
                break
            msg = json.loads(body.decode("utf-8"))
            t = msg.get("t")
            if t in (MSG_RESULT, MSG_ERROR, MSG_SUSPEND, MSG_EXIT_FOR_RECOVERY):
                fut = self._turn_future
                if fut is not None and not fut.done():
                    fut.set_result(msg)
            else:
                await self._dispatch(msg)
        # stdout EOF — the child exited.
        self._alive = False
        fut = self._turn_future
        if fut is not None and not fut.done():
            if self._we_killed:
                fut.set_exception(_WorkerKilled())
            else:
                fut.set_exception(
                    WorkerCrash(f"persistent worker {self._proc.pid} exited (rc={self._proc.returncode})")
                )

    async def _dispatch(self, msg: dict) -> None:
        bridge = self._current_bridge
        if bridge is None:
            return
        t = msg.get("t")
        if t == MSG_EMIT:
            await bridge.stream_emit(msg["stream_id"], msg["payload"], msg.get("close", False))
        elif t == MSG_STREAM_CLOSE:
            await bridge.stream_close(msg["stream_id"])
        elif t == MSG_REQ:
            await self._handle_request(msg, bridge)

    async def _handle_request(self, msg: dict, bridge: IsolationBridge) -> None:
        rid = msg.get("id")
        kind = msg.get("kind")
        value: Any = None
        try:
            if kind == REQ_FLUSH:
                await bridge.apply_flush(msg.get("namespace"), msg.get("data") or {})
            elif kind == REQ_LAST_CURSOR:
                value = await bridge.stream_last_cursor(msg["stream_id"])
            elif kind == REQ_PENDING_COUNT:
                value = bridge.get_pending_count()
        except Exception:  # pylint: disable=broad-except
            logger.warning("persistent worker: bridge request %s failed", kind, exc_info=True)
        await self._send({"t": MSG_RESP, "id": rid, "value": value})

    async def _forward_stderr(self) -> None:
        if self._proc.stderr is None:
            return  # fork transport: child shares the parent's stderr directly
        while True:
            line = await self._proc.stderr.readline()
            if not line:
                break
            logger.info("[worker %s] %s", self._proc.pid, line.decode("utf-8", "replace").rstrip())

    async def aclose(self) -> None:
        """Graceful teardown: ask the child to exit, else kill; reap tasks."""
        if self._alive:
            try:
                await self.signal_shutdown()
            except Exception:  # pylint: disable=broad-except
                pass
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except Exception:  # pylint: disable=broad-except
                try:
                    self._proc.kill()
                except ProcessLookupError:
                    pass
        self._alive = False
        for task in (self._reader_task, self._stderr_task):
            if task is not None and not task.done():
                task.cancel()


async def start_persistent_worker(*, python_exe: Optional[str] = None) -> PersistentWorker:
    """Launch a reusable worker process and begin pumping its protocol.

    No RUN is sent here; the first (and every subsequent) turn is started by
    :meth:`PersistentWorker.run_turn`.

    :return: A ready :class:`PersistentWorker`.
    """
    proc = await asyncio.create_subprocess_exec(
        *_worker_command(python_exe),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=os.environ.copy(),
    )
    worker = PersistentWorker(proc)
    worker._reader_task = asyncio.create_task(worker._read_loop())  # noqa: SLF001
    worker._stderr_task = asyncio.create_task(worker._forward_stderr())  # noqa: SLF001
    return worker


# ===========================================================================
# FORK BACKEND (Unix) — coexists with the spawn path
# ===========================================================================
#
# The spawn path launches a blank interpreter (`python -m ..._isolation`) that
# re-imports the app (~1-2s) and rebuilds ctx from a snapshot. The fork path
# instead ``os.fork()``s a child from the (already-imported) parent, so the app
# + all modules are inherited (no re-import, COW memory, ~ms start). We reuse
# ALL higher-level logic: the same ``_ChildProtocol`` (over one socket instead
# of std pipes), the same ``_build_child_context`` / ``_resolve_handler`` (whose
# ``import_module`` is a no-op hit on the inherited ``sys.modules``), and the
# same parent-side ``IsolatedRun`` / ``PersistentWorker`` (via an adapter that
# presents the mp process + socket like a subprocess). Fork-only concern: the
# child must sanitize the inherited async/threaded parent (fresh event loop,
# close the inherited peer socket, neutralize the inherited task-manager) — see
# ``_after_fork_child``.


def _after_fork_child(*, sock_fd: int, dead_fds: "list[int]") -> None:
    """Sanitize a freshly-forked child before it runs any handler.

    The child inherited the parent's entire memory image — a running event loop,
    reader threads' locks, open store/lease sockets, and the live task-manager
    singleton. Make the child a clean compute unit:

    * neutralize the inherited task-manager so ``get_task_manager()`` raises just
      like in the spawn child (no accidental direct store/lease access →
      no split-brain),
    * close the inherited peer (parent-side) socket fds so parent-death EOF works
      and the fd is not leaked,
    * drop the inherited event loop (a fresh one is created by ``asyncio.run``).

    :keyword sock_fd: The child's own IPC socket fd (kept open).
    :keyword dead_fds: Inherited fds to close (e.g. the parent-side socketpair end).
    """
    try:
        from ._manager import set_task_manager  # pylint: disable=import-outside-toplevel

        set_task_manager(None)
    except Exception:  # pylint: disable=broad-except
        pass
    for fd in dead_fds:
        if fd == sock_fd:
            continue
        try:
            os.close(fd)
        except OSError:
            pass
    # The inherited asyncio loop must never be used; asyncio.run() in the child
    # entry creates and owns a brand-new loop.


async def _fork_child_amain(sock_fd: int, reuse: bool) -> None:
    """Child-side async entry for the fork backend.

    Uses one bidirectional socket (``sock_fd``) for the whole protocol instead of
    the spawn path's stdin/stdout/stderr split. Turn-mode is always enabled so
    the RUN message(s) arrive through the reader; one-shot processes exactly one
    RUN then returns (process exit → parent EOF), reuse loops until shutdown/EOF.
    """
    loop = asyncio.get_running_loop()
    proto = _ChildProtocol(in_fd=sock_fd, out_fd=sock_fd, loop=loop)
    _install_stream_proxy(proto)
    proto.enable_turn_mode()
    proto.start_reader()

    if reuse:
        first = True
        while True:
            snapshot = await proto.next_run()
            if snapshot is None:
                break
            await _fork_run_one_turn(proto, snapshot, reset=not first)
            first = False
    else:
        snapshot = await proto.next_run()
        if snapshot is not None:
            await _fork_run_one_turn(proto, snapshot, reset=False)
    proto.close()


async def _fork_run_one_turn(proto: _ChildProtocol, snapshot: dict, *, reset: bool) -> None:
    """Run a single turn in the forked child and emit its terminal message."""
    if reset:
        proto.begin_turn()
    handler = _resolve_handler(snapshot["handler_module"], snapshot["handler_name"])
    ctx, meta = _build_child_context(snapshot, proto)  # binds ctx + swaps IO handles
    # A CANCEL may have arrived between the reader starting and ctx binding;
    # re-sync the cause booleans (the cancel Event itself is shared via
    # ctx.cancel = proto.cancel, so is_set() already reflects it).
    ctx.timeout_exceeded = proto.timeout_exceeded
    ctx.cancel_requested = proto.cancel_requested
    try:
        result = await handler(ctx)
        term = _classify_terminal(result, meta)
    except BaseException as exc:  # noqa: BLE001  pylint: disable=broad-except
        term = {
            "t": MSG_ERROR,
            "exc_type": type(exc).__name__,
            "exc_msg": str(exc)[:4000],
            "traceback": traceback.format_exc()[:8000],
            "metadata": meta.snapshot(),
        }
    proto.terminal(term)


def _fork_child_entry(child_sock: "socket.socket", parent_fd: int, reuse: bool) -> None:
    """Process target for a forked worker (runs in the child)."""
    sock_fd = child_sock.fileno()
    _after_fork_child(sock_fd=sock_fd, dead_fds=[parent_fd])
    try:
        asyncio.run(_fork_child_amain(sock_fd, reuse))
    except Exception:  # pylint: disable=broad-except
        traceback.print_exc()


class _ForkProcAdapter:
    """Presents a forked ``multiprocessing.Process`` + socket like a subprocess.

    Exposes the small surface ``IsolatedRun`` / ``PersistentWorker`` use
    (``stdin`` writer, ``stdout`` reader, ``stderr`` None, ``pid``, ``kill()``,
    ``wait()``, ``returncode``) so all their read-loop / dispatch / run_turn /
    kill logic works unchanged over the fork transport.
    """

    def __init__(
        self,
        proc: "multiprocessing.process.BaseProcess",
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self._proc = proc
        self.stdin = writer
        self.stdout = reader
        self.stderr = None

    @property
    def pid(self) -> int:
        return self._proc.pid or -1

    @property
    def returncode(self) -> Optional[int]:
        return self._proc.exitcode

    def kill(self) -> None:
        try:
            if self._proc.is_alive():
                self._proc.kill()
        except (ProcessLookupError, ValueError, AssertionError):
            pass

    async def wait(self) -> Optional[int]:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._proc.join)
        return self._proc.exitcode


async def _start_fork_process(reuse: bool) -> "tuple[_ForkProcAdapter, socket.socket]":
    """Fork a worker and wrap its process+socket in a ``_ForkProcAdapter``."""
    parent_sock, child_sock = socket.socketpair()
    ctx = multiprocessing.get_context("fork")
    proc = ctx.Process(
        target=_fork_child_entry,
        args=(child_sock, parent_sock.fileno(), reuse),
        name="agentserver-fork-worker",
        daemon=False,
    )
    proc.start()
    child_sock.close()  # parent keeps only its end
    parent_sock.setblocking(False)
    reader, writer = await asyncio.open_connection(sock=parent_sock)
    return _ForkProcAdapter(proc, reader, writer), parent_sock


async def start_forked(snapshot: dict, bridge: IsolationBridge) -> IsolatedRun:
    """Fork a one-shot worker (per-turn) — the fork analogue of :func:`start_isolated`.

    :param snapshot: The ctx snapshot + handler_module/handler_name.
    :param bridge: Main-process callbacks the worker proxies to.
    :return: A running :class:`IsolatedRun` over the fork transport.
    """
    adapter, _sock = await _start_fork_process(reuse=False)
    run = IsolatedRun(adapter, bridge)  # type: ignore[arg-type]
    run._reader_task = asyncio.create_task(run._read_loop())  # noqa: SLF001
    # No stderr task: the forked child shares the parent's stderr directly.
    await run._send({"t": MSG_RUN, "snapshot": snapshot})  # noqa: SLF001
    return run


async def start_forked_worker() -> PersistentWorker:
    """Fork a reusable worker — the fork analogue of :func:`start_persistent_worker`.

    No RUN is sent here; each turn is started by :meth:`PersistentWorker.run_turn`.

    :return: A ready :class:`PersistentWorker` over the fork transport.
    """
    adapter, _sock = await _start_fork_process(reuse=True)
    worker = PersistentWorker(adapter)  # type: ignore[arg-type]
    worker._reader_task = asyncio.create_task(worker._read_loop())  # noqa: SLF001
    # No stderr task: the forked child shares the parent's stderr directly.
    return worker


if __name__ == "__main__":
    _child_main()