import pytest

from azure.ai.ml.entities import *


ERROR_MSG = "Can't instantiate abstract class"


@pytest.mark.unittest
def test_smoke():
    from azure.ai.ml.entities import (
        Model,
        Environment,
        CommandComponent,
        ParallelComponent,
        CommandJob,
        PipelineJob,
        BatchDeployment,
        BatchEndpoint,
        OnlineDeployment,
        OnlineEndpoint,
        Component,
        Asset,
        Resource,
    )
    from azure.ai.ml.sweep import SweepJob
    from azure.ai.ml.entities._assets import Code, Data
    from azure.ai.ml.entities._builders import Command, Parallel

    Environment()
    Model()
    Code()
    CommandComponent()
    ParallelComponent()
    Data()
    Command(component="fake_component")
    Parallel(component="fake_component")
    CommandJob()
    SweepJob()
    PipelineJob()
    BatchEndpoint()
    BatchDeployment(name="bla")

    with pytest.raises(TypeError) as e:
        OnlineDeployment()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        OnlineEndpoint()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        Component()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        Asset()
        assert ERROR_MSG in e.msg
    with pytest.raises(TypeError) as e:
        Resource()
        assert ERROR_MSG in e.msg


# nopycln: file
