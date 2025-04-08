# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading
import importlib.util
import sys
import os
from typing import Coroutine, Any
from typing_extensions import TypeVar


def import_from_path(file_path):
    full_path = os.path.abspath(file_path)
    module_name = os.path.basename(full_path)
    dirname = os.path.dirname(full_path)
    if os.path.isdir(full_path):
        full_path = os.path.join(full_path, "__init__.py")
    elif os.path.isfile(full_path):
        module_name = os.path.splitext(module_name)[0]
    else:
        raise ImportError(f"Module {module_name} not found at {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, dirname)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module


T = TypeVar("T")


def run_coroutine_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    # TODO: Found this on StackOverflow - needs further inspection
    # https://stackoverflow.com/questions/55647753/call-async-function-from-sync-function-while-the-synchronous-function-continues

    def run_in_new_loop():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        with ThreadPoolExecutor() as pool:
            future = pool.submit(run_in_new_loop)
            return future.result(timeout=timeout)
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()
