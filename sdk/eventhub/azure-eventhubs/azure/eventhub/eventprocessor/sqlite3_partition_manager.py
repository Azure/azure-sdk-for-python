# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import uuid
import sqlite3
from .partition_manager import PartitionManager


class Sqlite3PartitionManager(PartitionManager):
    """An implementation of PartitionManager by using the sqlite3 in Python standard library.
    Sqlite3 is a mini sql database that runs in memory or files.


    """
    def __init__(self, db_filename=":memory:", ownership_table="ownership"):
        """

        :param db_filename: name of file that saves the sql data.
        Sqlite3 will run in memory without a file when db_filename is ":memory:".
        :param ownership_table: The table name of the sqlite3 database.
        """
        super(Sqlite3PartitionManager, self).__init__()
        self.ownership_table = ownership_table
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        try:
            c.execute("create table " + ownership_table +
                      "(eventhub_name text,"
                      "consumer_group_name text,"
                      "instance_id text,"
                      "partition_id text,"
                      "owner_level integer,"
                      "sequence_number integer,"
                      "offset integer,"
                      "last_modified_time integer,"
                      "etag text)")
        except sqlite3.OperationalError:
            pass
        finally:
            c.close()
        self.conn = conn

    async def list_ownership(self, eventhub_name, consumer_group_name):
        cursor = self.conn.cursor()
        try:
            fields = ["eventhub_name", "consumer_group_name", "instance_id", "partition_id", "owner_level",
                      "sequence_number",
                      "offset", "last_modified_time", "etag"]
            cursor.execute("select " + ",".join(fields) +
                                " from "+self.ownership_table+" where eventhub_name=? "
                                "and consumer_group_name=?",
                                (eventhub_name, consumer_group_name))
            result_list = []

            for row in cursor.fetchall():
                d = dict(zip(fields, row))
                result_list.append(d)
            return result_list
        finally:
            cursor.close()

    async def claim_ownership(self, partitions):
        cursor = self.conn.cursor()
        try:
            for p in partitions:
                cursor.execute("select * from " + self.ownership_table +
                                    " where eventhub_name=? "
                                    "and consumer_group_name=? "
                                    "and partition_id =?",
                                    (p["eventhub_name"], p["consumer_group_name"],
                                     p["partition_id"]))
                if not cursor.fetchall():
                    cursor.execute("insert into " + self.ownership_table +
                                   " (eventhub_name,consumer_group_name,partition_id,instance_id,owner_level,last_modified_time,etag) "
                                   "values (?,?,?,?,?,?,?)",
                                   (p["eventhub_name"], p["consumer_group_name"], p["partition_id"], p["instance_id"], p["owner_level"],
                                    time.time(), str(uuid.uuid4())
                                    ))
                else:
                    cursor.execute("update "+self.ownership_table+" set instance_id=?, owner_level=?, last_modified_time=?, etag=? "
                                   "where eventhub_name=? and consumer_group_name=? and partition_id=?",
                                   (p["instance_id"], p["owner_level"], time.time(), str(uuid.uuid4()),
                                    p["eventhub_name"], p["consumer_group_name"], p["partition_id"]))
            self.conn.commit()
            return partitions
        finally:
            cursor.close()

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, instance_id,
            offset, sequence_number):
        cursor = self.conn.cursor()
        try:
            cursor.execute("update "+self.ownership_table+" set offset=?, sequence_number=? where eventhub_name=? and consumer_group_name=? and partition_id=?",
                           (offset, sequence_number, eventhub_name, consumer_group_name, partition_id))
            self.conn.commit()
        finally:
            cursor.close()

    async def close(self):
        self.conn.close()
