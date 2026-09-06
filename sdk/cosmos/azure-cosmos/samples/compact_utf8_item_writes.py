# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import config

# ----------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------
# Sample - demonstrates the `enable_compact_utf8_item_writes` client option.
#
# By default, the SDK serializes item bodies with `ensure_ascii=True`, so every non-ASCII
# character is expanded into a `\uXXXX` escape sequence. A single CJK character occupies 3 bytes
# as raw UTF-8 but 6 bytes once escaped, and a 4-byte emoji occupies 12 bytes as an escaped
# surrogate pair. For Unicode-heavy items that expansion increases the size of the request sent
# over the network and can push a request past the 2 MiB request size limit.
#
# Setting `enable_compact_utf8_item_writes=True` sends the body as compact UTF-8 instead. The
# option is:
#   * opt-in - the default (False) keeps the existing escaped wire format exactly as-is.
#   * scoped to item writes - create, upsert, replace, patch, and transactional batch.
#     Queries, control-plane bodies, and the partition-key header are unaffected.
#
# Both representations describe the same JSON document, so the stored item and the values
# returned on reads are identical. Only the bytes on the wire change.
# ----------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create the configured Database if it does not already exist, and
# leaves that Database in place. It creates and then deletes a Container within it. Each time a
# Container is created the account will be billed for 1 hour of usage based on the provisioned
# throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']

# A dedicated container for this sample. The shared container id from config is created by other
# samples with a '/id' partition key path, so this sample uses its own container to stay
# independent of the order in which the samples are run.
CONTAINER_ID = 'compact-utf8-item-writes'
PARTITION_KEY_VALUE = 'compact-utf8-sample'


def show_wire_size_difference(item):
    """Print the request body size with and without ASCII escape expansion."""
    escaped = json.dumps(item, separators=(',', ':')).encode('utf-8')
    compact = json.dumps(item, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    print('Escaped body (default):      {0} bytes'.format(len(escaped)))
    print('Compact UTF-8 body (opt-in): {0} bytes'.format(len(compact)))
    print('Saved:                       {0} bytes'.format(len(escaped) - len(compact)))


def write_compact_utf8_item(container):
    """Write a Unicode-heavy item without ASCII escape expansion."""
    item_id = 'compact-utf8-' + str(uuid.uuid4())
    item = {
        'id': item_id,
        'pk': PARTITION_KEY_VALUE,
        # Repeated so the size difference is easy to see in the output.
        'content': 'Customer text: 日本語 🎉' * 200,  # cspell:disable-line
    }

    show_wire_size_difference(item)

    created_item = container.create_item(item)
    print('Created compact UTF-8 item: {0}'.format(created_item['id']))

    # The value stored in the service is the same either way - only the
    # serialization of the outgoing request changed.
    read_item = container.read_item(item_id, partition_key=PARTITION_KEY_VALUE)
    print('Round trip preserved content: {0}'.format(
        read_item['content'] == item['content']))

    container.delete_item(item_id, partition_key=PARTITION_KEY_VALUE)


def run_sample():
    """Run the compact UTF-8 item write sample."""
    # The option is set once at client construction and applies to every item
    # write issued by this client. It is disabled by default.
    client = cosmos_client.CosmosClient(
        HOST,
        {'masterKey': MASTER_KEY},
        enable_compact_utf8_item_writes=True,
    )
    db = None
    container = None
    try:
        # setup database for this sample
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        # setup container for this sample
        container = db.create_container_if_not_exists(
            id=CONTAINER_ID,
            partition_key=PartitionKey(path='/pk', kind='Hash'),
        )

        write_compact_utf8_item(container)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        # cleanup container after sample, even if the sample failed part way through
        if db is not None and container is not None:
            try:
                db.delete_container(container)

            except exceptions.CosmosHttpResponseError:
                pass

        print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()
