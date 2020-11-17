__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore
from azure.media.lva.edge._generated.models import MediaGraphTopologySetRequestBody, MediaGraphTopologySetRequest, MediaGraphInstanceSetRequest, MediaGraphInstanceSetRequestBody

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