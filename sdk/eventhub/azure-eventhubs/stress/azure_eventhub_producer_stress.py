import sys
import os
import logging
import threading
import time
import asyncio
from argparse import ArgumentParser
from azure.eventhub import EventHubProducerClient, EventData, EventHubSharedKeyCredential, EventPosition
from azure.eventhub.aio import EventHubProducerClient as EventHubProducerClientAsync
from azure.identity import ClientSecretCredential
from logger import get_logger


def stress_send_sync(producer: EventHubProducerClient, args, logger):
    batch = producer.create_batch(max_size=256*1024)
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.try_add(event_data)
    except ValueError:
        producer.send(batch)
        return len(batch)


async def stress_send_async(producer: EventHubProducerClientAsync, args, logger):
    batch = await producer.create_batch(max_size=256*1024)
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.try_add(event_data)
    except ValueError:
        await producer.send(batch)
        return len(batch)


class StressTestRunner(object):
    def __init__(self, argument_parser):
        self.argument_parser = argument_parser
        self.argument_parser.add_argument("-m", "--method", required=True)
        self.argument_parser.add_argument("--output_interval", type=float, default=1000)
        self.argument_parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
        self.argument_parser.add_argument("--consumer", help="Consumer group name", default="$default")
        self.argument_parser.add_argument("--offset", help="Starting offset", default="-1")
        self.argument_parser.add_argument("--partitions", help="Number of partitions. 0 means to get partitions from eventhubs", type=int, default=0)
        self.argument_parser.add_argument("--conn_str", help="EventHub connection string",
                            default=os.environ.get('EVENT_HUB_PERF_32_CONN_STR'))
        self.argument_parser.add_argument("--eventhub", help="Name of EventHub")
        self.argument_parser.add_argument("--address", help="Address URI to the EventHub entity")
        self.argument_parser.add_argument("--sas_policy", help="Name of the shared access policy to authenticate with")
        self.argument_parser.add_argument("--sas_key", help="Shared access key")
        self.argument_parser.add_argument("--aad_client_id", help="AAD client id")
        self.argument_parser.add_argument("--aad_secret", help="AAD secret")
        self.argument_parser.add_argument("--aad_tenant_id", help="AAD tenant id")
        self.argument_parser.add_argument("--payload", help="payload size", type=int, default=1024)
        self.argument_parser.add_argument("--print_console", help="print to console", type=bool, default=False)
        self.args, _ = parser.parse_known_args()

        self.running = False

    def create_client(self, client_class):
        if self.args.conn_str:
            client = client_class.from_connection_string(
                self.args.conn_str,
                eventhub_name=self.args.eventhub, logging_enable=False)
        elif self.args.address:
            client = client_class(host=self.args.address,
                                    eventhub_name=self.args.eventhub,
                                    credential=EventHubSharedKeyCredential(self.args.sas_policy, self.args.sas_key),
                                    auth_timeout=240,
                                    logging_enable=False)
        elif self.args.aad_client_id:
            client = client_class(host=self.args.address,
                                  eventhub_name=self.args.eventhub,
                                  credential=ClientSecretCredential(self.args.tenant_id, self.args.aad_client_id,
                                                                    self.args.aad_secret),
                                  logging_enable=False)
        else:
            raise ValueError("Argument error. Must have one of connection string, sas and aad credentials")

        return client

    def run(self):
        method_name = self.args.method
        if "async" in method_name:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_async())
        else:
            self.run_sync()

    def run_sync(self):
        class EventHubProducerClientTest(EventHubProducerClient):
            def get_partition_ids(self_inner):
                if self.args.partitions != 0:
                    return [str(i) for i in range(self.args.partitions)]
                else:
                    return super(EventHubProducerClientTest, self_inner).get_partition_ids()

        method_name = self.args.method
        logger = get_logger("{}.log".format(method_name), method_name,
                            level=logging.INFO, print_console=self.args.print_console)
        test_method = globals()[method_name]
        client = self.create_client(EventHubProducerClientTest)
        self.running = True
        self.run_test_method(test_method, client, logger)

    def stop(self):
        self.running = False

    def run_test_method(self, test_method, worker, logger):
        deadline = time.time() + self.args.duration
        with worker:
            total_processed = 0
            iter_processed = 0
            start_time = time.perf_counter()
            while self.running and time.time() < deadline:
                try:
                    processed = test_method(worker, self.args, logger)
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        time_elapsed = time.perf_counter() - start_time
                        logger.info("Total sent: %r, Time elapsed: %r, Speed: %r/s", total_processed, time_elapsed, total_processed / time_elapsed)
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("keyboard interrupted")
                    self.stop()
                except Exception as e:
                    logger.exception("%r failed:", type(worker))
                    self.stop()
            logger.info("%r has finished testing", test_method)

    async def run_async(self):
        class EventHubProducerClientTestAsync(EventHubProducerClientAsync):
            async def get_partition_ids(self_inner):
                if self.args.partitions != 0:
                    return [str(i) for i in range(self.args.partitions)]
                else:
                    return await super(EventHubProducerClientTestAsync, self_inner).get_partition_ids()

        method_name = self.args.method
        logger = get_logger("{}.log".format(method_name), method_name,
                            level=logging.INFO, print_console=self.args.print_console)
        test_method = globals()[method_name]
        client = self.create_client(EventHubProducerClientTestAsync)
        self.running = True
        await self.run_test_method_async(test_method, client, logger)

    async def run_test_method_async(self, test_method, worker, logger):
        deadline = time.time() + self.args.duration
        async with worker:
            total_processed = 0
            iter_processed = 0
            start_time = time.perf_counter()
            while self.running and time.time() < deadline:
                try:
                    processed = await test_method(worker, self.args, logger)
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        time_elapsed = time.perf_counter() - start_time
                        logger.info("Total sent: %r, Time elapsed: %r, Speed: %r/s", total_processed, time_elapsed, total_processed / time_elapsed)
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("keyboard interrupted")
                    self.stop()
                except Exception as e:
                    logger.exception("%r failed:", type(worker))
                    self.stop()
            logger.info("%r has finished testing", test_method)


if __name__ == '__main__':
    parser = ArgumentParser()
    runner = StressTestRunner(parser)
    runner.run()
