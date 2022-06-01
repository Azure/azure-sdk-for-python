# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy

from azure.ai.ml._restclient.v2021_10_01.models import (
    EarlyTerminationPolicy as RestEarlyTerminationPolicy,
    BanditPolicy as RestBanditPolicy,
    MedianStoppingPolicy as RestMedianStoppingPolicy,
    TruncationSelectionPolicy as RestTruncationSelectionPolicy,
    EarlyTerminationPolicyType,
)
from azure.ai.ml.entities._util import SnakeToPascalDescriptor


class EarlyTerminationPolicy:

    type = SnakeToPascalDescriptor(private_name="policy_type")

    def __init__(self) -> None:
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: RestEarlyTerminationPolicy) -> "EarlyTerminationPolicy":
        if not rest_obj:
            return None

        policy = None
        if rest_obj.policy_type == EarlyTerminationPolicyType.BANDIT:
            policy = BanditPolicy()

        if rest_obj.policy_type == EarlyTerminationPolicyType.MEDIAN_STOPPING:
            policy = MedianStoppingPolicy()

        if rest_obj.policy_type == EarlyTerminationPolicyType.TRUNCATION_SELECTION:
            policy = TruncationSelectionPolicy()

        if policy:
            policy.__dict__.update(rest_obj.as_dict())

        return policy

    def _to_rest_object(self):
        base_dict = copy.deepcopy(self.__dict__)
        for key_to_del in ["additional_properties"]:
            if key_to_del in base_dict:
                del base_dict[key_to_del]
        return base_dict


class BanditPolicy(RestBanditPolicy, EarlyTerminationPolicy):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class MedianStoppingPolicy(RestMedianStoppingPolicy, EarlyTerminationPolicy):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class TruncationSelectionPolicy(RestTruncationSelectionPolicy, EarlyTerminationPolicy):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
