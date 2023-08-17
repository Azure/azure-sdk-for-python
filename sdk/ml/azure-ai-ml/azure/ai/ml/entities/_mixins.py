# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from typing import Any, Dict

from azure.ai.ml._utils.utils import dump_yaml


class RestTranslatableMixin:
    def _to_rest_object(self) -> Any:
        pass

    @classmethod
    def _from_rest_object(cls, obj: Any) -> Any:
        pass


class DictMixin(object):
    def __contains__(self, item):
        return self.__dict__.__contains__(item)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __setitem__(self, key, item):
        # type: (Any, Any) -> None
        self.__dict__[key] = item

    def __getitem__(self, key):
        # type: (Any) -> Any
        return self.__dict__[key]

    def __repr__(self):
        # type: () -> str
        return str(self)

    def __len__(self):
        # type: () -> int
        return len(self.keys())

    def __delitem__(self, key):
        # type: (Any) -> None
        self.__dict__[key] = None

    def __eq__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes.

        :param other: The other object
        :type other: Any
        :return: True if both object are the same class and have matching __dict__, False otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes.

        :param other: The other object
        :type other: Any
        :return: not self.__eq__(other)
        :rtype: bool
        """
        return not self.__eq__(other)

    def __str__(self):
        # type: () -> str
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_") and v is not None})

    def has_key(self, k):
        # type: (Any) -> bool
        return k in self.__dict__

    def update(self, *args, **kwargs):
        # type: (Any, Any) -> None
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        # type: () -> list
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        # type: () -> list
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        # type: () -> list
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        # type: (Any, Optional[Any]) -> Any
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class TelemetryMixin:
    # pylint: disable-next=docstring-missing-param
    def _get_telemetry_values(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Return the telemetry values of object.

        :return: The telemetry values
        :rtype: Dict
        """
        return {}


class YamlTranslatableMixin:
    @abstractmethod
    def _to_dict(self) -> Dict:
        """Dump the object into a dictionary."""

    def _to_ordered_dict_for_yaml_dump(self) -> Dict:
        """Dump the object into a dictionary with a specific key order.

        :return: The ordered dict
        :rtype: Dict
        """
        order_keys = [
            "$schema",
            "name",
            "version",
            "display_name",
            "description",
            "tags",
            "type",
            "inputs",
            "outputs",
            "command",
            "environment",
            "code",
            "resources",
            "limits",
            "schedule",
            "jobs",
        ]
        nested_keys = ["component", "trial"]

        def _sort_dict_according_to_list(order_keys, dict_value):
            for nested_key in nested_keys:
                if nested_key in dict_value and isinstance(dict_value[nested_key], dict):
                    dict_value[nested_key] = _sort_dict_according_to_list(order_keys, dict_value[nested_key])
            if "jobs" in dict_value:
                for node_name, node in dict_value["jobs"].items():
                    dict_value["jobs"][node_name] = _sort_dict_according_to_list(order_keys, node)
            difference = list(set(dict_value.keys()).difference(set(order_keys)))
            # keys not in order_keys will be put at the end of the list in the order of alphabetic
            order_keys.extend(sorted(difference))
            return dict(
                sorted(
                    dict_value.items(),
                    key=lambda dict_value_: order_keys.index(dict_value_[0]),
                )
            )

        return _sort_dict_according_to_list(order_keys, self._to_dict())

    def _to_yaml(self) -> str:
        """Dump the object content into a sorted yaml string.

        :return: YAML formatted string
        :rtype: str
        """
        return dump_yaml(self._to_ordered_dict_for_yaml_dump(), sort_keys=False)


class LocalizableMixin:
    def _localize(self, base_path: str):
        """Called on an asset got from service to clean up remote attributes like id, creation_context, etc.

        :param base_path: The base path
        :type base_path: str
        """
