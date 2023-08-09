from pathlib import Path

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline

upstream_component = load_component(Path(__file__).parent / "upstream_node.yml")
downstream_component = load_component(Path(__file__).parent / "downstream_node.yml")
inner_component = load_component(Path(__file__).parent / "inner_node.yml")


@pipeline
def pipeline_component_func():
    node = inner_component()
    return {"__hash__": node.outputs["__contains__"]}


@pipeline
def pipeline_func():
    upstream_node = upstream_component()
    downstream_node = downstream_component(keys=upstream_node.outputs["items"])  # noqa: F841
    pipeline_component_func()


pipeline_job = pipeline_func()
pipeline_job.settings.default_compute = "cpu-cluster"
