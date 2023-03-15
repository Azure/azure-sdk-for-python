# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from .resource_configuration import ResourceConfigurationSchema


class JobResourceConfigurationSchema(ResourceConfigurationSchema):
    locations = fields.List(fields.Str())
    shm_size = fields.Str(
        metadata={
            "description": (
                "The size of the docker container's shared memory block. "
                "This should be in the format of `<number><unit>` where number as "
                "to be greater than 0 and the unit can be one of "
                "`b` (bytes), `k` (kilobytes), `m` (megabytes), or `g` (gigabytes)."
            )
        }
    )
    docker_args = fields.Str(metadata={"description": "arguments to pass to the Docker run command."})

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import JobResourceConfiguration

        return JobResourceConfiguration(**data)
