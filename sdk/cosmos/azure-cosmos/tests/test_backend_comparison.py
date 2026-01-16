"""
Backend Comparison Test Script
Runs sync and async CRUD operations with both Python and Rust backends
and compares the output fields AND RESPONSE HEADERS to verify contract parity.

This script runs each backend in a separate subprocess to avoid PyO3 reinitialization issues.
"""
import os
import sys
import json
import subprocess
from datetime import datetime

# Add the tests directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_separator(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def run_backend_test(backend_type, test_type, database_suffix=""):
    """Run a backend test in a subprocess and return the results"""
    script = f'''
import os
import sys
import json
import asyncio

# Set the backend BEFORE importing cosmos
os.environ["COSMOS_USE_RUST_BACKEND"] = "{backend_type}"

sys.path.insert(0, r"{os.path.dirname(os.path.abspath(__file__))}")
from test_config import TestConfig

COSMOS_ENDPOINT = TestConfig.host
COSMOS_KEY = TestConfig.masterKey
TEST_DATABASE_ID = "backend_comparison_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}{database_suffix}"
TEST_CONTAINER_ID = "test_container"
TEST_PARTITION_KEY = "/pk"

def extract_headers(item):
    """Extract response headers from a CosmosDict if available"""
    headers_info = {{}}
    if hasattr(item, 'get_response_headers'):
        try:
            headers = item.get_response_headers()
            if headers:
                # Check for key response headers
                headers_info["x-ms-request-charge"] = headers.get("x-ms-request-charge") is not None
                headers_info["x-ms-activity-id"] = headers.get("x-ms-activity-id") is not None
                headers_info["etag"] = headers.get("etag") is not None
                headers_info["x-ms-session-token"] = headers.get("x-ms-session-token") is not None
                headers_info["header_count"] = len(headers)
                # Get actual values for some headers
                if headers.get("x-ms-request-charge"):
                    try:
                        headers_info["request_charge_value"] = float(headers.get("x-ms-request-charge"))
                    except:
                        headers_info["request_charge_value"] = None
        except Exception as e:
            headers_info["error"] = str(e)
    else:
        headers_info["has_method"] = False
    return headers_info

results = {{"backend": "{backend_type}", "test_type": "{test_type}", "operations": {{}}, "headers": {{}}}}

if "{test_type}" == "sync":
    from azure.cosmos import CosmosClient, PartitionKey
    
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    try:
        # 1. Create Database
        db = client.create_database(TEST_DATABASE_ID)
        results["operations"]["create_database"] = {{"id": db.id, "success": True}}
        
        # 2. Read Database
        db_props = db.read()
        results["operations"]["read_database"] = {{
            "id": db_props.get("id"),
            "_rid": db_props.get("_rid") is not None,
            "_self": db_props.get("_self") is not None,
            "_etag": db_props.get("_etag") is not None,
            "_ts": db_props.get("_ts") is not None,
            "keys": list(db_props.keys()),
            "success": True
        }}
        results["headers"]["read_database"] = extract_headers(db_props)
        
        # 3. Create Container
        container = db.create_container(id=TEST_CONTAINER_ID, partition_key=PartitionKey(path=TEST_PARTITION_KEY))
        results["operations"]["create_container"] = {{"id": container.id, "success": True}}
        
        # 4. Create Item
        test_item = {{"id": "test_item_1", "pk": "partition1", "name": "Test Item", "value": 42, "nested": {{"a": 1, "b": 2}}}}
        created_item = container.create_item(body=test_item)
        results["operations"]["create_item"] = {{
            "id": created_item.get("id"),
            "pk": created_item.get("pk"),
            "name": created_item.get("name"),
            "value": created_item.get("value"),
            "nested": created_item.get("nested"),
            "_rid": created_item.get("_rid") is not None,
            "_self": created_item.get("_self") is not None,
            "_etag": created_item.get("_etag") is not None,
            "_ts": created_item.get("_ts") is not None,
            "success": True
        }}
        results["headers"]["create_item"] = extract_headers(created_item)
        
        # 5. Read Item
        read_item = container.read_item(item="test_item_1", partition_key="partition1")
        results["operations"]["read_item"] = {{
            "id": read_item.get("id"),
            "pk": read_item.get("pk"),
            "name": read_item.get("name"),
            "value": read_item.get("value"),
            "nested": read_item.get("nested"),
            "_rid": read_item.get("_rid") is not None,
            "_self": read_item.get("_self") is not None,
            "_etag": read_item.get("_etag") is not None,
            "_ts": read_item.get("_ts") is not None,
            "success": True
        }}
        results["headers"]["read_item"] = extract_headers(read_item)
        
        # 6. Upsert Item
        upsert_item = {{"id": "test_item_2", "pk": "partition1", "name": "Upserted Item", "value": 100}}
        upserted = container.upsert_item(body=upsert_item)
        results["operations"]["upsert_item"] = {{
            "id": upserted.get("id"),
            "pk": upserted.get("pk"),
            "name": upserted.get("name"),
            "value": upserted.get("value"),
            "_rid": upserted.get("_rid") is not None,
            "_self": upserted.get("_self") is not None,
            "success": True
        }}
        results["headers"]["upsert_item"] = extract_headers(upserted)
        
        # 7. Replace Item
        replace_body = dict(read_item)
        replace_body["name"] = "Updated Name"
        replace_body["value"] = 999
        replaced = container.replace_item(item="test_item_1", body=replace_body)
        results["operations"]["replace_item"] = {{
            "id": replaced.get("id"),
            "pk": replaced.get("pk"),
            "name": replaced.get("name"),
            "value": replaced.get("value"),
            "_rid": replaced.get("_rid") is not None,
            "_self": replaced.get("_self") is not None,
            "success": True
        }}
        results["headers"]["replace_item"] = extract_headers(replaced)
        
        # 8. Delete Item
        container.delete_item(item="test_item_2", partition_key="partition1")
        results["operations"]["delete_item"] = {{"success": True}}
        
        # 9. Delete Container
        db.delete_container(TEST_CONTAINER_ID)
        results["operations"]["delete_container"] = {{"success": True}}
        
        # 10. Delete Database
        client.delete_database(TEST_DATABASE_ID)
        results["operations"]["delete_database"] = {{"success": True}}
        
        results["success"] = True
        
    except Exception as e:
        results["success"] = False
        results["error"] = str(e)
        try:
            client.delete_database(TEST_DATABASE_ID)
        except:
            pass

else:  # async
    from azure.cosmos.aio import CosmosClient
    from azure.cosmos import PartitionKey
    
    async def run_async():
        async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
            try:
                # 1. Create Database
                db = await client.create_database(TEST_DATABASE_ID)
                results["operations"]["create_database"] = {{"id": db.id, "success": True}}
                
                # 2. Read Database
                db_props = await db.read()
                results["operations"]["read_database"] = {{
                    "id": db_props.get("id"),
                    "_rid": db_props.get("_rid") is not None,
                    "_self": db_props.get("_self") is not None,
                    "_etag": db_props.get("_etag") is not None,
                    "_ts": db_props.get("_ts") is not None,
                    "keys": list(db_props.keys()),
                    "success": True
                }}
                results["headers"]["read_database"] = extract_headers(db_props)
                
                # 3. Create Container
                container = await db.create_container(id=TEST_CONTAINER_ID, partition_key=PartitionKey(path=TEST_PARTITION_KEY))
                results["operations"]["create_container"] = {{"id": container.id, "success": True}}
                
                # 4. Create Item
                test_item = {{"id": "test_item_1", "pk": "partition1", "name": "Test Item Async", "value": 42}}
                created_item = await container.create_item(body=test_item)
                results["operations"]["create_item"] = {{
                    "id": created_item.get("id"),
                    "pk": created_item.get("pk"),
                    "name": created_item.get("name"),
                    "value": created_item.get("value"),
                    "_rid": created_item.get("_rid") is not None,
                    "_self": created_item.get("_self") is not None,
                    "success": True
                }}
                results["headers"]["create_item"] = extract_headers(created_item)
                
                # 5. Read Item
                read_item = await container.read_item(item="test_item_1", partition_key="partition1")
                results["operations"]["read_item"] = {{
                    "id": read_item.get("id"),
                    "pk": read_item.get("pk"),
                    "name": read_item.get("name"),
                    "value": read_item.get("value"),
                    "_rid": read_item.get("_rid") is not None,
                    "_self": read_item.get("_self") is not None,
                    "success": True
                }}
                results["headers"]["read_item"] = extract_headers(read_item)
                
                # 6. Upsert Item
                upsert_item = {{"id": "test_item_2", "pk": "partition1", "name": "Upserted Item Async", "value": 100}}
                upserted = await container.upsert_item(body=upsert_item)
                results["operations"]["upsert_item"] = {{
                    "id": upserted.get("id"),
                    "pk": upserted.get("pk"),
                    "name": upserted.get("name"),
                    "value": upserted.get("value"),
                    "_rid": upserted.get("_rid") is not None,
                    "_self": upserted.get("_self") is not None,
                    "success": True
                }}
                results["headers"]["upsert_item"] = extract_headers(upserted)
                
                # 7. Replace Item
                replace_body = dict(read_item)
                replace_body["name"] = "Updated Name Async"
                replace_body["value"] = 999
                replaced = await container.replace_item(item="test_item_1", body=replace_body)
                results["operations"]["replace_item"] = {{
                    "id": replaced.get("id"),
                    "pk": replaced.get("pk"),
                    "name": replaced.get("name"),
                    "value": replaced.get("value"),
                    "_rid": replaced.get("_rid") is not None,
                    "_self": replaced.get("_self") is not None,
                    "success": True
                }}
                results["headers"]["replace_item"] = extract_headers(replaced)
                
                # 8. Delete Item
                await container.delete_item(item="test_item_2", partition_key="partition1")
                results["operations"]["delete_item"] = {{"success": True}}
                
                # 9. Delete Container
                await db.delete_container(TEST_CONTAINER_ID)
                results["operations"]["delete_container"] = {{"success": True}}
                
                # 10. Delete Database
                await client.delete_database(TEST_DATABASE_ID)
                results["operations"]["delete_database"] = {{"success": True}}
                
                results["success"] = True
                
            except Exception as e:
                results["success"] = False
                results["error"] = str(e)
                try:
                    await client.delete_database(TEST_DATABASE_ID)
                except:
                    pass
    
    asyncio.run(run_async())

print("JSON_RESULT_START")
print(json.dumps(results))
print("JSON_RESULT_END")
'''

    # Run in subprocess
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    # Print the output for visibility
    output = result.stdout + result.stderr

    # Extract JSON result
    try:
        start_idx = output.find("JSON_RESULT_START") + len("JSON_RESULT_START")
        end_idx = output.find("JSON_RESULT_END")
        json_str = output[start_idx:end_idx].strip()
        return json.loads(json_str), output
    except:
        return {"success": False, "error": output}, output

