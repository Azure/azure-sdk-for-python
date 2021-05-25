import sys
import pkgutil

from azure.communication.siprouting._sip_routing_client import SIPRoutingClient

import os

print(os.getcwd())


def main():
    client = SIPRoutingClient("test_endpoint")
    test = client.get_sip_configuration(False)
    print(test)

if __name__ == "__main__":
    main()