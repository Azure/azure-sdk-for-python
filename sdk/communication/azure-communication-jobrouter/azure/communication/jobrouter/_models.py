# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import MutableMapping
from collections import Counter

from ._generated.models import JobQueueInternal


def _validate_value(value):
    primitive = (int,
                 float,
                 str,
                 bool)
    return isinstance(value, primitive)


class LabelCollection(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__store = {}
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if _validate_value(value):
                self.__store[key] = value
            else:
                raise ValueError("Unsupported value type " + str(type(value)))
        else:
            raise ValueError("Unsupported key type " + str(type(key)))

    def __delitem__(self, key):
        del self.__store[key]

    def __getitem__(self, item):
        return self.__store[item]

    def __iter__(self):
        return iter(self.__store)

    def __len__(self):
        return len(self.__store)

    def __repr__(self):
        return repr(self.__store)

    def __eq__(self, other):
        return Counter(self.__store) == Counter(other)


class JobQueue(object):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('identifier', None)
        self.name = kwargs.pop('name', None)
        self.distribution_policy_id = kwargs.pop('distribution_policy_id', None)
        self.labels = kwargs.pop('labels', None)
        self.exception_policy_id = kwargs.pop('exception_policy_id', None)

    @classmethod
    def _from_generated(cls, job_queue_generated):
        return cls(
            identifier = job_queue_generated.id,
            name = job_queue_generated.name,
            distribution_policy_id = job_queue_generated.distribution_policy_id,
            labels = LabelCollection(job_queue_generated.labels),
            exception_policy_id = job_queue_generated.exception_policy_id
        )

    def _to_generated(self):
        return JobQueueInternal(
            name = self.name,
            distribution_policy_id = self.distribution_policy_id,
            labels = self.labels,
            exception_policy_id = self.exception_policy_id
        )
