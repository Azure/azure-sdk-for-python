import pytest

from azure.ai.ml.entities import *

ERROR_MSG = "Can't instantiate abstract class"


@pytest.mark.unittest
@pytest.mark.core_sdk_test
def test_smoke():
    from azure.ai.ml.entities import (
        Asset,
        BatchDeployment,
        BatchEndpoint,
        CommandComponent,
        CommandJob,
        Component,
        Environment,
        Model,
        OnlineDeployment,
        OnlineEndpoint,
        ParallelComponent,
        PipelineJob,
        Resource,
        SparkComponent,
        SparkJob,
    )
    from azure.ai.ml.entities._assets import Code, Data
    from azure.ai.ml.entities._builders import Command, Parallel, Spark
    from azure.ai.ml.sweep import SweepJob

    Environment()
    Model()
    Code()
    Component()
    CommandComponent()
    ParallelComponent()
    SparkComponent()
    Data()
    Command(component="fake_component")
    Parallel(component="fake_component")
    Spark(component="fake_component")
    CommandJob()
    SweepJob()
    PipelineJob()
    SparkJob()
    BatchEndpoint()
    BatchDeployment(name="bla")

    with pytest.raises(TypeError) as e:
        OnlineDeployment()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        OnlineEndpoint()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        Asset()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        Resource()
        assert ERROR_MSG in e.msg


# nopycln: file
