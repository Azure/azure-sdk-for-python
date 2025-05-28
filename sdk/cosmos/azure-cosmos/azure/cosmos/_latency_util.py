# The MIT License (MIT)
# Copyright (c) 2025 Microsoft Corporation

"""
Light-weight synchronous latency probes to Azure Cosmos DB regional
end-points. Called from both sync and async clients; async callers
execute it in a worker thread to avoid blocking the event-loop.
"""

import asyncio
import socket
import time
from azure.core.tracing.decorator import distributed_trace
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from ._constants import _Constants
from ._cosmos_regions import CosmosRegion


@distributed_trace
def _tcp_ping(host: str, port: int, timeout: float = _Constants.LATENCY_PROBE_TIMEOUT_SEC) -> float | None:
    """
    Return round-trip (RTT) time in ms or None on any network error / timeout.
    
    :param str host: Azure Cosmos DB regional endpoint, e.g. "myaccount-eastus.documents.azure.com"
    :param int port: TCP port to connect to.
    :param float timeout: Socket timeout (seconds)
    :returns: Round-trip time to regional endpoint in ms or None
    :rtype: float | None
    """
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            pass
        return (time.perf_counter() - start) * 1000.0 # convert time to ms
    except Exception:
        return None

@distributed_trace
def _rank_regions_by_latency(
    region_endpoint_map: dict[CosmosRegion, str],
    probe_count: int = _Constants.LATENCY_PROBE_COUNT,
    per_probe_timeout: float = _Constants.LATENCY_PROBE_TIMEOUT_SEC,
    total_timeout: float = _Constants.LATENCY_PROBE_TOTAL_TIMEOUT_SEC,
    max_workers: int = _Constants.LATENCY_PROBE_MAX_WORKERS
) -> list[CosmosRegion]:
    """
    Return regions ordered by round-trip time (RTT) to the regional endpoint.
    Regions with no RTT are appended to the end of the list.

    :param dict[CosmosRegion, str] region_endpoint_map: Mapping of regions to their respective endpoints.
    :param int probe_count: Number of probes to take per region.
    :param float per_probe_timeout: Timeout for each probe in seconds.
    :param float total_timeout: Total timeout for all probes in seconds.
    :param int max_workers: Maximum number of concurrent workers.
    :returns: List of regions ordered by round-trip time (RTT).
    :rtype: list[CosmosRegion]
    """
    total_time = (time.perf_counter() + total_timeout)

    # Parse Azure Cosmos DB regional endpoints and extract host and port.
    region_host_map: dict[CosmosRegion, tuple[str, int]] = {}
    for region, endpoint in region_endpoint_map.items():
        parsed = urlparse(endpoint)
        if not parsed.hostname or not parsed.port:
            raise ValueError(f"Invalid endpoint URL: {endpoint}")
        host = parsed.hostname
        port = parsed.port
        region_host_map[region] = (host, port)

    def _one_probe(region: CosmosRegion, host: str, port: int) -> tuple[CosmosRegion, float | None]:
        # Respect global timeout for all probes and exit early if exceeded.
        time_now = time.perf_counter()
        remaining_time = total_time - time_now
        if remaining_time < 0:
            return region, None
        else:
            return region, _tcp_ping(host, port, timeout=min(per_probe_timeout, remaining_time))

    region_latencies: dict[CosmosRegion, list[float | None]] = {r: [] for r in region_host_map}

    # Use ThreadPoolExecutor to parallelize the probes
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = [
            pool.submit(_one_probe, region, host, port)
            for _ in range(probe_count)
            for region, (host, port) in region_host_map.items()
        ]
        for fut in as_completed(futs):
            region, rtt = fut.result()
            region_latencies[region].append(rtt)

    # Sort regions in ascending order by RTT. None is replaced with float("inf") 
    # for sorting, effectively pushing unreachable regions to the end.
    regions_by_latency: list[CosmosRegion] = sorted(
        region_latencies, 
        key=lambda r: min((v for v in region_latencies[r] if v is not None), 
                          default=float("inf")))

    return regions_by_latency

@distributed_trace
async def _rank_regions_by_latency_async(*args, **kwargs) -> list[CosmosRegion]:
    """
    Async wrapper for :pyfunc:`_rank_regions_by_latency`. It forwards ``**args`` and ``**kwargs`` 
    unchanged to the sync version.

    :param tuple args: Same positional parameters as :pyfunc:`_rank_regions_by_latency`.
    :param dict[str, Any] kwargs: Same keyword parameters as :pyfunc:`_rank_regions_by_latency`.
    :returns: List of regions ordered by round-trip time (RTT).
    :rtype: list[CosmosRegion]
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _rank_regions_by_latency, *args, **kwargs)
