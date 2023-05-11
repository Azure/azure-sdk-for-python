import os.path
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live_and_not_recording
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
)
@pytest.mark.pipeline_test
class TestComponentHash(AzureRecordedTestCase):
    def test_component_recreated_with_pycache(self, client: MLClient, randstr: Callable[[str], str]) -> None:
        # TODO: seems that this still can't trigger the automatic Windows path shortening
        long_dir_name = ("a" * 50 + "/") * 3
        with build_temp_folder(
            extra_files_to_create={
                long_dir_name + "code/hello.py": "def hello():\n    print('hello')\n",
                long_dir_name + "code/__pycache__/__init__.cpython-36.pyc": "hello",
                long_dir_name + "code_copy/hello.py": "def hello():\n    print('hello')\n",
                long_dir_name + "code_copy/__pycache__/__init__.cpython-36.pyc": "world",
            },
        ) as base_dir:
            component_name = randstr("component_name")
            component: CommandComponent = create_component(
                client, component_name, params_override=[{"code": os.path.join(base_dir, long_dir_name + "code")}]
            )

            # a service error saying that code is immutable will be raised if __pycache__ is not ignored in
            # asset hash calculation or
            recreated_component: CommandComponent = create_component(
                client, component_name, params_override=[{"code": os.path.join(base_dir, long_dir_name + "code_copy")}]
            )

            # no change, so arm id should be the same
            assert recreated_component.id == component.id
            assert recreated_component.code == component.code
