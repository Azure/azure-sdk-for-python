#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Example showing how to use Azure Monitor OpenTelemetry performance counters.

This example demonstrates the performance counters feature that automatically
collects system and process-level metrics like CPU usage, memory usage, etc.
"""

import os
import time
from azure.monitor.opentelemetry import configure_azure_monitor


def main():
    # Configure Azure Monitor with performance counters enabled (default)
    configure_azure_monitor(
        connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=00000000-0000-0000-0000-000000000000"),
        enable_performance_counters=True,  # This is the default
    )
    
    print("Azure Monitor configured with performance counters enabled.")
    print("Performance counters being collected:")
    print("  - Available Memory (\\Memory\\Available Bytes)")
    print("  - Process CPU Usage (\\Process(??APP_WIN32_PROC??)\\% Processor Time)")
    print("  - Process Private Bytes (\\Process(??APP_WIN32_PROC??)\\Private Bytes)")
    print("  - Processor Time (\\Processor(_Total)\\% Processor Time)")
    print()
    print("These metrics will be automatically sent to Application Insights.")
    print("Running for 60 seconds to collect and send metrics...")
    
    # Simulate some work to generate CPU/memory activity
    for i in range(60):
        # Do some CPU work
        sum(range(10000))
        
        # Allocate some memory
        data = [0] * 1000
        
        if i % 10 == 0:
            print(f"Running... {60-i} seconds remaining")
        
        time.sleep(1)
    
    print("Example completed. Check your Application Insights resource for the performance counter metrics.")


if __name__ == "__main__":
    main()
