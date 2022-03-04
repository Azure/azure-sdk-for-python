CONNECTION_STRING = "endpoint=https://e2e_test.communication.azure.com/;accesskey=qGUv+J0z5Xv8TtjC0qZhy34sodSOMKG5HS7NfsjhqxaB/ZP4UnuS4FspWPo3JowuqAb+75COGi4ErREkB76/UQ=="
CONNECTION_STRING_SAMPLE = "endpoint=https://e2e_test.communication.azure.com/;accesskey=qGUv+J0z5Xv8TtjC0qZhy34sodSOMKG5HS7NfsjhqxaB/ZP4UnuS4FspWPo3JowuqAb+75COGi4ErREkB76/UQ=="

def print_results(trunks, routes):
    print("routes")
    for route in routes:
        print(route.name)
        print(route.number_pattern)
    print("trunks")
    for trunk in trunks:
        print(trunk.fqdn)
        print(trunk.sip_signaling_port)