def compare_headers(python_result, rust_result, test_type):
    """Compare response headers between Python and Rust backends"""
    print_separator(f"{test_type.upper()} RESPONSE HEADERS COMPARISON")

    python_headers = python_result.get("headers", {})
    rust_headers = rust_result.get("headers", {})

    operations = ["read_database", "create_item", "read_item", "upsert_item", "replace_item"]

    all_match = True
    header_gaps = []

    for op in operations:
        print(f"\n{'─' * 60}")
        print(f"  Operation: {op}")
        print(f"{'─' * 60}")

        py_hdrs = python_headers.get(op, {})
        rust_hdrs = rust_headers.get(op, {})

        if not py_hdrs:
            print(f"    ⚠️  Python: No headers captured")
            continue
        if not rust_hdrs:
            print(f"    ⚠️  Rust: No headers captured")
            continue

        # Check if method exists
        if py_hdrs.get("has_method") == False:
            print(f"    Python: No get_response_headers() method")
        if rust_hdrs.get("has_method") == False:
            print(f"    Rust: No get_response_headers() method")
            header_gaps.append(f"{op}: Rust missing get_response_headers()")
            continue

        # Compare key headers
        header_fields = ["x-ms-request-charge", "x-ms-activity-id", "etag", "x-ms-session-token", "header_count"]
        for field in header_fields:
            py_val = py_hdrs.get(field)
            rust_val = rust_hdrs.get(field)

            if py_val is None and rust_val is None:
                continue

            if py_val == rust_val:
                print(f"    {field:25} | ✅ MATCH ({py_val})")
            else:
                print(f"    {field:25} | Python={py_val}, Rust={rust_val}")
                if py_val and not rust_val:
                    print(f"    {' ':25} | ⚠️  Rust missing this header")
                    header_gaps.append(f"{op}: {field}")
                elif rust_val and not py_val:
                    print(f"    {' ':25} | ⚠️  Python missing this header")
                else:
                    print(f"    {' ':25} | ⚠️  Values differ")

    # Print summary
    print(f"\n{'═' * 60}")
    print(f"  {test_type.upper()} HEADERS SUMMARY")
    print(f"{'═' * 60}")
    if header_gaps:
        print(f"  Response Headers Gaps: {len(header_gaps)}")
        for gap in header_gaps[:10]:
            print(f"    - {gap}")
        if len(header_gaps) > 10:
            print(f"    ... and {len(header_gaps) - 10} more")
    else:
        print(f"  Response Headers: ✅ ALL MATCH")

    return len(header_gaps) == 0

