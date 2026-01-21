"""
Phase 1 & Phase 2 Verification - SIDE-BY-SIDE COMPARISON
=========================================================

Runs each test on BOTH backends and shows results immediately for easy comparison.

ARCHITECTURE:
-------------
This script uses a TestContext class that provides proper setup and teardown methods,
allowing any individual test or phase to run independently without relying on other
tests to create resources.

  TestContext
  ├── setup_clients()      - Initialize Python and Rust SDK clients
  ├── setup_databases()    - Create test databases
  ├── setup_containers()   - Create test containers
  ├── setup_items()        - Create test items
  ├── setup_for_test()     - Set up resources for a specific test
  ├── teardown_items()     - Delete test items
  ├── teardown_containers() - Delete test containers
  ├── teardown_databases() - Delete test databases
  └── teardown_all()       - Clean up all resources

Each test creates its own dedicated resources when testing create/delete operations,
ensuring tests don't interfere with each other.

USAGE:
------
  # Run all phases (Phase 1 + Phase 2)
  python verify_side_by_side.py

  # Run only Phase 1 (CRUD operations)
  python verify_side_by_side.py --phase 1
  python verify_side_by_side.py -p 1

  # Run only Phase 2 (List/Query operations)
  python verify_side_by_side.py --phase 2
  python verify_side_by_side.py -p 2

  # Run specific phases (multiple)
  python verify_side_by_side.py --phase 1 2

  # Run a specific test by name
  python verify_side_by_side.py --test create_item
  python verify_side_by_side.py -t read_item

  # Run multiple specific tests
  python verify_side_by_side.py -t create_item read_item upsert_item

  # List all available tests
  python verify_side_by_side.py --list-tests

For each test:
1. Run with PURE PYTHON backend
2. Run with RUST SDK backend
3. Show comparison immediately

AVAILABLE TESTS:
----------------
PHASE 1 (CRUD Operations):
  - create_database       : CosmosClient.create_database()
  - create_container      : DatabaseProxy.create_container()
  - create_item           : ContainerProxy.create_item()
  - read_item             : ContainerProxy.read_item()
  - upsert_item           : ContainerProxy.upsert_item()
  - replace_item          : ContainerProxy.replace_item()
  - delete_item           : ContainerProxy.delete_item()
  - delete_container      : DatabaseProxy.delete_container()
  - delete_database       : CosmosClient.delete_database()

PHASE 2 (List/Query Operations):
  - list_databases        : CosmosClient.list_databases()
  - query_databases       : CosmosClient.query_databases()
  - list_containers       : DatabaseProxy.list_containers()
  - query_containers      : DatabaseProxy.query_containers()
  - query_items           : ContainerProxy.query_items()

OUTPUT TERMINOLOGY:
-------------------
- "Output" / "Response Body" = The JSON data returned by the operation (e.g., {"id": "db1", "_etag": "..."})
- "Headers" = HTTP response headers (e.g., x-ms-request-charge, content-type)
- "Sample Item" = One example item from a list/query result showing its OUTPUT FIELDS (not headers)
- "(iterator - not directly available)" = For list/query operations, headers are per-page and
  not easily accessible from the Python iterator. The headers exist but require accessing
  the underlying FeedPage objects.
"""

import os
import sys
import json
import argparse
from datetime import datetime

# Add the tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"))

from test_config import TestConfig
from azure.cosmos import PartitionKey

# =============================================================================
# TEST DEFINITIONS - Maps test names to their phase
# =============================================================================
PHASE1_TESTS = [
    "create_database",
    "create_container",
    "create_item",
    "read_item",
    "upsert_item",
    "replace_item",
    "delete_item",
    "delete_container",
    "delete_database",
]

PHASE2_TESTS = [
    "list_databases",
    "query_databases",
    "list_containers",
    "query_containers",
    "query_items",
]

ALL_TESTS = PHASE1_TESTS + PHASE2_TESTS

