#!/bin/bash
python azure_eventhub_producer_stress.py  -m stress_send_sync --duration 720 --payload 524288 &
python azure_eventhub_producer_stress.py  -m stress_send_sync --duration 720 --payload 524288 &
python azure_eventhub_producer_stress.py  -m stress_send_sync --duration 720 --payload 524288 &
python azure_eventhub_producer_stress.py  -m stress_send_sync --duration 720 --payload 524288 &
wait