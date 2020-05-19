# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import logging
import threading
import time
import asyncio
from argparse import ArgumentParser
from azure.eventhub import EventHubProducerClient, EventData, EventHubSharedKeyCredential, TransportType
from azure.eventhub.exceptions import EventHubError
from azure.eventhub.aio import EventHubProducerClient as EventHubProducerClientAsync
from azure.identity import ClientSecretCredential
from azure.identity.aio import ClientSecretCredential as ClientSecretCredentialAsync
from logger import get_logger
from process_monitor import ProcessMonitor


def stress_send_sync(producer: EventHubProducerClient, args, logger):
    batch = producer.create_batch(partition_id=args.send_partition_id, partition_key=args.send_partition_key)
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.add(event_data)
    except ValueError:
        try:
            producer.send_batch(batch)
        except EventHubError as e:
            if args.ignore_send_failure:
                logger.warning("Sync send failed due to error: %r.", e)
                return 0
            raise
    return len(batch)


def stress_send_list_sync(producer: EventHubProducerClient, args, logger):
    quantity = int(256*1023 / args.payload)
    send_list = []
    for _ in range(quantity):
        send_list.append(EventData(body=b"D" * args.payload))
    try:
        producer.send_batch(send_list)
    except EventHubError as e:
        if args.ignore_send_failure:
            logger.warning("Sync send failed due to error: %r.", e)
            return 0
        raise
    return len(send_list)


async def stress_send_async(producer: EventHubProducerClientAsync, args, logger):
    batch = await producer.create_batch()
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.add(event_data)
    except ValueError:
        try:
            await producer.send_batch(batch)
        except EventHubError as e:
            if args.ignore_send_failure:
                logger.warning("ASync send failed due to error: %r.", e)
                return 0
            raise
    return len(batch)


async def stress_send_list_async(producer: EventHubProducerClientAsync, args, logger):
    quantity = int(256*1023 / args.payload)
    send_list = []
    for _ in range(quantity):
        send_list.append(EventData(body=b"D" * args.payload))
    try:
        await producer.send_batch(send_list)
    except EventHubError as e:
        if args.ignore_send_failure:
            logger.warning("ASync send failed due to error: %r.", e)
            return 0
        raise
    return len(send_list)


