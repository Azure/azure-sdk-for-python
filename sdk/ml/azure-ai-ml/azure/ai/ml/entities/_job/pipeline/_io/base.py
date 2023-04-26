# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import re
from abc import ABC, abstractmethod
from typing import List, Optional, Union

from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpressionMixin
from azure.ai.ml.entities._util import resolve_pipeline_parameter
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, UserErrorException, ValidationException


def _build_data_binding(data: Union["PipelineInput", "Output"]) -> str:
    """Build input builders to data bindings."""
    if isinstance(data, (InputOutputBase)):
        # Build data binding when data is PipelineInput, Output
        result = data._data_binding()
    else:
        # Otherwise just return the data
        result = data
    return result


def _resolve_builders_2_data_bindings(data: Union[list, dict]) -> Union[list, dict, str]:
    """Traverse data and build input builders inside it to data bindings."""
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                data[key] = _resolve_builders_2_data_bindings(val)
            else:
                data[key] = _build_data_binding(val)
        return data
    if isinstance(data, list):
        resolved_data = []
        for val in data:
            resolved_data.append(_resolve_builders_2_data_bindings(val))
        return resolved_data
    return _build_data_binding(data)


def _data_to_input(data):
    """Convert a Data object to an Input object."""
    if data.id:
        return Input(type=data.type, path=data.id)
    return Input(type=data.type, path=f"{data.name}:{data.version}")


class InputOutputBase(ABC):
    # TODO: refine this code, always use _data to store builder level settings and use _meta to store definition
    # TODO: when _data missing, return value from _meta

    def __init__(self, meta: Union[Input, Output], data, default_data=None, **kwargs):
        """Base class of input & output.

        :param meta: Metadata of this input/output, eg: type, min, max, etc.
        :type meta: Union[Input, Output]
        :param data: Actual value of input/output, None means un-configured data.
        :type data: Union[None, int, bool, float, str
                          azure.ai.ml.Input,
                          azure.ai.ml.Output]
        :param default_data: default value of input/output, None means un-configured data.
        :type default_data: Union[None, int, bool, float, str
                          azure.ai.ml.Input,
                          azure.ai.ml.Output]
        """
        self._meta = meta
        self._original_data = data
        self._data = self._build_data(data)
        self._default_data = default_data
        self._type = meta.type if meta is not None else kwargs.pop("type", None)
        self._mode = self._get_mode(original_data=data, data=self._data, kwargs=kwargs)
        self._description = (
            self._data.description
            if self._data is not None and hasattr(self._data, "description") and self._data.description
            else kwargs.pop("description", None)
        )
        # TODO: remove this
        self._attribute_map = {}
        super(InputOutputBase, self).__init__(**kwargs)

    @abstractmethod
    def _build_data(self, data, key=None):  # pylint: disable=unused-argument, no-self-use
        """Validate if data matches type and translate it to Input/Output acceptable type."""

    @abstractmethod
    def _build_default_data(self):
        """Build default data when data not configured."""

    @property
    def type(self) -> str:
        """Type of input/output."""
        return self._type

    @type.setter
    def type(self, type):  # pylint: disable=redefined-builtin
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        self._type = type
        if isinstance(self._data, (Input, Output)):
            self._data.type = type
        else:  # when type of self._data is InputOutputBase or its child class
            self._data._type = type

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, mode):
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        self._mode = mode
        if isinstance(self._data, (Input, Output)):
            self._data.mode = mode
        else:
            self._data._mode = mode

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description):
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        self._description = description
        if isinstance(self._data, (Input, Output)):
            self._data.description = description
        else:
            self._data._description = description

    @property
    def path(self) -> str:
        # This property is introduced for static intellisense.
        if hasattr(self._data, "path"):
            return self._data.path
        msg = f"{type(self._data)} does not have path."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.PIPELINE,
            error_category=ErrorCategory.USER_ERROR,
        )

    @path.setter
    def path(self, path):
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        if hasattr(self._data, "path"):
            self._data.path = path
        else:
            msg = f"{type(self._data)} does not support setting path."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _data_binding(self) -> str:
        """Return data binding string representation for this input/output."""
        raise NotImplementedError()

    # Why did we have this function? It prevents the DictMixin from being applied.
    # Unclear if we explicitly do NOT want the mapping protocol to be applied to this, or it this was just
    # confirmation that it didn't at the time.
    def keys(self):
        # This property is introduced to raise catchable Exception in marshmallow mapping validation trial.
        raise TypeError(f"'{type(self).__name__}' object is not a mapping")

    def __str__(self):
        try:
            return self._data_binding()
        except AttributeError:
            return super(InputOutputBase, self).__str__()

    def __hash__(self):
        return id(self)

    @classmethod
    def _get_mode(cls, original_data, data, kwargs):
        """Get mode of this input/output builder.

        :param original_data: Original value of input/output.
        :type original_data: Union[None, int, bool, float, str
                          azure.ai.ml.Input,
                          azure.ai.ml.Output,
                          azure.ai.ml.entities._job.pipeline._io.PipelineInput]
        :param data: Built input/output data.
        :type data: Union[None, int, bool, float, str
                          azure.ai.ml.Input,
                          azure.ai.ml.Output]
        """
        # pipeline level inputs won't pass mode to bound node level inputs
        if isinstance(original_data, PipelineInput):
            return None
        return data.mode if data is not None and hasattr(data, "mode") else kwargs.pop("mode", None)


