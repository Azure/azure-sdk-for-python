import pytest
from azure.media.analyticsedge import *

class TestGraphBuildSerialize():
    def test_build_graph_serialize(self):
        graph_topology_name = "graphTopology1"
        graph_properties = MediaGraphTopologyProperties()
        graph_properties.description = "Continuous video recording to an Azure Media Services Asset"
        user_name_param = MediaGraphParameterDeclaration(name="rtspUserName",type="String",default="dummyusername")
        password_param = MediaGraphParameterDeclaration(name="rtspPassword",type="String",default="dummypassword")
        url_param = MediaGraphParameterDeclaration(name="rtspUrl",type="String",default="rtsp://www.sample.com")

        source = MediaGraphRtspSource(name="rtspSource", endpoint=MediaGraphUnsecuredEndpoint(url="${rtspUrl}",credentials=MediaGraphUsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
        node = MediaGraphNodeInput(node_name="rtspSource")
        sink = MediaGraphAssetSink(name="assetsink", inputs=[node],asset_name_pattern='sampleAsset-${System.GraphTopologyName}-${System.GraphInstanceName}', segment_length="PT0H0M30S",local_media_cache_maximum_size_mi_b=2048,local_media_cache_path="/var/lib/azuremediaservices/tmp/")
        graph_properties.parameters = [user_name_param, password_param, url_param]
        graph_properties.sources = [source]
        graph_properties.sinks = [sink]
        graph = MediaGraphTopology(name=graph_topology_name,properties=graph_properties)

        set_graph_method = MediaGraphTopologySetRequest(graph=graph)
        set_graph_method_serialize = set_graph_method.serialize()
        assert set_graph_method_serialize['name'] == graph_topology_name