class StressTestRunner(object):
    def __init__(self, argument_parser):
        self.argument_parser = argument_parser
        self.argument_parser.add_argument("-m", "--method", required=True)
        self.argument_parser.add_argument("--output_interval", type=float, default=1000)
        self.argument_parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
        self.argument_parser.add_argument(
            "--partitions",
            help="Number of partitions. 0 means to get partitions from eventhubs",
            type=int,
            default=0
        )
        self.argument_parser.add_argument(
            "--send_partition_id",
            help="Send messages to a specific partition",
            type=int
        )
        self.argument_parser.add_argument(
            "--send_partition_key",
            help="Send messages to a specific partition key",
            type=str
        )
        self.argument_parser.add_argument("--conn_str", help="EventHub connection string",
                                          default=os.environ.get('EVENT_HUB_PERF_32_CONN_STR'))
        parser.add_argument("--auth_timeout", help="Authorization Timeout", type=float, default=60)
        self.argument_parser.add_argument("--eventhub", help="Name of EventHub")
        self.argument_parser.add_argument(
            "--transport_type",
            help="Transport type, 0 means AMQP, 1 means AMQP over WebSocket",
            type=int,
            default=0
        )
        self.argument_parser.add_argument("--parallel_send_cnt", help="Number of parallelling sending", type=int)
        self.argument_parser.add_argument(
            "--parallel_create_new_client",
            action="store_true",
            help="Whether create new client for each sending",
        )
        self.argument_parser.add_argument("--proxy_hostname", type=str)
        self.argument_parser.add_argument("--proxy_port", type=str)
        self.argument_parser.add_argument("--proxy_username", type=str)
        self.argument_parser.add_argument("--proxy_password", type=str)
        self.argument_parser.add_argument("--hostname", help="The fully qualified host name for the Event Hubs namespace.")
        self.argument_parser.add_argument("--sas_policy", help="Name of the shared access policy to authenticate with")
        self.argument_parser.add_argument("--sas_key", help="Shared access key")
        self.argument_parser.add_argument("--aad_client_id", help="AAD client id")
        self.argument_parser.add_argument("--aad_secret", help="AAD secret")
        self.argument_parser.add_argument("--aad_tenant_id", help="AAD tenant id")
        self.argument_parser.add_argument("--payload", help="payload size", type=int, default=1024)
        self.argument_parser.add_argument("--uamqp_logging_enable", help="uamqp logging enable", action="store_true")
        self.argument_parser.add_argument("--print_console", action="store_true")
        self.argument_parser.add_argument("--log_filename", help="log file name", type=str)
        self.argument_parser.add_argument("--retry_total", type=int, default=3)
        self.argument_parser.add_argument("--retry_backoff_factor", type=float, default=0.8)
        self.argument_parser.add_argument("--retry_backoff_max", type=float, default=120)
        self.argument_parser.add_argument("--ignore_send_failure", help="ignore sending failures", action="store_true")
        self.args, _ = parser.parse_known_args()

        if self.args.send_partition_key and self.args.send_partition_id:
            raise ValueError("Cannot set send_partition_key and send_partition_id at the same time.")

        self.running = False

    def create_client(self, client_class, is_async=False):

        transport_type = TransportType.Amqp if self.args.transport_type == 0 else TransportType.AmqpOverWebsocket
        http_proxy = None
        retry_options = {
            "retry_total": self.args.retry_total,
            "retry_backoff_factor": self.args.retry_backoff_factor,
            "retry_backoff_max": self.args.retry_backoff_max
        }
        if self.args.proxy_hostname:
            http_proxy = {
                "proxy_hostname": self.args.proxy_hostname,
                "proxy_port": self.args.proxy_port,
                "username": self.args.proxy_username,
                "password": self.args.proxy_password,
            }

        if self.args.conn_str:
            client = client_class.from_connection_string(
                self.args.conn_str,
                eventhub_name=self.args.eventhub,
                auth_timeout=self.args.auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type,
                logging_enable=self.args.uamqp_logging_enable,
                **retry_options
            )
        elif self.args.hostname:
            client = client_class(
                fully_qualified_namespace=self.args.hostname,
                eventhub_name=self.args.eventhub,
                credential=EventHubSharedKeyCredential(self.args.sas_policy, self.args.sas_key),
                auth_timeout=self.args.auth_timeout,
                http_proxy=http_proxy,
                transport_type=transport_type,
                logging_enable=self.args.uamqp_logging_enable,
                **retry_options
            )
        elif self.args.aad_client_id:
            if is_async:
                credential = ClientSecretCredentialAsync(self.args.tenant_id, self.args.aad_client_id, self.args.aad_secret)
            else:
                credential = ClientSecretCredential(self.args.tenant_id, self.args.aad_client_id, self.args.aad_secret)
            client = client_class(
                fully_qualified_namespace=self.args.hostname,
                eventhub_name=self.args.eventhub,
                auth_timeout=self.args.auth_timeout,
                credential=credential,
                http_proxy=http_proxy,
                transport_type=transport_type,
                logging_enable=self.args.uamqp_logging_enable,
                **retry_options
            )
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
        with ProcessMonitor("monitor_{}".format(self.args.log_filename), "producer_stress_sync", print_console=self.args.print_console):
            class EventHubProducerClientTest(EventHubProducerClient):
                def get_partition_ids(self_inner):
                    if self.args.partitions != 0:
                        return [str(i) for i in range(self.args.partitions)]
                    else:
                        return super(EventHubProducerClientTest, self_inner).get_partition_ids()

            method_name = self.args.method
            logger = get_logger(self.args.log_filename, method_name,
                                level=logging.INFO, print_console=self.args.print_console)
            test_method = globals()[method_name]
            self.running = True

            if self.args.parallel_send_cnt and self.args.parallel_send_cnt > 1:
                if self.args.parallel_create_new_client:
                    clients = [
                        self.create_client(EventHubProducerClientTest) for _ in range(self.args.parallel_send_cnt)
                    ]
                else:
                    clients = [self.create_client(EventHubProducerClientTest)]
                self.run_test_method_parallel(test_method, clients, logger)
            else:
                client = self.create_client(EventHubProducerClientTest)
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
                    cur_iter_start_time = time.perf_counter()
                    processed = test_method(worker, self.args, logger)
                    now_time = time.perf_counter()
                    cur_iter_time_elapsed = now_time - cur_iter_start_time
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        time_elapsed = now_time - start_time
                        logger.info(
                            "Total sent: %r, Time elapsed: %r, Speed: %r/s, Current Iteration Speed: %r/s",
                            total_processed,
                            time_elapsed,
                            total_processed / time_elapsed,
                            processed / cur_iter_time_elapsed
                        )
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("keyboard interrupted")
                    self.stop()
                except Exception as e:
                    logger.exception("%r failed:", type(worker), e)
                    self.stop()
            logger.info("%r has finished testing", test_method)

    def run_test_method_parallel(self, test_method, workers, logger):
        cnt = self.args.parallel_send_cnt
        threads = []
        if self.args.parallel_create_new_client:
            for i in range(cnt):
                threads.append(threading.Thread(
                    target=self.run_test_method,
                    args=(
                        test_method,
                        workers[i],
                        logger
                    ),
                    daemon=True
                ))
        else:
            threads = [threading.Thread(
                target=self.run_test_method,
                args=(
                    test_method,
                    workers[0],
                    logger
                ),
                daemon=True
            ) for _ in range(cnt)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=self.args.duration)

    async def run_async(self):
        with ProcessMonitor("monitor_{}".format(self.args.log_filename), "producer_stress_async", print_console=self.args.print_console):
            class EventHubProducerClientTestAsync(EventHubProducerClientAsync):
                async def get_partition_ids(self_inner):
                    if self.args.partitions != 0:
                        return [str(i) for i in range(self.args.partitions)]
                    else:
                        return await super(EventHubProducerClientTestAsync, self_inner).get_partition_ids()

            method_name = self.args.method
            logger = get_logger(self.args.log_filename, method_name,
                                level=logging.INFO, print_console=self.args.print_console)
            test_method = globals()[method_name]
            self.running = True

            if self.args.parallel_send_cnt and self.args.parallel_send_cnt > 1:
                if self.args.parallel_create_new_client:
                    clients = [
                        self.create_client(EventHubProducerClientTestAsync, is_async=True) for _ in range(self.args.parallel_send_cnt)
                    ]
                else:
                    clients = [self.create_client(EventHubProducerClientTestAsync, is_async=True)]
                await self.run_test_method_parallel_async(test_method, clients, logger)
            else:
                client = self.create_client(EventHubProducerClientTestAsync, is_async=True)
                await self.run_test_method_async(test_method, client, logger)

    async def run_test_method_async(self, test_method, worker, logger):
        deadline = time.time() + self.args.duration
        async with worker:
            total_processed = 0
            iter_processed = 0
            start_time = time.perf_counter()
            while self.running and time.time() < deadline:
                try:
                    cur_iter_start_time = time.perf_counter()
                    processed = await test_method(worker, self.args, logger)
                    now_time = time.perf_counter()
                    cur_iter_time_elapsed = now_time - cur_iter_start_time
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        time_elapsed = now_time - start_time
                        logger.info(
                            "Total sent: %r, Time elapsed: %r, Overall Speed: %r/s, Current Iteration Speed: %r/s",
                            total_processed,
                            time_elapsed,
                            total_processed / time_elapsed,
                            processed / cur_iter_time_elapsed,
                        )
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("keyboard interrupted")
                    self.stop()
                except Exception as e:
                    logger.exception("%r failed: ", type(worker), e)
                    self.stop()
            logger.info("%r has finished testing", test_method)

    async def run_test_method_parallel_async(self, test_method, worker, logger):
        cnt = self.args.parallel_send_cnt
        tasks = []
        if self.args.parallel_create_new_client:
            for i in range(cnt):
                tasks.append(
                    asyncio.ensure_future(
                        self.run_test_method_async(
                            test_method,
                            worker[i],
                            logger
                        )
                    )
                )
        else:
            tasks = [
                asyncio.ensure_future(
                    self.run_test_method_async(
                        test_method,
                        worker[0],
                        logger
                    )
                ) for _ in range(cnt)
            ]

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    parser = ArgumentParser()
    runner = StressTestRunner(parser)
    runner.run()
