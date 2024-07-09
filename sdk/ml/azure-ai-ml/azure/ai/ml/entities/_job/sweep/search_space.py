# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from abc import ABC
from typing import Any, List, Optional, Union

from azure.ai.ml.constants._common import TYPE
from azure.ai.ml.constants._job.sweep import SearchSpace
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException


class SweepDistribution(ABC, RestTranslatableMixin):
    """Base class for sweep distribution configuration.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :keyword type: Type of distribution.
    :paramtype type: str
    """

    def __init__(self, *, type: Optional[str] = None) -> None:  # pylint: disable=redefined-builtin
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

        ss_class: Any = mapping.get(obj[0], None)
        if ss_class:
            res: SweepDistribution = ss_class._from_rest_object(obj)
            return res

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
        res: bool = self._to_rest_object() == other._to_rest_object()
        return res


class Choice(SweepDistribution):
    """Choice distribution configuration.

    :param values: List of values to choose from.
    :type values: list[Union[float, str, dict]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_choice_loguniform]
            :end-before: [END configure_sweep_job_choice_loguniform]
            :language: python
            :dedent: 8
            :caption: Using Choice distribution to set values for a hyperparameter sweep
    """

    def __init__(self, values: Optional[List[Union[float, str, dict]]] = None, **kwargs: Any) -> None:
        kwargs.setdefault(TYPE, SearchSpace.CHOICE)
        super().__init__(**kwargs)
        self.values = values

    def _to_rest_object(self) -> List:
        items: List = []
        if self.values is not None:
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
                    except Exception:  # pylint: disable=W0718
                        # if an exception is raised, assume that the value was not a valid distribution and use the
                        # value as it is for deserialization
                        from_rest_dict[k] = v
                from_rest_values.append(from_rest_dict)
            else:
                from_rest_values.append(rest_value)
        return Choice(values=from_rest_values)  # type: ignore[arg-type]


class Normal(SweepDistribution):
    """Normal distribution configuration.

    :param mu: Mean of the distribution.
    :type mu: float
    :param sigma: Standard deviation of the distribution.
    :type sigma: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_randint_normal]
            :end-before: [END configure_sweep_job_randint_normal]
            :language: python
            :dedent: 8
            :caption: Configuring Normal distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, **kwargs: Any) -> None:
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

    :param mu: Mean of the log of the distribution.
    :type mu: float
    :param sigma: Standard deviation of the log of the distribution.
    :type sigma: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_lognormal_qlognormal]
            :end-before: [END configure_sweep_job_lognormal_qlognormal]
            :language: python
            :dedent: 8
            :caption: Configuring LogNormal distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(self, mu: Optional[float] = None, sigma: Optional[float] = None, **kwargs: Any) -> None:
        kwargs.setdefault(TYPE, SearchSpace.LOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, **kwargs)


class QNormal(Normal):
    """QNormal distribution configuration.

    :param mu: Mean of the distribution.
    :type mu: float
    :param sigma: Standard deviation of the distribution.
    :type sigma: float
    :param q: Quantization factor.
    :type q: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_qloguniform_qnormal]
            :end-before: [END configure_sweep_job_qloguniform_qnormal]
            :language: python
            :dedent: 8
            :caption: Configuring QNormal distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(
        self, mu: Optional[float] = None, sigma: Optional[float] = None, q: Optional[int] = None, **kwargs: Any
    ) -> None:
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

    :param mu: Mean of the log of the distribution.
    :type mu: Optional[float]
    :param sigma: Standard deviation of the log of the distribution.
    :type sigma: Optional[float]
    :param q: Quantization factor.
    :type q: Optional[int]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_lognormal_qlognormal]
            :end-before: [END configure_sweep_job_lognormal_qlognormal]
            :language: python
            :dedent: 8
            :caption: Configuring QLogNormal distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(
        self, mu: Optional[float] = None, sigma: Optional[float] = None, q: Optional[int] = None, **kwargs: Any
    ) -> None:
        kwargs.setdefault(TYPE, SearchSpace.QLOGNORMAL)
        super().__init__(mu=mu, sigma=sigma, q=q, **kwargs)


class Randint(SweepDistribution):
    """Randint distribution configuration.

    :param upper: Upper bound of the distribution.
    :type upper: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_randint_normal]
            :end-before: [END configure_sweep_job_randint_normal]
            :language: python
            :dedent: 8
            :caption: Configuring Randint distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(self, upper: Optional[int] = None, **kwargs: Any) -> None:
        kwargs.setdefault(TYPE, SearchSpace.RANDINT)
        super().__init__(**kwargs)
        self.upper = upper

    def _to_rest_object(self) -> List:
        return [self.type, [self.upper]]

    @classmethod
    def _from_rest_object(cls, obj: List) -> "Randint":
        return cls(upper=obj[1][0])


class Uniform(SweepDistribution):
    """

    Uniform distribution configuration.

    :param min_value: Minimum value of the distribution.
    :type min_value: float
    :param max_value: Maximum value of the distribution.
    :type max_value: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_uniform]
            :end-before: [END configure_sweep_job_uniform]
            :language: python
            :dedent: 8
            :caption: Configuring Uniform distributions for learning rates and momentum
                during a hyperparameter sweep on a Command job.
    """

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, **kwargs: Any) -> None:
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

    :param min_value: Minimum value of the log of the distribution.
    :type min_value: float
    :param max_value: Maximum value of the log of the distribution.
    :type max_value: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_choice_loguniform]
            :end-before: [END configure_sweep_job_choice_loguniform]
            :language: python
            :dedent: 8
            :caption: Configuring a LogUniform distribution for a hyperparameter sweep job learning rate
    """

    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None, **kwargs: Any) -> None:
        kwargs.setdefault(TYPE, SearchSpace.LOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, **kwargs)


class QUniform(Uniform):
    """QUniform distribution configuration.

    :param min_value: Minimum value of the distribution.
    :type min_value: Optional[Union[int, float]]
    :param max_value: Maximum value of the distribution.
    :type max_value: Optional[Union[int, float]]
    :param q: Quantization factor.
    :type q: Optional[int]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_truncation_selection_policy]
            :end-before: [END configure_sweep_job_truncation_selection_policy]
            :language: python
            :dedent: 8
            :caption: Configuring QUniform distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        q: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
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

    :param min_value: Minimum value of the log of the distribution.
    :type min_value: Optional[float]
    :param max_value: Maximum value of the log of the distribution.
    :type max_value: Optional[float]
    :param q: Quantization factor.
    :type q: Optional[int]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_qloguniform_qnormal]
            :end-before: [END configure_sweep_job_qloguniform_qnormal]
            :language: python
            :dedent: 8
            :caption: Configuring QLogUniform distributions for a hyperparameter sweep on a Command job.
    """

    def __init__(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        q: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault(TYPE, SearchSpace.QLOGUNIFORM)
        super().__init__(min_value=min_value, max_value=max_value, q=q, **kwargs)
