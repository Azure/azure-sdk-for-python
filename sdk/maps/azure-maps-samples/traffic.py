# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.
import argparse

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy
import os

from azure.maps.traffic.models import TextFormat, TrafficFlowSegmentStyle, TileFormat, TrafficIncidentDetailStyle
from azure.maps.traffic import TrafficClient

def write_stream_to_file(stream, filename: str):
    with open(filename, "wb") as file:
        bytes = bytearray()
        for line in stream:
            bytes.extend(line)
        file.write(bytes)
    # open file
    os.system('start {}'.format(filename))

parser = argparse.ArgumentParser(
    description='Traffic Samples Program. Set SUBSCRIPTION_KEY env variable.')
parser.parse_args()

client = TrafficClient('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(
    AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key"))


result = client.traffic.get_traffic_flow_segment(
    TextFormat.JSON, TrafficFlowSegmentStyle.ABSOLUTE, 10, "52.41072,4.84239")
print("Get Traffic Flow Segment")
print(result)


result = client.traffic.get_traffic_flow_tile(
    TileFormat.PNG, TrafficFlowSegmentStyle.ABSOLUTE, 12, 2044, 1360)
print("Get Traffic Flow Tile")
write_stream_to_file(result, "tmp/traffic_flow_tile.png")


result = client.traffic.get_traffic_incident_detail(
    TextFormat.JSON, TrafficIncidentDetailStyle.S3, "6841263.950712,511972.674418,6886056.049288,582676.925582", 11, "1335294634919")
print("Get Traffic Incident Detail")
print(result)


result = client.traffic.get_traffic_incident_tile(
    TileFormat.PNG, TrafficIncidentDetailStyle.NIGHT, 10, 175, 408)
print("Get Traffic Incident Tile")
write_stream_to_file(result, "tmp/traffic_incident_tile.png")


result = client.traffic.get_traffic_incident_viewport(TextFormat.JSON, "-939584.4813015489,-23954526.723651607,14675583.153020501,25043442.895825107",
                                                2, "-939584.4813018347,-23954526.723651607,14675583.153020501,25043442.8958229083", 2)
print("Get Traffic Incident Viewport")
print(result)