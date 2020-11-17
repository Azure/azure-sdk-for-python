
import json
import os 
from azure.media.lva.edge._generated.models import *
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
from datetime import time

device_id = "lva-sample-device"
module_d = "lvaEdge"
connection_string = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
graph_instance_name = "graphInstance1"
graph_topology_name = "graphTopology1"


def build_graph_topology():
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

    return graph

def build_graph_instance():
    url_param = MediaGraphParameterDefinition(name="rtspUrl", value="rtsp://rtspsim:554/media/camera-300s.mkv")
    graph_instance_properties = MediaGraphInstanceProperties(description="Sample graph description", topology_name=graph_topology_name, parameters=[url_param])

    graph_instance = MediaGraphInstance(name=graph_instance_name, properties=graph_instance_properties)

    return graph_instance

def invoke_method(method):
    direct_method = CloudToDeviceMethod(method_name=method.method_name, payload=method.serialize())
    registry_manager = IoTHubRegistryManager(connection_string)

    return registry_manager.invoke_device_module_method(device_id, module_d, direct_method)

def main():
    graph_topology = build_graph_topology()
    graph_instance = build_graph_instance()

    try:
        set_graph = invoke_method(MediaGraphTopologySetRequest(graph=graph_topology))
        set_graph_result = MediaGraphTopology.deserialize(set_graph)

        list_graph = invoke_method(MediaGraphTopologyListRequest())
        list_graph_result = MediaGraphTopology.deserialize(list_graph)

        get_graph = invoke_method(MediaGraphTopologyGetRequest(name=graph_topology_name))
        get_graph_result = MediaGraphTopology.deserialize(get_graph)

        set_graph_instance = invoke_method(MediaGraphInstanceSetRequest(instance=graph_instance))
        set_graph_instance_result = MediaGraphInstance.deserialize(set_graph_instance)

        activate_graph_instance = invoke_method(MediaGraphInstanceActivateRequest(name=graph_instance_name))
        activate_graph_instance_result = MediaGraphInstance.deserialize(activate_graph_instance)

        get_graph_instance = invoke_method(MediaGraphInstanceGetRequest(name=graph_instance_name))
        get_graph_instance_result = MediaGraphInstance.deserialize(get_graph_instance)

        deactivate_graph_instance = invoke_method(MediaGraphInstanceDeActivateRequest(name=graph_instance_name))
        deactivate_graph_instance_result = MediaGraphInstance.deserialize(deactivate_graph_instance)

        delete_graph_instance = invoke_method(MediaGraphInstanceDeleteRequest(name=graph_instance_name))
        delete_graph_instance_result = MediaGraphInstance.deserialize(delete_graph_instance)

        delete_graph = invoke_method(MediaGraphTopologyDeleteRequest(name=graph_topology_name))
        delete_graph_result = MediaGraphTopology.deserialize(delete_graph)

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()