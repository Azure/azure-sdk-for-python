#!/bin/bash
python azure_eventhub_producer_stress.py -m stress_send_sync &
python azure_eventhub_consumer_stress_sync.py --auth_timeout 50 &
wait