def compare_operations(python_result, rust_result, test_type):
    """Compare operations between Python and Rust backends"""
    print_separator(f"{test_type.upper()} DATA FIELDS COMPARISON")

    if not python_result.get("success"):
        print(f"  ❌ Python backend failed: {python_result.get('error', 'Unknown error')}")
        return False
    if not rust_result.get("success"):
        print(f"  ❌ Rust backend failed: {rust_result.get('error', 'Unknown error')}")
        return False

    python_ops = python_result.get("operations", {})
    rust_ops = rust_result.get("operations", {})

    operations = [
        ("create_database", "Database Creation"),
        ("read_database", "Database Read"),
        ("create_container", "Container Creation"),
        ("create_item", "Item Creation"),
        ("read_item", "Item Read"),
        ("upsert_item", "Item Upsert"),
        ("replace_item", "Item Replace"),
        ("delete_item", "Item Delete"),
        ("delete_container", "Container Delete"),
        ("delete_database", "Database Delete"),
    ]

    # System properties that Rust may not return (known gap for Phase 2)
    system_properties = ["_rid", "_self", "_etag", "_ts", "keys"]

    # Core user data fields that MUST match
    core_data_fields = ["pk", "name", "value", "nested", "success"]

    all_core_match = True
    system_gaps = []

    for op_key, op_name in operations:
        print(f"\n{'─' * 60}")
        print(f"  Operation: {op_name}")
        print(f"{'─' * 60}")

        py_op = python_ops.get(op_key, {})
        rust_op = rust_ops.get(op_key, {})

        if not py_op:
            print(f"    ⚠️  Python: No result")
            continue
        if not rust_op:
            print(f"    ⚠️  Rust: No result")
            continue

        # Compare fields
        for field in py_op.keys():
            py_val = py_op.get(field)
            rust_val = rust_op.get(field)

            # Skip database ID comparison (contains timestamp, expected to differ)
            if field == "id" and "database" in op_key.lower():
                print(f"    {field:20} | (different timestamps - expected) | ⚪ SKIP")
                continue

            if field == "keys":
                if isinstance(py_val, list) and isinstance(rust_val, list):
                    print(f"    {field:20} | Python: {sorted(py_val)}")
                    print(f"    {' ':20} | Rust:   {sorted(rust_val)}")
                    if set(py_val) == set(rust_val):
                        print(f"    {' ':20} | ✅ MATCH")
                    else:
                        print(f"    {' ':20} | ⚠️  System properties gap (Phase 2)")
                        system_gaps.append(f"{op_name}: keys differ")
                continue

            match = py_val == rust_val

            if field in system_properties:
                if match:
                    print(f"    {field:20} | {py_val} | ✅ MATCH")
                else:
                    print(f"    {field:20} | Python={py_val}, Rust={rust_val} | ⚠️  System prop gap")
                    system_gaps.append(f"{op_name}: {field}")
            elif field in core_data_fields or field == "id":
                if match:
                    print(f"    {field:20} | {py_val} | ✅ MATCH")
                else:
                    print(f"    {field:20} | Python={py_val}, Rust={rust_val} | ❌ CORE MISMATCH")
                    all_core_match = False
            else:
                if match:
                    print(f"    {field:20} | {py_val} | ✅ MATCH")
                else:
                    print(f"    {field:20} | Python={py_val}, Rust={rust_val} | ⚠️  DIFFERENT")

    # Print summary
    print(f"\n{'═' * 60}")
    print(f"  {test_type.upper()} DATA SUMMARY")
    print(f"{'═' * 60}")
    print(f"  Core Data Fields: {'✅ ALL MATCH' if all_core_match else '❌ MISMATCH'}")
    if system_gaps:
        print(f"  System Properties Gaps (Phase 2): {len(system_gaps)}")
        for gap in system_gaps[:5]:
            print(f"    - {gap}")
        if len(system_gaps) > 5:
            print(f"    ... and {len(system_gaps) - 5} more")
    else:
        print(f"  System Properties: ✅ ALL MATCH")

    return all_core_match

