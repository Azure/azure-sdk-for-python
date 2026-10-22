from pathlib import Path

from azure.ai.ml import Input, load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._do_while import do_while

component_func = load_component(Path(__file__).parent / "component.yml")


@pipeline
def loop_func(**kwargs):
    node = component_func(
        required_input=kwargs["required_input"],
        optional_input=kwargs["optional_input"],
    )
    return {
        "output1": node.outputs.output1,
        "output2": node.outputs.output2,
    }


@pipeline
def pipeline_func(required_input: Input(type="uri_folder")):
    init_inputs = {
        "required_input": required_input,
        "optional_input": None,
    }
    loop_body = loop_func(**init_inputs)
    do_while(
        body=loop_body,
        mapping={
            "output1": loop_body.inputs.required_input,
            "output2": loop_body.inputs.optional_input,
        },
        max_iteration_count=3,
    )


pipeline_job = pipeline_func(required_input=Input(path="./dummy_model", type="uri_folder"))
pipeline_job.settings.default_compute = "cpu-cluster"
