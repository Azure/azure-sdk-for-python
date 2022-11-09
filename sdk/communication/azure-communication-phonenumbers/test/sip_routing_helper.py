# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import uuid

def get_randomised_domain():
    return "." + uuid.uuid4().hex + ".com"

def get_trunk_with_actual_domain(trunk_fqdn, actual_trunk_fqdn):
    actual_domain = actual_trunk_fqdn.split(".",1)[1]
    return trunk_fqdn[0:5] + actual_domain

def trunks_are_equal(response_trunks, request_trunks):
    assert len(response_trunks) == len(request_trunks), "Length of trunk list doesn't match."

    for k in range(len(request_trunks)):
        assert _compare_fqdns_domain_agnostic(response_trunks[k].fqdn, request_trunks[k].fqdn), "Trunk FQDNs don't match."
        assert (
            response_trunks[k].sip_signaling_port==request_trunks[k].sip_signaling_port
        ), "SIP signaling ports don't match."

def routes_are_equal(response_routes, request_routes):
    assert len(response_routes) == len(request_routes)

    for k in range(len(request_routes)):
        assert request_routes[k].name == response_routes[k].name, "Names don't match."
        assert request_routes[k].description == response_routes[k].description, "Descriptions don't match."
        assert (
            request_routes[k].number_pattern == response_routes[k].number_pattern
        ), "Number patterns don't match."
        assert len(request_routes[k].trunks) == len(response_routes[k].trunks), "Trunk lists length doesn't match."
        for m in range(len(request_routes[k].trunks)):
            assert _compare_fqdns_domain_agnostic(request_routes[k].trunks[m], response_routes[k].trunks[m]) , "Trunk lists don't match."

def _compare_fqdns_domain_agnostic(trunk1_fqdn, trunk2_fqdn):
    trunk1_fqdn_no_domain = trunk1_fqdn.split(".",)[0]
    trunk2_fqdn_no_domain = trunk2_fqdn.split(".",)[0]
    return trunk1_fqdn_no_domain == trunk2_fqdn_no_domain
