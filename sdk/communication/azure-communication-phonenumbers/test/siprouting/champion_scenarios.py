from azure.communication.phonenumbers.siprouting import SipRoutingClient, SipTrunk, SipTrunkRoute
from config import CONNECTION_STRING_SAMPLE, print_results

### Setup SIP routing client
sip_routing_client = SipRoutingClient.from_connection_string(CONNECTION_STRING_SAMPLE)
sip_routing_client.replace_routes([])
sip_routing_client.replace_trunks([])

# 1. Setup initial configuration
trunks = [SipTrunk(fqdn="sbs1.sipconfigsample.com", sip_signaling_port=1000),
          SipTrunk(fqdn="sbs2.sipconfigsample.com", sip_signaling_port=2000)]
routes = [SipTrunkRoute(name="FirstRoute", description="Handle numbers starting with '+1'", number_pattern="\+1[0-9]+", trunks=["sbs1.sipconfigsample.com"]),
          SipTrunkRoute(name="SecondRoute", description="Handle rest of the numbers", number_pattern="\+[0-9]+", trunks=["sbs2.sipconfigsample.com"])]

sip_routing_client.replace_trunks(trunks)
sip_routing_client.replace_routes(routes)

# 2. Read current configuration
trunks = sip_routing_client.get_trunks()
routes = sip_routing_client.get_routes()

# 3. Onboard new SIP trunk and modify routes accordingly
new_trunk = SipTrunk(fqdn="sbs3.sipconfigsample.com", sip_signaling_port=3000)
sip_routing_client.set_trunk(new_trunk)

updated_route = SipTrunkRoute(name="SecondRoute", description="Handle numbers starting with '+2", number_pattern="\+2[0-9]+", trunks=["sbs2.sipconfigsample.com","sbs3.sipconfigsample.com"])
sip_routing_client.set_route(updated_route)

new_route = SipTrunkRoute(name="ThirdRoute", description="Handle rest of the numbers", number_pattern="\+[0-9]+", trunks=["sbs3.sipconfigsample.com","sbs2.sipconfigsample.com","sbs1.sipconfigsample.com"])
sip_routing_client.set_route(new_route)

### Alternatively: sip_routing_client.replace_routes([FirstRoute,SecondRoute,ThirdRoute])

# 4. Remove SIP trunk
trunk_to_remove_fqdn = "sbs1.sipconfigsample.com"
routes = sip_routing_client.get_routes()

### First remove routes containing the trunk we want to remove
updated_third_route = SipTrunkRoute(name=routes[2].name, description=routes[2].description, number_pattern=routes[2].number_pattern,trunks=["sbs3.sipconfigsample.com","sbs2.sipconfigsample.com"])
new_routes = [routes[1], updated_third_route]
sip_routing_client.replace_routes(new_routes)

### Now the SIP trunk can be removed
sip_routing_client.delete_trunk(trunk_to_remove_fqdn)



###print_results(trunks, routes)
