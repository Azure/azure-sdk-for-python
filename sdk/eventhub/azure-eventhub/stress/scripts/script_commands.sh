#!/bin/bash
python azure_eventhub_producer_stress.py -m stress_send_sync --duration 7200 &
wait