import importlib
import re
import sys
from importlib import reload

import pip
import pytest

from azure.ai.ml._utils import _func_utils


class MockClass:
    mock_cls_attr = 2

    def __init__(self, mock_arg):
        self.mock_arg = mock_arg

    def mock_instance_func(self, arg):
        result = self.mock_arg + arg
        return result

    @classmethod
    def mock_class_method(cls, arg):
        result = cls.mock_cls_attr + arg
        return result

    def __call__(self, arg):
        result = self.mock_arg + arg
        return result


def mock_conflict_function(__self):
    return __self


def mock_function_with_self(self):
    return self


is_true = True


def mock_function_multi_return(mock_arg):
    if is_true:
        mock_local_variable = 1
        return mock_local_variable, mock_arg
    else:
        mock_local_variable = 2
        return mock_local_variable, mock_arg


def mock_function_multi_return_expected(__self, mock_arg):
    try:
        if is_true:
            mock_local_variable = 1
            return mock_local_variable, mock_arg
        else:
            mock_local_variable = 2
            return mock_local_variable, mock_arg
    finally:
        __self._locals = locals().copy()


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPersistentLocalsProfiler:
    @classmethod
    def get_persistent_locals_builder(cls) -> _func_utils.PersistentLocalsFunctionBuilder:
        return _func_utils.PersistentLocalsFunctionProfilerBuilder()

    def get_outputs_and_locals(self, func, injected_params):
        return self.get_persistent_locals_builder().call(func, injected_params)

    def test_simple(self):
        def mock_function(mock_arg):
            mock_local_variable = 1
            return mock_local_variable, mock_arg

        outputs, _locals = self.get_outputs_and_locals(mock_function, {"mock_arg": 1})
        assert outputs == (1, 1)
        assert set(_locals.keys()) == {"mock_arg", "mock_local_variable"}

    def test_func_with_named_self_argument(self):
        outputs, _locals = self.get_outputs_and_locals(mock_function_with_self, {"self": 1})
        assert outputs == 1
        assert set(_locals.keys()) == {"self"}

    def test_raise_exception(self):
        def mock_error_exception():
            mock_local_variable = 1
            return mock_local_variable / 0

        with pytest.raises(ZeroDivisionError):
            self.get_outputs_and_locals(mock_error_exception, {})

    def test_instance_func(self):
        mock_obj = MockClass(1)
        outputs, _locals = self.get_outputs_and_locals(mock_obj.mock_instance_func, {"arg": 1})
        assert outputs == 2
        assert set(_locals.keys()) == {"result", "arg", "self"}

    def test_class_method(self):
        mock_obj = MockClass(1)
        outputs, _locals = self.get_outputs_and_locals(mock_obj.mock_class_method, {"arg": 1})
        assert outputs == 3
        assert set(_locals.keys()) == {"result", "arg", "cls"}

    def test_instance_call(self):
        mock_obj = MockClass(1)
        outputs, _locals = self.get_outputs_and_locals(mock_obj, {"arg": 1})
        assert outputs == 2
        assert set(_locals.keys()) == {"result", "arg", "self"}

    def test_invalid_passed_func(self):
        with pytest.raises(TypeError, match="func must be a function or a callable object"):
            self.get_outputs_and_locals(1, {"arg": 1})

    def test_param_conflict(self):
        with pytest.raises(
            ValueError,
            match=re.escape("Injected param name __self conflicts with function args ['__self']"),
        ):
            self.get_outputs_and_locals(mock_conflict_function, {"arg": 1})

    def test_multiple_return(self):
        outputs, _locals = self.get_outputs_and_locals(mock_function_multi_return, {"mock_arg": 1})
        assert outputs == (1, 1)
        assert set(_locals.keys()) == {"mock_arg", "mock_local_variable"}


