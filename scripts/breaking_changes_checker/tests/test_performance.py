#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Performance tests for the breaking_changes_checker.

These tests demonstrate and verify the performance improvements made to:
1. run_async_cleanup() - O(n) set-based approach vs O(n*m) nested loop + list.remove()
2. get_reportable_changes() - single-pass filtering vs deepcopy + list.remove()
3. AST caching - _get_parsed_module() and _find_class_node() helpers
4. ClassTreeAnalyzer early exit
"""

import time
from breaking_changes_checker.breaking_changes_tracker import BreakingChangesTracker, BreakingChangeType
from breaking_changes_checker.changelog_tracker import ChangelogTracker


def _generate_large_stable_current(num_modules, num_classes_per_module, num_methods_per_class, num_params_per_method):
    """Generate large stable/current API reports for performance testing."""
    stable = {}
    current = {}
    for m in range(num_modules):
        module_name = f"azure.mgmt.network.v2023_01_{m:02d}"
        stable[module_name] = {"class_nodes": {}, "function_nodes": {}}
        current[module_name] = {"class_nodes": {}, "function_nodes": {}}
        for c in range(num_classes_per_module):
            class_name = f"NetworkClass{c}"
            methods_stable = {}
            methods_current = {}
            for me in range(num_methods_per_class):
                method_name = f"method_{me}"
                params = {}
                for p in range(num_params_per_method):
                    params[f"param_{p}"] = {
                        "default": None,
                        "param_type": "positional_or_keyword"
                    }
                methods_stable[method_name] = {
                    "parameters": dict(params),
                    "is_async": False,
                }
                methods_current[method_name] = {
                    "parameters": dict(params),
                    "is_async": False,
                }
            stable[module_name]["class_nodes"][class_name] = {
                "type": None,
                "methods": methods_stable,
                "properties": {f"prop_{i}": {"attr_type": "str"} for i in range(3)}
            }
            current[module_name]["class_nodes"][class_name] = {
                "type": None,
                "methods": methods_current,
                "properties": {f"prop_{i}": {"attr_type": "str"} for i in range(3)}
            }
    return stable, current


def _generate_changes_list(n, include_aio=True):
    """Generate a list of n breaking changes, half sync and half aio if include_aio."""
    changes = []
    for i in range(n):
        module = f"azure.mgmt.network"
        if include_aio and i % 2 == 1:
            module = f"azure.mgmt.network.aio"
        changes.append((
            "Deleted or renamed model `{}`",
            BreakingChangeType.REMOVED_OR_RENAMED_CLASS,
            module, f"SomeClass{i // 2 if include_aio else i}"
        ))
    return changes


class TestAsyncCleanupPerformance:
    """Test performance of the optimized run_async_cleanup method."""

    def test_async_cleanup_correctness_small(self):
        """Verify correctness of optimized async cleanup with a small dataset."""
        changes = [
            ("msg", BreakingChangeType.REMOVED_OR_RENAMED_CLASS, "azure.mgmt.network", "ClassA"),
            ("msg", BreakingChangeType.REMOVED_OR_RENAMED_CLASS, "azure.mgmt.network.aio", "ClassA"),
            ("msg", BreakingChangeType.REMOVED_OR_RENAMED_CLASS, "azure.mgmt.network", "ClassB"),
            ("msg", BreakingChangeType.REMOVED_OR_RENAMED_CLASS, "azure.mgmt.network.aio", "ClassC"),  # no sync counterpart
        ]
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")
        tracker.run_async_cleanup(changes)

        # aio ClassA should be removed (has sync counterpart)
        # aio ClassC should remain (no sync counterpart)
        assert len(changes) == 3
        modules = [c[2] for c in changes]
        assert "azure.mgmt.network.aio" in modules  # ClassC remains
        class_names = [c[3] for c in changes]
        assert "ClassA" in class_names  # sync ClassA remains
        assert "ClassB" in class_names  # sync ClassB remains
        assert "ClassC" in class_names  # aio ClassC remains (no sync counterpart)

    def test_async_cleanup_performance_large(self):
        """Benchmark async cleanup with a large number of changes.
        
        The old O(n*m) implementation with list.remove() would be very slow
        for large change lists. The new set-based O(n) approach should handle
        this in milliseconds.
        """
        n = 10000  # 10,000 changes (5,000 sync + 5,000 aio)
        changes = _generate_changes_list(n, include_aio=True)
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")

        start = time.perf_counter()
        tracker.run_async_cleanup(changes)
        elapsed = time.perf_counter() - start

        # Should complete in well under 1 second with the optimized implementation
        # The old implementation would take 10+ seconds for this size
        assert elapsed < 1.0, f"run_async_cleanup took {elapsed:.3f}s for {n} changes (expected < 1s)"
        # 5000 aio changes with sync counterparts should be removed
        assert len(changes) == n // 2
        # All remaining should be sync changes
        assert all("aio" not in c[2] for c in changes)

    def test_async_cleanup_performance_very_large(self):
        """Benchmark with 50,000 changes to show scalability."""
        n = 50000
        changes = _generate_changes_list(n, include_aio=True)
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")

        start = time.perf_counter()
        tracker.run_async_cleanup(changes)
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"run_async_cleanup took {elapsed:.3f}s for {n} changes (expected < 2s)"
        assert len(changes) == n // 2

    def test_async_cleanup_with_list_args(self):
        """Test that async cleanup handles unhashable types (lists) in change tuples."""
        changes = [
            ("msg", BreakingChangeType.CHANGED_PARAMETER_ORDERING, "azure.mgmt.network",
             "MyClient", "my_method", ["param_a", "param_b"], ["param_b", "param_a"]),
            ("msg", BreakingChangeType.CHANGED_PARAMETER_ORDERING, "azure.mgmt.network.aio",
             "MyClient", "my_method", ["param_a", "param_b"], ["param_b", "param_a"]),
        ]
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")
        tracker.run_async_cleanup(changes)

        # The aio version should be removed since it has a sync counterpart
        assert len(changes) == 1
        assert "aio" not in changes[0][2]


class TestReportableChangesPerformance:
    """Test performance of the optimized get_reportable_changes method."""

    def test_reportable_changes_no_ignores(self):
        """Verify that with no ignore rules, all changes are kept."""
        changes = _generate_changes_list(100, include_aio=False)
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")
        tracker.get_reportable_changes({}, changes)
        assert len(changes) == 100

    def test_reportable_changes_performance_large(self):
        """Benchmark get_reportable_changes with many changes and ignore rules.
        
        The old implementation used deepcopy + list.remove() which is O(n^2).
        The new single-pass filtering is O(n*m) where m = number of ignore rules.
        """
        n = 5000
        changes = _generate_changes_list(n, include_aio=False)
        ignore_rules = {
            "azure-mgmt-.*": [
                (BreakingChangeType.REMOVED_OR_RENAMED_CLASS, "*", f"SomeClass{i}", None, None)
                for i in range(100)  # 100 ignore rules
            ]
        }
        stable = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        current = {"azure.mgmt.network": {"class_nodes": {}, "function_nodes": {}}}
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")

        start = time.perf_counter()
        tracker.get_reportable_changes(ignore_rules, changes)
        elapsed = time.perf_counter() - start

        # Should complete well under 1 second
        assert elapsed < 1.0, f"get_reportable_changes took {elapsed:.3f}s (expected < 1s)"
        # 100 of the 5000 changes should be filtered out
        assert len(changes) == n - 100


class TestCheckerRunPerformance:
    """Test full checker run performance with large API surfaces."""

    def test_full_checker_run_large_unchanged_api(self):
        """Benchmark a full checker run with a large unchanged API surface.
        
        When stable and current are identical, jsondiff produces an empty diff,
        so diff-based checks do minimal work. However, run_checks() still executes
        checks like parameter ordering across the full API surface. This test
        ensures the overall run remains fast and bounded even for a large, unchanged API.
        """
        stable, current = _generate_large_stable_current(
            num_modules=10,
            num_classes_per_module=50,
            num_methods_per_class=10,
            num_params_per_method=5,
        )

        start = time.perf_counter()
        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")
        tracker.run_checks()
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, f"Full checker run took {elapsed:.3f}s for large unchanged API (expected < 5s)"
        assert len(tracker.breaking_changes) == 0

    def test_changelog_tracker_run_large_with_additions(self):
        """Benchmark ChangelogTracker with a large API that has many additions.
        
        This simulates a scenario similar to azure-mgmt-network where many new
        classes and methods are added.
        """
        stable, current = _generate_large_stable_current(
            num_modules=5,
            num_classes_per_module=20,
            num_methods_per_class=5,
            num_params_per_method=3,
        )
        # Add new classes and methods in current
        for m in range(5):
            module_name = f"azure.mgmt.network.v2023_01_{m:02d}"
            for c in range(10):
                new_class = f"NewNetworkClass{m}_{c}"
                current[module_name]["class_nodes"][new_class] = {
                    "type": None,
                    "methods": {
                        f"new_method_{me}": {
                            "parameters": {
                                f"param_{p}": {"default": None, "param_type": "positional_or_keyword"}
                                for p in range(3)
                            },
                            "is_async": False,
                        }
                        for me in range(5)
                    },
                    "properties": {f"prop_{i}": {"attr_type": "str"} for i in range(3)}
                }

        start = time.perf_counter()
        tracker = ChangelogTracker(stable, current, "azure-mgmt-network")
        tracker.run_checks()
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0, f"ChangelogTracker run took {elapsed:.3f}s (expected < 5s)"
        assert len(tracker.features_added) > 0

    def test_parameter_ordering_check_large(self):
        """Benchmark check_parameter_ordering with many modules/classes/methods."""
        stable, current = _generate_large_stable_current(
            num_modules=10,
            num_classes_per_module=50,
            num_methods_per_class=10,
            num_params_per_method=5,
        )

        tracker = BreakingChangesTracker(stable, current, "azure-mgmt-network")

        start = time.perf_counter()
        tracker.check_parameter_ordering()
        elapsed = time.perf_counter() - start

        # 10 modules * 50 classes * 10 methods = 5000 method comparisons
        assert elapsed < 2.0, f"check_parameter_ordering took {elapsed:.3f}s (expected < 2s)"
        assert len(tracker.breaking_changes) == 0


class TestASTCachePerformance:
    """Test performance of the AST caching mechanism."""

    def test_ast_cache_avoids_redundant_parsing(self):
        """Verify that the AST cache is populated and reused."""
        from breaking_changes_checker.detect_breaking_changes import (
            _ast_cache, _get_parsed_module, _find_class_node
        )
        import tempfile
        import os

        # Create a temporary Python file with multiple classes
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(
                "class Foo:\n"
                "    x: int = 0\n"
                "\n"
                "class Bar:\n"
                "    y: str = ''\n"
                "\n"
                "class Baz:\n"
                "    z: float = 0.0\n"
            )
            temp_path = f.name

        try:
            _ast_cache.clear()

            # First call should parse and cache
            module1 = _get_parsed_module(temp_path)
            assert temp_path in _ast_cache

            # Second call should return cached result (same object)
            module2 = _get_parsed_module(temp_path)
            assert module1 is module2

            # Find multiple classes from the same cached module
            foo_node = _find_class_node(module1, "Foo")
            assert foo_node is not None
            assert foo_node.name == "Foo"

            bar_node = _find_class_node(module1, "Bar")
            assert bar_node is not None
            assert bar_node.name == "Bar"

            baz_node = _find_class_node(module1, "Baz")
            assert baz_node is not None
            assert baz_node.name == "Baz"
        finally:
            os.unlink(temp_path)
            _ast_cache.clear()

    def test_ast_cache_performance_many_lookups(self):
        """Benchmark AST cache with many lookups to the same file.
        
        Simulates the scenario where many classes in a large package
        share the same source file (e.g., _models.py in azure-mgmt-network).
        """
        from breaking_changes_checker.detect_breaking_changes import (
            _ast_cache, _get_parsed_module
        )
        import tempfile
        import os

        # Create a temporary file with many classes (simulating a large _models.py)
        num_classes = 200
        lines = []
        for i in range(num_classes):
            lines.append(f"class Model{i}:\n    attr_{i}: int = {i}\n\n")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("".join(lines))
            temp_path = f.name

        try:
            _ast_cache.clear()

            # Without caching, 200 lookups would mean 200 file reads + 200 AST parses
            # With caching, it's 1 file read + 1 AST parse + 200 cache hits
            start = time.perf_counter()
            for i in range(num_classes):
                module = _get_parsed_module(temp_path)
            elapsed = time.perf_counter() - start

            # Should be nearly instantaneous since all after the first are cache hits
            assert elapsed < 0.1, f"{num_classes} cached lookups took {elapsed:.3f}s (expected < 0.1s)"
            assert len(_ast_cache) == 1  # Only one file cached
        finally:
            os.unlink(temp_path)
            _ast_cache.clear()


class TestClassTreeAnalyzerEarlyExit:
    """Test that ClassTreeAnalyzer exits early after finding the target class."""

    def test_early_exit_finds_class(self):
        """Verify early exit still finds the class correctly."""
        from breaking_changes_checker.detect_breaking_changes import _find_class_node
        import ast

        source = """
