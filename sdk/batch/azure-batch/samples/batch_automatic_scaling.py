"""Snippets extracted from articles/batch/batch-automatic-scaling.md.

Migrated from azure-batch 14.x to 15.1.0 (azure.batch.BatchClient).
"""

import datetime

from azure.batch import BatchClient, models


def autoscale_create_and_enable(batch_client: BatchClient, pool_id: str) -> None:
    # [START autoscale_pool_create_enable_python]
    # Create a pool; specify configuration
    new_pool = models.BatchPoolCreateOptions(
        id="autoscale-enabled-pool",
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=models.BatchVmImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="20.04-LTS",
                version="latest",
            ),
            node_agent_sku_id="batch.node.ubuntu 20.04",
        ),
        vm_size="STANDARD_D1_v2",
        target_dedicated_nodes=0,
        target_low_priority_nodes=0,
    )
    batch_client.create_pool(pool=new_pool)  # Add the pool to the service client

    formula = (
        "$curTime = time();\n"
        "$workHours = $curTime.hour >= 8 && $curTime.hour < 18;\n"
        "$isWeekday = $curTime.weekday >= 1 && $curTime.weekday <= 5;\n"
        "$isWorkingWeekdayHour = $workHours && $isWeekday;\n"
        "$TargetDedicated = $isWorkingWeekdayHour ? 20:10;"
    )

    # Enable autoscale; specify the formula
    enable_options = models.BatchPoolEnableAutoScaleOptions(
        auto_scale_formula=formula,
        auto_scale_evaluation_interval=datetime.timedelta(minutes=10),
    )
    batch_client.enable_pool_auto_scale(pool_id=pool_id, enable_auto_scale_options=enable_options)
    # [END autoscale_pool_create_enable_python]
