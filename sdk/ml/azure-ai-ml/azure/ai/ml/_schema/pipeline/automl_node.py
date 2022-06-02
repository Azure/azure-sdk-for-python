# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, Schema, pre_dump, post_dump, INCLUDE
from pydash import get

from azure.ai.ml._schema._utils.data_binding import support_data_binding_for_fields
from azure.ai.ml._schema.automl import AutoMLClassificationSchema, AutoMLRegressionSchema, AutoMLForecastingSchema
from azure.ai.ml._schema.automl.image_vertical.image_object_detection import (
    ImageObjectDetectionSchema,
    ImageInstanceSegmentationSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_classification import (
    ImageClassificationSchema,
    ImageClassificationMultilabelSchema,
)
from azure.ai.ml._schema.automl.nlp_vertical.text_classification import TextClassificationSchema
from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import TextClassificationMultilableSchema
from azure.ai.ml._schema.automl.nlp_vertical.text_ner import TextNerSchema
from azure.ai.ml._schema.core.fields import ComputeField, UnionField, NestedField, StringTransformedEnum, ArmStr
from azure.ai.ml._schema.job.input_output_entry import OutputSchema
from azure.ai.ml._schema.job.input_output_fields_provider import InputsField
from azure.ai.ml._schema.pipeline.pipeline_job_io import OutputBindingStr


class AutoMLNodeMixin:
    """Inherit this mixin to change automl job schemas to automl node schema.

    eg: Compute is required for automl job but not required for automl node in pipeline.
    Note: Inherit this before BaseJobSchema to make sure optional takes affect."""

    compute = ComputeField(required=False)
    outputs = fields.Dict(
        keys=fields.Str(),
        values=UnionField([NestedField(OutputSchema), OutputBindingStr], allow_none=True),
    )

    @pre_dump
    def resolve_outputs(self, job: "AutoMLJob", **kwargs):
        # Try resolve object's inputs & outputs and return a resolved new object
        import copy

        result = copy.copy(job)
        result._outputs = job._build_outputs()
        return result

    @post_dump(pass_original=True)
    def resolve_nested_data(self, job_dict: dict, job: "AutoMLJob", **kwargs):
        """Resolve nested data into flatten format."""
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        if not isinstance(job, AutoMLJob):
            return job_dict
        # change output to rest output dicts
        job_dict["outputs"] = job._to_rest_outputs()
        # change input to flatten format
        # TODO(1780201): remove this when referring to June API
        job._resolve_data_inputs()
        job_dict.update(job._data.as_dict())
        # flatten data to one liner
        # TODO(1780196): change to support inline data
        if get(job, "_data.training_data.data", None):
            job_dict["training_data"] = str(job._data.training_data.data)
        else:
            job_dict.pop("training_data", None)
        if get(job, "_data.validation_data.data", None):
            job_dict["validation_data"] = str(job._data.validation_data.data)
        else:
            job_dict.pop("validation_data", None)
        if get(job, "_data.test_data.data", None):
            job_dict["test_data"] = str(job._data.test_data.data)
        else:
            job_dict.pop("test_data", None)

        if get(job, "_data.validation_data.validation_data_size", None):
            job_dict["validation_data_size"] = job._data.validation_data.validation_data_size
        if get(job, "_data.validation_data.n_cross_validations", None):
            job_dict["n_cross_validations"] = job._data.validation_data.n_cross_validations
        # TODO: parse other potential fields
        return job_dict


class AutoMLClassificationNodeSchema(AutoMLNodeMixin, AutoMLClassificationSchema):
    def __init__(self, **kwargs):
        super(AutoMLClassificationNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support, won't bind task as data binding
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])
    test_data = UnionField([fields.Str(), InputsField()])


class AutoMLRegressionNodeSchema(AutoMLNodeMixin, AutoMLRegressionSchema):
    def __init__(self, **kwargs):
        super(AutoMLRegressionNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])
    test_data = UnionField([fields.Str(), InputsField()])


class AutoMLForecastingNodeSchema(AutoMLNodeMixin, AutoMLForecastingSchema):
    def __init__(self, **kwargs):
        super(AutoMLForecastingNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])
    test_data = UnionField([fields.Str(), InputsField()])


class AutoMLTextClassificationNode(AutoMLNodeMixin, TextClassificationSchema):
    def __init__(self, **kwargs):
        super(TextClassificationSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class AutoMLTextClassificationMultilabelNode(AutoMLNodeMixin, TextClassificationMultilableSchema):
    def __init__(self, **kwargs):
        super(TextClassificationMultilableSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class AutoMLTextNerNode(AutoMLNodeMixin, TextNerSchema):
    def __init__(self, **kwargs):
        super(TextNerSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class ImageClassificationMulticlassNodeSchema(AutoMLNodeMixin, ImageClassificationSchema):
    def __init__(self, **kwargs):
        super(ImageClassificationMulticlassNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class ImageClassificationMultilabelNodeSchema(AutoMLNodeMixin, ImageClassificationMultilabelSchema):
    def __init__(self, **kwargs):
        super(ImageClassificationMultilabelNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class ImageObjectDetectionNodeSchema(AutoMLNodeMixin, ImageObjectDetectionSchema):
    def __init__(self, **kwargs):
        super(ImageObjectDetectionNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


class ImageInstanceSegmentationNodeSchema(AutoMLNodeMixin, ImageInstanceSegmentationSchema):
    def __init__(self, **kwargs):
        super(ImageInstanceSegmentationNodeSchema, self).__init__(**kwargs)
        # update field objects and add data binding support
        support_data_binding_for_fields(self, attrs_to_skip=["task_type"])

    training_data = UnionField([fields.Str(), InputsField()])
    validation_data = UnionField([fields.Str(), InputsField()])


def AutoMLNodeSchema(**kwargs):
    return UnionField(
        [
            # region: automl node schemas
            NestedField(AutoMLClassificationNodeSchema, **kwargs),
            NestedField(AutoMLRegressionNodeSchema, **kwargs),
            NestedField(AutoMLForecastingNodeSchema, **kwargs),
            # Vision
            NestedField(ImageClassificationMulticlassNodeSchema, **kwargs),
            NestedField(ImageClassificationMultilabelNodeSchema, **kwargs),
            NestedField(ImageObjectDetectionNodeSchema, **kwargs),
            NestedField(ImageInstanceSegmentationNodeSchema, **kwargs),
            # NLP
            NestedField(AutoMLTextClassificationNode, **kwargs),
            NestedField(AutoMLTextClassificationMultilabelNode, **kwargs),
            NestedField(AutoMLTextNerNode, **kwargs),
            # endregion
        ]
    )
