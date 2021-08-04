
import json
import os 
from azure.media.analyticsedge import *
from azure.iot.hub import IoTHubRegistryManager #run pip install azure-iot-hub to get this package
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
from datetime import time

device_id = "device-id"
module_d = "module-id"
connection_string = "connection-string"
graph_instance_name = "graphInstance1"
graph_topology_name = "graphTopology1"
graph_url = "rtsp://sample-url-from-camera"

def build_graph_topology():
    graph_properties = MediaGraphTopologyProperties()
    graph_properties.description = "Continuous video recording to an Azure Media Services Asset"
    user_name_param = MediaGraphParameterDeclaration(name="rtspUserName",type="String",default="dummyusername")
    password_param = MediaGraphParameterDeclaration(name="rtspPassword",type="SecretString",default="dummypassword")
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
    url_param = MediaGraphParameterDefinition(name="rtspUrl", value=graph_url)
    pass_param = MediaGraphParameterDefinition(name="rtspPassword", value='testpass')
    graph_instance_properties = MediaGraphInstanceProperties(description="Sample graph description", topology_name=graph_topology_name, parameters=[url_param])

    graph_instance = MediaGraphInstance(name=graph_instance_name, properties=graph_instance_properties)

    return graph_instance

def invoke_method_helper(method):
    direct_method = CloudToDeviceMethod(method_name=method.method_name, payload=method.serialize())
    registry_manager = IoTHubRegistryManager(connection_string)

    payload = registry_manager.invoke_device_module_method(device_id, module_d, direct_method).payload
    if payload is not None and 'error' in payload:
        print(payload['error'])
        return None

    return payload

def main():
    graph_topology = build_graph_topology()
    graph_instance = build_graph_instance()

    try:
        set_graph_response = invoke_method_helper(MediaGraphTopologySetRequest(graph=graph_topology))
        
        list_graph_response = invoke_method_helper(MediaGraphTopologyListRequest())
        if list_graph_response:
            list_graph_result = MediaGraphTopologyCollection.deserialize(list_graph_response)

        get_graph_response = invoke_method_helper(MediaGraphTopologyGetRequest(name=graph_topology_name))
        if get_graph_response:
            get_graph_result = MediaGraphTopology.deserialize(get_graph_response)

        set_graph_instance_response = invoke_method_helper(MediaGraphInstanceSetRequest(instance=graph_instance))

        activate_graph_instance_response = invoke_method_helper(MediaGraphInstanceActivateRequest(name=graph_instance_name))

        get_graph_instance_response = invoke_method_helper(MediaGraphInstanceGetRequest(name=graph_instance_name))
        if get_graph_instance_response:
            get_graph_instance_result = MediaGraphInstance.deserialize(get_graph_instance_response)

        deactivate_graph_instance_response = invoke_method_helper(MediaGraphInstanceDeActivateRequest(name=graph_instance_name))

        delete_graph_instance_response = invoke_method_helper(MediaGraphInstanceDeleteRequest(name=graph_instance_name))

        delete_graph_response = invoke_method_helper(MediaGraphTopologyDeleteRequest(name=graph_topology_name))

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()