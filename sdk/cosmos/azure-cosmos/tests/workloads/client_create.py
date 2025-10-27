from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.cosmos.aio import CosmosClient as AsyncClient
import time
import psutil

from workload_utils import *
from workload_configs import *


async def run_workload(client_id, client_logger):
    scope = "https://cosmos.azure.com/.default"
    os.environ["AZURE_COSMOS_AAD_SCOPE_OVERRIDE"] = scope
    await COSMOS_CREDENTIAL.get_token(scope)
    metrics = []

    try:
        for i in range(1):
            tasks = []
            for i in range(200):
                tasks.append(initialize_client(client_id, client_logger, metrics))
            await asyncio.gather(*tasks)
            client_logger.info(f"cpu percentage={psutil.cpu_percent(interval=5)}")
        if metrics:
            # compute stats
            sorted_vals = sorted(metrics)
            count = len(sorted_vals)
            min_ms = sorted_vals[0]
            max_ms = sorted_vals[-1]
            avg_ms = sum(sorted_vals) / count
            median_ms = sorted_vals[count // 2] if count % 2 == 1 else (sorted_vals[count // 2 - 1] + sorted_vals[count // 2]) / 2
            def pct(p: float) -> float:
                if count == 1:
                    return sorted_vals[0]
                # nearest-rank method
                idx = int(round((p / 100.0) * (count - 1)))
                return sorted_vals[idx]
            p90 = pct(90)
            p95 = pct(95)
            p99 = pct(99)
            client_logger.info(
                f"__aenter__ latency stats ms: count={count} min={min_ms:.2f} max={max_ms:.2f} avg={avg_ms:.2f} "
                f"median={median_ms:.2f} p90={p90:.2f} p95={p95:.2f} p99={p99:.2f}"
            )

    except Exception as e:
        client_logger.info("Exception in application layer")
        client_logger.error(e)

async def initialize_client(client_id, client_logger, metrics):
    session = create_custom_session()
    client = AsyncClient(COSMOS_URI, COSMOS_CREDENTIAL, multiple_write_locations=USE_MULTIPLE_WRITABLE_LOCATIONS,
                         preferred_locations=PREFERRED_LOCATIONS, excluded_locations=CLIENT_EXCLUDED_LOCATIONS,
                         transport=AioHttpTransport(session=session, session_owner=False),
                         enable_diagnostics_logging=True, logger=client_logger,
                         user_agent=get_user_agent(client_id))
    start = time.perf_counter()
    await client.__aenter__()
    end = time.perf_counter()
    await client.close()
    elapsed_ms = (end - start) * 1000.0
    metrics.append(elapsed_ms)
    client_logger.info(f"client_id={client_id} __aenter__ e2e_ms={elapsed_ms:.2f}")

if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    asyncio.run(run_workload(prefix, logger))