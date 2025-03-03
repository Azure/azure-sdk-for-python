#!/bin/bash
python3 r-proxy-workload.py &
python3 r-w-q-proxy-workload.py &
python3 r-w-q-workload.py &
python3 r-workload.py &
python3 w-workload.py &
python3 w-proxy-workload.py &
