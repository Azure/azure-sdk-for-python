# pylint: disable=missing-docstring, invalid-name

import pytest
from kwargs.kwargs import App, run

def test_can_create_app():
    app = App(lambda: None)
    assert isinstance(app, App)

@pytest.mark.parametrize('x,y,result', [
    (6, 2, 3),
    (294, 7, 42),
    (1, 1, 1)
])
def test_with_positional_arguments(x, y, result):
    app = App(lambda x, y: x / y)
    assert app.run(x, y) == result


@pytest.mark.parametrize('x,y,result', [
    (6, 2, 3),
    (294, 7, 42),
    (1, 1, 1)
])
def test_shorthand_with_positional_arguments(x, y, result):
    assert run(lambda x, y: x / y, x, y) == result