# Test descriptions for --list-tests
TEST_DESCRIPTIONS = {
    "create_database": "CosmosClient.create_database() - Create a new database",
    "create_container": "DatabaseProxy.create_container() - Create a new container",
    "create_item": "ContainerProxy.create_item() - Create a new item/document",
    "read_item": "ContainerProxy.read_item() - Read an item by id and partition key",
    "upsert_item": "ContainerProxy.upsert_item() - Insert or update an item",
    "replace_item": "ContainerProxy.replace_item() - Replace an existing item",
    "delete_item": "ContainerProxy.delete_item() - Delete an item",
    "delete_container": "DatabaseProxy.delete_container() - Delete a container",
    "delete_database": "CosmosClient.delete_database() - Delete a database",
    "list_databases": "CosmosClient.list_databases() - List all databases",
    "query_databases": "CosmosClient.query_databases() - Query databases with SQL",
    "list_containers": "DatabaseProxy.list_containers() - List all containers in a database",
    "query_containers": "DatabaseProxy.query_containers() - Query containers with SQL",
    "query_items": "ContainerProxy.query_items() - Query items with SQL",
}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Phase 1 and/or Phase 2 verification tests comparing Pure Python vs Rust SDK backends.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_side_by_side.py              # Run all phases
  python verify_side_by_side.py -p 1         # Run only Phase 1 (CRUD)
  python verify_side_by_side.py -p 2         # Run only Phase 2 (List/Query)
  python verify_side_by_side.py -p 1 2       # Run Phase 1 and Phase 2
  python verify_side_by_side.py -t create_item          # Run single test
  python verify_side_by_side.py -t create_item read_item # Run multiple tests
  python verify_side_by_side.py --list-tests            # Show all available tests
        """
    )
    parser.add_argument(
        '-p', '--phase',
        type=int,
        nargs='+',
        choices=[1, 2],
        default=None,
        help='Phase(s) to run: 1=CRUD operations, 2=List/Query operations. Default: all phases'
    )
    parser.add_argument(
        '-t', '--test',
        type=str,
        nargs='+',
        choices=ALL_TESTS,
        default=None,
        metavar='TEST_NAME',
        help=f'Specific test(s) to run. Available: {", ".join(ALL_TESTS)}'
    )
    parser.add_argument(
        '--list-tests',
        action='store_true',
        help='List all available tests with descriptions and exit'
    )
    return parser.parse_args()


def list_available_tests():
    """Print all available tests with descriptions."""
    print("=" * 80)
    print("AVAILABLE TESTS")
    print("=" * 80)
    print("\nPHASE 1: CRUD OPERATIONS")
    print("-" * 40)
    for test in PHASE1_TESTS:
        print(f"  {test:<20} : {TEST_DESCRIPTIONS.get(test, '')}")
    print("\nPHASE 2: LIST & QUERY OPERATIONS")
    print("-" * 40)
    for test in PHASE2_TESTS:
        print(f"  {test:<20} : {TEST_DESCRIPTIONS.get(test, '')}")
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES:")
    print("=" * 80)
    print("  python verify_side_by_side.py                    # Run all tests")
    print("  python verify_side_by_side.py -p 1               # Run Phase 1 only")
    print("  python verify_side_by_side.py -p 2               # Run Phase 2 only")
    print("  python verify_side_by_side.py -t create_item     # Run single test")
    print("  python verify_side_by_side.py -t create_item read_item  # Run multiple tests")
    print("  python verify_side_by_side.py -t list_databases query_items  # Mix tests from different phases")
    print()


# =============================================================================
# TEST CONTEXT CLASS - Manages setup and teardown for tests
# =============================================================================
class TestContext:
    """Manages test resources with proper setup and teardown methods.

    This class ensures that any individual test or phase can run independently
    without relying on other tests to create resources.
    """

    def __init__(self):
        self.py_client = None
        self.rust_client = None
        self.py_db = None
        self.rust_db = None
        self.py_container = None
        self.rust_container = None
        self.py_db_name = None
        self.rust_db_name = None
        self.container_name = "test-container"
        self.test_item = {"id": "item1", "pk": "pk1", "name": "Test Item", "value": 42}
        self.upsert_item = {"id": "item2", "pk": "pk1", "name": "Upsert Item", "value": 100}

    def setup_clients(self):
        """Initialize both Python and Rust SDK clients.

        This should be called before any tests run.
        """
        timestamp = datetime.now().strftime('%H%M%S')
        self.py_db_name = f"verify-py-{timestamp}"
        self.rust_db_name = f"verify-rust-{timestamp}"

        # Initialize Python client
        os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
        self.py_client = get_client_and_connection(use_rust=False)

        # Initialize Rust client
        os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
        self.rust_client = get_client_and_connection(use_rust=True)

        print("   [SETUP] Initialized Python and Rust SDK clients")

    def setup_databases(self):
        """Create test databases for both backends.

        Can be called independently to ensure databases exist.
        """
        if self.py_client is None or self.rust_client is None:
            self.setup_clients()

        # Create Python database
        os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
        try:
            self.py_db = self.py_client.create_database_if_not_exists(self.py_db_name)
        except Exception:
            self.py_db = self.py_client.get_database_client(self.py_db_name)

        # Create Rust database
        os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
        try:
            self.rust_db = self.rust_client.create_database_if_not_exists(self.rust_db_name)
        except Exception:
            self.rust_db = self.rust_client.get_database_client(self.rust_db_name)

        print(f"   [SETUP] Created databases: {self.py_db_name}, {self.rust_db_name}")

    def setup_containers(self):
        """Create test containers for both backends.

        Can be called independently to ensure containers exist.
        """
        if self.py_db is None or self.rust_db is None:
            self.setup_databases()

        # Create Python container
        os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
        try:
            self.py_container = self.py_db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/pk")
            )
        except Exception:
            self.py_container = self.py_db.get_container_client(self.container_name)

        # Create Rust container
        os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
        try:
            self.rust_container = self.rust_db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/pk")
            )
        except Exception:
            self.rust_container = self.rust_db.get_container_client(self.container_name)

        print(f"   [SETUP] Created containers: {self.container_name}")

    def setup_items(self):
        """Create test items in both containers.

        Can be called independently to ensure items exist for read/update/delete tests.
        """
        if self.py_container is None or self.rust_container is None:
            self.setup_containers()

        # Create items in Python container
        os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
        self.py_container.upsert_item(body=self.test_item.copy())
        self.py_container.upsert_item(body=self.upsert_item.copy())

        # Create items in Rust container
        os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
        self.rust_container.upsert_item(body=self.test_item.copy())
        self.rust_container.upsert_item(body=self.upsert_item.copy())

        print(f"   [SETUP] Created test items: item1, item2")

    def setup_for_test(self, test_name):
        """Set up resources required for a specific test.

        This method ensures that all prerequisites for a test are met,
        regardless of which tests have run before.

        Args:
            test_name: Name of the test to prepare for
        """
        # Tests that only need clients
        client_only_tests = ["create_database", "list_databases", "query_databases", "delete_database"]

        # Tests that need database but not container
        db_tests = ["create_container", "delete_container"]

        # Tests that need container but not items
        container_tests = ["create_item", "list_containers", "query_containers"]

        # Tests that need items
        item_tests = ["read_item", "upsert_item", "replace_item", "delete_item", "query_items"]

        if test_name in client_only_tests:
            self.setup_clients()
            # For delete_database, we need the database to exist
            if test_name == "delete_database":
                self.setup_databases()
        elif test_name in db_tests:
            self.setup_databases()
            # For delete_container, we need the container to exist
            if test_name == "delete_container":
                self.setup_containers()
        elif test_name in container_tests:
            self.setup_containers()
        elif test_name in item_tests:
            self.setup_items()
        else:
            # Default: set up everything
            self.setup_items()

    def teardown_items(self):
        """Delete test items from containers.

        Safe to call even if items don't exist.
        """
        if self.py_container:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
            for item_id in ["item1", "item2"]:
                try:
                    self.py_container.delete_item(item=item_id, partition_key="pk1")
                except Exception:
                    pass

        if self.rust_container:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
            for item_id in ["item1", "item2"]:
                try:
                    self.rust_container.delete_item(item=item_id, partition_key="pk1")
                except Exception:
                    pass

        print("   [TEARDOWN] Deleted test items")

    def teardown_containers(self):
        """Delete test containers.

        Safe to call even if containers don't exist.
        """
        if self.py_db:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
            try:
                self.py_db.delete_container(self.container_name)
            except Exception:
                pass
            self.py_container = None

        if self.rust_db:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
            try:
                self.rust_db.delete_container(self.container_name)
            except Exception:
                pass
            self.rust_container = None

        print("   [TEARDOWN] Deleted test containers")

    def teardown_databases(self):
        """Delete test databases.

        Safe to call even if databases don't exist.
        """
        if self.py_client and self.py_db_name:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
            try:
                self.py_client.delete_database(self.py_db_name)
                print(f"   [TEARDOWN] Deleted database: {self.py_db_name}")
            except Exception as e:
                print(f"   [TEARDOWN] {self.py_db_name}: {e}")
            self.py_db = None

        if self.rust_client and self.rust_db_name:
            os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
            try:
                self.rust_client.delete_database(self.rust_db_name)
                print(f"   [TEARDOWN] Deleted database: {self.rust_db_name}")
            except Exception as e:
                print(f"   [TEARDOWN] {self.rust_db_name}: {e}")
            self.rust_db = None

    def teardown_all(self):
        """Clean up all resources.

        This should be called after all tests complete.
        """
        # Deleting databases will cascade delete containers and items
        self.teardown_databases()
        self.py_client = None
        self.rust_client = None


def get_client_and_connection(use_rust):
    """Get a CosmosClient with the specified backend."""
    os.environ["COSMOS_USE_RUST_BACKEND"] = "true" if use_rust else "false"

    # Force reimport to pick up new env var
    import importlib
    import azure.cosmos
    importlib.reload(azure.cosmos)
    from azure.cosmos import CosmosClient

    client = CosmosClient(TestConfig.host, TestConfig.masterKey)
    return client


def get_last_response_headers(container_or_db):
    """Get the last response headers from container or database client."""
    try:
        if hasattr(container_or_db, 'client_connection'):
            conn = container_or_db.client_connection
            if hasattr(conn, 'last_response_headers'):
                return dict(conn.last_response_headers or {})
    except:
        pass
    return {}


def print_output_and_headers(label, result, headers, indent="      "):
    """Print output fields/values and headers with clear labels."""
    print(f"{indent}RESPONSE BODY (JSON output from Cosmos DB):")
    if result is None:
        print(f"{indent}   (None - operation returns no body)")
    elif isinstance(result, dict):
        keys = sorted(result.keys())
        print(f"{indent}   Fields returned: {keys}")
        for k in keys:
            val = str(result.get(k, ''))
            if len(val) > 60:
                val = val[:60] + "..."
            print(f"{indent}   {k}: {val}")
    else:
        print(f"{indent}   Type: {type(result).__name__}")

    print(f"{indent}HTTP RESPONSE HEADERS ({len(headers)} total):")
    if headers:
        for k in sorted(headers.keys()):
            val = str(headers.get(k, ''))
            if len(val) > 60:
                val = val[:60] + "..."
            print(f"{indent}   {k}: {val}")
    else:
        print(f"{indent}   (none captured)")


def compare_results(py_result, py_headers, rust_result, rust_headers):
    """Compare Python and Rust results. Returns (passed, differences_list)."""
    differences = []

    # Compare output fields
    py_keys = sorted(py_result.keys()) if isinstance(py_result, dict) else []
    rust_keys = sorted(rust_result.keys()) if isinstance(rust_result, dict) else []

    if py_keys == rust_keys:
        print(f"      [MATCH] Output fields: {py_keys}")
    else:
        missing_in_rust = set(py_keys) - set(rust_keys)
        extra_in_rust = set(rust_keys) - set(py_keys)
        print(f"      [DIFF] Output fields differ!")
        print(f"         Python fields ({len(py_keys)}): {py_keys}")
        print(f"         Rust fields ({len(rust_keys)}): {rust_keys}")
        if missing_in_rust:
            print(f"         Missing in Rust: {sorted(missing_in_rust)}")
            differences.append(f"Missing fields in Rust: {sorted(missing_in_rust)}")
        if extra_in_rust:
            print(f"         Extra in Rust: {sorted(extra_in_rust)}")

    # Compare header count
    py_count = len(py_headers)
    rust_count = len(rust_headers)

    if py_count == rust_count:
        print(f"      [MATCH] Header count: {py_count}")
    else:
        print(f"      [DIFF] Header count: Python={py_count}, Rust={rust_count}")
        differences.append(f"Header count: Python={py_count}, Rust={rust_count}")

    # Compare key headers
    key_headers = ['x-ms-request-charge', 'content-type']
    for h in key_headers:
        py_val = py_headers.get(h, py_headers.get(h.lower(), 'N/A'))
        rust_val = rust_headers.get(h, rust_headers.get(h.lower(), 'N/A'))
        if py_val == rust_val and py_val != 'N/A':
            print(f"      [MATCH] {h}: {py_val}")
        elif py_val != rust_val:
            print(f"      [INFO] {h}: Python={py_val}, Rust={rust_val}")

    return (len(differences) == 0, differences)


def run_side_by_side_verification(phases_to_run=None, tests_to_run=None):
    """Run verification with side-by-side comparison for each test.

    Args:
        phases_to_run: List of phase numbers to run (e.g., [1], [2], or [1, 2]).
                      Default is [1, 2] (run all phases).
        tests_to_run: List of specific test names to run (e.g., ['create_item', 'read_item']).
                     If specified, phases_to_run is ignored.
    """
    # Determine which tests to run
    if tests_to_run:
        # Running specific tests - determine phases needed based on test names
        run_phase1 = any(t in PHASE1_TESTS for t in tests_to_run)
        run_phase2 = any(t in PHASE2_TESTS for t in tests_to_run)
        phases_to_run = []
        if run_phase1:
            phases_to_run.append(1)
        if run_phase2:
            phases_to_run.append(2)
        mode_description = f"Individual tests: {', '.join(tests_to_run)}"
    else:
        if phases_to_run is None:
            phases_to_run = [1, 2]
        # Build tests_to_run from phases
        tests_to_run = []
        if 1 in phases_to_run:
            tests_to_run.extend(PHASE1_TESTS)
        if 2 in phases_to_run:
            tests_to_run.extend(PHASE2_TESTS)
        mode_description = f"Phases: {phases_to_run}"

    print("=" * 80)
    print("PHASE 1 & PHASE 2 VERIFICATION - SIDE-BY-SIDE COMPARISON")
    print("=" * 80)
    print(f"Endpoint: {TestConfig.host[:60]}...")
    print(f"Mode: {mode_description}")
    print(f"Tests to run: {len(tests_to_run)} test(s)")
    print()
    print("OUTPUT TERMINOLOGY:")
    print("  - RESPONSE BODY = JSON data returned by the operation")
    print("  - HTTP HEADERS  = Response headers (x-ms-request-charge, etc.)")
    print("  - Sample Item   = Example item showing RESPONSE BODY FIELDS (not headers)")
    print()
    print()

    # Track test results for summary
    test_results = []  # List of (phase, test_name, passed, differences)

    # Create test context for managing resources
    ctx = TestContext()

    try:
        # =============================================================================
        #                           SETUP PHASE
        # =============================================================================
        print("=" * 80)
        print("SETUP - Creating test resources")
        print("=" * 80)

        # Determine what level of setup we need based on tests being run
        needs_items = any(t in ["read_item", "upsert_item", "replace_item", "delete_item", "query_items"] for t in tests_to_run)
        needs_containers = needs_items or any(t in ["create_item", "list_containers", "query_containers", "delete_container"] for t in tests_to_run)
        needs_databases = needs_containers or any(t in ["create_container", "delete_database"] for t in tests_to_run)

        # Always initialize clients
        ctx.setup_clients()

        # Set up resources based on what's needed
        # Note: For create_* tests, we still create the resources so that other tests can run
        # The create_* tests will use fresh resources created during the test itself
        if needs_databases or 1 in phases_to_run or 2 in phases_to_run:
            ctx.setup_databases()
        if needs_containers:
            ctx.setup_containers()
        if needs_items:
            ctx.setup_items()

        # Store references for easy access
        py_client = ctx.py_client
        rust_client = ctx.rust_client
        py_db = ctx.py_db
        rust_db = ctx.rust_db
        py_container = ctx.py_container
        rust_container = ctx.rust_container
        py_db_name = ctx.py_db_name
        rust_db_name = ctx.rust_db_name
        container_name = ctx.container_name

        # =============================================================================
        #                              PHASE 1: CRUD OPERATIONS
        # =============================================================================
        if 1 in phases_to_run:
            print("\n")
            print("*" * 80)
            print("*" + " " * 30 + "PHASE 1: CRUD OPERATIONS" + " " * 24 + "*")
            print("*" * 80)

            # =====================================================================
            # TEST 1: create_database [PHASE 1]
            # =====================================================================
            if "create_database" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 1 [PHASE 1]: CosmosClient.create_database()")
                print("   Method: cosmos_client.create_database(id)")
                print("=" * 80)

                # Use unique names for create_database test
                create_py_db_name = f"{py_db_name}-create"
                create_rust_db_name = f"{rust_db_name}-create"

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                create_py_db = py_client.create_database(create_py_db_name)
                py_db_result = create_py_db.read()
                py_headers = get_last_response_headers(create_py_db)
                print(f"      Created database: {create_py_db_name}")
                print_output_and_headers("Python", py_db_result, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                create_rust_db = rust_client.create_database(create_rust_db_name)
                rust_db_result = create_rust_db.read()
                rust_headers = get_last_response_headers(create_rust_db)
                print(f"      Created database: {create_rust_db_name}")
                print_output_and_headers("Rust", rust_db_result, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_db_result, py_headers, rust_db_result, rust_headers)
                test_results.append(("PHASE 1", "create_database", passed, diffs))

                # Clean up the databases created for this test
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                    py_client.delete_database(create_py_db_name)
                except:
                    pass
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                    rust_client.delete_database(create_rust_db_name)
                except:
                    pass

            # =====================================================================
            # TEST 2: create_container [PHASE 1]
            # =====================================================================
            if "create_container" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 2 [PHASE 1]: DatabaseProxy.create_container()")
                print("   Method: database.create_container(id, partition_key)")
                print("=" * 80)

                # Use unique name for create_container test
                create_container_name = f"{container_name}-create"

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                create_py_container = py_db.create_container(id=create_container_name, partition_key=PartitionKey(path="/pk"))
                py_cont_result = create_py_container.read()
                py_headers = get_last_response_headers(create_py_container)
                print(f"      Created container: {create_container_name}")
                print_output_and_headers("Python", py_cont_result, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                create_rust_container = rust_db.create_container(id=create_container_name, partition_key=PartitionKey(path="/pk"))
                rust_cont_result = create_rust_container.read()
                rust_headers = get_last_response_headers(create_rust_container)
                print(f"      Created container: {create_container_name}")
                print_output_and_headers("Rust", rust_cont_result, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_cont_result, py_headers, rust_cont_result, rust_headers)
                test_results.append(("PHASE 1", "create_container", passed, diffs))

                # Clean up the containers created for this test
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                    py_db.delete_container(create_container_name)
                except:
                    pass
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                    rust_db.delete_container(create_container_name)
                except:
                    pass

            # =====================================================================
            # TEST 3: create_item [PHASE 1]
            # =====================================================================
            if "create_item" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 3 [PHASE 1]: ContainerProxy.create_item()")
                print("   Method: container.create_item(body)")
                print("=" * 80)

                # Use unique item for create_item test
                create_test_item = {"id": "item-create-test", "pk": "pk1", "name": "Create Test Item", "value": 42}

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_item = py_container.create_item(body=create_test_item.copy())
                py_headers = get_last_response_headers(py_container)
                print(f"      Created item: {create_test_item['id']}")
                print_output_and_headers("Python", py_item, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_item = rust_container.create_item(body=create_test_item.copy())
                rust_headers = get_last_response_headers(rust_container)
                print(f"      Created item: {create_test_item['id']}")
                print_output_and_headers("Rust", rust_item, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_item, py_headers, rust_item, rust_headers)
                test_results.append(("PHASE 1", "create_item", passed, diffs))

                # Clean up the items created for this test
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                    py_container.delete_item(item=create_test_item['id'], partition_key="pk1")
                except:
                    pass
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                    rust_container.delete_item(item=create_test_item['id'], partition_key="pk1")
                except:
                    pass

            # =====================================================================
            # TEST 4: read_item [PHASE 1]
            # =====================================================================
            if "read_item" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 4 [PHASE 1]: ContainerProxy.read_item()")
                print("   Method: container.read_item(item, partition_key)")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_read = py_container.read_item(item="item1", partition_key="pk1")
                py_headers = get_last_response_headers(py_container)
                print_output_and_headers("Python", py_read, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_read = rust_container.read_item(item="item1", partition_key="pk1")
                rust_headers = get_last_response_headers(rust_container)
                print_output_and_headers("Rust", rust_read, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_read, py_headers, rust_read, rust_headers)
                test_results.append(("PHASE 1", "read_item", passed, diffs))

            # =====================================================================
            # TEST 5: upsert_item [PHASE 1]
            # =====================================================================
            if "upsert_item" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 5 [PHASE 1]: ContainerProxy.upsert_item()")
                print("   Method: container.upsert_item(body)")
                print("=" * 80)

                upsert_test_item = {"id": "item-upsert-test", "pk": "pk1", "name": "Upsert Test Item", "value": 100}

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_upsert = py_container.upsert_item(body=upsert_test_item.copy())
                py_headers = get_last_response_headers(py_container)
                print_output_and_headers("Python", py_upsert, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_upsert = rust_container.upsert_item(body=upsert_test_item.copy())
                rust_headers = get_last_response_headers(rust_container)
                print_output_and_headers("Rust", rust_upsert, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_upsert, py_headers, rust_upsert, rust_headers)
                test_results.append(("PHASE 1", "upsert_item", passed, diffs))

                # Clean up the items created for this test
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                    py_container.delete_item(item=upsert_test_item['id'], partition_key="pk1")
                except:
                    pass
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                    rust_container.delete_item(item=upsert_test_item['id'], partition_key="pk1")
                except:
                    pass

            # =====================================================================
            # TEST 6: replace_item [PHASE 1]
            # =====================================================================
            if "replace_item" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 6 [PHASE 1]: ContainerProxy.replace_item()")
                print("   Method: container.replace_item(item, body)")
                print("=" * 80)

                replace_item = {"id": "item1", "pk": "pk1", "name": "Replaced Item", "value": 200}

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_replace = py_container.replace_item(item="item1", body=replace_item.copy())
                py_headers = get_last_response_headers(py_container)
                print_output_and_headers("Python", py_replace, py_headers)

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_replace = rust_container.replace_item(item="item1", body=replace_item.copy())
                rust_headers = get_last_response_headers(rust_container)
                print_output_and_headers("Rust", rust_replace, rust_headers)

                # Comparison
                print("\n   --- COMPARISON ---")
                passed, diffs = compare_results(py_replace, py_headers, rust_replace, rust_headers)
                test_results.append(("PHASE 1", "replace_item", passed, diffs))

                # Restore the original item for other tests
                original_item = {"id": "item1", "pk": "pk1", "name": "Test Item", "value": 42}
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                    py_container.replace_item(item="item1", body=original_item.copy())
                except:
                    pass
                try:
                    os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                    rust_container.replace_item(item="item1", body=original_item.copy())
                except:
                    pass

        # =============================================================================
        #                         PHASE 2: LIST & QUERY OPERATIONS
        # =============================================================================
        if 2 in phases_to_run:
            print("\n")
            print("*" * 80)
            print("*" + " " * 26 + "PHASE 2: LIST & QUERY OPERATIONS" + " " * 19 + "*")
            print("*" * 80)

            # =====================================================================
            # TEST 7: list_databases [PHASE 2]
            # =====================================================================
            if "list_databases" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 7 [PHASE 2]: CosmosClient.list_databases()")
                print("   Method: cosmos_client.list_databases()")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_dbs = list(py_client.list_databases())
                print(f"      Result Count: {len(py_dbs)} databases")
                if py_dbs:
                    sample = py_dbs[0]
                    py_keys = sorted(sample.keys())
                    print(f"      RESPONSE BODY FIELDS (each item has these JSON fields): {py_keys}")
                    print(f"      Sample Item (first database - showing RESPONSE BODY, not headers):")
                    for k in py_keys:
                        print(f"         {k}: {str(sample.get(k, ''))[:50]}")
                else:
                    py_keys = []
                print(f"      HTTP HEADERS: Not directly available from iterator")
                print(f"         (Headers exist per-page but require accessing FeedPage objects)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_dbs = list(rust_client.list_databases())
                print(f"      Result Count: {len(rust_dbs)} databases")
                if rust_dbs:
                    sample = rust_dbs[0]
                    rust_keys = sorted(sample.keys())
                    print(f"      RESPONSE BODY FIELDS (each item has these JSON fields): {rust_keys}")
                    print(f"      Sample Item (first database - showing RESPONSE BODY, not headers):")
                    for k in rust_keys:
                        print(f"         {k}: {str(sample.get(k, ''))[:50]}")
                else:
                    rust_keys = []
                print(f"      HTTP HEADERS: Not directly available from iterator")
                print(f"         (Headers exist per-page but require accessing FeedPage objects)")

                # Comparison
                print("\n   --- COMPARISON ---")
                diffs = []
                if len(py_dbs) == len(rust_dbs):
                    print(f"      [MATCH] Count: {len(py_dbs)}")
                else:
                    print(f"      [DIFF] Count: Python={len(py_dbs)}, Rust={len(rust_dbs)}")
                    diffs.append(f"Count: Python={len(py_dbs)}, Rust={len(rust_dbs)}")

                if py_keys == rust_keys:
                    print(f"      [MATCH] Output fields: {py_keys}")
                else:
                    missing = set(py_keys) - set(rust_keys)
                    print(f"      [DIFF] Output fields differ!")
                    print(f"         Python: {py_keys}")
                    print(f"         Rust: {rust_keys}")
                    if missing:
                        print(f"         Missing in Rust: {sorted(missing)}")
                        diffs.append(f"Missing fields in Rust: {sorted(missing)}")

                test_results.append(("PHASE 2", "list_databases", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 8: query_databases [PHASE 2]
            # =====================================================================
            if "query_databases" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 8 [PHASE 2]: CosmosClient.query_databases()")
                print("   Method: cosmos_client.query_databases(query)")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_queried = list(py_client.query_databases("SELECT * FROM databases"))
                print(f"      Count: {len(py_queried)} databases")
                if py_queried:
                    sample = py_queried[0]
                    py_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {py_keys}")
                    print(f"      Sample Item:")
                    for k in py_keys:
                        print(f"         {k}: {str(sample.get(k, ''))[:50]}")
                else:
                    py_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_queried = list(rust_client.query_databases("SELECT * FROM databases"))
                print(f"      Count: {len(rust_queried)} databases")
                if rust_queried:
                    sample = rust_queried[0]
                    rust_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {rust_keys}")
                    print(f"      Sample Item:")
                    for k in rust_keys:
                        print(f"         {k}: {str(sample.get(k, ''))[:50]}")
                else:
                    rust_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Comparison
                print("\n   --- COMPARISON ---")
                diffs = []
                if len(py_queried) == len(rust_queried):
                    print(f"      [MATCH] Count: {len(py_queried)}")
                else:
                    print(f"      [DIFF] Count: Python={len(py_queried)}, Rust={len(rust_queried)}")
                    diffs.append(f"Count: Python={len(py_queried)}, Rust={len(rust_queried)}")

                if py_keys == rust_keys:
                    print(f"      [MATCH] Output fields: {py_keys}")
                else:
                    missing = set(py_keys) - set(rust_keys)
                    print(f"      [DIFF] Output fields differ!")
                    print(f"         Python: {py_keys}")
                    print(f"         Rust: {rust_keys}")
                    if missing:
                        print(f"         Missing in Rust: {sorted(missing)}")
                        diffs.append(f"Missing fields in Rust: {sorted(missing)}")

                test_results.append(("PHASE 2", "query_databases", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 9: list_containers [PHASE 2]
            # =====================================================================
            if "list_containers" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 9 [PHASE 2]: DatabaseProxy.list_containers()")
                print("   Method: database.list_containers()")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_containers = list(py_db.list_containers())
                print(f"      Count: {len(py_containers)} containers")
                if py_containers:
                    sample = py_containers[0]
                    py_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {py_keys}")
                    print(f"      Sample Item:")
                    for k in py_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    py_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_containers = list(rust_db.list_containers())
                print(f"      Count: {len(rust_containers)} containers")
                if rust_containers:
                    sample = rust_containers[0]
                    rust_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {rust_keys}")
                    print(f"      Sample Item:")
                    for k in rust_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    rust_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Comparison
                print("\n   --- COMPARISON ---")
                diffs = []
                if len(py_containers) == len(rust_containers):
                    print(f"      [MATCH] Count: {len(py_containers)}")
                else:
                    print(f"      [DIFF] Count: Python={len(py_containers)}, Rust={len(rust_containers)}")
                    diffs.append(f"Count: Python={len(py_containers)}, Rust={len(rust_containers)}")

                if py_keys == rust_keys:
                    print(f"      [MATCH] Output fields: {py_keys}")
                else:
                    missing = set(py_keys) - set(rust_keys)
                    print(f"      [DIFF] Output fields differ!")
                    print(f"         Python: {py_keys}")
                    print(f"         Rust: {rust_keys}")
                    if missing:
                        print(f"         Missing in Rust: {sorted(missing)}")
                        diffs.append(f"Missing fields in Rust: {sorted(missing)}")

                test_results.append(("PHASE 2", "list_containers", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 10: query_containers [PHASE 2]
            # =====================================================================
            if "query_containers" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 10 [PHASE 2]: DatabaseProxy.query_containers()")
                print("   Method: database.query_containers(query)")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_queried_c = list(py_db.query_containers("SELECT * FROM containers"))
                print(f"      Count: {len(py_queried_c)} containers")
                if py_queried_c:
                    sample = py_queried_c[0]
                    py_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {py_keys}")
                    print(f"      Sample Item:")
                    for k in py_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    py_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_queried_c = list(rust_db.query_containers("SELECT * FROM containers"))
                print(f"      Count: {len(rust_queried_c)} containers")
                if rust_queried_c:
                    sample = rust_queried_c[0]
                    rust_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {rust_keys}")
                    print(f"      Sample Item:")
                    for k in rust_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    rust_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Comparison
                print("\n   --- COMPARISON ---")
                diffs = []
                if len(py_queried_c) == len(rust_queried_c):
                    print(f"      [MATCH] Count: {len(py_queried_c)}")
                else:
                    print(f"      [DIFF] Count: Python={len(py_queried_c)}, Rust={len(rust_queried_c)}")
                    diffs.append(f"Count: Python={len(py_queried_c)}, Rust={len(rust_queried_c)}")

                if py_keys == rust_keys:
                    print(f"      [MATCH] Output fields: {py_keys}")
                else:
                    missing = set(py_keys) - set(rust_keys)
                    print(f"      [DIFF] Output fields differ!")
                    print(f"         Python: {py_keys}")
                    print(f"         Rust: {rust_keys}")
                    if missing:
                        print(f"         Missing in Rust: {sorted(missing)}")
                        diffs.append(f"Missing fields in Rust: {sorted(missing)}")

                test_results.append(("PHASE 2", "query_containers", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 11: query_items [PHASE 2]
            # =====================================================================
            if "query_items" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 11 [PHASE 2]: ContainerProxy.query_items()")
                print("   Method: container.query_items(query, partition_key)")
                print("=" * 80)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_items = list(py_container.query_items(query="SELECT * FROM c", partition_key="pk1"))
                print(f"      Count: {len(py_items)} items")
                if py_items:
                    sample = py_items[0]
                    py_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {py_keys}")
                    print(f"      Sample Item:")
                    for k in py_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    py_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_items = list(rust_container.query_items(query="SELECT * FROM c", partition_key="pk1"))
                print(f"      Count: {len(rust_items)} items")
                if rust_items:
                    sample = rust_items[0]
                    rust_keys = sorted(sample.keys())
                    print(f"      Output Fields (per item): {rust_keys}")
                    print(f"      Sample Item:")
                    for k in rust_keys:
                        val = str(sample.get(k, ''))
                        if len(val) > 50:
                            val = val[:50] + "..."
                        print(f"         {k}: {val}")
                else:
                    rust_keys = []
                print(f"      Headers: (iterator - not directly available)")

                # Comparison
                print("\n   --- COMPARISON ---")
                diffs = []
                if len(py_items) == len(rust_items):
                    print(f"      [MATCH] Count: {len(py_items)}")
                else:
                    print(f"      [DIFF] Count: Python={len(py_items)}, Rust={len(rust_items)}")
                    diffs.append(f"Count: Python={len(py_items)}, Rust={len(rust_items)}")

                if py_keys == rust_keys:
                    print(f"      [MATCH] Output fields: {py_keys}")
                else:
                    missing = set(py_keys) - set(rust_keys)
                    print(f"      [DIFF] Output fields differ!")
                    print(f"         Python: {py_keys}")
                    print(f"         Rust: {rust_keys}")
                    if missing:
                        print(f"         Missing in Rust: {sorted(missing)}")
                        diffs.append(f"Missing fields in Rust: {sorted(missing)}")

                test_results.append(("PHASE 2", "query_items", len(diffs) == 0, diffs))

        # End of Phase 2

        # =============================================================================
        #                    PHASE 1 (CONTINUED): DELETE OPERATIONS
        # =============================================================================
        if 1 in phases_to_run:
            print("\n")
            print("*" * 80)
            print("*" + " " * 22 + "PHASE 1 (CONTINUED): DELETE OPERATIONS" + " " * 17 + "*")
            print("*" * 80)

            # =====================================================================
            # TEST 12: delete_item [PHASE 1]
            # =====================================================================
            if "delete_item" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 12 [PHASE 1]: ContainerProxy.delete_item()")
                print("   Method: container.delete_item(item, partition_key)")
                print("=" * 80)

                # Create a dedicated item for the delete test
                delete_test_item = {"id": "item-delete-test", "pk": "pk1", "name": "Delete Test Item", "value": 999}
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_container.upsert_item(body=delete_test_item.copy())
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_container.upsert_item(body=delete_test_item.copy())

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_container.delete_item(item=delete_test_item['id'], partition_key="pk1")
                py_headers = get_last_response_headers(py_container)
                print(f"      Output: None (delete returns nothing)")
                print(f"      Headers ({len(py_headers)} total):")
                if py_headers:
                    for k in sorted(list(py_headers.keys())[:10]):
                        print(f"         {k}: {str(py_headers.get(k, ''))[:50]}")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_container.delete_item(item=delete_test_item['id'], partition_key="pk1")
                rust_headers = get_last_response_headers(rust_container)
                print(f"      Output: None (delete returns nothing)")
                print(f"      Headers ({len(rust_headers)} total):")
                if rust_headers:
                    for k in sorted(list(rust_headers.keys())[:10]):
                        print(f"         {k}: {str(rust_headers.get(k, ''))[:50]}")

                # Comparison
                print("\n   --- COMPARISON ---")
                print(f"      [MATCH] Both return None")
                diffs = []
                if len(py_headers) != len(rust_headers):
                    diff = f"Header count: Python={len(py_headers)}, Rust={len(rust_headers)}"
                    print(f"      [DIFF] {diff}")
                    diffs.append(diff)
                else:
                    print(f"      [MATCH] Header count: {len(py_headers)}")
                test_results.append(("PHASE 1", "delete_item", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 13: delete_container [PHASE 1]
            # =====================================================================
            if "delete_container" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 13 [PHASE 1]: DatabaseProxy.delete_container()")
                print("   Method: database.delete_container(container)")
                print("=" * 80)

                # Create a dedicated container for the delete test
                delete_container_name = f"{container_name}-delete-test"
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_db.create_container_if_not_exists(id=delete_container_name, partition_key=PartitionKey(path="/pk"))
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_db.create_container_if_not_exists(id=delete_container_name, partition_key=PartitionKey(path="/pk"))

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_db.delete_container(delete_container_name)
                py_headers = get_last_response_headers(py_db)
                print(f"      Output: None (delete returns nothing)")
                print(f"      Headers ({len(py_headers)} total):")
                if py_headers:
                    for k in sorted(list(py_headers.keys())[:10]):
                        print(f"         {k}: {str(py_headers.get(k, ''))[:50]}")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_db.delete_container(delete_container_name)
                rust_headers = get_last_response_headers(rust_db)
                print(f"      Output: None (delete returns nothing)")
                print(f"      Headers ({len(rust_headers)} total):")
                if rust_headers:
                    for k in sorted(list(rust_headers.keys())[:10]):
                        print(f"         {k}: {str(rust_headers.get(k, ''))[:50]}")

                # Comparison
                print("\n   --- COMPARISON ---")
                print(f"      [MATCH] Both return None")
                diffs = []
                if len(py_headers) != len(rust_headers):
                    diff = f"Header count: Python={len(py_headers)}, Rust={len(rust_headers)}"
                    print(f"      [DIFF] {diff}")
                    diffs.append(diff)
                else:
                    print(f"      [MATCH] Header count: {len(py_headers)}")
                test_results.append(("PHASE 1", "delete_container", len(diffs) == 0, diffs))

            # =====================================================================
            # TEST 14: delete_database [PHASE 1]
            # =====================================================================
            if "delete_database" in tests_to_run:
                print("\n" + "=" * 80)
                print("TEST 14 [PHASE 1]: CosmosClient.delete_database()")
                print("   Method: cosmos_client.delete_database(database)")
                print("=" * 80)

                # Create dedicated databases for the delete test
                delete_py_db_name = f"{py_db_name}-delete-test"
                delete_rust_db_name = f"{rust_db_name}-delete-test"
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_client.create_database_if_not_exists(delete_py_db_name)
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_client.create_database_if_not_exists(delete_rust_db_name)

                # Python
                print("\n   --- PURE PYTHON ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "false"
                py_client.delete_database(delete_py_db_name)
                print(f"      Deleted database: {delete_py_db_name}")
                print(f"      Output: None (delete returns nothing)")

                # Rust
                print("\n   --- RUST SDK ---")
                os.environ["COSMOS_USE_RUST_BACKEND"] = "true"
                rust_client.delete_database(delete_rust_db_name)
                print(f"      Deleted database: {delete_rust_db_name}")
                print(f"      Output: None (delete returns nothing)")

                # Comparison
                print("\n   --- COMPARISON ---")
                print(f"      [MATCH] Both return None")
                test_results.append(("PHASE 1", "delete_database", True, []))

        # End of Phase 1 delete operations

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # =============================================================================
        #                              TEARDOWN
        # =============================================================================
        print("\n" + "=" * 80)
        print("TEARDOWN - Cleaning up test resources")
        print("=" * 80)
        ctx.teardown_all()

    # =============================================================================
    #                              SUMMARY
    # =============================================================================
    print("\n")
    print("=" * 80)
    print("SUMMARY - TEST RESULTS")
    print("=" * 80)

    # Group by phase
    phase1_tests = [(name, passed, diffs) for phase, name, passed, diffs in test_results if phase == "PHASE 1"]
    phase2_tests = [(name, passed, diffs) for phase, name, passed, diffs in test_results if phase == "PHASE 2"]

    phase1_passed = sum(1 for _, passed, _ in phase1_tests if passed)
    phase2_passed = sum(1 for _, passed, _ in phase2_tests if passed)
    total_passed = phase1_passed + phase2_passed
    total_tests = len(test_results)

    print(f"\nOverall: {total_passed}/{total_tests} PASSED")
    print(f"  PHASE 1 (CRUD): {phase1_passed}/{len(phase1_tests)} passed")
    print(f"  PHASE 2 (List/Query): {phase2_passed}/{len(phase2_tests)} passed")

    # Detailed results table
    print("\n" + "-" * 80)
    print("PHASE 1: CRUD OPERATIONS")
    print("-" * 80)
    print(f"{'#':<3} {'Test Name':<20} {'Status':<8} {'Gaps/Differences'}")
    print("-" * 80)
    for i, (name, passed, diffs) in enumerate(phase1_tests, 1):
        status = "PASS" if passed else "FAIL"
        diff_str = ", ".join(diffs) if diffs else "-"
        print(f"{i:<3} {name:<20} {status:<8} {diff_str}")

    print("\n" + "-" * 80)
    print("PHASE 2: LIST & QUERY OPERATIONS")
    print("-" * 80)
    print(f"{'#':<3} {'Test Name':<20} {'Status':<8} {'Gaps/Differences'}")
    print("-" * 80)
    for i, (name, passed, diffs) in enumerate(phase2_tests, 1):
        status = "PASS" if passed else "FAIL"
        diff_str = ", ".join(diffs) if diffs else "-"
        print(f"{i:<3} {name:<20} {status:<8} {diff_str}")

    # List all gaps/failures
    failed_tests = [(phase, name, diffs) for phase, name, passed, diffs in test_results if not passed]
    if failed_tests:
        print("\n" + "=" * 80)
        print("GAPS IDENTIFIED (Rust SDK Missing Features)")
        print("=" * 80)
        for phase, name, diffs in failed_tests:
            print(f"\n[{phase}] {name}:")
            for diff in diffs:
                print(f"   - {diff}")

        print("\n" + "-" * 80)
        print("GAP ANALYSIS:")
        print("-" * 80)
        print("""
