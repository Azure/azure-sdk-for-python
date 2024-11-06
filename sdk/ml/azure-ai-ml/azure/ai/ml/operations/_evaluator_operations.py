# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-value-for-parameter,disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype,ungrouped-imports,line-too-long,too-many-statements

from os import PathLike
from typing import Any, Dict, Iterable, Optional, Union, cast
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2023_08_01_preview import (
    AzureMachineLearningWorkspaces as ServiceClient082023Preview,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ListViewType,
)
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils.utils import (
    _get_evaluator_properties,
    _is_evaluator,
)
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.entities._assets.workspace_asset_reference import (
    WorkspaceAssetReference,
)
from azure.ai.ml.exceptions import (
    UnsupportedOperationError,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml.operations._model_operations import ModelOperations

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class EvaluatorOperations(_ScopeDependentOperations):
    """EvaluatorOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.

    :param operation_scope: Scope variables for the operations classes of an MLClient object.
    :type operation_scope: ~azure.ai.ml._scope_dependent_operations.OperationScope
    :param operation_config: Common configuration for operations classes of an MLClient object.
    :type operation_config: ~azure.ai.ml._scope_dependent_operations.OperationConfig
    :param service_client: Service client to allow end users to operate on Azure Machine Learning Workspace
        resources (ServiceClient082023Preview or ServiceClient102021Dataplane).
    :type service_client: typing.Union[
        azure.ai.ml._restclient.v2023_04_01_preview._azure_machine_learning_workspaces.AzureMachineLearningWorkspaces,
        azure.ai.ml._restclient.v2021_10_01_dataplanepreview._azure_machine_learning_workspaces.
        AzureMachineLearningWorkspaces]
    :param datastore_operations: Represents a client for performing operations on Datastores.
    :type datastore_operations: ~azure.ai.ml.operations._datastore_operations.DatastoreOperations
    :param all_operations: All operations classes of an MLClient object.
    :type all_operations: ~azure.ai.ml._scope_dependent_operations.OperationsContainer
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient082023Preview, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        all_operations: Optional[OperationsContainer] = None,
        **kwargs,
    ):
        super(EvaluatorOperations, self).__init__(operation_scope, operation_config)

        ops_logger.update_info(kwargs)
        self._model_op = ModelOperations(
            operation_scope=operation_scope,
            operation_config=operation_config,
            service_client=service_client,
            datastore_operations=datastore_operations,
            all_operations=all_operations,
            **{ModelOperations._IS_EVALUATOR: True},
            **kwargs,
        )
        self._operation_scope = self._model_op._operation_scope
        self._datastore_operation = self._model_op._datastore_operation

    @monitor_with_activity(ops_logger, "Evaluator.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(  # type: ignore
        self, model: Union[Model, WorkspaceAssetReference], **kwargs: Any
    ) -> Model:  # TODO: Are we going to implement job_name?
        """Returns created or updated model asset.

        :param model: Model asset object.
        :type model: ~azure.ai.ml.entities.Model
        :raises ~azure.ai.ml.exceptions.AssetPathException: Raised when the Model artifact path is
            already linked to another asset
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Model asset object.
        :rtype: ~azure.ai.ml.entities.Model
        """
        model.properties.update(_get_evaluator_properties())
        return self._model_op.create_or_update(model)

    def _raise_if_not_evaluator(self, properties: Optional[Dict[str, Any]], message: str) -> None:
        """
        :param properties: The properties of a model.
        :type properties: dict[str, str]
        :param message: The message to be set on exception.
        :type message: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if model is not an
                                                             evaluator.
        """
        if properties is not None and not _is_evaluator(properties):
            raise ResourceNotFoundError(
                message=message,
                response=None,
            )

    @monitor_with_activity(ops_logger, "Evaluator.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, *, version: Optional[str] = None, label: Optional[str] = None, **kwargs) -> Model:
        """Returns information about the specified model asset.

        :param name: Name of the model.
        :type name: str
        :keyword version: Version of the model.
        :paramtype version: str
        :keyword label: Label of the model. (mutually exclusive with version)
        :paramtype label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Model cannot be successfully validated.
            Details will be provided in the error message.
        :return: Model asset object.
        :rtype: ~azure.ai.ml.entities.Model
        """
        model = self._model_op.get(name, version, label)

        properties = None if model is None else model.properties
        self._raise_if_not_evaluator(
            properties,
            f"Evaluator {name} with version {version} not found.",
        )

        return model

    @monitor_with_activity(ops_logger, "Evaluator.Download", ActivityType.PUBLICAPI)
    def download(self, name: str, version: str, download_path: Union[PathLike, str] = ".", **kwargs: Any) -> None:
        """Download files related to a model.

        :param name: Name of the model.
        :type name: str
        :param version: Version of the model.
        :type version: str
        :param download_path: Local path as download destination, defaults to current working directory of the current
            user. Contents will be overwritten.
        :type download_path: Union[PathLike, str]
        :raises ResourceNotFoundError: if can't find a model matching provided name.
        """
        self._model_op.download(name, version, download_path)

    @monitor_with_activity(ops_logger, "Evaluator.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: str,
        stage: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
        **kwargs: Any,
    ) -> Iterable[Model]:
        """List all model assets in workspace.

        :param name: Name of the model.
        :type name: str
        :param stage: The Model stage
        :type stage: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived models.
            Defaults to :attr:`ListViewType.ACTIVE_ONLY`.
        :paramtype list_view_type: ListViewType
        :return: An iterator like instance of Model objects
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.Model]
        """
        properties_str = "is-promptflow=true,is-evaluator=true"
        if name:
            return cast(
                Iterable[Model],
                (
                    self._model_op._model_versions_operation.list(
                        name=name,
                        registry_name=self._model_op._registry_name,
                        cls=lambda objs: [Model._from_rest_object(obj) for obj in objs],
                        properties=properties_str,
                        **self._model_op._scope_kwargs,
                    )
                    if self._registry_name
                    else self._model_op._model_versions_operation.list(
                        name=name,
                        workspace_name=self._model_op._workspace_name,
                        cls=lambda objs: [Model._from_rest_object(obj) for obj in objs],
                        list_view_type=list_view_type,
                        properties=properties_str,
                        stage=stage,
                        **self._model_op._scope_kwargs,
                    )
                ),
            )
        # ModelContainer object does not carry properties.
        raise UnsupportedOperationError("list on evaluation operations without name provided")
        # TODO: Implement filtering of the ModelContainerOperations list output
        # return cast(
        #     Iterable[Model], (
        #         self._model_container_operation.list(
        #             registry_name=self._registry_name,
        #             cls=lambda objs: [Model._from_container_rest_object(obj) for obj in objs],
        #             list_view_type=list_view_type,
        #             **self._scope_kwargs,
        #         )
        #         if self._registry_name
        #         else self._model_container_operation.list(
        #             workspace_name=self._workspace_name,
        #             cls=lambda objs: [Model._from_container_rest_object(obj) for obj in objs],
        #             list_view_type=list_view_type,
        #             **self._scope_kwargs,
        #         )
        #     )
        # )
