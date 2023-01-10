from pathlib import Path

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._group_decorator import group

command_component_func = load_component(Path(__file__).parent / "command_component.yml")
pipeline_component_func = load_component(Path(__file__).parent / "pipeline_component.yml")


@group
class ParameterGroup:
    int_param: int
    str_param: str


@pipeline
def pipeline_func(pg: ParameterGroup):
    # init job consume items from group
    init_job = command_component_func(  # noqa: F841
        component_in_number=pg.int_param,
        component_in_string=pg.str_param,
    )
    # finalize job consume parameter group
    finalize_job = pipeline_component_func(pg=pg)  # noqa: F841
    # execution jobs
    take = command_component_func(  # noqa: F841
        component_in_number=pg.int_param,
        component_in_string=pg.str_param,
    )


pipeline_job = pipeline_func(pg=ParameterGroup(int_param=1, str_param="a"))
pipeline_job.settings.default_compute = "cpu-cluster"
pipeline_job.settings.on_init = "init_job"
pipeline_job.settings.on_finalize = "finalize_job"
