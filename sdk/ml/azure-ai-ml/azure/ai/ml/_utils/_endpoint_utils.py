# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import concurrent.futures
from concurrent.futures import Future
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.mgmt.core.exceptions import ARMErrorFormat
import logging
from azure.ai.ml.entities._deployment.deployment import Deployment
import requests
import time
from azure.core.polling import LROPoller
from typing import Callable, Any, Union
from .utils import show_debug_info, initialize_logger_info

from azure.ai.ml.constants import AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource
from azure.ai.ml.entities._assets._artifacts.code import Code

from azure.ai.ml._operations.operation_orchestrator import OperationOrchestrator

module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")


def polling_wait(
    poller: Union[LROPoller, Future],
    message: str = None,
    start_time: float = None,
    is_local=False,
    timeout=LROConfigurations.POLLING_TIMEOUT,
) -> Any:
    """Print out status while polling and time of operation once completed.

    :param Union[LROPoller, concurrent.futures.Future] poller: An poller which will return status update via function done().
    :param (str, optional) message: Message to print out before starting operation write-out.
    :param (float, optional) start_time: Start time of operation.
    :param (bool, optional) is_local: If poller is for a local endpoint, so the timeout is removed.
    :param (int, optional) timeout: New value to overwrite the default timeout.
    """
    module_logger.info(f"{message}")

    if is_local:
        """We removed timeout on local endpoints in case
        it takes a long time to pull image or install conda env.
        We want user to be able to see that.
        """
        while not poller.done():
            module_logger.info(".")
            time.sleep(LROConfigurations.SLEEP_TIME)
    else:
        poller.result(timeout=timeout)

    if poller.done():
        module_logger.info("Done ")
    else:
        module_logger.warning("Timeout waiting for long running operation")

    if start_time:
        end_time = time.time()
        duration = divmod(int(round(end_time - start_time)), 60)
        module_logger.info(f"({duration[0]}m {duration[1]}s)\n")


def local_endpoint_polling_wrapper(func: Callable, message: str, **kwargs) -> Any:
    """Wrapper for polling local endpoint operations.

    :param Callable func: Name of the endpoint.
    :param str message: Message to print out before starting operation write-out.
    :param dict kwargs: kwargs to be passed to the func
    :return: The type returned by Func
    """
    pool = concurrent.futures.ThreadPoolExecutor()
    start_time = time.time()
    event = pool.submit(func, **kwargs)
    polling_wait(poller=event, start_time=start_time, message=message, is_local=True)
    return event.result()


def post_and_validate_response(url, data=None, json=None, headers=None, **kwargs) -> requests.Response:
    r"""Sends a POST request and validate the response.
    :param url: URL for the new :class:`Request` object.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) json data to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    logging = kwargs.pop("logging_enable", None)
    response = requests.post(url=url, data=data, json=json, headers=headers, **kwargs)
    r_json = {}

    if logging:
        show_debug_info(response)

    if response.status_code not in [200, 201]:
        # We need to check for an empty response body or catch the exception raised.
        # It is possible the server responded with a 204 No Content response, and json parsing fails.
        if response.status_code != 204:
            try:
                r_json = response.json()
            except ValueError:
                # exception is not in the json format
                raise Exception(response.content.decode("utf-8"))
        failure_msg = r_json.get("error", {}).get("message", response)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        raise HttpResponseError(response=response, message=failure_msg, error_format=ARMErrorFormat)

    return response


def upload_dependencies(deployment: Deployment, orchestrators: OperationOrchestrator) -> None:
    """Upload code, dependency, model dependencies.
    For BatchDeployment only register compute.
    :param Deployment deployment: Endpoint deployment object.
    :param OperationOrchestrator orchestrators: Operation Orchestrator.
    """

    module_logger.debug(f"Uploading the dependencies for deployment {deployment.name}")

    # Create a code asset if code is not already an ARM ID
    if deployment.code_configuration and not is_ARM_id_for_resource(
        deployment.code_configuration.code, AzureMLResourceType.CODE
    ):
        deployment.code_configuration.code = orchestrators.get_asset_arm_id(
            Code(base_path=deployment._base_path, path=deployment.code_configuration.code),
            azureml_type=AzureMLResourceType.CODE,
        )
    deployment.environment = (
        orchestrators.get_asset_arm_id(deployment.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)
        if deployment.environment
        else None
    )
    deployment.model = (
        orchestrators.get_asset_arm_id(deployment.model, azureml_type=AzureMLResourceType.MODEL)
        if deployment.model
        else None
    )
    if isinstance(deployment, BatchDeployment) and deployment.compute:
        deployment.compute = orchestrators.get_asset_arm_id(
            deployment.compute, azureml_type=AzureMLResourceType.COMPUTE
        )
