#!/bin/bash
python azure_eventhub_producer_stress.py -m stress_send_sync --azure_identity True --hostname 'eh-llawstress.servicebus.windows.net' --eventhub 'eh-llawstress-hub' --duration 7200 &
wait