
import json
import os 
from azure.media.videoanalyzeredge import *
from azure.iot.hub import IoTHubRegistryManager #run pip install azure-iot-hub to get this package
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult
from datetime import time

device_id = os.getenv("iothub_deviceid");
module_d = os.getenv("iothub_moduleid");
connection_string = os.getenv("iothub_connectionstring");
live_pipeline_name = "pipelineInstance1"
pipeline_topology_name = "pipelineTopology1"
url = "rtsp://camerasimulator:8554"


def build_pipeline_topology():
    pipeline_topology_properties = PipelineTopologyProperties()
    pipeline_topology_properties.description = "Continuous video recording to an Azure Media Services Asset"
    user_name_param = ParameterDeclaration(name="rtspUserName",type="String",default="testusername")
    password_param = ParameterDeclaration(name="rtspPassword",type="SecretString",default="testpassword")
    url_param = ParameterDeclaration(name="rtspUrl",type="String",default="rtsp://www.sample.com")

    source = RtspSource(name="rtspSource", endpoint=UnsecuredEndpoint(url="${rtspUrl}",credentials=UsernamePasswordCredentials(username="${rtspUserName}",password="${rtspPassword}")))
    node = NodeInput(node_name="rtspSource")
    sink = VideoSink(name="videoSink", inputs=[node], video_name="video", local_media_cache_path="/var/lib/videoanalyzer/tmp/", local_media_cache_maximum_size_mi_b="1024");
    pipeline_topology_properties.parameters = [user_name_param, password_param, url_param]
    pipeline_topology_properties.sources = [source]
    pipeline_topology_properties.sinks = [sink]
    pipeline_topology = PipelineTopology(name=pipeline_topology_name,properties=pipeline_topology_properties)

    return pipeline_topology


def build_live_pipeline():
    url_param = ParameterDefinition(name="rtspUrl", value=url)
    pass_param = ParameterDefinition(name="rtspPassword", value="secret_password")
    live_pipeline_properties = LivePipelineProperties(description="Sample description", topology_name=pipeline_topology_name, parameters=[url_param])

    live_pipeline = LivePipeline(name=live_pipeline_name, properties=live_pipeline_properties)

    return live_pipeline


def invoke_method_helper(method):
    direct_method = CloudToDeviceMethod(method_name=method.method_name, payload=method.serialize())
    registry_manager = IoTHubRegistryManager(connection_string=connection_string)

    payload = registry_manager.invoke_device_module_method(device_id=device_id, module_id=module_d, direct_method_request=direct_method).payload
    if payload is not None and 'error' in payload:
        print(payload['error'])
        return None

    return payload


def create_remote_device_adapter(device_name, iot_device_name):
    registry_manager = IoTHubRegistryManager(connection_string=connection_string)
    try:
        iot_device = registry_manager.get_device(device_id=iot_device_name)
    except Exception as ex:
        iot_device = registry_manager.create_device_with_certificate_authority(device_id=iot_device_name, status="enabled")

    remote_device_properties = RemoteDeviceAdapterProperties(target=RemoteDeviceAdapterTarget(host="camerasimulator"), iot_hub_device_connection=IotHubDeviceConnection(device_id=iot_device_name,credentials=SymmetricKeyCredentials(key=iot_device.authentication.symmetric_key)))
    return RemoteDeviceAdapter(name=device_name, properties=remote_device_properties)


def sendPipelineRequests(pipeline_topology, live_pipeline):
    set_pipeline_top_response = invoke_method_helper(PipelineTopologySetRequest(pipeline_topology=pipeline_topology))
    if set_pipeline_top_response:
        set_pipeline_top_result = PipelineTopology.deserialize((set_pipeline_top_response))

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


def sendDeviceRequests(remote_device_adapter):
    remote_device_adapter_set_response = invoke_method_helper(
        RemoteDeviceAdapterSetRequest(remote_device_adapter=remote_device_adapter))
    if remote_device_adapter_set_response:
        remote_device_adapter_set_result = RemoteDeviceAdapter.deserialize(remote_device_adapter_set_response)

    remote_device_adapter_get_response = invoke_method_helper(
        RemoteDeviceAdapterGetRequest(name=remote_device_adapter.name))
    if remote_device_adapter_get_response:
        remote_device_adapter_get_result = RemoteDeviceAdapter.deserialize(remote_device_adapter_get_response)

    remote_device_adapter_list_response = invoke_method_helper(RemoteDeviceAdapterListRequest())
    if remote_device_adapter_list_response:
        remote_device_adapter_list_result = RemoteDeviceAdapterCollection.deserialize(
            remote_device_adapter_list_response)

    remote_device_adapter_delete_response = invoke_method_helper(
        RemoteDeviceAdapterDeleteRequest(name=remote_device_adapter.name))

    onvif_list_response = invoke_method_helper(OnvifDeviceDiscoverRequest())

    onvif_get_response = invoke_method_helper(
        OnvifDeviceGetRequest(endpoint=UnsecuredEndpoint(url="rtsp://camerasimulator:8554")))


def main():
    pipeline_topology = build_pipeline_topology()
    live_pipeline = build_live_pipeline()
    remote_device_adapter = create_remote_device_adapter(device_name="RemoteDeviceAdapter1", iot_device_name="iotdevicesample1")
    try:
        sendPipelineRequests(pipeline_topology=pipeline_topology, live_pipeline=live_pipeline)
        sendDeviceRequests(remote_device_adapter=remote_device_adapter)
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()