import pytest
from azure.ai.ml.entities._job.pipeline._exceptions import UnsupportedOperationError
from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict
from azure.ai.ml.entities import Component as ComponentEntity
from azure.ai.ml.entities._builders import Command
from azure.ai.ml import load_component

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
class TestAttrDict:
    def test_attr_dict(self):
        obj = _AttrDict()
        obj.resource_layout.node_count = 2
        obj.resource_layout.process_count_per_node = 2
        # setting same filed twice will return same object
        assert obj.resource_layout == {"node_count": 2, "process_count_per_node": 2}
        # setting internal attribute will not be arbitrary attribute
        obj._target = "target"

        obj.target = "aml"
        # all set attribute should be recorded
        assert obj._get_attrs() == {"resource_layout": {"node_count": 2, "process_count_per_node": 2}, "target": "aml"}
        # getting non-exist attribute will return an empty dict
        assert obj.sweep == {}

        # only calling existing methods in object is allowed
        with pytest.raises(TypeError):
            obj.resource_layout()

        # only setting resource_layout.node_count and resource_layout.process_count_per_node is allowed
        obj = _AttrDict(allowed_keys={"resource_layout": {"node_count": None, "process_count_per_node": None}})
        obj.resource_layout.node_count = 2
        obj.resource_layout.process_count_per_node = 2
        assert obj.resource_layout == {"node_count": 2, "process_count_per_node": 2}

        # target will not be arbitrary attribute
        obj.target = "aml"
        assert obj._get_attrs() == {"resource_layout": {"node_count": 2, "process_count_per_node": 2}}
        assert "target" in obj.__dict__.keys()
        assert "target" not in obj.items()

        # set/get item is not supported
        # currently we use copy.copy to dump a pipeline/component, which depends on __setitem__
        # disable this check for now
        # with pytest.raises(UnsupportedOperationError) as e:
        #     obj["target"] = "aml"
        # assert "Operation __setitem__ is not supported." in str(e)

        # with pytest.raises(UnsupportedOperationError) as e:
        #     obj.resource_layout = obj["target"]
        # assert "Operation __getitem__ is not supported." in str(e)

    def test_allowed_keys_unsupported_type(self):
        # Only dict and None are supported as allowed_keys
        with pytest.raises(TypeError):
            _AttrDict(allowed_keys=object())

    def test_component_attr_dict(self):
        command_component = load_component(path="./tests/test_configs/components/helloworld_component.yml")
        node = Command(component=command_component)
        node.resource_layout.node_count = 2
        node.resource_layout.process_count_per_node = 2
        assert node.resource_layout == {"node_count": 2, "process_count_per_node": 2}
        # compute is already an attribute, settings it won't change arbitrary dict.
        node.compute = "aml"
        assert not isinstance(node.compute, _AttrDict)
        assert node._get_attrs() == {"resource_layout": {"node_count": 2, "process_count_per_node": 2}}
