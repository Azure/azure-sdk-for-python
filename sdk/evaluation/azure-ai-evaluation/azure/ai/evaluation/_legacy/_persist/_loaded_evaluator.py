# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import copy
import importlib.util

from datetime import datetime
from inspect import isclass, isfunction
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional, Tuple, Type, final

from azure.ai.evaluation._evaluators._common._base_eval import AsyncEvaluatorBase
from azure.ai.evaluation._evaluate._batch_run.batch_clients import HasAsyncCallable
from azure.ai.evaluation._legacy._batch_engine._utils import normalize_identifier_name
from azure.ai.evaluation._legacy._adapters.utils import async_run_allowing_running_loop
from azure.ai.evaluation._legacy._persist._callable_metadata import CallableMetadata
from azure.ai.evaluation._legacy._persist._exceptions import EvaluationLoadError

class LoadedEvaluator:
    """A loaded evaluator from a flow flex file.
    
    :param CallableMetadata meta: The metadata of the loaded evaluator.
    :param Path working_dir: The working directory to load the evaluator from.
    """

    def __init__(self, meta: CallableMetadata, working_dir: Path, **kwargs: Any) -> None:
        """Initialize the loaded evaluator. Use the kwargs to pass any init arguments for the loaded
        evaluator.
        
        :param CallableMetadata meta: The metadata of the loaded evaluator.
        :param Path working_dir: The working directory to load the evaluator from."""
        self._meta: CallableMetadata = copy.deepcopy(meta)
        self._working_dir: Path = working_dir.resolve()

        module_name, class_or_func_name = [ e.strip() for e in self._meta["entry"].split(":", 2) ]

        # to prevent name collisions, let's generate a unique name for the module we are about to import
        self._module_name = normalize_identifier_name(
            working_dir.name + "_" + module_name + "_"
            + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        )
        self._code_path = (working_dir / (module_name.replace(".", "/") + ".py")).resolve().absolute()
        if not self._code_path.exists():
            raise EvaluationLoadError(
                f"Evaluator code file {self._code_path} does not exist. Please check the path."
            )

        # preload the module to get errors early
        self._module: ModuleType = self._load_module(self._code_path)
        self._callable, self._class = self._get_callable(self._module, class_or_func_name)
        self._is_async: bool = False

        if self._class is not None:
            # if the callable is a class, we need to instantiate it
            self._instance: Any = self._class(**kwargs)
            self._callable = self._instance.__call__
            self._is_async = isinstance(self._instance, HasAsyncCallable)

        # Pass the loaded callable to the base class. This works around the limitations of the legacy SDK
        # which did not inspect oveloads when generating type signatures and column mappings.
        self._async_eval = AsyncEvaluatorBase(real_call=self._real_call)

    def __call__(self, **kwargs: Any) -> Any:
        if self._is_async:
            async_run_allowing_running_loop(self._async_eval, **kwargs)
        else:
            return self._callable(**kwargs)

    async def _real_call(self, **kwargs: Any) -> Any:
        res = self._callable(**kwargs)
        if inspect.isawaitable(res):
            res = await res
        return res

    @final
    def _to_async(self) -> AsyncEvaluatorBase:
        # For compatibility with how the legacy interacted with async evaluators
        return self._async_eval

    @staticmethod
    def _load_module(python_file: Path) -> ModuleType:
        """Load the module from the specified path.
        
        :param str module_name: The name of the module to load.
        :param Path python_file: The absolute path to the python file.
        :return: The loaded evaluator class.
        :rtype: EvaluatorBase
        """

        try:
            spec = importlib.util.spec_from_file_location(python_file.stem, location=python_file)
            if spec is None or spec.loader is None:
                raise EvaluationLoadError(
                    f"Failed to load python file '{python_file}'. Please make sure it is a valid .py file.")

            module_type = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module_type)
            return module_type
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_type_and_message = f"({e.__class__.__name__}) {e}"
            raise EvaluationLoadError(
                f"Failed to load python module from file '{python_file}': {error_type_and_message}"
            ) from e

    @staticmethod
    def _get_callable(module: ModuleType, class_or_func_name: str) -> Tuple[Callable, Optional[Type]]:
        """Get the callable from the loaded module.
        
        :param ModuleType module: The loaded module.
        :param str class_or_func_name: The name of the callable to load.
        :return: The loaded callable, and optionally the class if it is a class.
        :rtype: Tuple[Callable, Optional[Any]]
        """

        func_or_class: Optional[Callable] = getattr(module, class_or_func_name, None)
        if isfunction(func_or_class):
            return func_or_class, None
        elif isclass(func_or_class) and hasattr(func_or_class, "__call__"):
            return func_or_class.__call__, func_or_class

        raise EvaluationLoadError(
            f"Failed to load callable '{class_or_func_name}' from module '{module.__name__}'. "
            "Please make sure it is a valid function, or callable class."
        )

