import sys
import os
import logging
import threading
import time
import asyncio
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser
from azure.eventhub import EventHubClient, EventPosition, EventData, \
    EventHubConsumer, EventHubProducer, EventHubSharedKeyCredential, EventDataBatch
from azure.eventhub.aio import EventHubClient as EventHubClientAsync
from azure.identity import ClientSecretCredential


def stress_receive_sync(receiver, args, logger):
    batch = receiver.receive(timeout=5)
    return len(batch)


async def stress_receive_async(receiver, args, logger):
    batch = await receiver.receive(timeout=5)
    return len(batch)


def stress_receive_iterator_sync(receiver, args, logger):
    duration = args.duration
    deadline = time.time() + duration
    total_count = 0
    logging_count = 0
    try:
        for _ in receiver:
            total_count += 1
            logging_count += 1
            if logging_count >= args.output_interval:
                logger.info("Partition:%r, received:%r", receiver._partition, total_count)
                logging_count -= args.output_interval
            if time.time() > deadline:
                break
    finally:
        return total_count


async def stress_receive_iterator_async(receiver, args, logger):
    duration = args.duration
    deadline = time.time() + duration
    total_count = 0
    logging_count = 0
    try:
        async for _ in receiver:
            total_count += 1
            logging_count += 1
            if logging_count >= args.output_interval:
                logger.info("Partition:%r, received:%r", receiver._partition, total_count)
                logging_count -= args.output_interval
            if time.time() > deadline:
                break
    finally:
        return total_count


def stress_send_sync(producer: EventHubProducer, args, logger):
    batch = producer.create_batch()
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.try_add(event_data)
    except ValueError:
        producer.send(batch)
        return len(batch)


async def stress_send_async(producer, args, logger):
    batch = await producer.create_batch()
    try:
        while True:
            event_data = EventData(body=b"D" * args.payload)
            batch.try_add(event_data)
    except ValueError:
        await producer.send(batch)
        return len(batch)


def get_logger(filename, method_name, level=logging.INFO, print_console=False):
    stress_logger = logging.getLogger(method_name)
    stress_logger.setLevel(level)
    azure_logger = logging.getLogger("azure.eventhub")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    if print_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter)
        if not azure_logger.handlers:
            azure_logger.addHandler(console_handler)
        if not uamqp_logger.handlers:
            uamqp_logger.addHandler(console_handler)
        if not stress_logger.handlers:
            stress_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=20*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)
        uamqp_logger.addHandler(file_handler)
        stress_logger.addHandler(file_handler)

    return stress_logger


class StressTestRunner(object):
    def __init__(self, argument_parser):
        self.argument_parser = argument_parser
        self.argument_parser.add_argument("-m", "--method", required=True)
        self.argument_parser.add_argument("--output_interval", type=float, default=1000)
        self.argument_parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
        self.argument_parser.add_argument("--consumer", help="Consumer group name", default="$default")
        self.argument_parser.add_argument("--offset", help="Starting offset", default="-1")
        self.argument_parser.add_argument("-p", "--partitions", help="Comma seperated partition IDs", default="0")
        self.argument_parser.add_argument("--conn-str", help="EventHub connection string",
                            default=os.environ.get('EVENT_HUB_PERF_CONN_STR'))
        self.argument_parser.add_argument("--eventhub", help="Name of EventHub")
        self.argument_parser.add_argument("--address", help="Address URI to the EventHub entity")
        self.argument_parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
        self.argument_parser.add_argument("--sas-key", help="Shared access key")
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
                event_hub_path=self.args.eventhub, network_tracing=False)
        elif self.args.address:
            client = client_class(host=self.args.address,
                                    event_hub_path=self.args.eventhub,
                                    credential=EventHubSharedKeyCredential(self.args.sas_policy, self.args.sas_key),
                                    auth_timeout=240,
                                    network_tracing=False)
        elif self.args.aad_client_id:
            client = client_class(host=self.args.address,
                                  event_hub_path=self.args.eventhub,
                                  credential=ClientSecretCredential(self.args.tenant_id, self.args.aad_client_id,
                                                                    self.args.aad_secret),
                                  network_tracing=False)
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
        method_name = self.args.method
        logger = get_logger("{}.log".format(method_name), method_name,
                            level=logging.INFO, print_console=self.args.print_console)
        test_method = globals()[method_name]
        client = self.create_client(EventHubClient)
        self.running = True
        if self.args.partitions.lower() != "all":
            partitions = self.args.partitions.split(",")
        else:
            partitions = client.get_partition_ids()
        threads = []
        for pid in partitions:
            if "receive" in method_name:
                worker = client.create_consumer(consumer_group=self.args.consumer,
                                                  partition_id=pid,
                                                  event_position=EventPosition(self.args.offset),
                                                  prefetch=300)
            else:  # "send" in method_name
                worker = client.create_producer(partition_id=pid)
            thread = threading.Thread(target=self.run_test_method, args=(test_method, worker, logger))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

    def stop(self):
        self.running = False

    def run_test_method(self, test_method, worker, logger):
        deadline = time.time() + self.args.duration
        with worker:
            total_processed = 0
            iter_processed = 0
            while self.running and time.time() < deadline:
                try:
                    processed = test_method(worker, self.args, logger)
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        logger.info("Partition:%r, Total processed: %r", worker._partition, total_processed)
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("Partition:%r, keyboard interrupted", worker._partition)
                    self.stop()
                except Exception as e:
                    logger.exception("Partition:%r, %r failed:", worker._partition, type(worker))
                    self.stop()
            logger.info("Partition:%r, %r has finished testing", worker._partition, test_method)

    async def run_async(self):
        method_name = self.args.method
        logger = get_logger("{}.log".format(method_name), method_name,
                            level=logging.INFO, print_console=self.args.print_console)
        test_method = globals()[method_name]
        client = self.create_client(EventHubClientAsync)
        self.running = True
        if self.args.partitions.lower() != "all":
            partitions = self.args.partitions.split(",")
        else:
            partitions = await client.get_partition_ids()
        tasks = []
        for pid in partitions:
            if "receive" in method_name:
                worker = client.create_consumer(consumer_group=self.args.consumer,
                                                     partition_id=pid,
                                                     event_position=EventPosition(self.args.offset),
                                                     prefetch=300)
            else:  # "send" in method_name
                worker = client.create_producer(partition_id=pid)
            task = self.run_test_method_async(test_method, worker, logger)
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def run_test_method_async(self, test_method, worker, logger):
        deadline = time.time() + self.args.duration
        async with worker:
            total_processed = 0
            iter_processed = 0
            while self.running and time.time() < deadline:
                try:
                    processed = await test_method(worker, self.args, logger)
                    total_processed += processed
                    iter_processed += processed
                    if iter_processed >= self.args.output_interval:
                        logger.info("Partition:%r, Total processed: %r", worker._partition, total_processed)
                        iter_processed -= self.args.output_interval
                except KeyboardInterrupt:
                    logger.info("Partition:%r, keyboard interrupted", worker._partition)
                    self.stop()
                except Exception as e:
                    logger.exception("Partition:%r, %r failed:", worker._partition, type(worker))
                    self.stop()
            logger.info("Partition:%r, %r has finished testing", worker._partition, test_method)


if __name__ == '__main__':
    parser = ArgumentParser()
    runner = StressTestRunner(parser)
    runner.run()
