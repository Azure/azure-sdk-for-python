# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own the Windows test worker and its descendants without selecting processes by name."""

import ctypes
from ctypes import wintypes
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


class _Accounting(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
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

    def close(self):
        if self.handle is None:
            return
        try:
            _check(self.api.TerminateJobObject(self.handle, 1))
            deadline = time.monotonic() + 5
            while True:
                accounting = _Accounting()
                _check(
                    self.api.QueryInformationJobObject(
                        self.handle, 1, ctypes.byref(accounting), ctypes.sizeof(accounting), None
                    )
                )
                if accounting.ActiveProcesses == 0:
                    self.stopped = True
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError("Owned worker process tree did not stop")
                time.sleep(0.01)
        finally:
            _check(self.api.CloseHandle(self.handle))
            self.handle = None


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
