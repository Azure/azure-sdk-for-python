# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.monitoring.monitor_definition import MonitorDefinitionSchema
from azure.ai.ml._schema.schedule.schedule import ScheduleSchema


class MonitorScheduleSchema(ScheduleSchema):
    create_monitor = NestedField(MonitorDefinitionSchema)
