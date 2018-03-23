# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import logging
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler

def get_logger(filename, level=logging.INFO):
    logger = logging.getLogger("eventhub")
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    file_handler = RotatingFileHandler(filename, maxBytes=5*1024*1024, backupCount=2)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def parse_conn_str(conn_str):
    endpoint = None
    shared_access_key_name = None
    shared_access_key = None
    entity_path = None
    for element in conn_str.split(';'):
        key, _, value = element.partition('=')
        if key == 'Endpoint':
            endpoint = value.rstrip('/')
        elif key == 'SharedAccessKeyName':
            shared_access_key_name = value
        elif key == 'SharedAccessKey':
            shared_access_key = value
        elif key == 'EntityPath':
            entity_path = value
    if not all([endpoint, shared_access_key_name, shared_access_key]):
        raise ValueError("Invalid connection string")
    return endpoint, shared_access_key_name, shared_access_key, entity_path


def build_uri(address, entity):
    parsed = urlparse(address)
    if parsed.path:
        print(parsed.path)
        return address
    if not entity:
        raise ValueError("No EventHub specified")
    address += "/" + str(entity)
    return address