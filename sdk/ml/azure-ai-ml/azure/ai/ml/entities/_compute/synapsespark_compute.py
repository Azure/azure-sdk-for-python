# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional

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
    """Auto scale settings for synapse spark compute"""

    def __init__(
        self,
        *,
        min_node_count: Optional[int] = None,
        max_node_count: Optional[int] = None,
        enabled: Optional[bool] = None,
    ):
        """Auto scale settings for synapse spark compute

        :param min_node_count: Min node count
        :type min_node_count: int
        :param max_node_count: Max node count
        :type max_node_count: int
        :param auto_scale_enabled:  Auto scale enabled
        :type auto_scale_enabled: bool
        """
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
    """Auto pause settings for synapse spark compute"""

    def __init__(self, *, delay_in_minutes: Optional[int] = None, enabled: Optional[bool] = None):
        """Auto pause settings for synapse spark compute

        :param delay_in_minutes: ideal time delay in minutes before pause cluster
        :type delay_in_minutes: int
        :param auto_scale_enabled:  Auto pause enabled
        :type auto_scale_enabled: bool
        """
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
    """SynapseSpark Compute resource

    :param name: Name of the compute
    :type name: str
    :param location: The resource location, defaults to None
    :type location: Optional[str], optional
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param resource_id: ARM resource id of the underlying compute, defaults to None
    :type resource_id: Optional[str], optional
    :param tags: A set of tags. Contains resource tags defined as key/value pairs.
    :type tags: Optional[dict[str, str]]
    :param identity:  The identity configuration, identities that are associated with the compute cluster.
    :type identity: IdentityConfiguration, optional
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[dict] = None,
        node_count: Optional[int] = None,
        node_family: Optional[str] = None,
        node_size: Optional[str] = None,
        spark_version: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        scale_settings: Optional[AutoScaleSettings] = None,
        auto_pause_settings: Optional[AutoPauseSettings] = None,
        **kwargs,
    ):
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
            provisioning_errors=prop.provisioning_errors[0].error.code
            if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
            else None,
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return SynapseSparkComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "SynapseSparkCompute":
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
