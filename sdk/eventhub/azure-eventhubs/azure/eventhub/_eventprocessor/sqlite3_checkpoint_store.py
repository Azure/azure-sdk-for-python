# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import threading
import uuid
import sqlite3
import logging
from .checkpoint_store import CheckpointStore

_LOGGER = logging.getLogger(__name__)


def _check_table_name(table_name):
    for c in table_name:
        if not (c.isalnum() or c == "_"):
            raise ValueError("Table name \"{}\" is not in correct format".format(table_name))
    return table_name


class Sqlite3CheckpointStore(CheckpointStore):
    """An implementation of CheckpointStore by using the sqlite3 in Python standard library.
    Sqlite3 is a mini sql database that runs in memory or files.
    Please don't use this CheckpointStore for production use.


    """
    primary_keys_dict = {"fully_qualified_namespace": "text", "eventhub_name": "text",
                         "consumer_group": "text", "partition_id": "text"}
    primary_keys = list(primary_keys_dict.keys())

    ownership_data_fields_dict = {"owner_id": "text", "last_modified_time": "real", "etag": "text"}
    ownership_fields_dict = dict(primary_keys_dict)
    ownership_fields_dict.update(ownership_data_fields_dict)
    ownership_data_fields = list(ownership_data_fields_dict.keys())
    ownership_fields = primary_keys + ownership_data_fields

    checkpoint_data_fields_dict = {"sequence_number": "integer", "offset": "text"}
    checkpoint_data_fields = list(checkpoint_data_fields_dict.keys())
    checkpoint_fields_dict = dict(primary_keys_dict)
    checkpoint_fields_dict.update(checkpoint_data_fields_dict)
    checkpoint_fields = primary_keys + checkpoint_data_fields

    def __init__(self, db_filename=":memory:",
                 ownership_table="ownership", checkpoint_table="checkpoint"):
        # type: (str, str, str) -> None
        """
        :param db_filename: name of file that saves the sql data. Sqlite3 will run in memory without
         a file when db_filename is ":memory:".
        :param ownership_table: The table name of the sqlite3 database.

        """
        super(Sqlite3CheckpointStore, self).__init__()
        self.ownership_table = _check_table_name(ownership_table)
        self.checkpoint_table = _check_table_name(checkpoint_table)
        conn = sqlite3.connect(db_filename, check_same_thread=False)
        self._lock = threading.RLock()

        c = conn.cursor()
        try:
            ownership_sql = "create table if not exists " + self.ownership_table\
                              + "("\
                              + ",".join([x[0]+" "+x[1] for x in self.ownership_fields_dict.items()])\
                              + ", constraint pk_ownership PRIMARY KEY ("\
                              + ",".join(self.primary_keys)\
                              + "))"
            c.execute(ownership_sql)

            checkpoint_sql = "create table if not exists " + self.checkpoint_table \
                             + "(" \
                             + ",".join([x[0] + " " + x[1] for x in self.checkpoint_fields_dict.items()]) \
                             + ", constraint pk_ownership PRIMARY KEY (" \
                             + ",".join(self.primary_keys) \
                             + "))"
            c.execute(checkpoint_sql)
        finally:
            c.close()
        self.conn = conn

    def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select " + ",".join(self.ownership_fields) +
                           " from "+_check_table_name(self.ownership_table) +
                           " where fully_qualified_namespace=? and eventhub_name=? and consumer_group=?",
                           (fully_qualified_namespace, eventhub_name, consumer_group))
            return [dict(zip(self.ownership_fields, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def claim_ownership(self, ownership_list):
        with self._lock:
            result = []
            cursor = self.conn.cursor()
            try:
                for p in ownership_list:
                    cursor.execute("select etag from " + _check_table_name(self.ownership_table) +
                                        " where "+ " and ".join([field+"=?" for field in self.primary_keys]),
                                        tuple(p.get(field) for field in self.primary_keys))
                    cursor_fetch = cursor.fetchall()
                    if not cursor_fetch:
                        p["last_modified_time"] = time.time()
                        p["etag"] = str(uuid.uuid4())
                        try:
                            sql = "insert into " + _check_table_name(self.ownership_table) + " (" \
                                  + ",".join(self.ownership_fields) \
                                  + ") values ("+",".join(["?"] * len(self.ownership_fields)) + ")"
                            cursor.execute(sql, tuple(p.get(field) for field in self.ownership_fields))
                        except sqlite3.OperationalError as op_err:
                            _LOGGER.info("EventProcessor %r failed to claim partition %r "
                                         "because it was claimed by another EventProcessor at the same time. "
                                         "The Sqlite3 exception is %r", p["owner_id"], p["partition_id"], op_err)
                            continue
                        else:
                            result.append(p)
                    else:
                        if p.get("etag") == cursor_fetch[0][0]:
                            p["last_modified_time"] = time.time()
                            p["etag"] = str(uuid.uuid4())
                            sql = "update " + _check_table_name(self.ownership_table) + " set "\
                                           + ','.join([field+"=?" for field in self.ownership_data_fields])\
                                           + " where "\
                                           + " and ".join([field+"=?" for field in self.primary_keys])

                            cursor.execute(sql, tuple(p.get(field) for field in self.ownership_data_fields)
                                           + tuple(p.get(field) for field in self.primary_keys))
                            result.append(p)
                        else:
                            _LOGGER.info("EventProcessor %r failed to claim partition %r "
                                         "because it was claimed by another EventProcessor at the same time",
                                         p["owner_id"],
                                         p["partition_id"])
                self.conn.commit()
                return result
            finally:
                cursor.close()

    def update_checkpoint(self, checkpoint):
        with self._lock:
            cursor = self.conn.cursor()
            try:
                cursor.execute("insert or replace into " + self.checkpoint_table + "("
                               + ",".join([field for field in self.checkpoint_fields])
                               + ") values ("
                               + ",".join(["?"] * len(self.checkpoint_fields))
                               + ")",
                               tuple(checkpoint[field] for field in self.checkpoint_fields)
                               )
                self.conn.commit()
            finally:
                cursor.close()

    def list_checkpoints(self, fully_qualified_namespace, eventhub_name, consumer_group):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select "
                           + ",".join(self.checkpoint_fields)
                           + " from "
                           + self.checkpoint_table
                           + " where fully_qualified_namespace=? and eventhub_name=? and consumer_group=?",
                           (fully_qualified_namespace, eventhub_name, consumer_group)
                           )
            return [dict(zip(self.checkpoint_fields, row)) for row in cursor.fetchall()]

        finally:
            cursor.close()

    def close(self):
        with self._lock:
            self.conn.close()
