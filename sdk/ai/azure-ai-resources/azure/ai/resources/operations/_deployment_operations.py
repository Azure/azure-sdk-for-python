# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import ast
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, List, Union, Iterable


from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineDeployment, ManagedOnlineEndpoint, Model as AzureMLModel, DataCollector, DeploymentCollection, Environment, BuildContext
from azure.core.tracing.decorator import distributed_trace

from .._utils._scoring_script_utils import create_chat_scoring_script, create_mlmodel_file
from .._utils._registry_utils import get_registry_model
from .._utils._deployment_utils import get_default_allowed_instance_type_for_hugging_face
from ..entities.deployment import Deployment
from ..entities.deployment_keys import DeploymentKeys
from ..entities.models import Model, PromptflowModel

from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin, OpsLogger

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class DeploymentOperations:
    def __init__(self, ml_client: MLClient, connections, **kwargs) -> None:
        self._ml_client = ml_client
        self._connections = connections
        ops_logger.update_info(kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, deployment: Deployment) -> Any:
        model = deployment.model
        endpoint_name = deployment.endpoint_name if deployment.endpoint_name else deployment.name

        data_collector = None
        if deployment.data_collector_enabled:
            data_collector = DataCollector(
                collections={
                    "model_inputs": DeploymentCollection(
                        enabled="true",
                    ),
                    "model_outputs": DeploymentCollection(
                        enabled="true",
                    )
                },
                sampling_rate=1,
            )

        v2_endpoint = ManagedOnlineEndpoint(
            name=endpoint_name,
            properties={
                "enforce_access_to_default_secret_stores": "enabled"
            }
        )
        created_endpoint = self._ml_client.begin_create_or_update(v2_endpoint).result()
        model = deployment.model
        v2_deployment = None
        temp_dir = tempfile.TemporaryDirectory()
        if isinstance(model, PromptflowModel):
            if not deployment.instance_type:
                deployment.instance_type = "Standard_DS3_v2"
            # Create dockerfile
            with open(f"{model.path}/Dockerfile", "w+") as f:
                base_image = "mcr.microsoft.com/azureml/promptflow/promptflow-runtime:latest" if not model.base_image else model.base_image
                f.writelines([f"FROM {base_image}\n", "COPY ./* /\n", "RUN pip install -r requirements.txt\n"])
            azureml_environment = Environment(
                build=BuildContext(
                    path=model.path
                ),
                inference_config={
                    "liveness_route": {"path": "/health", "port": 8080},
                    "readiness_route": {"path": "/health", "port": 8080},
                    "scoring_route": {"path": "/score", "port": 8080},
                },
                is_anonymous=True,
            )
            azureml_model = AzureMLModel(name=f"{deployment.name}-deployment-pf", path=model.path, type="custom_model")
            deployment_environment_variables = (
                deployment.environment_variables if deployment.environment_variables else {}
            )
            v2_deployment = ManagedOnlineDeployment(
                name=deployment.name,
                endpoint_name=endpoint_name,
                model=azureml_model,
                environment=azureml_environment,
                instance_type=deployment.instance_type,
                instance_count=deployment.instance_count if not deployment.instance_count else 1,
                environment_variables={
                    "PROMPTFLOW_RUN_MODE": "serving",
                    "PRT_CONFIG_OVERRIDE": f"deployment.subscription_id={self._ml_client.subscription_id},deployment.resource_group={self._ml_client.resource_group_name},deployment.workspace_name={self._ml_client.workspace_name},deployment.endpoint_name={endpoint_name},deployment.deployment_name={deployment.name}",
                    **deployment_environment_variables,
                },
                app_insights_enabled=deployment.app_insights_enabled,
                data_collector=data_collector,
            )
        if isinstance(model, Model):
            if not deployment.instance_type:
                deployment.instance_type = "Standard_DS3_v2"
            if model.loader_module and model.chat_module:
                raise Exception("Only one of loader_module or chat_module for a model can be specified but not both.")
            azureml_environment = None
            scoring_script = None
            azureml_model = None
            if model.conda_file and model.loader_module:
                create_mlmodel_file(model)
                azureml_model = AzureMLModel(name=f"{deployment.name}-deployment-model", path=model.path, type="mlflow_model")
            if model.conda_file and model.chat_module:
                azureml_model = AzureMLModel(name=f"{deployment.name}-deployment-model", path=model.path, type="custom_model")
                chat_module = f"{Path(model.path).resolve().name}.{model.chat_module}"
                create_chat_scoring_script(temp_dir.name, chat_module)
                azureml_environment = Environment(
                    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
                    conda_file=str(Path(model.path) / model.conda_file),
                    is_anonymous=True,
                )
                scoring_script = "score.py"
            else:
                # validate that path has an mlmodel file and continue
                if "mlmodel" not in [path.lower() for path in os.listdir(model.path)]:
                    raise Exception(
                        "An MLModel file must be present in model directory if not"
                        " specifying conda_file and one of loader_module or chat_module for deployment."
                    )

            v2_deployment = ManagedOnlineDeployment(
                name=deployment.name,
                endpoint_name=endpoint_name,
                model=azureml_model,
                environment=azureml_environment,
                code_path=temp_dir.name if scoring_script else None,
                scoring_script=scoring_script,
                instance_type=deployment.instance_type,
                instance_count=1,
                environment_variables=deployment.environment_variables,
                app_insights_enabled=deployment.app_insights_enabled,
                data_collector=data_collector,
            )
        if isinstance(model, str) and "registries" in model:
            model_details = get_registry_model(
                self._ml_client._credential,
                id=model,
            )
            model_id = model

            if not deployment.instance_type:
                if "registries/HuggingFace" in model_details.id:
                    default_instance_type, allowed_instance_types = get_default_allowed_instance_type_for_hugging_face(
                        model_details, self._ml_client._credential
                    )
                    self._check_default_instance_type_and_populate(
                        default_instance_type, deployment, allowed_instance_types=allowed_instance_types
                    )

                if "registries/azureml" in model_details.id:
                    default_instance_type = model_details.properties["inference-recommended-sku"]
                    min_sku_spec = model_details.properties["inference-min-sku-spec"].split("|")
                    self._check_default_instance_type_and_populate(
                        default_instance_type, deployment, min_sku_spec=min_sku_spec
                    )
                if "registries/azureml-meta" in model_details.id:
                    allowed_skus = ast.literal_eval(model_details.tags["inference_compute_allow_list"])
                    # check available quota for each sku in the allowed_sku list
                    # pick the sku that has available quota and is the cheapest
                    vm_sizes = self._ml_client.compute._vmsize_operations.list(
                        location=self._ml_client.compute._get_workspace_location()
                    )
                    # create mapping of allowed SKU to (SKU family, number of vCPUs, and cost per hour on linux)
                    filtered_vm_sizes = [vm_size for vm_size in vm_sizes.value if vm_size.name in allowed_skus]
                    sku_to_family_vcpu_cost_map = {}
                    sku_families = []
                    for vm_size in filtered_vm_sizes:
                        cost = None
                        for vm_price in vm_size.estimated_vm_prices.values:
                            if vm_price.os_type == "Linux" and vm_price.vm_tier == "Standard":
                                cost = vm_price.retail_price
                        sku_to_family_vcpu_cost_map[vm_size.name] = (vm_size.family, vm_size.v_cp_us, cost)
                        sku_families.append(vm_size.family)

                    # sort allowed skus by price and find the first vm that has enough quota
                    sku_to_family_vcpu_cost_map = dict(
                        sorted(sku_to_family_vcpu_cost_map.items(), key=lambda item: item[1][2])
                    )
                    # get usage info and filter it down to dedicated usage for each SKU family
                    usage_info = self._ml_client.compute.list_usage()
                    filtered_usage_info = {
                        filtered_usage.name["value"]: filtered_usage
                        for filtered_usage in [
                            usage
                            for usage in usage_info
                            if usage.name["value"] in sku_families and "Dedicated" in usage.name["localized_value"]
                        ]
                    }

                    # loop over each sku and check if the family has enough cores available that will not
                    # exceed family limit
                    for sku_name, sku_details in sku_to_family_vcpu_cost_map.items():
                        family, vcpus, cost = sku_details
                        family_usage = filtered_usage_info[family]
                        if deployment.instance_count * vcpus + family_usage.current_value <= family_usage.limit:
                            deployment.instance_type = sku_name
                            break
                    if not deployment.instance_type:
                        # if not enough quota, raise an exception and list out SKUs that user needs to request quota for
                        raise Exception(
                            f"There is no quota in the project's region for these model's allowed inference instance types: {allowed_skus}. "
                            "Please request a quota increase for one of these instance types or try to deploying to a project in a region "
                            "with more quota."
                        )

            v2_deployment = ManagedOnlineDeployment(
                name=deployment.name,
                endpoint_name=endpoint_name,
                model=model_id,
                instance_type=deployment.instance_type,
                instance_count=1,
                app_insights_enabled=deployment.app_insights_enabled,
                data_collector=data_collector,
            )

        v2_deployment.tags = deployment.tags
        v2_deployment.properties = deployment.properties
        create_deployment_poller = self._ml_client.begin_create_or_update(v2_deployment)
        shutil.rmtree(temp_dir.name)
        created_deployment = create_deployment_poller.result()

        created_endpoint.traffic = {deployment.name: 100}
        update_endpoint_poller = self._ml_client.begin_create_or_update(created_endpoint)
        updated_endpoint = update_endpoint_poller.result()

        return Deployment._from_v2_endpoint_deployment(updated_endpoint, deployment)

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, endpoint_name: str = None) -> Deployment:
        endpoint_name = endpoint_name if endpoint_name else name
        deployment = self._ml_client.online_deployments.get(
            name=name,
            endpoint_name=endpoint_name if endpoint_name else name,
        )
        endpoint = self._ml_client.online_endpoints.get(endpoint_name)

        return Deployment._from_v2_endpoint_deployment(endpoint, deployment)

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.List", ActivityType.PUBLICAPI)
    def list(self) -> Iterable[Deployment]:
        deployments = []
        endpoints = self._ml_client.online_endpoints.list()
        for endpoint in endpoints:
            v2_deployments = self._ml_client.online_deployments.list(endpoint.name)
            deployments.extend([Deployment._from_v2_endpoint_deployment(endpoint, deployment) for deployment in v2_deployments])
        return deployments

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.GetKeys", ActivityType.PUBLICAPI)
    def get_keys(self, name: str, endpoint_name: str = None) -> DeploymentKeys:
        endpoint_name = endpoint_name if endpoint_name else name
        return DeploymentKeys._from_v2_endpoint_keys(self._ml_client.online_endpoints.get_keys(endpoint_name))

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, endpoint_name: str = None) -> None:
        self._ml_client.online_deployments.delete(
            name=name,
            endpoint_name=endpoint_name if endpoint_name else name,
        ).result()

    @distributed_trace
    @monitor_with_activity(logger, "Deployment.Invoke", ActivityType.PUBLICAPI)
    def invoke(self, name: str, request_file: Union[str, os.PathLike], endpoint_name: str = None) -> Any:
        return self._ml_client.online_endpoints.invoke(
            endpoint_name=endpoint_name if endpoint_name else name,
            request_file=request_file,
            deployment_name=name,
        )

    def _check_default_instance_type_and_populate(
        self,
        instance_type: str,
        deployment: Deployment,
        allowed_instance_types: List[str] = None,
        min_sku_spec: str = None,
    ) -> bool:
        vm_sizes = self._ml_client.compute.list_sizes()
        inference_sku_vm_info = [vm for vm in vm_sizes if vm.name == instance_type][0]
        usage_info = self._ml_client.compute.list_usage()
        # from the list of all usage, get the usage specific to the recommend sku's family
        sku_family_usage = next(
            (
                usage
                for usage in usage_info
                if (
                    usage.name["value"] == inference_sku_vm_info.family and "Dedicated" in usage.name["localized_value"]
                )
            )
        )

        # if the family has enough cores available that will not exceed family limit, choose as deployment sku
        if (
            sku_family_usage.current_value + inference_sku_vm_info.v_cp_us * deployment.instance_count
            <= sku_family_usage.limit
        ):
            deployment.instance_type = instance_type
        else:
            exception_message = f"The recommended inference instance type for this model is {instance_type}, for which there is not enough quota.\n"
            if allowed_instance_types:
                exception_message += (
                    f"The following instance types are allowed for this model: {allowed_instance_types}. Please provide an instance type from this "
                    "list for which there is enough quota."
                )
            elif min_sku_spec:
                cpu, gpu, ram, storage = min_sku_spec.split("|")

                exception_message += (
                    f"Please provide an instance_type that meets the following minimum parameters: {cpu} vCPU cores, {gpu} GPU cores, "
                    f"{ram} GB of vRAM, {storage} GB of storage."
                )
            raise Exception(exception_message)
