# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own the Windows Toxiproxy worker and its descendants without selecting processes by name."""

import ctypes
from ctypes import wintypes
from contextlib import ExitStack
import os
import subprocess
import time


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_ulonglong)
        for name in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class _ProcessIdList(ctypes.Structure):
    _fields_ = [
        ("NumberOfAssignedProcesses", wintypes.DWORD),
        ("NumberOfProcessIdsInList", wintypes.DWORD),
    ]


def _check(result):
    if not result:
        raise ctypes.WinError(ctypes.get_last_error())
    return result


class OwnedProcessTree:
    def __init__(self):
        if os.name != "nt":
            raise OSError("The pinned Toxiproxy runner requires Windows")
        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD],
                wintypes.BOOL,
            ),
            "QueryInformationJobObject": (
                [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p],
                wintypes.BOOL,
            ),
            "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            "IsProcessInJob": ([wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)], wintypes.BOOL),
            "TerminateProcess": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "WaitForSingleObject": ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.api, name)
            function.argtypes, function.restype = arguments, result
        self.handle = _check(self.api.CreateJobObjectW(None, None))
        self.stopped = False
        try:
            limits = _ExtendedLimits()
            limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            _check(self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        except BaseException:
            _check(self.api.CloseHandle(self.handle))
            self.handle = None
            raise

    def assign(self, pid):
        process = _check(self.api.OpenProcess(0x0100 | 0x0001, False, pid))  # SET_QUOTA | TERMINATE
        try:
            _check(self.api.AssignProcessToJobObject(self.handle, process))
        finally:
            _check(self.api.CloseHandle(process))

    def _member_pids(self, deadline):
        capacity = 16
        while True:
            buffer = ctypes.create_string_buffer(
                ctypes.sizeof(_ProcessIdList) + capacity * ctypes.sizeof(ctypes.c_size_t)
            )
            result = self.api.QueryInformationJobObject(self.handle, 3, buffer, len(buffer), None)
            error = ctypes.get_last_error() if not result else 0
            if not result and error != 234:  # ERROR_MORE_DATA
                raise ctypes.WinError(error)
            info = _ProcessIdList.from_buffer(buffer)
            if result and info.NumberOfProcessIdsInList == info.NumberOfAssignedProcesses:
                pids = (ctypes.c_size_t * info.NumberOfProcessIdsInList).from_buffer(
                    buffer, ctypes.sizeof(_ProcessIdList)
                )
                return list(pids)
            if time.monotonic() >= deadline:
                raise TimeoutError("Owned worker process list did not stabilize")
            capacity = max(capacity * 2, info.NumberOfAssignedProcesses)

    def _close_handle(self, handle):
        _check(self.api.CloseHandle(handle))

    def close(self):
        if self.handle is None:
            return
        try:
            deadline = time.monotonic() + 5
            with ExitStack() as handles:
                members = {}
                while True:
                    pids = self._member_pids(deadline)
                    if not pids:
                        break
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Owned worker process tree did not stop")
                    for pid in pids:
                        if pid in members:
                            continue
                        # Pin the process identity and verify ownership before terminating it.
                        process = self.api.OpenProcess(0x00100000 | 0x1000 | 0x0001, False, pid)
                        if not process:
                            error = ctypes.get_last_error()
                            if error == 87:  # ERROR_INVALID_PARAMETER: process already exited
                                continue
                            raise ctypes.WinError(error)
                        handles.callback(self._close_handle, process)
                        member = wintypes.BOOL()
                        _check(self.api.IsProcessInJob(process, self.handle, ctypes.byref(member)))
                        if not member.value:
                            continue
                        members[pid] = process
                        termination_error = None
                        if not self.api.TerminateProcess(process, 1):
                            termination_error = ctypes.get_last_error()
                            if termination_error != 5:
                                raise ctypes.WinError(termination_error)
                        # Repeated termination can be denied while process teardown is still pending.
                        remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
                        result = self.api.WaitForSingleObject(process, remaining_ms)
                        if result == 0x102:  # WAIT_TIMEOUT
                            if termination_error is not None:
                                raise ctypes.WinError(termination_error)
                            raise TimeoutError("Owned worker process tree did not stop")
                        if result == 0xFFFFFFFF:  # WAIT_FAILED
                            raise ctypes.WinError(ctypes.get_last_error())
                        if result != 0:  # WAIT_OBJECT_0
                            raise OSError(f"Unexpected process wait result: {result}")
                    time.sleep(0.01)
        finally:
            try:
                # Job-wide termination is a safety net, not proof that process teardown finished.
                _check(self.api.TerminateJobObject(self.handle, 1))
            finally:
                self._close_handle(self.handle)
                self.handle = None
        self.stopped = True


def run_owned_worker(command, *, cwd, env, log, state, timeout=600):
    """Release the stdin-gated worker only after its descendants are covered by the job."""
    job = OwnedProcessTree()
    process = None
    state["process_tree_stopped"] = False
    state["outer_timeout"] = False
    try:
        process = subprocess.Popen(
            command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT
        )
        state["worker_pid"] = process.pid
        job.assign(process.pid)
        process.stdin.write(b"1")
        process.stdin.flush()
        process.stdin.close()
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            state["outer_timeout"] = True
            raise
    finally:
        try:
            job.close()
        finally:
            if process is not None:
                try:
                    # Assignment can fail while the worker is still waiting for permission.
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=5)
                finally:
                    process.stdin.close()
        state["process_tree_stopped"] = job.stopped
