# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Dict, Iterable, Any, Type, Optional
from collections import OrderedDict
from datetime import timedelta
from msrest.serialization import Model
from ._generated.models import QueueDescription


QUEUE_DESCRIPTION_SERIALIZE_ATTRIBUTES = (
    'lock_duration',
    'max_size_in_megabytes',
    'requires_duplicate_detection',
    'requires_session',
    'default_message_time_to_live',
    'dead_lettering_on_message_expiration',
    'duplicate_detection_history_time_window',
    'max_delivery_count',
    'enable_batched_operations',
    'size_in_bytes',
    'message_count',
    'is_anonymous_accessible',
    'authorization_rules',
    'status',
    'created_at',
    'updated_at',
    'accessed_at',
    'support_ordering',
    'message_count_details',
    'auto_delete_on_idle',
    'enable_partitioning',
    'entity_availability_status',
    'enable_express',
)


def avoid_timedelta_overflow(td):
    # type: (Optional[timedelta]) -> Optional[timedelta]
    """Service Bus REST API uses "P10675199DT2H48M5.4775807S" as default value for some properties, which are of type
    datetime.timedelta. When they are deserialized, Python round the milliseconds from 4775807 to 477581.
    When we get an entity (for instance, QueueDescription) and update this entity, this default value is
    deserialized to "P10675199DT2H48M5.477581S". Service Bus doesn't accept this value probably because it's too large.
    The workaround is to deduct the milliseconds by 0.000001.
    """
    result = td
    if td is not None and td.days == 10675199 and td.microseconds >= 477581:
        result = timedelta(seconds=td.total_seconds() - 0.000001)
    return result


def adjust_dict_key_sequence(dct, keys):
    # type: (Dict[str, Any], Iterable[str]) -> Dict[str, Any]

    result = OrderedDict()
    for key in keys:
        result[key] = dct.pop(key)
    result.update(dct)
    return result


def adjust_attribute_map(class_):
    # type: (Type[Model]) -> None
    """update_queue will serialize QueueDescription to XML. The tags sequence is important to service. It doesn't
    make sense but it is what it is. This workaround is to adjust the sequence of the items in Model
    class _attribute_map so the serialized XML tags has the correct sequence.
    """
    # pylint:disable=protected-access
    class_._attribute_map = adjust_dict_key_sequence(
        class_._attribute_map,
        QUEUE_DESCRIPTION_SERIALIZE_ATTRIBUTES
    )


adjust_attribute_map(QueueDescription)
