# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import time
from urllib.parse import urlparse
import dns.asyncresolver
from dns.resolver import NXDOMAIN, YXDOMAIN, LifetimeTimeout, NoNameservers  # cspell:disable-line
from dns.rdatatype import SRV  # cspell:disable-line
from .._discovery import SRVRecord, HTTPS_PREFIX, request_retry_period, _get_known_domain, _validate


async def find_auto_failover_endpoints(endpoint: str, replica_discovery_enabled: bool):
    if not replica_discovery_enabled:
        return []
    known_domain = _get_known_domain(endpoint)
    if known_domain is None:
        return []

    origin = await _find_origin(endpoint)
    if origin is None or not _validate(known_domain, origin.target):
        return []

    replicas = await _find_replicas(origin.target)

    if not replicas:
        return None  # Timeout

    srv_records = [origin] + replicas
    endpoints = []
    if endpoint.startswith(HTTPS_PREFIX):
        endpoint = endpoint[len(HTTPS_PREFIX) :]
    for srv_record in srv_records:
        if _validate(known_domain, srv_record.target) and srv_record.target != endpoint:
            endpoints.append(HTTPS_PREFIX + srv_record.target)
    return endpoints


async def _find_origin(endpoint):
    uri = urlparse(endpoint).hostname
    request = f"_origin._tcp.{uri}"
    srv_records = await _request_record(request)
    if not srv_records:
        return None
    return SRVRecord(srv_records[0])


async def _find_replicas(origin):
    replicas = []
    i = 0
    while True:
        request = f"_alt{str(i)}._tcp.{origin}"
        answers = await _request_record(request)
        if answers is None:
            return None  # Timeout
        if len(answers) == 0:
            break
        for answer in answers:
            replicas.append(SRVRecord(answer))
        i += 1
    return replicas


async def _request_record(request):
    start_time = time.time()
    while time.time() - start_time < request_retry_period:
        try:
            return await dns.asyncresolver.resolve(request, SRV)
        except (NXDOMAIN, YXDOMAIN):  # cspell:disable-line
            return []  # No records found
        except (LifetimeTimeout, NoNameservers):
            continue
    return None  # Timeout
