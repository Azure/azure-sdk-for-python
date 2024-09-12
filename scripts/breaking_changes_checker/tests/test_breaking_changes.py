#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
import pytest
from breaking_changes_checker.breaking_changes_tracker import BreakingChangesTracker
from breaking_changes_checker.detect_breaking_changes import main
from breaking_changes_checker.checkers.removed_method_overloads_checker import RemovedMethodOverloadChecker

def format_breaking_changes(breaking_changes):
    formatted = "\n"
    for bc in breaking_changes:
        formatted += f"{bc}\n"
    
    formatted += f"\nFound {len(breaking_changes)} breaking changes.\n"
    formatted += "\nSee aka.ms/azsdk/breaking-changes-tool to resolve " \
                    "any reported breaking changes or false positives.\n"
    return formatted

EXPECTED = [
    "(RemovedOrRenamedInstanceAttribute): Model `Metrics` deleted or renamed its instance variable `retention_policy`",
    "(RemovedOrRenamedInstanceAttribute): Client `QueueClient` deleted or renamed instance variable `queue_name`",
    "(ChangedParameterKind): Method `QueueClient.from_queue_url` changed its parameter `credential` from `positional_or_keyword` to `keyword_only`",
    "(AddedPositionalParam): Method `QueueClient.get_queue_access_policy` inserted a `positional_or_keyword` parameter `queue_name`",
    "(RemovedOrRenamedPositionalParam): Method `QueueClient.set_queue_access_policy` deleted or renamed its parameter `signed_identifiers` of kind `positional_or_keyword`",
    "(ChangedParameterDefaultValue): Method `QueueClient.set_queue_metadata` parameter `metadata` changed default value from `None` to ``",
    "(RemovedOrRenamedClassMethod): Deleted or renamed method `QueueSasPermissions.from_string`",
    "(RemovedFunctionKwargs): Method `QueueServiceClient.set_service_properties` changed from accepting keyword arguments to not accepting them",
    "(RemovedOrRenamedClientMethod): Deleted or renamed client method `QueueServiceClient.get_service_properties`",
    "(RemovedOrRenamedEnumValue): Deleted or renamed enum value `StorageErrorCode.queue_not_found`",
    "(RemovedOrRenamedClass): Deleted or renamed model `QueueMessage`",
    "(ChangedParameterDefaultValue): Function `generate_queue_sas` parameter `permission` changed default value from `None` to ``",
    "(ChangedParameterKind): Function `generate_queue_sas` changed its parameter `ip` from `positional_or_keyword` to `keyword_only`",
    "(AddedPositionalParam): Function `generate_queue_sas` inserted a `positional_or_keyword` parameter `conn_str`",
    "(RemovedOrRenamedPositionalParam): Function `generate_queue_sas` deleted or renamed its parameter `account_name` of kind `positional_or_keyword`",
    "(RemovedOrRenamedModuleLevelFunction): Deleted or renamed function `generate_account_sas`",
    "(RemovedParameterDefaultValue): Method `QueueClient.update_message` removed default value `None` from its parameter `pop_receipt`",
    "(ChangedFunctionKind): Method `QueueServiceClient.get_service_stats` changed from `asynchronous` to `synchronous`",
    "(ChangedParameterOrdering): Method `QueueClient.from_connection_string` re-ordered its parameters from `['conn_str', 'queue_name', 'credential', 'kwargs']` to `['queue_name', 'conn_str', 'credential', 'kwargs']`",
]


def test_multiple_checkers():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


def test_ignore_checks():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)

    ignore = {
        "azure-storage-queue": [
            ("ChangedParameterOrdering", "*", "QueueClient", "from_connection_string"),
        ]
    }

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue", ignore=ignore)
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED[:-1])
    assert len(bc.breaking_changes)+1 == len(EXPECTED)
    assert changes == expected_msg


