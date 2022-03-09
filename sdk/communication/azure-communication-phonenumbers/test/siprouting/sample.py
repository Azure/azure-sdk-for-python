from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunk, SipTrunkRoute
from config import CONNECTION_STRING

# Create SIP routing client from connection string
sip_routing_client = SipRoutingClient.from_connection_string(CONNECTION_STRING)

TRUNKS = [SipTrunk(fqdn="sbs1.sipconfigsample.com", sip_signaling_port=1000),
          SipTrunk(fqdn="sbs2.sipconfigsample.com", sip_signaling_port=2000)]
ROUTES = [SipTrunkRoute(name="FirstRule", description="Handle numbers starting with '+123'", number_pattern="\+123[0-9]+", trunks=["sbs1.sipconfigsample.com"])]

# Replace whole collection
sip_routing_client.replace_routes([])
sip_routing_client.replace_trunks(TRUNKS)
sip_routing_client.replace_routes(ROUTES)

# Retrieve one item
route = sip_routing_client.get_route("FirstRule")
trunk = sip_routing_client.get_trunk("sbs2.sipconfigsample.com")

# Set one item 
updated_route = SipTrunkRoute(name="FirstRule", description="Handle numbers starting with '+123'", number_pattern="\+999[0-9]+", trunks=["sbs1.sipconfigsample.com"])
route = sip_routing_client.set_route(updated_route)
route = sip_routing_client.get_route("FirstRule")

sip_routing_client.set_trunk(SipTrunk(fqdn="sbs3.sipconfigsample.com", sip_signaling_port=3000))
route = sip_routing_client.get_trunk("sbs3.sipconfigsample.com")

# Delete one item
sip_routing_client.delete_route("FirstRule")
sip_routing_client.delete_trunk("sbs3.sipconfigsample.com")

# Retrieve whole collection
routes = sip_routing_client.get_routes()
trunks = sip_routing_client.get_trunks()

routes = sip_routing_client.get_routes()
print("routes")
for route in routes:
    print(route.name)
    print(route.number_pattern)

trunks = sip_routing_client.get_trunks()
print("trunks")
for trunk in trunks:
    print(trunk.fqdn)
    print(trunk.sip_signaling_port)