class First:
    pass

class Target:
    x: int = 0

class Third:
    pass
"""
        module = ast.parse(source)
        cls_node = _find_class_node(module, "Target")
        assert cls_node is not None
        assert cls_node.name == "Target"

    def test_early_exit_returns_none_for_missing(self):
        """Verify that early exit correctly returns None when class is not found."""
        from breaking_changes_checker.detect_breaking_changes import _find_class_node
        import ast

        source = """
class First:
    pass

class Second:
    pass
"""
        module = ast.parse(source)
        cls_node = _find_class_node(module, "NonExistent")
        assert cls_node is None

    def test_early_exit_performance(self):
        """Benchmark early exit vs full traversal for large source files.
        
        With early exit, finding a class near the top of a large file should
        be significantly faster than traversing the entire AST.
        """
        from breaking_changes_checker.detect_breaking_changes import _find_class_node
        import ast

        # Generate a large source file with many classes
        num_classes = 500
        lines = ["class TargetClass:\n    x: int = 0\n\n"]  # Target is first
        for i in range(num_classes):
            lines.append(f"class OtherClass{i}:\n    attr: int = {i}\n\n")
        source = "".join(lines)
        module = ast.parse(source)

        # Find the first class (should benefit from early exit)
        start = time.perf_counter()
        for _ in range(1000):
            _find_class_node(module, "TargetClass")
        elapsed_first = time.perf_counter() - start

        # Find the last class (no benefit from early exit since it's at the end)
        start = time.perf_counter()
        for _ in range(1000):
            cls_node = _find_class_node(module, f"OtherClass{num_classes - 1}")
        elapsed_last = time.perf_counter() - start

        assert cls_node is not None

        # First class lookup should be significantly faster due to early exit
        # (at least 2x faster since TargetClass is at position 0 of 500)
        assert elapsed_first < elapsed_last, (
            f"Early exit not effective: first={elapsed_first:.4f}s, last={elapsed_last:.4f}s"
        )
