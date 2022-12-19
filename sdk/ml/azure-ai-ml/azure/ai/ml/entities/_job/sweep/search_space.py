# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from abc import ABC
from typing import List, Optional, Union

from azure.ai.ml.constants._common import TYPE
from azure.ai.ml.constants._job.sweep import SearchSpace
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException


class SweepDistribution(ABC, RestTranslatableMixin):
    def __init__(self, *, type: Optional[str] = None):  # pylint: disable=redefined-builtin
        self.type = type

    @classmethod
    def _from_rest_object(cls, obj: List) -> "SweepDistribution":

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

        ss_class = mapping.get(obj[0], None)
        if ss_class:
            return ss_class._from_rest_object(obj)

        msg = f"Unknown search space type: {obj[0]}"
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
    """Choice distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "choice" for this class.
    :vartype type: str
    """

    def __init__(self, values: Optional[List[Union[float, str, dict]]] = None, **kwargs):
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
    def _from_rest_object(cls, obj: List) -> "Choice":
        rest_values = obj[1][0]
        from_rest_values = []
        for rest_value in rest_values:
            if isinstance(rest_value, dict):
                from_rest_dict = {}
                for k, v in rest_value.items():
                    try:
                        # first assume that any dictionary value is a valid distribution (i.e. normal, uniform, etc)
                        # and try to deserialize it into a the correct SDK distribution object
                        from_rest_dict[k] = SweepDistribution._from_rest_object(v)
                    except Exception:  # pylint: disable=broad-except
                        # if an exception is raised, assume that the value was not a valid distribution and use the
                        # value as it is for deserialization
                        from_rest_dict[k] = v
                from_rest_values.append(from_rest_dict)
            else:
                from_rest_values.append(rest_value)
        return Choice(values=from_rest_values)


class Normal(SweepDistribution):
    """Normal distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "normal" for this class.
    :vartype type: str
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.NORMAL)
        super().__init__(**kwargs)
        self.mu = mu
        self.sigma = sigma

    def _to_rest_object(self) -> List:
        return [self.type, [self.mu, self.sigma]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "Normal":
        return cls(mu=obj[1][0], sigma=obj[1][1])


class LogNormal(Normal):
    """LogNormal distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "lognormal" for this class.
    :vartype type: str
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.LOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, **kwargs)


class QNormal(Normal):
    """QNormal distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "qnormal" for this class.
    :vartype type: str
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, q: Optional[int] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.QNORMAL)
        super().__init__(mu=mu, sigma=sigma, **kwargs)
        self.q = q

    def _to_rest_object(self) -> List:
        return [self.type, [self.mu, self.sigma, self.q]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "QNormal":
        return cls(mu=obj[1][0], sigma=obj[1][1], q=obj[1][2])


class QLogNormal(QNormal):
    """QLogNormal distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "qlognormal" for this class.
    :vartype type: str
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, q: Optional[int] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.QLOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, q=q, **kwargs)


class Randint(SweepDistribution):
    """Randint distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "randint" for this class.
    :vartype type: str
    """

    def __init__(self, upper: Optional[int] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.RANDINT)
        super().__init__(**kwargs)
        self.upper = upper

    def _to_rest_object(self) -> List:
        return [self.type, [self.upper]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "Randint":
        return cls(upper=obj[1][0])


class Uniform(SweepDistribution):
    """Uniform distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "uniform" for this class.
    :vartype type: str
    """

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.UNIFORM)
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def _to_rest_object(self) -> List:
        return [self.type, [self.min_value, self.max_value]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "Uniform":
        return cls(min_value=obj[1][0], max_value=obj[1][1])


class LogUniform(Uniform):
    """LogUniform distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "loguniform" for this class.
    :vartype type: str
    """

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, **kwargs):
        kwargs.setdefault(TYPE, SearchSpace.LOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, **kwargs)


class QUniform(Uniform):
    """QUniform distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "quniform" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        q: Optional[int] = None,
        **kwargs,
    ):
        kwargs.setdefault(TYPE, SearchSpace.QUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, **kwargs)
        self.q = q

    def _to_rest_object(self) -> List:
        return [self.type, [self.min_value, self.max_value, self.q]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "QUniform":
        return cls(min_value=obj[1][0], max_value=obj[1][1], q=obj[1][2])


class QLogUniform(QUniform):
    """QLogUniform distribution configuration.

    :ivar type: Specifies the type of sweep distribution. Set automatically to "qloguniform" for this class.
    :vartype type: str
    """

    def __init__(
        self, min_value: Optional[float] = None, max_value: Optional[float] = None, q: Optional[int] = None, **kwargs
    ):
        kwargs.setdefault(TYPE, SearchSpace.QLOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, q=q, **kwargs)
