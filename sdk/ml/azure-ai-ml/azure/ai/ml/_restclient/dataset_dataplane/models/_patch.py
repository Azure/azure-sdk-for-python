# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict

from ._models import DataVersionEntity

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def _additional_properties(self: DataVersionEntity) -> Dict[str, Any]:
    """Backwards-compatibility shim for the removed msrest ``additional_properties`` attribute.

    When this client was migrated to TypeSpec, ``DataVersionEntity`` became a hybrid
    (``MutableMapping``) model, which does not expose the msrest ``additional_properties``
    attribute. External consumers still depend on it -- notably the ``mltable`` package's local
    data-asset resolution path (``MLClient.jobs._dataset_dataplane_operations._operation.get``),
    which reads ``data_version.additional_properties['isV2' | 'legacyDataflow']``. Losing the
    attribute raised ``AttributeError`` when loading an ``azureml://`` MLTable data asset.

    This restores the original contract by returning the un-modeled wire keys, i.e. the keys
    present on the wire payload that are not backed by a declared ``rest_field`` on the model.

    :return: The wire properties not declared as fields on the model.
    :rtype: dict[str, typing.Any]
    """
    # Wire names of the declared fields (e.g. ``dataVersion``, ``entityMetadata``).
    modeled = {
        getattr(rf, "_rest_name", None)  # pylint: disable=protected-access
        for rf in getattr(self, "_attr_to_rest_field", {}).values()
    }
    raw = getattr(self, "_data", None)  # pylint: disable=protected-access
    items = raw.items() if isinstance(raw, dict) else self.items()
    return {key: value for key, value in items if key not in modeled}


# Attach only when the generated model does not already provide it, so a future TypeSpec
# regeneration that restores ``additional_properties`` natively takes precedence.
if not hasattr(DataVersionEntity, "additional_properties"):
    DataVersionEntity.additional_properties = property(_additional_properties)  # type: ignore[attr-defined]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
