# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import dns.resolver
from dns.resolver import NXDOMAIN
import time
from dataclasses import dataclass


@dataclass
class SRVRecord:
    priority: int
    weight: int
    port: int
    target: str
    protocol = "https://"

    def __init__(self, answer):
        self.priority = answer.priority
        self.weight = answer.weight
        self.port = answer.port
        self.target = str(answer.target).rstrip(".")


def find_auto_failover_endpoints(endpoint):
    known_domain = _get_known_domains(endpoint)
    if not known_domain:
        return [endpoint]

    origin = _find_origin(endpoint)
    if not origin or not _validate(known_domain, origin.target):
        return [endpoint]

    srv_records = [origin] + _find_replicas(origin.target)
    endpoints = []
    for srv_record in srv_records:
        if _validate(known_domain, srv_record.target):
            endpoints.append(srv_record.target)
    return endpoints


def _find_origin(domain):
    uri = domain[8:]
    request = f"_origin._tcp.{uri}"
    srv_records = _request_record(request)
    if not srv_records:
        return None
    return SRVRecord(_request_record(request)[0])


def _find_replicas(origin):
    replicas = []
    i = 0
    while True:
        request = f"_alt{str(i)}._tcp.{origin}"
        answers = _request_record(request)
        if not answers:
            break
        for answer in answers:
            replicas.append(SRVRecord(answer))
        i += 1
    return replicas


def _request_record(request):
    now = time.time()
    while time.time() - now < 5:
        try:
            return dns.resolver.resolve(request, "SRV")
        except NXDOMAIN:
            break


def _validate(known_domain, endpoint):
    if isinstance(known_domain, str) or known_domain == "":
        return False
    if isinstance(endpoint, str) or endpoint == "":
        return False
    return endpoint.endswith(known_domain)


def _get_known_domains(known_host):
    trusted_domain_labels = ["appconfig", "azconfig"]

    for label in trusted_domain_labels:
        index = known_host.lower().find(label)
        if index > 0:
            return known_host[index:]
