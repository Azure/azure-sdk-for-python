# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from . import _models

    # The Data Factory service sends and expects the data flow reference of an
    # ExecuteDataFlowActivity as lowercase ``typeProperties.dataflow``, but the
    # generated model maps ``data_flow`` to ``typeProperties.dataFlow``, which
    # loses the reference on deserialization and drops it from serialized
    # payloads. Point the field at the wire name the service actually uses.
    # https://github.com/Azure/azure-sdk-for-python/issues/48704
    data_flow_field = _models.ExecuteDataFlowActivityTypeProperties.__dict__["data_flow"]
    data_flow_field._rest_name_input = "dataflow"  # pylint: disable=protected-access
