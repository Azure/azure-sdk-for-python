#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

def iterate_containers(self, prefix=None, include=None):
    next_marker = None
    while True:
        results = self.list_containers(
            prefix=prefix,
            marker=next_marker,
            include=include,
        )

        for result in results:
            yield result

        next_marker = results.next_marker
        if not next_marker:
            break

def iterate_queues(self, prefix=None, include=None):
    next_marker = None
    while True:
        results = self.list_queues(
            prefix=prefix,
            marker=next_marker,
            include=include,
        )

        for result in results:
            yield result

        next_marker = results.next_marker
        if not next_marker:
            break

def iterate_tables(self, table_name=None):
    next_marker = None
    while True:
        results = self.query_tables(
            table_name=table_name,
            next_table_name=next_marker,
        )

        for result in results:
            yield result

        if hasattr(results, 'x_ms_continuation'):
            next_marker = results.x_ms_continuation.get('NextTableName')
        else:
            break

def iterate_shares(self, prefix=None, include=None):
    next_marker = None
    while True:
        results = self.list_shares(
            prefix=prefix,
            marker=next_marker,
            include=include,
        )

        for result in results:
            yield result

        next_marker = results.next_marker
        if not next_marker:
            break

def iterate_blobs(self, container_name, prefix=None, include=None, delimiter=None):
    next_marker = None
    while True:
        results = self.list_blobs(
            container_name,
            marker=next_marker,
            prefix=prefix,
            include=include,
            delimiter=delimiter,
        )

        for result in results:
            yield result

        next_marker = results.next_marker
        if not next_marker:
            break
