import functools
import io
import os.path
from typing import Callable

import mock
import pytest
from devtools_testutils import AzureRecordedTestCase
from test_utilities.utils import build_temp_folder

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.entities import CommandComponent

from .._util import _COMPONENT_TIMEOUT_SECOND


def create_component(
    client: MLClient,
    component_name: str,
    path="./tests/test_configs/components/helloworld_component.yml",
    params_override=None,
    is_anonymous=False,
):
    default_param_override = [{"name": component_name}]
    if params_override is None:
        params_override = default_param_override
    else:
        params_override += default_param_override

    command_component = load_component(
        source=path,
        params_override=params_override,
    )
    return client.components.create_or_update(command_component, is_anonymous=is_anonymous)


@pytest.mark.e2etest
@pytest.mark.timeout(_COMPONENT_TIMEOUT_SECOND)
@pytest.mark.usefixtures(
    "recorded_test",
    "mock_asset_name",
    "mock_component_hash",
)
@pytest.mark.pipeline_test
class TestComponentHash(AzureRecordedTestCase):
    @classmethod
    def _assert_recreated_component_no_change(cls, base_dir, client, randstr, with_code_diff=False):
        component_name = randstr("component_name")
        component: CommandComponent = create_component(
            client, component_name, params_override=[{"code": os.path.join(base_dir, "code")}]
        )

        # a service error saying that code is immutable will be raised if __pycache__ is not ignored in
        # asset hash calculation or
        recreated_component: CommandComponent = create_component(
            client, component_name, params_override=[{"code": os.path.join(base_dir, "code_copy")}]
        )

        if not with_code_diff:
            # no change, so arm id should be the same
            assert recreated_component.id == component.id
            assert recreated_component.code == component.code

        return component, recreated_component

    def test_component_recreated_with_pycache(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        with build_temp_folder(
            extra_files_to_create={
                "code/hello.py": b"def hello():\n    print('hello')\n",
                "code/__pycache__/__init__.cpython-36.pyc": "hello",
                "code_copy/hello.py": b"def hello():\n    print('hello')\n",
                "code_copy/__pycache__/__init__.cpython-36.pyc": "world",
            },
        ) as base_dir:
            self._assert_recreated_component_no_change(base_dir, client, randstr)

    @pytest.mark.skip(reason="seems that this still can't trigger the automatic Windows path shortening")
    def test_component_recreate_with_long_path(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        long_dir_name = os.path.join(*(["a" * 50] * 10))
        with build_temp_folder(
            extra_files_to_create={
                os.path.join(long_dir_name, "code", "hello.py"): "def hello():\n    print('hello')\n",
                os.path.join(long_dir_name, "code_copy", "hello.py"): "def hello():\n    print('hello')\n",
            },
        ) as base_dir:
            self._assert_recreated_component_no_change(os.path.join(base_dir, long_dir_name), client, randstr)

    def test_component_recreate_cross_os(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        with build_temp_folder(
            extra_files_to_create={
                "code/hello.py": b"def hello():\n    print('hello')\n",
                "code_copy/hello.py": b"def hello():\r\n    print('hello')\r\n",
            },
        ) as base_dir:
            component_name = randstr("component_name")

            linux_component: CommandComponent = create_component(
                client, component_name, params_override=[{"code": os.path.join(base_dir, "code")}]
            )

            windows_component: CommandComponent = create_component(
                client, component_name, params_override=[{"code": os.path.join(base_dir, "code")}]
            )

            # although local hash is different for lf file and CRLF file, the remote hash should be the same
            assert linux_component.id == windows_component.id
            assert linux_component.code == windows_component.code
