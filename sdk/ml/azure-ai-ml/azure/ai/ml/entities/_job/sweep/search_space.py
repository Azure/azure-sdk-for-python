# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from abc import ABC
from typing import List, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, JobException
from azure.ai.ml.constants import TYPE, SearchSpace
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class SweepDistribution(ABC, RestTranslatableMixin):
    def __init__(self, *, type: str = None):
        self.type = type

    @classmethod
    def _from_rest_object(cls, rest: List) -> "SweepDistribution":

        mapping = {
            SearchSpace.CHOICE: Choice,
            SearchSpace.NORMAL: Normal,
            SearchSpace.LOGNORMAL: LogNormal,
            SearchSpace.QNORMAL: QNormal,
            SearchSpace.QLOGNORMAL: QLogNormal,
            SearchSpace.RANDINT: Randint,
            SearchSpace.UNIFORM: Uniform,
            SearchSpace.QUNIFORM: QUniform,
            SearchSpace.LOGUNIFORM: LogUniform,
            SearchSpace.QLOGUNIFORM: QLogUniform,
        }

        ss_class = mapping.get(rest[0], None)
        if ss_class:
            return ss_class._from_rest_object(rest)
        else:
            msg = f"Unknown search space type: {rest[0]}"
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.SWEEP_JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SweepDistribution):
            return NotImplemented
        return self._to_rest_object() == other._to_rest_object()


class Choice(SweepDistribution):
    def __init__(self, values: List[Union[float, str, dict]] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.CHOICE)
        super().__init__(**kwargs)
        self.values = values

    def _to_rest_object(self) -> List:
        items = []
        for value in self.values:
            if isinstance(value, dict):
                rest_dict = {}
                for k, v in value.items():
                    if isinstance(v, SweepDistribution):
                        rest_dict[k] = v._to_rest_object()
                    else:
                        rest_dict[k] = v
                items.append(rest_dict)
            else:
                items.append(value)
        return [self.type, [items]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "Choice":
        rest_values = rest[1][0]
        from_rest_values = []
        for rest_value in rest_values:
            if isinstance(rest_value, dict):
                from_rest_dict = {}
                for k, v in rest_value.items():
                    try:
                        # first assume that any dictionary value is a valid distribution (i.e. normal, uniform, etc)
                        # and try to deserialize it into a the correct SDK distribution object
                        from_rest_dict[k] = SweepDistribution._from_rest_object(v)
                    except Exception:
                        # if an exception is raised, assume that the value was not a valid distribution and use the
                        # value as it is for deserialization
                        from_rest_dict[k] = v
                from_rest_values.append(from_rest_dict)
            else:
                from_rest_values.append(rest_value)
        return Choice(values=from_rest_values)


class Normal(SweepDistribution):
    def __init__(self, mu: float = None, sigma: float = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.NORMAL)
        super().__init__(**kwargs)
        self.mu = mu
        self.sigma = sigma

    def _to_rest_object(self) -> List:
        return [self.type, [self.mu, self.sigma]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "Normal":
        return cls(mu=rest[1][0], sigma=rest[1][1])


class LogNormal(Normal):
    def __init__(self, mu: float = None, sigma: float = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.LOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, **kwargs)


class QNormal(Normal):
    def __init__(self, mu: float = None, sigma: float = None, q: int = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.QNORMAL)
        super().__init__(mu=mu, sigma=sigma, **kwargs)
        self.q = q

    def _to_rest_object(self) -> List:
        return [self.type, [self.mu, self.sigma, self.q]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "QNormal":
        return cls(mu=rest[1][0], sigma=rest[1][1], q=rest[1][2])


class QLogNormal(QNormal):
    def __init__(self, mu: float = None, sigma: float = None, q: int = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.QLOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, q=q, **kwargs)


class Randint(SweepDistribution):
    def __init__(self, upper: int = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.RANDINT)
        super().__init__(**kwargs)
        self.upper = upper

    def _to_rest_object(self) -> List:
        return [self.type, [self.upper]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "Randint":
        return cls(upper=rest[1][0])


class Uniform(SweepDistribution):
    def __init__(self, min_value: float = None, max_value: float = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.UNIFORM)
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def _to_rest_object(self) -> List:
        return [self.type, [self.min_value, self.max_value]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "Uniform":
        return cls(min_value=rest[1][0], max_value=rest[1][1])


class LogUniform(Uniform):
    def __init__(self, min_value: float = None, max_value: float = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.LOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, **kwargs)


class QUniform(Uniform):
    def __init__(
        self,
        min_value: Union[int, float] = None,
        max_value: Union[int, float] = None,
        q: int = None,
        **kwargs,
    ):
        kwargs.setdefault(TYPE, SearchSpace.QUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, **kwargs)
        self.q = q

    def _to_rest_object(self) -> List:
        return [self.type, [self.min_value, self.max_value, self.q]]

    @classmethod
    def _from_rest_object(cls, rest: List) -> "QUniform":
        return cls(min_value=rest[1][0], max_value=rest[1][1], q=rest[1][2])


class QLogUniform(QUniform):
    def __init__(self, min_value: float = None, max_value: float = None, q: int = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.QLOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, q=q, **kwargs)
