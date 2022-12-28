import re

import pytest

from azure.ai.ml._utils._func_utils import persistent_locals


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


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestPersistentLocals:
    def test_simple(self):
        def mock_function(mock_arg):
            mock_local_variable = 1
            return mock_local_variable, mock_arg

        persistent_func = persistent_locals(mock_function)
        assert persistent_func(mock_arg=1) == (1, 1)
        assert set(persistent_func.locals.keys()) == {'mock_arg', 'mock_local_variable'}

    def test_func_with_named_self_argument(self):
        persistent_func = persistent_locals(mock_function_with_self)
        assert persistent_func(self=1) == 1
        assert set(persistent_func.locals.keys()) == {'self'}

    def test_raise_exception(self):
        def mock_error_exception():
            mock_local_variable = 1
            return mock_local_variable / 0

        persistent_func = persistent_locals(mock_error_exception)
        with pytest.raises(ZeroDivisionError):
            persistent_func()
        assert list(persistent_func.locals.keys()) == ['mock_local_variable']

    def test_instance_func(self):
        mock_obj = MockClass(1)
        persistent_func = persistent_locals(mock_obj.mock_instance_func)
        assert persistent_func(1) == 2
        assert set(persistent_func.locals.keys()) == {'result', 'arg', 'self'}

    def test_class_method(self):
        mock_obj = MockClass(1)
        persistent_func = persistent_locals(mock_obj.mock_class_method)
        assert persistent_func(1) == 3
        assert set(persistent_func.locals.keys()) == {'result', 'arg', 'cls'}

    def test_instance_call(self):
        mock_obj = MockClass(1)
        persistent_func = persistent_locals(mock_obj)
        assert persistent_func(1) == 2
        assert set(persistent_func.locals.keys()) == {'result', 'arg', 'self'}

    def test_invalid_passed_func(self):
        with pytest.raises(TypeError, match='func must be a function or a callable object'):
            persistent_locals(1)

    def test_param_conflict(self):
        with pytest.raises(
            ValueError,
            match=re.escape('Injected param name __self conflicts with function args [\'__self\']'),
        ):
            persistent_locals(mock_conflict_function)
