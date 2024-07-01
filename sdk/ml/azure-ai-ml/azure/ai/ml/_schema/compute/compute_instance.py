# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from marshmallow.decorators import post_load

# pylint: disable=unused-argument
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.constants._compute import ComputeType, ComputeSizeTier

from ..core.fields import ExperimentalField, NestedField, StringTransformedEnum
from .compute import ComputeSchema, IdentitySchema, NetworkSettingsSchema
from .schedule import ComputeSchedulesSchema
from .setup_scripts import SetupScriptsSchema
from .custom_applications import CustomApplicationsSchema


class ComputeInstanceSshSettingsSchema(PathAwareSchema):
    admin_username = fields.Str(dump_only=True)
    ssh_port = fields.Str(dump_only=True)
    ssh_key_value = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ComputeInstanceSshSettings

        return ComputeInstanceSshSettings(**data)


class CreateOnBehalfOfSchema(PathAwareSchema):
    user_tenant_id = fields.Str()
    user_object_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import AssignedUserConfiguration

        return AssignedUserConfiguration(**data)


class OsImageMetadataSchema(PathAwareSchema):
    is_latest_os_image_version = fields.Bool(dump_only=True)
    current_image_version = fields.Str(dump_only=True)
    latest_image_version = fields.Str(dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import ImageMetadata

        return ImageMetadata(**data)


class ComputeInstanceSchema(ComputeSchema):
    type = StringTransformedEnum(allowed_values=[ComputeType.COMPUTEINSTANCE], required=True)
    size = fields.Str(metadata={"arm_type": ComputeSizeTier.COMPUTE_INSTANCE})
    network_settings = NestedField(NetworkSettingsSchema)
    create_on_behalf_of = NestedField(CreateOnBehalfOfSchema)
    ssh_settings = NestedField(ComputeInstanceSshSettingsSchema)
    ssh_public_access_enabled = fields.Bool(dump_default=None)
    state = fields.Str(dump_only=True)
    last_operation = fields.Dict(keys=fields.Str(), values=fields.Str(), dump_only=True)
    services = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), dump_only=True)
    schedules = NestedField(ComputeSchedulesSchema)
    identity = ExperimentalField(NestedField(IdentitySchema))
    idle_time_before_shutdown = fields.Str()
    idle_time_before_shutdown_minutes = fields.Int()
    custom_applications = fields.List(NestedField(CustomApplicationsSchema))
    setup_scripts = NestedField(SetupScriptsSchema)
    os_image_metadata = NestedField(OsImageMetadataSchema, dump_only=True)
    enable_node_public_ip = fields.Bool(
        metadata={"description": "Enable or disable node public IP address provisioning."}
    )
    enable_sso = fields.Bool(metadata={"description": "Enable or disable single sign-on for the compute instance."})
    enable_root_access = fields.Bool(
        metadata={"description": "Enable or disable root access for the compute instance."}
    )
    release_quota_on_stop = fields.Bool(
        metadata={"description": "Release quota on stop for the compute instance. Defaults to False."}
    )
    enable_os_patching = fields.Bool(
        metadata={"description": "Enable or disable OS patching for the compute instance. Defaults to False."}
    )
