# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, Any, Dict

from ._models import (
    CallLocator,
    GroupCallLocator,
    ServerCallLocator
    )

if TYPE_CHECKING:
    from ._generated.models import (
        CallLocatorModel
        )

def serialize_call_locator(call_locator):
    # type: (CallLocator) -> Dict[str, Any]
    """Serialize the CallLocator into CallLocatorModel

    :param call_locator: CallLocator object
    :type call_locator: CallLocator
    :return: CallLocatorModel
    """
    try:
        request_model = {}

        if call_locator.kind:
            request_model[call_locator.kind] = dict(call_locator.properties)
        return request_model
    except AttributeError:
        raise TypeError("Unsupported call locator type " + call_locator.__class__.__name__)


def deserialize_call_locator(call_locator_model):
    # type: (CallLocatorModel) -> CallLocator
    """
    Deserialize the CallLocatorModel into CallLocator

    :param call_locator_model: CallLocatorModel
    :type call_locator_model: CallLocatorModel
    :return: CallLocator
    """

    if call_locator_model.group_call_id and call_locator_model.kind == "groupCallLocator":
        return GroupCallLocator(call_locator_model.group_call_id)
    if call_locator_model.server_call_id and call_locator_model.kind == "serverCallLocator":
        return ServerCallLocator(call_locator_model.server_call_id)
    return None
