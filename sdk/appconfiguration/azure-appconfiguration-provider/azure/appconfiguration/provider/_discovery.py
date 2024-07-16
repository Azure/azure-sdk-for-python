# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import os
import time
import dns.resolver
from dns.resolver import NXDOMAIN, YXDOMAIN, LifetimeTimeout, NoNameservers  # cspell:disable-line
from dns.rdatatype import SRV  # cspell:disable-line
from urllib.parse import urlparse
from ._constants import DISABLE_APPCONFIGURATION_DISCOVERY, HTTPS_PREFIX

request_retry_period = 5  # seconds


class SRVRecord:
    priority: int
    weight: int
    port: int
    target: str

    def __init__(self, answer):
        self.priority = answer.priority
        self.weight = answer.weight
        self.port = answer.port
        self.target = str(answer.target).rstrip(".")


def find_auto_failover_endpoints(endpoint: str):
    if os.environ.get(DISABLE_APPCONFIGURATION_DISCOVERY, "").lower() == "true":
        return []
    known_domain = _get_known_domains(endpoint)
    if known_domain is None:
        return []

    origin = _find_origin(endpoint)
    if origin is None or not _validate(known_domain, origin.target):
        return []

    srv_records = [origin] + _find_replicas(origin.target)
    endpoints = []
    if endpoint.startswith(HTTPS_PREFIX):
        endpoint = endpoint[len(HTTPS_PREFIX) :]
    for srv_record in srv_records:
        if _validate(known_domain, srv_record.target) and srv_record.target != endpoint:
            endpoints.append(HTTPS_PREFIX + srv_record.target)
    return endpoints


def _find_origin(endpoint):
    uri = urlparse(endpoint).hostname
    request = f"_origin._tcp.{uri}"
    srv_records = _request_record(request)
    if not srv_records:
        return None
    return SRVRecord(srv_records[0])


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
    while time.time() - now < request_retry_period:
        try:
            return dns.resolver.resolve(request, SRV)
        except (NXDOMAIN, YXDOMAIN):  # cspell:disable-line
            break
        except (LifetimeTimeout, NoNameservers):
            continue
    return None


def _validate(known_domain, endpoint):
    if not isinstance(known_domain, str) or known_domain == "":
        return False
    if not isinstance(endpoint, str) or endpoint == "":
        return False
    return endpoint.endswith(known_domain)


def _get_known_domains(known_host):
    trusted_domain_labels = ["appconfig", "azconfig"]  # cspell:disable-line

    for label in trusted_domain_labels:
        index = known_host.lower().rfind(f".{label}.")
        if index > 0:
            return known_host[index:]
    return None