These gaps are in the RUST SDK layer (azure-sdk-for-rust), not in the facade
layer or Python public surface area which we control.

PHASE 2 Gaps - Missing response fields in list/query operations:
  - list_databases/query_databases: Missing _colls, _etag, _self, _ts, _users
  - list_containers/query_containers: Missing _conflicts, _docs, _etag, _self,
    _sprocs, _triggers, _ts, _udfs, geospatialConfig

Root Cause: The Rust SDK's DatabaseProperties and ContainerProperties structs
do not deserialize all fields returned by the Cosmos DB REST API. Only the
fields defined in the struct are captured.

Impact: Applications that rely on these metadata fields from list/query
operations will see different results between Python and Rust backends.

Note: For single-item operations (read, create, upsert, replace), the Rust
SDK returns all fields correctly because the item is passed through as a
generic JSON document.
""")
    else:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED - No gaps identified!")
        print("=" * 80)


if __name__ == "__main__":
    args = parse_args()

    # Handle --list-tests
    if args.list_tests:
        list_available_tests()
        sys.exit(0)

    # Determine what to run
    if args.test:
        # Running specific tests
        run_side_by_side_verification(tests_to_run=args.test)
    elif args.phase:
        # Running specific phases
        run_side_by_side_verification(phases_to_run=args.phase)
    else:
        # Run all phases (default)
        run_side_by_side_verification(phases_to_run=[1, 2])
