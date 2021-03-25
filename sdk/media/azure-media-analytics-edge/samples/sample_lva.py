
import json
import os 
from azure.media.analyticsedge import *
from azure.iot.hub import IoTHubRegistryManager #run pip install azure-iot-hub to get this package
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
from datetime import time

device_id = "lva-sample-device"
module_d = "lvaEdge"
connection_string = "connectionString"
live_pipeline_name = "graphInstance1"
pipeline_topology_name = "graphTopology1"
graph_url = "rtsp://sample-url-from-camera"

def build_pipeline_topology():
    pipeline_topology_properties = PipelineTopologyProperties()
    pipeline_topology_properties.description = "Continuous video recording to an Azure Media Services Asset"
    user_name_param = ParameterDeclaration(name="rtspUserName",type="String",default="dummyusername")
    password_param = ParameterDeclaration(name="rtspPassword",type="SecretString",default="dummypassword")
    url_param = ParameterDeclaration(name="rtspUrl",type="String",default="rtsp://www.sample.com")

    source = RtspSource(name="rtspSource", endpoint=UnsecuredEndpoint(url="${rtspUrl}",credentials=UsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
    node = NodeInput(node_name="rtspSource")
    sink = AssetSink(name="assetsink", inputs=[node],asset_container_sas_url='sampleAsset-${System.GraphTopologyName}-${System.GraphInstanceName}', segment_length="PT0H0M30S",local_media_cache_maximum_size_mi_b=2048,local_media_cache_path="/var/lib/azuremediaservices/tmp/")
    pipeline_topology_properties.parameters = [user_name_param, password_param, url_param]
    pipeline_topology_properties.sources = [source]
    pipeline_topology_properties.sinks = [sink]
    pipeline_topology = PipelineTopology(name=pipeline_topology_name,properties=pipeline_topology_properties)

    return pipeline_topology

def build_graph_instance():
    url_param = ParameterDefinition(name="rtspUrl", value=graph_url)
    pass_param = ParameterDefinition(name="rtspPassword", value='testpass')
    graph_instance_properties = LivePipelineProperties(description="Sample graph description", topology_name=pipeline_topology_name, parameters=[url_param])

    graph_instance = LivePipeline(name=live_pipeline_name, properties=graph_instance_properties)

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
    pipeline_topology = build_pipeline_topology()
    live_pipeline = build_graph_instance()

    try:
        set_pipeline_top_response = invoke_method_helper(PipelineTopologySetRequest(pipeline_topology=pipeline_topology))
        
        list_pipeline_top_response = invoke_method_helper(PipelineTopologyListRequest())
        if list_pipeline_top_response:
            list_pipeline_top_result = PipelineTopologyCollection.deserialize(list_pipeline_top_response)

        get_pipeline_top_response = invoke_method_helper(PipelineTopologyGetRequest(name=pipeline_topology_name))
        if get_pipeline_top_response:
            get_pipeline_top_result = PipelineTopology.deserialize(get_pipeline_top_response)

        set_live_pipeline_response = invoke_method_helper(LivePipelineSetRequest(live_pipeline=live_pipeline))

        activate_pipeline_response = invoke_method_helper(LivePipelineActivateRequest(name=live_pipeline_name))

        get_pipeline_response = invoke_method_helper(LivePipelineGetRequest(name=live_pipeline_name))
        if get_pipeline_response:
            get_pipeline_result = LivePipeline.deserialize(get_pipeline_response)

        deactivate_pipeline_response = invoke_method_helper(LivePipelineDeactivateRequest(name=live_pipeline_name))

        delete_pipeline_response = invoke_method_helper(LivePipelineDeleteRequest(name=live_pipeline_name))

        delete_pipeline_response = invoke_method_helper(PipelineTopologyDeleteRequest(name=pipeline_topology_name))

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()