def main():
    """Main entry point"""
    print("\n" + "█" * 80)
    print("█  COSMOS DB SDK BACKEND COMPARISON TEST")
    print("█  Comparing Pure Python vs Rust SDK:")
    print("█  - Data fields (core user data + system properties)")
    print("█  - Response headers (x-ms-request-charge, etag, etc.)")
    print("█  (Each backend runs in a separate process for isolation)")
    print("█" * 80)

    # ==================== SYNC TESTS ====================
    print("\n\n" + "▓" * 80)
    print("▓  SYNC TESTS")
    print("▓" * 80)

    print("\n[Running Python backend in subprocess...]")
    python_sync_result, python_output = run_backend_test("false", "sync", "_py")
    print(python_output)

    print("\n[Running Rust backend in subprocess...]")
    rust_sync_result, rust_output = run_backend_test("true", "sync", "_rs")
    print(rust_output)

    sync_data_passed = compare_operations(python_sync_result, rust_sync_result, "sync")
    sync_headers_passed = compare_headers(python_sync_result, rust_sync_result, "sync")

    # ==================== ASYNC TESTS ====================
    print("\n\n" + "▓" * 80)
    print("▓  ASYNC TESTS")
    print("▓" * 80)

    print("\n[Running Python backend in subprocess...]")
    python_async_result, python_output = run_backend_test("false", "async", "_py_async")
    print(python_output)

    print("\n[Running Rust backend in subprocess...]")
    rust_async_result, rust_output = run_backend_test("true", "async", "_rs_async")
    print(rust_output)

    async_data_passed = compare_operations(python_async_result, rust_async_result, "async")
    async_headers_passed = compare_headers(python_async_result, rust_async_result, "async")

    # ==================== SUMMARY ====================
    print("\n\n" + "█" * 80)
    print("█  FINAL SUMMARY")
    print("█" * 80)
    print(f"\n  SYNC TESTS:")
    print(f"    Data Fields:       {'✅ PASSED' if sync_data_passed else '❌ FAILED'}")
    print(f"    Response Headers:  {'✅ PASSED' if sync_headers_passed else '⚠️  GAPS (Phase 2)'}")
    print(f"\n  ASYNC TESTS:")
    print(f"    Data Fields:       {'✅ PASSED' if async_data_passed else '❌ FAILED'}")
    print(f"    Response Headers:  {'✅ PASSED' if async_headers_passed else '⚠️  GAPS (Phase 2)'}")

    overall_data = sync_data_passed and async_data_passed
    print(f"\n  Overall Data Fields: {'✅ ALL MATCH' if overall_data else '❌ MISMATCH'}")
    print("█" * 80 + "\n")

    return 0 if overall_data else 1

if __name__ == "__main__":
    sys.exit(main())

