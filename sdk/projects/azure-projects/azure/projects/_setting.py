# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Callable, Mapping, Optional, Union, List, Protocol
import os
import re

from azure.core.settings import _unset, _Unset, PrioritizedSetting, ValidInputType, ValueType

from ._bicep.expressions import Parameter, MISSING, Expression

_formatted_param = re.compile(r"\$\{(.*?)\}")


class SystemHookCallable(Protocol):
    def __call__(self, *, config_store: Optional[Mapping[str, Any]]): ...


class StoredPrioritizedSetting(PrioritizedSetting[ValidInputType, ValueType]):
    suffix: str

    def __init__(
        self,
        name: str,
        *,
        suffix: str = "",
        env_var: Optional[str] = None,
        env_vars: Optional[List[str]] = None,
        hook: Optional[SystemHookCallable] = None,
        default: Union[ValidInputType, _Unset] = _unset,
        user_value: Union[ValidInputType, _Unset] = _unset,
        convert: Optional[Callable[[Union[ValidInputType, str]], ValueType]] = None,
    ):
        super().__init__(
            name=name,
            env_var=env_var,
            default=default,
            convert=convert,
        )
        self.suffix = suffix or ""
        self._hook = hook
        self._user_value = user_value
        self._env_vars = env_vars or []

    def __call__(
        self, value: Optional[ValidInputType] = None, *, config_store: Optional[Mapping[str, Any]] = None
    ) -> ValueType:
        settingvalue = self._raw_value(value, config_store=config_store)
        if isinstance(settingvalue, str):
            for parameter in _formatted_param.findall(settingvalue):
                if not config_store:
                    raise RuntimeError(f"No config store provided to resolve parameterized value: '{settingvalue}'.")
                try:
                    # Mypy doesn't like this assignment, but we've already established settingvalue is str.
                    settingvalue = settingvalue.replace(  # type: ignore[assignment]
                        f"${{{parameter}}}", config_store[parameter]
                    )
                except KeyError as e:
                    raise RuntimeError(f"Unable to resolve parameterized value: '{settingvalue}'") from e
        return self._convert(settingvalue)

    def _convert_parameter(self, value: Parameter, *, config_store) -> ValidInputType:
        if value.name in config_store:
            return config_store[value.name]
        if value.env_var and os.environ.get(value.env_var) not in [None, ""]:
            # All settings with env vars are currently strings, so this should be fine.
            return os.environ[value.env_var]  # type: ignore[return-value]
        if value.default is not MISSING and not isinstance(value.default, Expression):
            return value.default
        raise RuntimeError(f"No value for parameter {value.name} found in config store.")

    def _raw_value(  # pylint: disable=too-many-return-statements, too-many-branches
        self, value: Optional[ValidInputType] = None, *, config_store: Optional[Mapping[str, Any]]
    ) -> ValidInputType:
        # 5. immediate values
        if value is not None:
            if isinstance(value, Parameter):
                return self._convert_parameter(value, config_store=config_store or {})
            return value

        # 4. previously user-set value
        if not isinstance(self._user_value, _Unset):
            if isinstance(self._user_value, Parameter):
                return self._convert_parameter(self._user_value, config_store=config_store or {})
            return self._user_value

        # 3. check a config store
        if config_store:
            if self.suffix:
                for env_var in self._env_vars:
                    if env_var + self.suffix in config_store:
                        return config_store[env_var + self.suffix]
            else:
                for env_var in self._env_vars:
                    for config_setting in config_store:
                        if config_setting.startswith(env_var):
                            return config_store[config_setting]
            if self._env_var and self._env_var in config_store:
                return config_store[self._env_var]

        # 2. environment variable
        if self.suffix:
            for env_var in self._env_vars:
                if env_var + self.suffix in os.environ:
                    # All settings with env vars are currently strings, so this should be fine.
                    return os.environ[env_var + self.suffix]  # type: ignore[return-value]
        else:
            # TODO: This will be very slow for a large number of env vars. However it will only
            # happen during the first loading of the AzureApp. Regardless, would be nice to find a better way.
            for env_var in self._env_vars:
                for env_setting in os.environ:
                    if env_setting.startswith(env_var):
                        return os.environ[env_setting]  # type: ignore[return-value]
        if self._env_var and self._env_var in os.environ:
            return os.environ[self._env_var]  # type: ignore[return-value]

        # 1. system setting
        if self._hook:
            try:
                value = self._hook(config_store=config_store)
                if isinstance(value, Parameter):
                    return self._convert_parameter(value, config_store=config_store or {})
                return value
            except RuntimeError:
                pass

        # 0. implicit default
        if not isinstance(self._default, _Unset):
            value = self._default
            if isinstance(value, Parameter):
                return self._convert_parameter(value, config_store=config_store or {})
            return value

        all_vars = "\n".join([e + self.suffix for e in self._env_vars])
        all_vars += "\n" if all_vars else ""
        if self._env_var:
            all_vars += f"{self._env_var}\n"
        message = f"No configured value found for setting {self._name!r}.\nChecked the following settings:\n{all_vars}"
        message += "\nYou may need to run the 'provision' command to populate resource settings."
        raise RuntimeError(message)

    def set_value(self, value: Union[PrioritizedSetting[ValidInputType, ValueType], ValidInputType]) -> None:
        """Specify a value for this setting programmatically.

        A value set this way takes precedence over all other methods except
        immediate values.

        :param value: a user-set value for this setting
        :type value: str or int or float
        """
        if isinstance(value, PrioritizedSetting):
            self._user_value = value._user_value  # pylint: disable=protected-access
        else:
            self._user_value = value
