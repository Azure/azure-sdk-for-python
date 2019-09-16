# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import uuid
import sqlite3
import logging
from azure.eventhub.aio.eventprocessor import PartitionManager, OwnershipLostError

logger = logging.getLogger(__name__)


def _check_table_name(table_name: str):
    for c in table_name:
        if not (c.isalnum() or c == "_"):
            raise ValueError("Table name \"{}\" is not in correct format".format(table_name))
    return table_name


class SamplePartitionManager(PartitionManager):
    """An implementation of PartitionManager by using the sqlite3 in Python standard library.
    Sqlite3 is a mini sql database that runs in memory or files.
    Please don't use this PartitionManager for production use.


    """
    primary_keys_dict = {"eventhub_name": "text", "consumer_group_name": "text", "partition_id": "text"}
    other_fields_dict = {"owner_id": "text", "owner_level": "integer", "sequence_number": "integer", "offset": "text",
                         "last_modified_time": "real", "etag": "text"}
    checkpoint_fields = ["sequence_number", "offset"]
    fields_dict = {**primary_keys_dict, **other_fields_dict}
    primary_keys = list(primary_keys_dict.keys())
    other_fields = list(other_fields_dict.keys())
    fields = primary_keys + other_fields

    def __init__(self, db_filename: str = ":memory:", ownership_table: str = "ownership"):
        """

        :param db_filename: name of file that saves the sql data.
         Sqlite3 will run in memory without a file when db_filename is ":memory:".
        :param ownership_table: The table name of the sqlite3 database.
        """
        super(SamplePartitionManager, self).__init__()
        self.ownership_table = _check_table_name(ownership_table)
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        try:
            sql = "create table if not exists " + _check_table_name(ownership_table)\
                  + "("\
                  + ",".join([x[0]+" "+x[1] for x in self.fields_dict.items()])\
                  + ", constraint pk_ownership PRIMARY KEY ("\
                  + ",".join(self.primary_keys)\
                  + "))"
            c.execute(sql)
        finally:
            c.close()
        self.conn = conn

    async def list_ownership(self, eventhub_name, consumer_group_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select " + ",".join(self.fields) +
                                " from "+_check_table_name(self.ownership_table)+" where eventhub_name=? "
                                "and consumer_group_name=?",
                                (eventhub_name, consumer_group_name))
            return [dict(zip(self.fields, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    async def claim_ownership(self, ownership_list):
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
                        fields_without_checkpoint = list(filter(lambda x: x not in self.checkpoint_fields, self.fields))
                        sql = "insert into " + _check_table_name(self.ownership_table) + " (" \
                              + ",".join(fields_without_checkpoint) \
                              + ") values (?,?,?,?,?,?,?)"
                        cursor.execute(sql, tuple(p.get(field) for field in fields_without_checkpoint))
                    except sqlite3.OperationalError as op_err:
                        logger.info("EventProcessor %r failed to claim partition %r "
                                    "because it was claimed by another EventProcessor at the same time. "
                                    "The Sqlite3 exception is %r", p["owner_id"], p["partition_id"], op_err)
                        continue
                    else:
                        result.append(p)
                else:
                    if p.get("etag") == cursor_fetch[0][0]:
                        p["last_modified_time"] = time.time()
                        p["etag"] = str(uuid.uuid4())
                        other_fields_without_checkpoint = list(
                            filter(lambda x: x not in self.checkpoint_fields, self.other_fields)
                        )
                        sql = "update " + _check_table_name(self.ownership_table) + " set "\
                                       + ','.join([field+"=?" for field in other_fields_without_checkpoint])\
                                       + " where "\
                                       + " and ".join([field+"=?" for field in self.primary_keys])

                        cursor.execute(sql, tuple(p.get(field) for field in other_fields_without_checkpoint)
                                       + tuple(p.get(field) for field in self.primary_keys))
                        result.append(p)
                    else:
                        logger.info("EventProcessor %r failed to claim partition %r "
                                    "because it was claimed by another EventProcessor at the same time", p["owner_id"],
                                    p["partition_id"])
            self.conn.commit()
            return result
        finally:
            cursor.close()

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, owner_id,
            offset, sequence_number):
        cursor = self.conn.cursor()
        try:
            cursor.execute("select owner_id from " + _check_table_name(self.ownership_table)
                           + " where eventhub_name=? and consumer_group_name=? and partition_id=?",
                           (eventhub_name, consumer_group_name, partition_id))
            cursor_fetch = cursor.fetchall()
            if cursor_fetch and owner_id == cursor_fetch[0][0]:
                cursor.execute("update " + _check_table_name(self.ownership_table)
                               + " set offset=?, sequence_number=? "
                                 "where eventhub_name=? and consumer_group_name=? and partition_id=?",
                               (offset, sequence_number, eventhub_name, consumer_group_name, partition_id))
                self.conn.commit()
            else:
                logger.info("EventProcessor couldn't checkpoint to partition %r because it no longer has the ownership",
                            partition_id)
                raise OwnershipLostError()

        finally:
            cursor.close()

    async def close(self):
        self.conn.close()
