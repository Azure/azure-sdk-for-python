#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import jsondiff
from breaking_changes_checker.breaking_changes_tracker import BreakingChangesTracker


EXPECTED = [
    "(RemovedOrRenamedInstanceAttribute): The model or publicly exposed class 'azure.storage.queue.Metrics' had its instance variable 'retention_policy' deleted or renamed in the current version",
    "(RemovedOrRenamedInstanceAttribute): The client 'azure.storage.queue.QueueClient' had its instance variable 'queue_name' deleted or renamed in the current version",
    "(ChangedParameterKind): The class 'azure.storage.queue.QueueClient' method 'from_queue_url' had its parameter 'credential' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(AddedPositionalParam): The 'azure.storage.queue.QueueClient method 'get_queue_access_policy' had a 'positional_or_keyword' parameter 'queue_name' inserted in the current version",
    "(RemovedOrRenamedPositionalParam): The 'azure.storage.queue.QueueClient method 'set_queue_access_policy' had its 'positional_or_keyword' parameter 'signed_identifiers' deleted or renamed in the current version",
    "(ChangedParameterDefaultValue): The class 'azure.storage.queue.QueueClient' method 'set_queue_metadata' had its parameter 'metadata' default value changed from 'None' to ''",
    "(RemovedOrRenamedClassMethod): The 'azure.storage.queue.QueueSasPermissions' method 'from_string' was deleted or renamed in the current version",
    "(RemovedFunctionKwargs): The class 'azure.storage.queue.QueueServiceClient' method 'set_service_properties' changed from accepting keyword arguments to not accepting them in the current version",
    "(RemovedOrRenamedClientMethod): The 'azure.storage.queue.QueueServiceClient' client method 'get_service_properties' was deleted or renamed in the current version",
    "(RemovedOrRenamedEnumValue): The 'azure.storage.queue.StorageErrorCode' enum had its value 'queue_not_found' deleted or renamed in the current version",
    "(RemovedOrRenamedClass): The model or publicly exposed class 'azure.storage.queue.QueueMessage' was deleted or renamed in the current version",
    "(ChangedParameterDefaultValue): The publicly exposed function 'azure.storage.queue.generate_queue_sas' had its parameter 'permission' default value changed from 'None' to ''",
    "(ChangedParameterKind): The function 'azure.storage.queue.generate_queue_sas' had its parameter 'ip' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(AddedPositionalParam): The function 'azure.storage.queue.generate_queue_sas' had a 'positional_or_keyword' parameter 'conn_str' inserted in the current version",
    "(RemovedOrRenamedPositionalParam): The function 'azure.storage.queue.generate_queue_sas' had its 'positional_or_keyword' parameter 'account_name' deleted or renamed in the current version",
    "(RemovedOrRenamedModuleLevelFunction): The publicly exposed function 'azure.storage.queue.generate_account_sas' was deleted or renamed in the current version",
    "(ChangedParameterKind): The class 'azure.storage.queue.aio.QueueClient' method 'from_queue_url' had its parameter 'credential' changed from 'positional_or_keyword' to 'keyword_only' in the current version",
    "(RemovedParameterDefaultValue): The class 'azure.storage.queue.aio.QueueClient' method 'update_message' had default value 'None' removed from its parameter 'pop_receipt' in the current version",
    "(ChangedFunctionKind): The class 'azure.storage.queue.aio.QueueServiceClient' method 'get_service_stats' changed from 'asynchronous' to 'synchronous' in the current version.",
    "(ChangedParameterOrdering): The class 'azure.storage.queue.aio.QueueClient' method 'from_connection_string' had its parameters re-ordered from '['conn_str', 'queue_name', 'credential', 'kwargs']' to '['queue_name', 'conn_str', 'credential', 'kwargs']' in the current version",
    "(ChangedParameterOrdering): The class 'azure.storage.queue.QueueClient' method 'from_connection_string' had its parameters re-ordered from '['conn_str', 'queue_name', 'credential', 'kwargs']' to '['queue_name', 'conn_str', 'credential', 'kwargs']' in the current version"
]


def test_multiple_checkers():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED


def test_ignore_checks():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    ignore = {
        "azure-storage-queue": [
            ("ChangedParameterOrdering", "azure.storage.queue.aio", "QueueClient", "from_connection_string"),
            ("ChangedParameterOrdering", "azure.storage.queue", "QueueClient", "from_connection_string"),
        ]
    }

    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue", ignore=ignore)
    bc.run_checks()

    assert len(bc.breaking_changes)+2 == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED[:-2]


