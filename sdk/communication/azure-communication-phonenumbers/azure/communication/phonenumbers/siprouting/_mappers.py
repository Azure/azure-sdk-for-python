# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._generated.models import SipTrunkInternal, SipTrunkRouteInternal, SipDomainInternal
from ._models import SipTrunk, SipTrunkRoute, SipDomain

def sip_trunk_from_generated(fqdn, generated):
    if generated is None:
        return None

    return SipTrunk(
        fqdn=fqdn,
        sip_signaling_port=generated.sip_signaling_port,
        enabled=generated.enabled,
        health=generated.health,
        direct_transfer=generated.direct_transfer,
        privacy_header=generated.privacy_header,
        ip_address_version=generated.ip_address_version,
    )

def sip_trunk_to_generated(constructed):
    return SipTrunkInternal(
        sip_signaling_port=constructed.sip_signaling_port,
        enabled=constructed.enabled,
        direct_transfer=constructed.direct_transfer,
        privacy_header=constructed.privacy_header,
        ip_address_version=constructed.ip_address_version,
    )

def sip_trunk_route_from_generated(generated):
    if generated is None:
        return None

    return SipTrunkRoute(
        description=generated.description,
        name=generated.name,
        number_pattern=generated.number_pattern,
        trunks=generated.trunks,
        caller_id_override=generated.caller_id_override,
    )

def sip_trunk_route_to_generated(constructed):
    return SipTrunkRouteInternal(
        description=constructed.description,
        name=constructed.name,
        number_pattern=constructed.number_pattern,
        trunks=constructed.trunks,
        caller_id_override=constructed.caller_id_override,
    )

def sip_domain_from_generated(fqdn, generated):
    if generated is None:
        return None

    return SipDomain(
        fqdn = fqdn,
        enabled=generated.enabled
    )

def sip_domain_to_generated(constructed):
    return SipDomainInternal(
        enabled=constructed.enabled
    )
