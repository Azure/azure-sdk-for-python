# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from azure.mgmt.datafactory import models as _models

# The service sends and expects the data flow reference as lowercase
# "typeProperties.dataflow". See
# https://github.com/Azure/azure-sdk-for-python/issues/48704
SERVICE_PAYLOAD = {
    "name": "df",
    "type": "ExecuteDataFlow",
    "typeProperties": {
        "dataflow": {"referenceName": "MyFlow", "type": "DataFlowReference"},
        "compute": {"computeType": "General", "coreCount": 8},
        "traceLevel": "Fine",
    },
}


def test_execute_data_flow_activity_deserializes_lowercase_dataflow():
    activity = _models.ExecuteDataFlowActivity(SERVICE_PAYLOAD)

    assert isinstance(activity, _models.ExecuteDataFlowActivity)
    assert isinstance(activity.data_flow, _models.DataFlowReference)
    assert activity.data_flow.reference_name == "MyFlow"
    # sibling properties with matching casing keep working
    assert activity.trace_level == "Fine"
    assert activity.compute.core_count == 8


def test_execute_data_flow_activity_serializes_lowercase_dataflow():
    activity = _models.ExecuteDataFlowActivity(
        name="df",
        type_properties=_models.ExecuteDataFlowActivityTypeProperties(
            data_flow=_models.DataFlowReference(
                type=_models.DataFlowReferenceType.DATA_FLOW_REFERENCE,
                reference_name="MyFlow",
            )
        ),
    )

    type_properties = activity.as_dict()["typeProperties"]
    assert "dataFlow" not in type_properties
    assert type_properties["dataflow"] == {"referenceName": "MyFlow", "type": "DataFlowReference"}


def test_execute_data_flow_activity_round_trip_preserves_data_flow():
    activity = _models.ExecuteDataFlowActivity(SERVICE_PAYLOAD)
    serialized = activity.as_dict()

    assert serialized["typeProperties"]["dataflow"] == {
        "referenceName": "MyFlow",
        "type": "DataFlowReference",
    }

    round_tripped = _models.ExecuteDataFlowActivity(serialized)
    assert round_tripped.data_flow.reference_name == "MyFlow"


def test_execute_data_flow_activity_flattened_data_flow_setter():
    activity = _models.ExecuteDataFlowActivity(name="df")
    activity.data_flow = _models.DataFlowReference(
        type=_models.DataFlowReferenceType.DATA_FLOW_REFERENCE,
        reference_name="MyFlow",
    )

    assert activity.type_properties.data_flow.reference_name == "MyFlow"
    assert activity.as_dict()["typeProperties"]["dataflow"]["referenceName"] == "MyFlow"