class NodeInput(InputOutputBase):
    """Define one input of a Component."""

    def __init__(
        self,
        port_name: str,
        meta: Input,
        *,
        data: Optional[Union[int, bool, float, str, Output, "PipelineInput", Input]] = None,
        owner: Optional[Union["BaseComponent", "PipelineJob"]] = None,
        **kwargs,
    ):
        """Initialize an input of a component.

        :param name: The name of the input.
        :type name: str
        :param meta: Metadata of this input, eg: type, min, max, etc.
        :type meta: Input
        :param data: The input data. Valid types include int, bool, float, str,
            Output of another component or pipeline input and Input.
            Note that the output of another component or pipeline input associated should be reachable in the scope
            of current pipeline. Input is introduced to support case like
            TODO: new examples
            component.inputs.xxx = Input(path="arm_id")
        :type data: Union[int, bool, float, str
                          azure.ai.ml.Output,
                          azure.ai.ml.Input]
        :param owner: The owner component of the input, used to calculate binding.
        :type owner: Union[azure.ai.ml.entities.BaseNode, azure.ai.ml.entities.PipelineJob]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        # TODO: validate data matches type in meta
        # TODO: validate supported data
        self._port_name = port_name
        self._owner = owner
        super().__init__(meta=meta, data=data, **kwargs)

    def _build_default_data(self):
        """Build default data when input not configured."""
        if self._data is None:
            self._data = Input()

    def _build_data(self, data, key=None):  # pylint: disable=unused-argument
        """Build input data according to assigned input, eg: node.inputs.key = data"""
        data = resolve_pipeline_parameter(data)
        if data is None:
            return data
        if type(data) is NodeInput:  # pylint: disable=unidiomatic-typecheck
            msg = "Can not bind input to another component's input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        if isinstance(data, (PipelineInput, NodeOutput)):
            # If value is input or output, it's a data binding, we require it have a owner so we can convert it to
            # a data binding, eg: ${{inputs.xxx}}
            if isinstance(data, NodeOutput) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return data
        # for data binding case, set is_singular=False for case like "${{parent.inputs.job_in_folder}}/sample1.csv"
        if isinstance(data, Input) or is_data_binding_expression(data, is_singular=False):
            return data
        if isinstance(data, (Data, Model)):
            return _data_to_input(data)
        # self._meta.type could be None when sub pipeline has no annotation
        if isinstance(self._meta, Input) and self._meta.type and not self._meta._is_primitive_type:
            if isinstance(data, str):
                return Input(type=self._meta.type, path=data)
            msg = "only path input is supported now but get {}: {}."
            raise UserErrorException(
                message=msg.format(type(data), data),
                no_personal_data_message=msg.format(type(data), "[data]"),
            )
        return data

    def _to_job_input(self):
        """convert the input to Input, this logic will change if backend contract changes."""
        if self._data is None:
            # None data means this input is not configured.
            result = None
        elif isinstance(self._data, (PipelineInput, NodeOutput)):
            # Build data binding when data is PipelineInput, Output
            result = Input(path=self._data._data_binding(), mode=self.mode)
        elif is_data_binding_expression(self._data):
            result = Input(path=self._data, mode=self.mode)
        else:
            data_binding = _build_data_binding(self._data)
            if is_data_binding_expression(self._data):
                result = Input(path=data_binding, mode=self.mode)
            else:
                result = data_binding
            # TODO: validate is self._data is supported

        return result

    def _data_binding(self):
        msg = "Input binding {} can only come from a pipeline, currently got {}"
        # call type(self._owner) to avoid circular import
        raise ValidationException(
            message=msg.format(self._port_name, type(self._owner)),
            target=ErrorTarget.PIPELINE,
            no_personal_data_message=msg.format("[port_name]", "[owner]"),
            error_category=ErrorCategory.USER_ERROR,
        )

    def _copy(self, owner):
        return NodeInput(
            port_name=self._port_name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return NodeInput(
            port_name=self._port_name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
        )

    def _get_data_owner(self) -> Optional["BaseNode"]:
        """Return the node if Input is from another node's output. Returns None if for literal value.
        Note: This only works for @pipeline, not for YAML pipeline.

        Note: Inner step will be returned as the owner when node's input is from sub pipeline's output.
            @pipeline
            def sub_pipeline():
                inner_node = component_func()
                return inner_node.outputs

            @pipeline
            def root_pipeline():
                pipeline_node = sub_pipeline()
                node = copy_files_component_func(input_dir=pipeline_node.outputs.output_dir)
                owner = node.inputs.input_dir._get_data_owner()
                assert owner == pipeline_node.nodes[0]
        """
        from azure.ai.ml.entities import Pipeline
        from azure.ai.ml.entities._builders import BaseNode

        def _resolve_data_owner(data) -> Optional["BaseNode"]:
            if isinstance(data, BaseNode) and not isinstance(data, Pipeline):
                return data
            while isinstance(data, PipelineInput):
                # for pipeline input, it's original value(can be literal value or another node's output)
                # is stored in _original_data
                return _resolve_data_owner(data._original_data)
            if isinstance(data, NodeOutput):
                if isinstance(data._owner, Pipeline):
                    # for input from subgraph's output, trace back to inner node
                    return _resolve_data_owner(data._binding_output)
                # for input from another node's output, return the node
                return _resolve_data_owner(data._owner)
            return None

        return _resolve_data_owner(self._data)


class NodeOutput(InputOutputBase, PipelineExpressionMixin):
    """Define one output of a Component."""

    def __init__(
        self,
        port_name: str,
        meta: Output,
        *,
        data: Optional[Union[Output, str]] = None,
        owner: Optional[Union["BaseComponent", "PipelineJob"]] = None,
        binding_output: Optional["NodeOutput"] = None,
        **kwargs,
    ):
        """Initialize an Output of a component.

        :param port_name: The port_name of the output.
        :type port_name: str
        :param name: The name used to register NodeOutput/PipelineOutput data.
        :type name: str
        :param version: The version used to register NodeOutput/PipelineOutput data.
        :ype version: str
        :param data: The output data. Valid types include str, Output
        :type data: Union[str
                          azure.ai.ml.entities.Output]
        :param mode: The mode of the output.
        :type mode: str
        :param owner: The owner component of the output, used to calculate binding.
        :type owner: Union[azure.ai.ml.entities.BaseNode, azure.ai.ml.entities.PipelineJob]
        :param binding_output: The node output bound to pipeline output, only available for pipeline.
        :type binding_output: azure.ai.ml.entities.NodeOutput
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if object cannot be successfully validated.
            Details will be provided in the error message.
        """
        # Allow inline output binding with string, eg: "component_out_path_1": "${{parents.outputs.job_out_data_1}}"
        if data is not None and not isinstance(data, (Output, str)):
            msg = "Got unexpected type for output: {}."
            raise ValidationException(
                message=msg.format(data),
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg.format("[data]"),
            )
        super().__init__(meta=meta, data=data, **kwargs)
        self._port_name = port_name
        self._owner = owner
        self._name = self._data.name if isinstance(self._data, Output) else None
        self._version = self._data.version if isinstance(self._data, Output) else None

        self._assert_name_and_version()

        self._is_control = meta.is_control if meta is not None else None
        # store original node output to be able to trace back to inner node from a pipeline output builder.
        self._binding_output = binding_output

    @property
    def is_control(self) -> str:
        return self._is_control

    @property
    def port_name(self) -> str:
        """The output port name, eg: node.outputs.port_name."""
        return self._port_name

    @property
    def name(self):
        """Used in registering output data."""
        return self._name

    @name.setter
    def name(self, name):
        """Receive input name, assign the name to NodeOutput/PipelineOutput and build data according to the name."""
        self._build_default_data()
        self._name = name
        if isinstance(self._data, (Input, Output)):
            self._data.name = name
        elif isinstance(self._data, InputOutputBase):
            self._data._name = name
        else:
            raise UserErrorException(
                f"We support self._data of Input, Output, InputOutputBase, NodeOutput and NodeInput,"
                f"but got type: {type(self._data)}."
            )

    @property
    def version(self) -> str:
        """Used in registering output data."""
        return self._version

    @version.setter
    def version(self, version):
        """Receive input version, assign the version to NodeOutput/PipelineOutput and build data according to the
        version."""
        self._build_default_data()
        self._version = version
        if isinstance(self._data, (Input, Output)):
            self._data.version = version
        elif isinstance(self._data, InputOutputBase):
            self._data._version = version
        else:
            raise UserErrorException(
                f"We support self._data of Input, Output, InputOutputBase, NodeOutput and NodeInput,"
                f"but got type: {type(self._data)}."
            )

    @property
    def path(self) -> Optional[str]:
        # For node output path,
        if hasattr(self._data, "path"):
            return self._data.path
        return None

    @path.setter
    def path(self, path):
        # For un-configured output, we build a default data entry for them.
        self._build_default_data()
        if hasattr(self._data, "path"):
            self._data.path = path
        else:
            # YAML job will have string output binding and do not support setting path for it.
            msg = f"{type(self._data)} does not support setting path."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _assert_name_and_version(self):
        if self.name and not (re.match("^[A-Za-z0-9_-]*$", self.name) and len(self.name) <= 255):
            raise UserErrorException(
                f"The output name {self.name} can only contain alphanumeric characters, dashes and underscores, "
                f"with a limit of 255 characters."
            )
        if self.version and not self.name:
            raise UserErrorException("Output name is required when output version is specified.")

    def _build_default_data(self):
        """Build default data when output not configured."""
        if self._data is None:
            # _meta will be None when node._component is not a Component object
            # so we just leave the type inference work to backend
            self._data = Output(type=None)

    def _build_data(self, data, key=None):
        """Build output data according to assigned input, eg: node.outputs.key = data"""
        if data is None:
            return data
        if not isinstance(data, (Output, str)):
            msg = f"{self.__class__.__name__} only allow set {Output.__name__} object, {type(data)} is not supported."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return data

    def _to_job_output(self):
        """Convert the output to Output, this logic will change if backend contract changes."""
        if self._data is None:
            # None data means this output is not configured.
            result = None
        elif isinstance(self._data, str):
            result = Output(path=self._data, mode=self.mode, name=self.name, version=self.version)
        elif isinstance(self._data, Output):
            result = self._data
        elif isinstance(self._data, PipelineOutput):
            is_control = self._meta.is_control if self._meta is not None else None
            result = Output(
                path=self._data._data_binding(),
                mode=self.mode,
                is_control=is_control,
                name=self._data.name,
                version=self._data.version,
                description=self.description,
            )
        else:
            msg = "Got unexpected type for output: {}."
            raise ValidationException(
                message=msg.format(self._data),
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg.format("[data]"),
            )
        return result

    def _data_binding(self):
        return f"${{{{parent.jobs.{self._owner.name}.outputs.{self._port_name}}}}}"

    def _copy(self, owner):
        return NodeOutput(
            port_name=self._port_name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return NodeOutput(
            port_name=self._port_name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
            binding_output=self._binding_output,
        )


class PipelineInput(NodeInput, PipelineExpressionMixin):
    """Define one input of a Pipeline."""

    def __init__(self, name: str, meta: Input, group_names: Optional[List[str]] = None, **kwargs):
        """Initialize a PipelineInput.

        :param name: The name of the input.
        :type name: str
        :param meta: Metadata of this input, eg: type, min, max, etc.
        :type meta: Input
        :param group_names: The input parameter's group names.
        :type group_names: List[str]
        """
        super(PipelineInput, self).__init__(port_name=name, meta=meta, **kwargs)
        self._group_names = group_names if group_names else []

    def result(self):
        """Return original value of pipeline input."""
        # example:
        #
        # @pipeline
        # def pipeline_func(param1):
        #   node1 = component_func(param1=param1.result())
        #   # node1's param1 will get actual value of param1 instead of a input binding.
        # use this to break self loop
        original_data_cache = set()
        original_data = self._original_data
        while isinstance(original_data, PipelineInput) and original_data not in original_data_cache:
            original_data_cache.add(original_data)
            original_data = original_data._original_data
        return original_data

    def __str__(self) -> str:
        return self._data_binding()

    def _build_data(self, data, key=None):  # pylint: disable=unused-argument
        """Build data according to input type."""
        if data is None:
            return data
        if type(data) is NodeInput:  # pylint: disable=unidiomatic-typecheck
            msg = "Can not bind input to another component's input."
            raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.PIPELINE)
        if isinstance(data, (PipelineInput, NodeOutput)):
            # If value is input or output, it's a data binding, owner is required to convert it to
            # a data binding, eg: ${{parent.inputs.xxx}}
            if isinstance(data, NodeOutput) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return data
        if isinstance(data, (Data, Model)):
            # If value is Data, we convert it to an corresponding Input
            return _data_to_input(data)
        return data

    def _data_binding(self):
        full_name = "%s.%s" % (".".join(self._group_names), self._port_name) if self._group_names else self._port_name
        return f"${{{{parent.inputs.{full_name}}}}}"

    def _to_input(self) -> Input:
        """Convert pipeline input to component input for pipeline component."""
        if self._data is None:
            # None data means this input is not configured.
            return self._meta
        data_type = self._data.type if isinstance(self._data, Input) else None
        # If type is asset type, return data type without default.
        # Else infer type from data and set it as default.
        if data_type and data_type.lower() in AssetTypes.__dict__.values():
            result = Input(type=data_type, mode=self._data.mode)
        elif type(self._data) in IOConstants.PRIMITIVE_TYPE_2_STR:
            result = Input(
                type=IOConstants.PRIMITIVE_TYPE_2_STR[type(self._data)],
                default=self._data,
            )
        else:
            msg = f"Unsupported Input type {type(self._data)} detected when translate job to component."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return result


class PipelineOutput(NodeOutput):
    """Define one output of a Pipeline."""

    def _to_job_output(self):
        if isinstance(self._data, Output):
            # For pipeline output with type Output, always pass to backend.
            result = self._data
        elif self._data is None and self._meta and self._meta.type:
            # For un-configured pipeline output with meta, we need to return Output with accurate type,
            # so it won't default to uri_folder.
            result = Output(type=self._meta.type, mode=self._meta.mode, description=self._meta.description)
        else:
            result = super(PipelineOutput, self)._to_job_output()
        # Copy meta type to avoid built output's None type default to uri_folder.
        if self.type and not result.type:
            result.type = self.type
        return result

    def _data_binding(self):
        return f"${{{{parent.outputs.{self._port_name}}}}}"

    def _to_output(self) -> Output:
        """Convert pipeline output to component output for pipeline component."""
        if self._data is None:
            # None data means this input is not configured.
            return None
        if isinstance(self._meta, Output):
            return self._meta
        # Assign type directly as we didn't have primitive output type for now.
        return Output(type=self._data.type, mode=self._data.mode)
