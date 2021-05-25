import pytest
from azure.media.videoanalyzeredge import *

class TestPipelineBuildSerialize():
    def test_build_pipeline_serialize(self):
        pipeline_topology_properties = PipelineTopologyProperties()
        pipeline_topology_name = 'pipelineTopologyTest'
        pipeline_topology_properties.description = "Continuous video recording to an Azure Media Services Asset"
        user_name_param = ParameterDeclaration(name="rtspUserName",type="String",default="testusername")
        password_param = ParameterDeclaration(name="rtspPassword",type="SecretString",default="testpassword")
        url_param = ParameterDeclaration(name="rtspUrl",type="String",default="rtsp://www.sample.com")
        hub_param = ParameterDeclaration(name="hubSinkOutputName",type="String")

        source = RtspSource(name="rtspSource", endpoint=UnsecuredEndpoint(url="${rtspUrl}",credentials=UsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
        node = NodeInput(node_name="rtspSource")
        pipeline_topology_properties.parameters = [user_name_param, password_param, url_param, hub_param]
        pipeline_topology_properties.sources = [source]
        pipeline_topology = PipelineTopology(name=pipeline_topology_name,properties=pipeline_topology_properties)



        set_top_method = PipelineTopologySetRequest(pipeline_topology=pipeline_topology)
        set_top_method_serialize = set_top_method.serialize()
        assert set_top_method_serialize['name'] == pipeline_topology_name