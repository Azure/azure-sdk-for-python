# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    AutoMLJob as RestAutoMLJob,
    InstanceSegmentationPrimaryMetrics,
    ImageInstanceSegmentation as RestImageInstanceSegmentation,
    JobBaseData,
    TaskType,
)
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.image.image_limit_settings import ImageLimitSettings
from azure.ai.ml.entities._job.automl.image.image_object_detection_search_space import (
    ImageObjectDetectionSearchSpace,
)
from azure.ai.ml.entities._job.automl.image.image_sweep_settings import ImageSweepSettings
from azure.ai.ml.entities._job.automl.image.automl_image_object_detection_base import (
    AutoMLImageObjectDetectionBase,
)
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml._utils._experimental import experimental


@experimental
class ImageInstanceSegmentationJob(AutoMLImageObjectDetectionBase):
    """
    Configuration for AutoML Image Instance Segmentation job.
    """

    _DEFAULT_PRIMARY_METRIC = InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION

    def __init__(
        self,
        *,
        primary_metric: Union[str, InstanceSegmentationPrimaryMetrics] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a new AutoML Image Instance Segmentation job.

        :param primary_metric: The primary metric to use for optimization
        :param kwargs: Job-specific arguments
        """
        # Extract any super class init settings
        data = kwargs.pop("data", None)
        limits = kwargs.pop("limits", None)
        sweep = kwargs.pop("sweep", None)
        image_model = kwargs.pop("image_model", None)
        search_space = kwargs.pop("search_space", None)

        super().__init__(
            task_type=TaskType.IMAGE_INSTANCE_SEGMENTATION,
            data=data,
            limits=limits,
            sweep=sweep,
            image_model=image_model,
            search_space=search_space,
            **kwargs,
        )
        self.primary_metric = primary_metric or ImageInstanceSegmentationJob._DEFAULT_PRIMARY_METRIC

    @property
    def primary_metric(self):
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, InstanceSegmentationPrimaryMetrics]):
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return
        self._primary_metric = (
            ImageInstanceSegmentationJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else InstanceSegmentationPrimaryMetrics[camel_to_snake(value).upper()]
        )

    def _to_rest_object(self) -> JobBaseData:
        self._resolve_data_inputs()

        image_instance_segmentation_task = RestImageInstanceSegmentation(
            data_settings=self._data,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            sweep_settings=self._sweep._to_rest_object() if self._sweep else None,
            model_settings=self._image_model,
            search_space=(
                [entry._to_rest_object() for entry in self._search_space if entry is not None]
                if self._search_space is not None
                else None
            ),
            primary_metric=self.primary_metric,
            log_verbosity=self.log_verbosity,
        )

        properties = RestAutoMLJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            compute_id=self.compute,
            properties=self.properties,
            environment_id=self.environment_id,
            environment_variables=self.environment_variables,
            services=self.services,
            outputs=to_rest_data_outputs(self.outputs),
            resources=self.resources,
            task_details=image_instance_segmentation_task,
            identity=self.identity,
        )

        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBaseData) -> "ImageInstanceSegmentationJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestImageInstanceSegmentation = properties.task_details

        job_args_dict = {
            "id": obj.id,
            "name": obj.name,
            "description": properties.description,
            "tags": properties.tags,
            "properties": properties.properties,
            "experiment_name": properties.experiment_name,
            "services": properties.services,
            "status": properties.status,
            "creation_context": obj.system_data,
            "display_name": properties.display_name,
            "compute": properties.compute_id,
            "outputs": from_rest_data_outputs(properties.outputs),
            "resources": properties.resources,
            "identity": properties.identity,
        }

        image_instance_segmentation_job = cls(
            data=task_details.data_settings,
            limits=(
                ImageLimitSettings._from_rest_object(task_details.limit_settings)
                if task_details.limit_settings
                else None
            ),
            sweep=(
                ImageSweepSettings._from_rest_object(task_details.sweep_settings)
                if task_details.sweep_settings
                else None
            ),
            image_model=task_details.model_settings,
            search_space=cls._get_search_space_from_str(task_details.search_space),
            primary_metric=task_details.primary_metric,
            log_verbosity=task_details.log_verbosity,
            **job_args_dict,
        )

        image_instance_segmentation_job._restore_data_inputs()

        return image_instance_segmentation_job

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, inside_pipeline=False, **kwargs
    ) -> "AutoMLJob":
        from azure.ai.ml._schema.automl.image_vertical.image_object_detection import ImageInstanceSegmentationSchema
        from azure.ai.ml._schema.pipeline.automl_node import ImageInstanceSegmentationNodeSchema

        if inside_pipeline:
            return load_from_dict(ImageInstanceSegmentationNodeSchema, data, context, additional_message, **kwargs)
        else:
            return load_from_dict(ImageInstanceSegmentationSchema, data, context, additional_message, **kwargs)

    def _to_dict(self, inside_pipeline=False) -> Dict:
        from azure.ai.ml._schema.automl.image_vertical.image_object_detection import ImageInstanceSegmentationSchema
        from azure.ai.ml._schema.pipeline.automl_node import ImageInstanceSegmentationNodeSchema

        if inside_pipeline:
            schema_dict = ImageInstanceSegmentationNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            schema_dict = ImageInstanceSegmentationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return schema_dict

    def __eq__(self, other) -> bool:
        if not isinstance(other, ImageInstanceSegmentationJob):
            return NotImplemented

        if not super().__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
