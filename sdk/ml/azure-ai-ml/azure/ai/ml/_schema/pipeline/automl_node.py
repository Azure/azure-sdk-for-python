# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

from marshmallow import fields, post_dump, post_load, pre_dump
from pydash import get

from azure.ai.ml._schema.core.schema import PathAwareSchema
from azure.ai.ml._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
from azure.ai.ml._schema.automl import AutoMLClassificationSchema, AutoMLForecastingSchema, AutoMLRegressionSchema
from azure.ai.ml._schema.automl.image_vertical.image_classification import (
    ImageClassificationMultilabelSchema,
    ImageClassificationSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_object_detection import (
    ImageInstanceSegmentationSchema,
    ImageObjectDetectionSchema,
)
from azure.ai.ml._schema.automl.nlp_vertical.text_classification import TextClassificationSchema
from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import TextClassificationMultilabelSchema
from azure.ai.ml._schema.automl.nlp_vertical.text_ner import TextNerSchema
from azure.ai.ml._schema.core.fields import ComputeField, NestedField, UnionField
from azure.ai.ml._schema.job.input_output_entry import MLTableInputSchema, OutputSchema
from azure.ai.ml._schema.pipeline.pipeline_job_io import OutputBindingStr


class AutoMLNodeMixin(PathAwareSchema):
    """Inherit this mixin to change automl job schemas to automl node schema.

    eg: Compute is required for automl job but not required for automl node in pipeline.
    Note: Inherit this before BaseJobSchema to make sure optional takes affect.
    """

    def __init__(self, **kwargs):
        super(AutoMLNodeMixin, self).__init__(**kwargs)
        # update field objects and add data binding support, won't bind task & type as data binding
        support_data_binding_expression_for_fields(self, attrs_to_skip=["task_type", "type"])

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

    @post_load
    def make(self, data, **kwargs):
        data["task"] = data.pop("task_type")
        return data


class AutoMLClassificationNodeSchema(AutoMLNodeMixin, AutoMLClassificationSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    test_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class AutoMLRegressionNodeSchema(AutoMLNodeMixin, AutoMLRegressionSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    test_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class AutoMLForecastingNodeSchema(AutoMLNodeMixin, AutoMLForecastingSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    test_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class AutoMLTextClassificationNode(AutoMLNodeMixin, TextClassificationSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class AutoMLTextClassificationMultilabelNode(AutoMLNodeMixin, TextClassificationMultilabelSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class AutoMLTextNerNode(AutoMLNodeMixin, TextNerSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class ImageClassificationMulticlassNodeSchema(AutoMLNodeMixin, ImageClassificationSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class ImageClassificationMultilabelNodeSchema(AutoMLNodeMixin, ImageClassificationMultilabelSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class ImageObjectDetectionNodeSchema(AutoMLNodeMixin, ImageObjectDetectionSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


class ImageInstanceSegmentationNodeSchema(AutoMLNodeMixin, ImageInstanceSegmentationSchema):
    training_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])
    validation_data = UnionField([fields.Str(), NestedField(MLTableInputSchema)])


def AutoMLNodeSchema(**kwargs):
    """Get the list of all nested schema for all AutoML nodes."""
    return [
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
