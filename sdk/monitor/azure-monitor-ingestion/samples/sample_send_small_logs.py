"""
Usage: python sample_send_small_logs.py
"""

import os
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ['LOGS_INGESTION_ENDPOINT']
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential)


