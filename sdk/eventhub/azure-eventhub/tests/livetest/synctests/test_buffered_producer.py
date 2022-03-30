#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# TODO: HAPPY PATH
#  send single
#  send batch
#  send single + batch
#  max wait time
#  max buffer length
#  flush
#  close
#  partition assignment
#
# TODO: ERROR PATH
#  callback errors
#  wrong input
#  flush timeout
#  send timeout (unable to enqueue)
#  underlying producer broken
#  long time inactivity(or maybe enable keep alive?)

# TODO: Stress test:
#  constantly sending to 32 partitions

