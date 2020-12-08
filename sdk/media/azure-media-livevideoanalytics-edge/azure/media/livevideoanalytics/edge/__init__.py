__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore
#from azure.media.livevideoanalytics.edge._generated.models import (MediaGraphTopologySetRequestBody,
#MediaGraphTopologySetRequest, MediaGraphInstanceSetRequest, MediaGraphInstanceSetRequestBody)

from ._generated.models import *

__all__ = [
    "MethodRequest",
    "ItemNonSetRequestBase",
    "MediaGraphSink"
    "MediaGraphAssetSink",
    "MediaGraphCertificateSource",
    "MediaGraphProcessor",
    "MediaGraphExtensionProcessorBase",
    "MediaGraphCognitiveServicesVisionExtension",
    "MediaGraphCredentials",
    "MediaGraphEndpoint",
    "MediaGraphFileSink",
    "MediaGraphGrpcExtension",
    "MediaGraphGrpcExtensionDataTransfer",
    "MediaGraphHttpExtension",
    "MediaGraphHttpHeaderCredentials",
    "MediaGraphImage",
    "MediaGraphImageFormat",
    "MediaGraphImageFormatBmp",
    "MediaGraphImageFormatJpeg",
    "MediaGraphImageFormatPng",
    "MediaGraphImageFormatRaw",
    "MediaGraphImageScale",
    "MediaGraphInstance",
    "MediaGraphInstanceActivateRequest",
    "MediaGraphInstanceCollection",
    "MediaGraphInstanceDeActivateRequest",
    "MediaGraphInstanceDeleteRequest",
    "MediaGraphInstanceGetRequest",
    "MediaGraphInstanceListRequest",
    "MediaGraphInstanceProperties",
    "MediaGraphInstanceSetRequest",
    "MediaGraphInstanceSetRequestBody",
    "MediaGraphIoTHubMessageSink",
    "MediaGraphSource",
    "MediaGraphIoTHubMessageSource",
    "MediaGraphMotionDetectionProcessor",
    "MediaGraphNodeInput",
    "MediaGraphOutputSelector",
    "MediaGraphParameterDeclaration",
    "MediaGraphParameterDefinition",
    "MediaGraphPemCertificateList",
    "MediaGraphRtspSource",
    "MediaGraphSamplingOptions",
    "MediaGraphSignalGateProcessor",
    "MediaGraphSystemData",
    "MediaGraphTlsEndpoint",
    "MediaGraphTlsValidationOptions",
    "MediaGraphTopology",
    "MediaGraphTopologyCollection",
    "MediaGraphTopologyDeleteRequest",
    "MediaGraphTopologyGetRequest",
    "MediaGraphTopologyListRequest",
    "MediaGraphTopologyProperties",
    "MediaGraphTopologySetRequest",
    "MediaGraphTopologySetRequestBody",
    "MediaGraphUnsecuredEndpoint",
    "MediaGraphUsernamePasswordCredentials"
]
def _OverrideTopologySetRequestSerialize(self):
    graph_body = MediaGraphTopologySetRequestBody(name=self.graph.name)
    graph_body.system_data = self.graph.system_data
    graph_body.properties = self.graph.properties

    return graph_body.serialize()

MediaGraphTopologySetRequest.serialize = _OverrideTopologySetRequestSerialize

def _OverrideInstanceSetRequestSerialize(self):
    graph_body = MediaGraphInstanceSetRequestBody(name=self.instance.name)
    graph_body.system_data = self.instance.system_data
    graph_body.properties = self.instance.properties

    return graph_body.serialize()

MediaGraphInstanceSetRequest.serialize = _OverrideInstanceSetRequestSerialize
