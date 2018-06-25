# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

Feature: Exercising Event Processor Host

#  Scenario: EPH single host, generic scenario.

#  Scenario: EPH runs with listen only claims.

#  Scenario: Host runs idle for a while by managing sender to send in intervals.

#  Scenario: No sends at all, hosts will stay idle.

#  Scenario: Spawns multiple test processes consuming from the same event hub.

#  Scenario: Registers and unregisters hosts as part of the regular iteration to introduce excessive partition moves.

  Scenario: Registers and unregisters hosts as part of the regular iteration to introduce excessive partition moves. No sends in this scenario.

  Scenario: Runs EPH on 256 partition entity.

#  Scenario: Runs EPH on multiple consumer groups.

#  Scenario: Runs EPH with web sockets enabled.