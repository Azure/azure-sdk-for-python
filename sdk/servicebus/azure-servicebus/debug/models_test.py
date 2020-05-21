from xml.etree import ElementTree
from lxml import etree
from azure.servicebus._control_client2._generated.models._models_py3 import *

# queue_description = QueueDescription()
# content = CreateQueueBodyContent(queue_description=queue_description)
# create_body = CreateQueueBody(content=content)
# s = ElementTree.tostring(create_body.serialize(is_xml=True, short_empty_elements=False))
# print(s)
# restored_object = CreateQueueBody.deserialize(data=s.decode(), content_type="application/xml")
# print(restored_object)
#
# xml = '<entry xmlns="http://www.w3.org/2005/Atom"><id>https://yijunsb.servicebus.windows.net/queue1/</id><title type="text">queue1</title><published>2020-05-16T07:47:47Z</published><updated>2020-05-16T07:47:47Z</updated><author><name>yijunsb</name></author><link rel="self" href="https://yijunsb.servicebus.windows.net/queue1/"/><content type="application/xml"><QueueDescription xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"><LockDuration>PT1M</LockDuration><MaxSizeInMegabytes>1024</MaxSizeInMegabytes><RequiresDuplicateDetection>false</RequiresDuplicateDetection><RequiresSession>false</RequiresSession><DefaultMessageTimeToLive>P10675199DT2H48M5.4775807S</DefaultMessageTimeToLive><DeadLetteringOnMessageExpiration>false</DeadLetteringOnMessageExpiration><DuplicateDetectionHistoryTimeWindow>PT10M</DuplicateDetectionHistoryTimeWindow><MaxDeliveryCount>10</MaxDeliveryCount><EnableBatchedOperations>true</EnableBatchedOperations><SizeInBytes>0</SizeInBytes><MessageCount>0</MessageCount></QueueDescription></content></entry>'
# dr = QueueDescriptionResponse.deserialize(xml, content_type="application/xml")
# print(dr)

dr = QueueDescriptionResponse(
    id="test id",
    published="test published",
    author=QueueDescriptionResponseAuthor(name="testname"),
    link=QueueDescriptionResponseLink(href="test href"),
    content=QueueDescriptionResponseContent()
)
et = dr.serialize(is_xml=True)  # type: ElementTree.Element
et.iter()
# s = ElementTree.tostring(et).decode("utf-8")
# print(s)
# restored_object = QueueDescriptionResponse.deserialize(s, content_type="application/xml")
# print(restored_object)
