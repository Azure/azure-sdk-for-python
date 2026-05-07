# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Snippets extracted from articles/batch/pool-endpoint-configuration.md (Python only).

from azure.batch import models


class AzureBatchAllow:
    def set_ports_pool(self, pool, **kwargs):
        # [START endpoint_config_allow_subnet_python]
        pool.network_configuration = models.NetworkConfiguration(
            endpoint_configuration=models.BatchPoolEndpointConfiguration(
                inbound_nat_pools=[models.BatchInboundNatPool(
                    name='SSH',
                    protocol=models.InboundEndpointProtocol.TCP,
                    backend_port=22,
                    frontend_port_range_start=4000,
                    frontend_port_range_end=4100,
                    network_security_group_rules=[
                        models.NetworkSecurityGroupRule(
                            priority=170,
                            access=models.NetworkSecurityGroupRuleAccess.ALLOW,
                            source_address_prefix='192.168.1.0/24'
                        ),
                        models.NetworkSecurityGroupRule(
                            priority=175,
                            access=models.NetworkSecurityGroupRuleAccess.DENY,
                            source_address_prefix='*'
                        )
                    ]
                )
                ]
            )
        )
        # [END endpoint_config_allow_subnet_python]


class AzureBatchDeny:
    def set_ports_pool(self, pool, **kwargs):
        # [START endpoint_config_deny_ssh_python]
        pool.network_configuration = models.NetworkConfiguration(
            endpoint_configuration=models.BatchPoolEndpointConfiguration(
                inbound_nat_pools=[models.BatchInboundNatPool(
                    name='SSH',
                    protocol=models.InboundEndpointProtocol.TCP,
                    backend_port=22,
                    frontend_port_range_start=4000,
                    frontend_port_range_end=4100,
                    network_security_group_rules=[
                        models.NetworkSecurityGroupRule(
                            priority=170,
                            access=models.NetworkSecurityGroupRuleAccess.DENY,
                            source_address_prefix='Internet'
                        )
                    ]
                )
                ]
            )
        )
        # [END endpoint_config_deny_ssh_python]