def test_ignore_with_wildcard_checks():
    with open(os.path.join(os.path.dirname(__file__), "test_stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(os.path.dirname(__file__), "test_current.json"), "r") as fd:
        current = json.load(fd)

    ignore = {
        "azure-storage-queue": [
            ("ChangedParameterOrdering", "*", "*", "from_connection_string"),
            ("ChangedFunctionKind", "azure.storage.queue.aio", "QueueServiceClient", "get_service_stats"),
        ]
    }

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue", ignore=ignore)
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED[:-2])
    assert len(bc.breaking_changes)+2 == len(EXPECTED)
    assert changes == expected_msg


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
        "(RemovedOrRenamedPositionalParam): Method `class_name.one` deleted or renamed its parameter `testing` of kind `positional_or_keyword`",
        "(RemovedOrRenamedPositionalParam): Method `class_name.two` deleted or renamed its parameter `testing2` of kind `positional_or_keyword`",
        "(RemovedOrRenamedPositionalParam): Function `my_function_name` deleted or renamed its parameter `testing` of kind `positional_or_keyword`",
        "(RemovedOrRenamedPositionalParam): Function `my_function_name` deleted or renamed its parameter `testing2` of kind `positional_or_keyword`"
    ]

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


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
        "(RemovedOrRenamedClassMethod): Deleted or renamed method `class_name.one`",
        "(RemovedOrRenamedClassMethod): Deleted or renamed method `class_name.two`",
        "(RemovedOrRenamedModuleLevelFunction): Deleted or renamed function `my_function_name`",
        "(RemovedOrRenamedModuleLevelFunction): Deleted or renamed function `my_function_name2`"
    ]

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


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
        "(RemovedOrRenamedClass): Deleted or renamed model `class_name`",
        "(RemovedOrRenamedClass): Deleted or renamed model `class_name2`"
    ]

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


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
        "(RemovedOrRenamedModule): Deleted or renamed module `azure.ai.formrecognizer`",
    ]

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


@pytest.mark.skip(reason="We need to regenerate the code reports for these tests and update the expected results")
def test_pass_custom_reports_breaking(capsys):
    source_report = "test_stable.json"
    target_report = "test_current.json"

    try:
        main(None, None, None, None, "tests", False, False, False, source_report, target_report)
    except SystemExit as e:
        if e.code == 1:
            out, _ = capsys.readouterr()
            # Check if we have some breaking changes reported
            assert out.endswith("See aka.ms/azsdk/breaking-changes-tool to resolve any reported breaking changes or false positives.\n\n")
        else:
            pytest.fail("test_compare_reports failed to report breaking changes when passing custom reports")


def test_removed_operation_group():
    current = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "methods": {},
                    "properties": {}
                }
            },
        }
    }

    stable = {
        "azure.contoso": {
            "class_nodes": {
                "ContosoClient": {
                    "methods": {},
                    "properties": {
                        "foo": {
                            "attr_type": "FooOperations",
                        }
                    }
                }
            },
        }
    }

    EXPECTED = [
        "(RemovedOrRenamedOperationGroup): Deleted or renamed client operation group `ContosoClient.foo`"
    ]

    bc = BreakingChangesTracker(stable, current, "azure-storage-queue")
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg


def test_async_breaking_changes_cleanup():
    breaking_changes = [
        ("Message", "RemovedOrRenamedClassMethod", "azure.contoso.aio.operations", "Foo", "foo"),
        ("Message", "RemovedOrRenamedClassMethod", "azure.contoso.operations", "Foo", "foo"),
        ("Message", "ChangedParameterOrdering", "azure.contoso", "FooClient", "from_connection_string"),
    ]

    # create dummy BreakingChangesTracker instance
    bct = BreakingChangesTracker({}, {}, "azure-contoso")
    bct.breaking_changes = breaking_changes

    bct.run_async_cleanup(bct.breaking_changes)

    assert len(bct.breaking_changes) == 2
    assert bct.breaking_changes[0] == ("Message", "RemovedOrRenamedClassMethod", "azure.contoso.operations", "Foo", "foo")
    assert bct.breaking_changes[1] == ("Message", "ChangedParameterOrdering", "azure.contoso", "FooClient", "from_connection_string")


def test_removed_overload():
    stable = {
        "azure.contoso": {
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
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "Test",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": "TestResult"
                                },
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "foo": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                    }
                }
            }
        }
    }

    current = {
        "azure.contoso": {
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
                            "is_async": True,
                            "overloads": [
                                {
                                    "parameters": {
                                        "testing": {
                                            "type": "JSON",
                                            "default": None,
                                            "param_type": "positional_or_keyword"
                                        }
                                    },
                                    "is_async": True,
                                    "return_type": None
                                }
                            ]
                        },
                        "two": {
                            "parameters": {
                                "testing2": {
                                    "default": None,
                                    "param_type": "positional_or_keyword"
                                }
                            },
                            "is_async": True,
                            "overloads": []
                        },
                    }
                }
            }
        }
    }

    EXPECTED = [
        "(RemovedMethodOverload): `class_name.one` had an overload `def one(testing: Test) -> TestResult` removed",
        "(RemovedMethodOverload): `class_name.two` had all overloads removed"
    ]

    bc = BreakingChangesTracker(stable, current, "azure-contoso", checkers=[RemovedMethodOverloadChecker()])
    bc.run_checks()

    changes = bc.report_changes()

    expected_msg = format_breaking_changes(EXPECTED)
    assert len(bc.breaking_changes) == len(EXPECTED)
    assert changes == expected_msg