@pytest.mark.unittest
@pytest.mark.pipeline_test
@pytest.mark.usefixtures("enable_pipeline_private_preview_features")
class TestPersistentLocalsPrivatePreview(TestPersistentLocalsProfiler):
    _PACKAGE = "bytecode"

    @classmethod
    def setup_class(cls):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        try:
            importlib.import_module(cls._PACKAGE)
        except ImportError:
            pip.main(["install", cls._PACKAGE])
            globals()[cls._PACKAGE] = importlib.import_module(cls._PACKAGE)

            # reload persistent locals function builder after installing bytecode
            reload(_func_utils)

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        if cls._PACKAGE not in globals():
            return

        del globals()[cls._PACKAGE]
        pip.main(["uninstall", cls._PACKAGE])
        reload(_func_utils)

    @classmethod
    def instr_to_str(cls, instr, labels):
        from bytecode import Label

        def _label_to_str(_label):
            if id(_label) not in labels:
                labels.append(id(_label))
            return f"{_label.__class__.__name__} {labels.index(id(_label))}"

        if isinstance(instr, Label):
            return _label_to_str(instr)

        if isinstance(instr.arg, Label):
            return f"{instr.name} {_label_to_str(instr.arg)}"

        return f"{instr.name} {instr.arg}"

    @classmethod
    def instructions_to_str(cls, instructions):
        labels = []
        return [cls.instr_to_str(instr, labels) for instr in instructions]

    @classmethod
    def get_persistent_locals_builder(cls):
        return _func_utils.PersistentLocalsFunctionBytecodeBuilder()

    def test_multiple_return(self):
        if (3, 8) > sys.version_info:
            super().test_multiple_return()
        else:
            outputs, _locals = self.get_outputs_and_locals(mock_function_multi_return, {"mock_arg": 1})
            assert outputs == (1, 1)

            # TODO: persist locals for multiple return in Python 3.8/3.9/3.10/3.11
            # builder = self.get_persistent_locals_builder()
            # expected_instructions = builder.get_instructions(mock_function_multi_return_expected)
            # actual_instructions = builder._build_instructions(mock_function_multi_return)
            # assert self.instructions_to_str(actual_instructions) == self.instructions_to_str(expected_instructions)


@pytest.mark.unittest
@pytest.mark.pipeline_test
@pytest.mark.skipif(
    condition=sys.version_info >= (3, 11), reason="historical implementation doesn't support Python 3.11+"
)
class TestPersistentLocalsHistoricalImplementation(TestPersistentLocalsPrivatePreview):
    """This is to test the implementation of persistent locals function in azuerml-components."""

    @classmethod
    def get_persistent_locals_builder(cls):
        from bytecode import Instr, Label

        class HistoricalPersistentLocalsFunctionProfilerBuilder(_func_utils.PersistentLocalsFunctionBytecodeBuilder):
            def _build_instructions(self, func):
                bytecode = self.get_instructions(func)
                # Add `try` at the begining of the code
                finally_label = Label()
                bytecode.insert(0, Instr("SETUP_FINALLY", finally_label))
                # Add `final` at the end of the code
                added_param = "__self"

                copy_locals_instructions = [
                    # __self._locals = locals().copy()
                    Instr("LOAD_GLOBAL", "locals"),
                    Instr("CALL_FUNCTION", 0),
                    Instr("LOAD_ATTR", "copy"),
                    Instr("CALL_FUNCTION", 0),
                    Instr("LOAD_FAST", added_param),
                    Instr("STORE_ATTR", "_locals"),
                ]

                if sys.version_info < (3, 8):
                    # python 3.6 and 3.7
                    bytecode.extend(
                        [finally_label]
                        + copy_locals_instructions
                        + [Instr("END_FINALLY"), Instr("LOAD_CONST", None), Instr("RETURN_VALUE")]
                    )
                elif sys.version_info < (3, 9):
                    # In python 3.8, add new instruction CALL_FINALLY
                    # https://docs.python.org/3.8/library/dis.html?highlight=call_finally#opcode-CALL_FINALLY
                    bytecode.insert(-1, Instr("CALL_FINALLY", finally_label))
                    bytecode.extend(
                        [finally_label]
                        + copy_locals_instructions
                        + [Instr("END_FINALLY"), Instr("LOAD_CONST", None), Instr("RETURN_VALUE")]
                    )
                elif sys.version_info < (3, 10):
                    # In python 3.9, add new instruction RERAISE and CALL_FINALLY is removed.
                    # https://docs.python.org/3.9/library/dis.html#opcode-RERAISE
                    raise_error = Label()
                    extend_instructions = (
                        copy_locals_instructions
                        + [Instr("JUMP_FORWARD", raise_error), finally_label]
                        + copy_locals_instructions
                        + [Instr("RERAISE"), raise_error]
                    )
                    bytecode[-1:-1] = extend_instructions
                else:
                    # python 3.10 and above
                    bytecode[-1:-1] = copy_locals_instructions
                    bytecode.extend([finally_label] + copy_locals_instructions + [Instr("RERAISE", 0)])
                return bytecode

        return HistoricalPersistentLocalsFunctionProfilerBuilder()

    def test_multiple_return(self):
        # historical implementation can save locals correctly for multiple return in Python 3.7 only
        if (3, 8) > sys.version_info:
            super().test_multiple_return()
        else:
            outputs, _locals = self.get_outputs_and_locals(mock_function_multi_return, {"mock_arg": 1})
            assert outputs == (1, 1)
