# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Generated API parameters
API_VERSION_PARAM_NAME = "api-version"
ENTITY_TYPE_QUEUES = "queues"
ENTITY_TYPE_TOPICS = "topics"
LIST_OP_SKIP = "$skip"
LIST_OP_TOP = "$top"

# XML namespace and tags
XML_SCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XML_SCHEMA_INSTANCE_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
ATOM_ENTRY_TAG = "{http://www.w3.org/2005/Atom}entry"
ATOM_CONTENT_TAG = "{http://www.w3.org/2005/Atom}content"

# ServiceBus XML namespace
SB_XML_NAMESPACE = "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"

# Rule XML tags
RULE_KEY_VALUE = "KeyValueOfstringanyType"
RULE_KEY = "Key"
RULE_VALUE = "Value"
RULE_VALUE_TYPE = "type"
RULE_VALUE_TYPE_XML_PREFIX = "d6p1"
RULE_SQL_COMPATIBILITY_LEVEL = "20"
RULE_DESCRIPTION_TAG = "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}RuleDescription"
RULE_FILTER_TAG = (
    "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Filter"
)
RULE_FILTER_COR_PROPERTIES_TAG = (
    "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Properties"
)
RULE_PARAMETERS_TAG = (
    "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Parameters"
)
RULE_ACTION_TAG = (
    "{http://schemas.microsoft.com/netservices/2010/10/servicebus/connect}Action"
)
RULE_KEY_VALUE_TAG = "{{{}}}{}".format(SB_XML_NAMESPACE, RULE_KEY_VALUE)
RULE_KEY_TAG = "{{{}}}{}".format(SB_XML_NAMESPACE, RULE_KEY)
RULE_VALUE_TAG = "{{{}}}{}".format(SB_XML_NAMESPACE, RULE_VALUE)
RULE_VALUE_TYPE_TAG = "{{{}}}{}".format(XML_SCHEMA_INSTANCE_NAMESPACE, RULE_VALUE_TYPE)
INT32_MAX_VALUE = 2147483647  # int32 max value used to tell if a Python int is an int32 or long in other languages
