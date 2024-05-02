# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    AutoPauseProperties,
    AutoScaleProperties,
    ComputeResource,
    SynapseSpark,
)
from azure.ai.ml._schema.compute.synapsespark_compute import SynapseSparkComputeSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities import Compute
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._util import load_from_dict


class AutoScaleSettings:
    """Auto-scale settings for Synapse Spark compute.

    :keyword min_node_count: The minimum compute node count.
    :paramtype min_node_count: Optional[int]
    :keyword max_node_count: The maximum compute node count.
    :paramtype max_node_count: Optional[int]
    :keyword enabled: Specifies if auto-scale is enabled.
    :paramtype enabled: Optional[bool]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START synapse_spark_compute_configuration]
            :end-before: [END synapse_spark_compute_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring AutoScaleSettings on SynapseSparkCompute.
    """

    def __init__(
        self,
        *,
        min_node_count: Optional[int] = None,
        max_node_count: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self.min_node_count = min_node_count
        self.max_node_count = max_node_count
        self.auto_scale_enabled = enabled

    def _to_auto_scale_settings(self) -> AutoScaleProperties:
        return AutoScaleProperties(
            min_node_count=self.min_node_count,
            max_node_count=self.max_node_count,
            auto_scale_enabled=self.auto_scale_enabled,
        )

    @classmethod
    def _from_auto_scale_settings(cls, autoscaleprops: AutoScaleProperties) -> "AutoScaleSettings":
        return cls(
            min_node_count=autoscaleprops.min_node_count,
            max_node_count=autoscaleprops.max_node_count,
            enabled=autoscaleprops.enabled,
        )


class AutoPauseSettings:
    """Auto pause settings for Synapse Spark compute.

    :keyword delay_in_minutes: The time delay in minutes before pausing cluster.
    :paramtype delay_in_minutes: Optional[int]
    :keyword enabled: Specifies if auto-pause is enabled.
    :paramtype enabled: Optional[bool]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START synapse_spark_compute_configuration]
            :end-before: [END synapse_spark_compute_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring AutoPauseSettings on SynapseSparkCompute.
    """

    def __init__(self, *, delay_in_minutes: Optional[int] = None, enabled: Optional[bool] = None) -> None:
        self.delay_in_minutes = delay_in_minutes
        self.auto_pause_enabled = enabled

    def _to_auto_pause_settings(self) -> AutoPauseProperties:
        return AutoPauseProperties(
            delay_in_minutes=self.delay_in_minutes,
            auto_pause_enabled=self.auto_pause_enabled,
        )

    @classmethod
    def _from_auto_pause_settings(cls, autopauseprops: AutoPauseProperties) -> "AutoPauseSettings":
        return cls(
            delay_in_minutes=autopauseprops.delay_in_minutes,
            enabled=autopauseprops.enabled,
        )


@experimental
class SynapseSparkCompute(Compute):
    """SynapseSpark Compute resource.

    :keyword name: The name of the compute.
    :paramtype name: str
    :keyword description: The description of the resource. Defaults to None.
    :paramtype description: Optional[str]
    :keyword tags: The set of resource tags defined as key/value pairs. Defaults to None.
    :paramtype tags: Optional[[dict[str, str]]
    :keyword node_count: The number of nodes in the compute.
    :paramtype node_count: Optional[int]
    :keyword node_family: The node family of the compute.
    :paramtype node_family: Optional[str]
    :keyword node_size: The size of the node.
    :paramtype node_size: Optional[str]
    :keyword spark_version: The version of Spark to use.
    :paramtype spark_version: Optional[str]
    :keyword identity: The configuration of identities that are associated with the compute cluster.
    :paramtype identity: Optional[~azure.ai.ml.entities.IdentityConfiguration]
    :keyword scale_settings: The scale settings for the compute.
    :paramtype scale_settings: Optional[~azure.ai.ml.entities.AutoScaleSettings]
    :keyword auto_pause_settings: The auto pause settings for the compute.
    :paramtype auto_pause_settings: Optional[~azure.ai.ml.entities.AutoPauseSettings]
    :keyword kwargs: Additional keyword arguments passed to the parent class.
    :paramtype kwargs: Optional[dict]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START synapse_spark_compute_configuration]
            :end-before: [END synapse_spark_compute_configuration]
            :language: python
            :dedent: 8
            :caption: Creating Synapse Spark compute.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        node_count: Optional[int] = None,
        node_family: Optional[str] = None,
        node_size: Optional[str] = None,
        spark_version: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        scale_settings: Optional[AutoScaleSettings] = None,
        auto_pause_settings: Optional[AutoPauseSettings] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = ComputeType.SYNAPSESPARK
        super().__init__(name=name, description=description, location=kwargs.pop("location", None), tags=tags, **kwargs)
        self.identity = identity
        self.node_count = node_count
        self.node_family = node_family
        self.node_size = node_size
        self.spark_version = spark_version
        self.scale_settings = scale_settings
        self.auto_pause_settings = auto_pause_settings

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "SynapseSparkCompute":
        prop = rest_obj.properties
        scale_settings = (
            # pylint: disable=protected-access
            AutoScaleSettings._from_auto_scale_settings(prop.properties.auto_scale_properties)
            if prop.properties.auto_scale_properties
            else None
        )

        auto_pause_settings = (
            # pylint: disable=protected-access
            AutoPauseSettings._from_auto_pause_settings(prop.properties.auto_pause_properties)
            if prop.properties.auto_pause_properties
            else None
        )

        return SynapseSparkCompute(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            tags=rest_obj.tags if rest_obj.tags else None,
            created_on=prop.created_on if prop.properties else None,
            node_count=prop.properties.node_count if prop.properties else None,
            node_family=prop.properties.node_size_family if prop.properties else None,
            node_size=prop.properties.node_size if prop.properties else None,
            spark_version=prop.properties.spark_version if prop.properties else None,
            # pylint: disable=protected-access
            identity=IdentityConfiguration._from_compute_rest_object(rest_obj.identity) if rest_obj.identity else None,
            scale_settings=scale_settings,
            auto_pause_settings=auto_pause_settings,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=(
                prop.provisioning_errors[0].error.code
                if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
                else None
            ),
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = SynapseSparkComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "SynapseSparkCompute":
        loaded_data = load_from_dict(SynapseSparkComputeSchema, data, context, **kwargs)
        return SynapseSparkCompute(**loaded_data)

    def _to_rest_object(self) -> ComputeResource:
        synapsespark_comp = SynapseSpark(
            name=self.name,
            compute_type=self.type,
            resource_id=self.resource_id,
            description=self.description,
        )
        return ComputeResource(
            location=self.location,
            properties=synapsespark_comp,
            name=self.name,
            identity=(
                # pylint: disable=protected-access
                self.identity._to_compute_rest_object()
                if self.identity
                else None
            ),
            tags=self.tags,
        )
