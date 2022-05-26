# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Union

from azure.ai.ml.entities._builders import Command
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
)
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin


def to_component(*, job: ComponentTranslatableMixin, **kwargs) -> Callable[..., Command]:
    """
    Translate a job object to a component function, provided job should be able to translate to a component.

    For example:

    .. code-block:: python

        # Load a local command job to a component function.
        my_job = load_job("my_job.yaml")
        component_func = dsl.to_component(my_job)
        # Load a remote command job component to a component function.
        my_job = ml_client.jobs.get("my_job")
        component_func = dsl.to_component(my_job)

        # Consuming the component func
        component = component_func(param1=xxx, param2=xxx)

    :param job: Job load from local or remote.
    :type job: ~azure.ai.ml.entities._job.pipeline._component_translatable.ComponentTranslatableMixin
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: Wrapped function call.
    :rtype: typing.Callable[..., ~azure.ai.ml.entities._builders.command.Command]
    """
    from pathlib import Path

    # set default base path as "./". Because if code path is relative path and base path is None, will raise error when
    # get arm id of Code
    return job._to_component(context={BASE_PATH_CONTEXT_KEY: Path("./")})


def _generate_package(
    *,
    assets: Union[list, dict, str] = None,
    package_name: str = "assets",
    source_directory: str = ".",
    force_regenerate: bool = False,
    mode: str = "reference",
    **kwargs,
) -> None:
    """For a set of components, generate a python module which contains component consumption functions and import it
    for use.

    :param assets: List[assets_identifier], dict[module_name, assets_identifier] or str

        * None: we will generate a module for default ml_client, not supported for now.

        * list example: specify as assets pattern list and we will generate modules

            .. code-block:: python

                # workspace assets, module name will be workspace name
                assets = ["azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/
                          workspaces/{workspace_name}"]

                # feed assets, module name will be feed name
                assets = ["azureml://feeds/HuggingFace"]

                # local assets, module name will be "local"
                assets = ["file:components/**/module_spec.yaml"]

        * dict example: module name as key and assets_identifier as value

            .. code-block:: python

                # module name with an assets identifier
                assets = {"module_name": "azureml://subscriptions/{subscription_id}/"
                                         "resourcegroups/{resource_group}/workspaces/{workspace_name}"}
                # module name with a list of assets identifier
                assets = {"module_name": ["azureml://subscriptions/{subscription_id}/"
                                          "resourcegroups/{resource_group}/workspaces/{workspace_name}",
                                          "file:components/**/module_spec.yaml"]}

        * str example: specify as ``assets.yaml`` and config file which contains the modules dict

        .. remarks::

            module_name: a string which is the name of the generated python module.
                If user specify "module_name", a python file will be created: module_name.py.
            components: single or list of glob string which specify a set of components. Example values:
                * assets from workspace
                    1. all assets
                        ``azureml://subscriptions/{subscription_id}/resource_group/{resource_group}/
                        workspaces/{workspace_name}``
                    2. components with name filter
                        ``azureml://subscriptions/{subscription_id}/resource_group/{resource_group}
                        /workspaces/{workspace_name}/components/microsoft_samples_*``
                    3. datasets
                        ``azureml://subscriptions/{subscription_id}/resource_group/{resource_group}
                        /workspaces/{workspace_name}/datasets``
                * components from local yaml
                    ``file:components/**/module_spec.yaml``
                * components from feeds
                    For feed concept, please see: `https://aka.ms/azuremlsharing`.
                    azureml://feeds/HuggingFace  # All assets in feed.
                    azureml://feeds/HuggingFace/components/Microsoft*

    :type assets: typing.Union[None, list, dict, str]
    :param source_directory: parent folder to generate source code.
        * If not specified, we generate the file relative to the folder of python file that triggers the
        dsl.generate_module call.
        * If specified, we also generate all non-exist intermediate path.
    :type source_directory: str
    :param package_name: name of the generated python package. Example: cool-component-package
        * If not specified, we generate the module directory under {source_directory}
        * If specified: we generate the module file to specified package.
        * If the cool-component-package folder does not exists, we will create a new skeleton package under
        {source_directory}/cool-component-package and print info in command line and ask user to do:
        ``pip install -e {source_directory}/cool-component-package``
        Then next user can do: 'from cool.component.package import module_name'
        * If the folder exists, we trigger the __init__.py in the folder.
    :type package_name: str
    :param force_regenerate: whether to force regenerate the python module file.
        * If True, will always generate and re-import the newly generated file.
        * If False, will reuse previous generated file. If the existing file not valid, raise import error.
    :type force_regenerate: bool
    :param mode: whether to retain a snapshot of assets in package.
        * reference: will not build/download snapshot of asset, load by name for remote assets.
        * snapshot: will build/download snapshot of asset, load from local yaml.
    :type mode: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """
    pass
