# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def test_import():
    import azure.mgmt.rdbms
    import azure.mgmt.rdbms.mysql
    import azure.mgmt.rdbms.mysql.models
    
    import azure.mgmt.rdbms.postgresql
    import azure.mgmt.rdbms.postgresql.models
    
    import azure.mgmt.rdbms.mysql_flexibleservers
    import azure.mgmt.rdbms.mysql_flexibleservers.models
    
    import azure.mgmt.rdbms.postgresql_flexibleservers
    import azure.mgmt.rdbms.postgresql_flexibleservers.models