def test_replace_all_params():
    current = {
        "azure.ai.formrecognizer": {
            "function_nodes": {
                "my_function_name": {
                    "parameters": {},
                    "is_async": False
                }
            },
            "class_nodes": {
                "class_name": {
                    "methods": {
                        "one": {
                            "parameters": {},
                            "is_async": True
                        },
                        "two": {
                            "parameters": {},
                            "is_async": True
                        },
                    }
                }
            }
        }
    }

    stable = {
        "azure.ai.formrecognizer": {
            "function_nodes": {
                "my_function_name": {
                    "is_async": False,
                    "parameters": {
                        "testing": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        },
                        "testing2": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        }
                    }
                }
            },
            "class_nodes": {
                "class_name": {
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                    }
                }
            }
        }
    }

    EXPECTED = [
        "(RemovedOrRenamedPositionalParam): The 'azure.ai.formrecognizer.class_name method 'one' had its 'positional_or_keyword' parameter 'testing' deleted or renamed in the current version",
        "(RemovedOrRenamedPositionalParam): The 'azure.ai.formrecognizer.class_name method 'two' had its 'positional_or_keyword' parameter 'testing2' deleted or renamed in the current version",
        "(RemovedOrRenamedPositionalParam): The function 'azure.ai.formrecognizer.my_function_name' had its 'positional_or_keyword' parameter 'testing' deleted or renamed in the current version",
        "(RemovedOrRenamedPositionalParam): The function 'azure.ai.formrecognizer.my_function_name' had its 'positional_or_keyword' parameter 'testing2' deleted or renamed in the current version"
    ]

    diff = jsondiff.diff(stable, current)
    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED


def test_replace_all_functions():
    current = {
        "azure.ai.formrecognizer": {
            "function_nodes": {},
            "class_nodes": {
                "class_name": {
                    "methods": {}
                }
            }

        }
    }

    stable = {
        "azure.ai.formrecognizer": {
            "function_nodes": {
                "my_function_name": {
                    "is_async": False,
                    "parameters": {
                        "testing": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        },
                        "testing2": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        }
                    }
                },
                "my_function_name2": {
                    "is_async": False,
                    "parameters": {
                        "testing": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        },
                        "testing2": {
                            "default": None,
                            "param_type": "positional_or_keyword"
                        }
                    }
                },
            },
            "class_nodes": {
                "class_name": {
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                    }
                }
            }
        }
    }

    EXPECTED = [
        "(RemovedOrRenamedClassMethod): The 'azure.ai.formrecognizer.class_name' method 'one' was deleted or renamed in the current version",
        "(RemovedOrRenamedClassMethod): The 'azure.ai.formrecognizer.class_name' method 'two' was deleted or renamed in the current version",
        "(RemovedOrRenamedModuleLevelFunction): The publicly exposed function 'azure.ai.formrecognizer.my_function_name' was deleted or renamed in the current version",
        "(RemovedOrRenamedModuleLevelFunction): The publicly exposed function 'azure.ai.formrecognizer.my_function_name2' was deleted or renamed in the current version"
    ]

    diff = jsondiff.diff(stable, current)
    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED


def test_replace_all_classes():
    current = {
        "azure.ai.formrecognizer": {
            "class_nodes": {}
        }
    }

    stable = {
        "azure.ai.formrecognizer": {
            "class_nodes": {
                "class_name": {
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                    }
                },
                "class_name2": {
                    "methods": {
                        "one": {
                            "parameters": {
                                "testing": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True
                        },
                    }
                },
            }
        }
    }

    EXPECTED = [
        "(RemovedOrRenamedClass): The model or publicly exposed class 'azure.ai.formrecognizer.class_name' was deleted or renamed in the current version",
        "(RemovedOrRenamedClass): The model or publicly exposed class 'azure.ai.formrecognizer.class_name2' was deleted or renamed in the current version"
    ]

    diff = jsondiff.diff(stable, current)
    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED


def test_replace_all_modules():
    current = {}

    stable = {
        "azure.ai.formrecognizer": {
            "class_nodes": {}
        },
        "azure.ai.formrecognizer.aio": {
            "class_nodes": {}
        },
    }

    EXPECTED = [
        "(RemovedOrRenamedModule): The 'azure.ai.formrecognizer' module was deleted or renamed in the current version",
        "(RemovedOrRenamedModule): The 'azure.ai.formrecognizer.aio' module was deleted or renamed in the current version"
    ]

    diff = jsondiff.diff(stable, current)
    bc = BreakingChangesTracker(stable, current, diff, "azure-storage-queue")
    bc.run_checks()

    assert len(bc.breaking_changes) == len(EXPECTED)
    for message in bc.breaking_changes:
        assert message in EXPECTED