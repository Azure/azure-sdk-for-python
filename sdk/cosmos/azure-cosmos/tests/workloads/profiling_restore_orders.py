# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Restore a confirmed, exclusively used orders target outside measured sequences."""

import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid

from azure.core import MatchConditions

from workload_utils import create_seed_item

_SYSTEM_FIELDS = {"_rid", "_self", "_etag", "_attachments", "_ts"}


def target(uri, database, container):
    parsed = urlsplit(uri)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or not database
        or not container
    ):
        raise ValueError("Expected an HTTPS account endpoint, database and container")
    return {
        "endpoint": f"https://{parsed.hostname}:{parsed.port or 443}",
        "database": database,
        "container": container,
    }


def restoration_config(environ, confirmed):
    required = (
        "COSMOS_URI",
        "COSMOS_DATABASE",
        "COSMOS_CONTAINER",
        "COSMOS_PARTITION_KEY",
        "COSMOS_MAX_ITEM_INDEX",
        "WORKLOAD_DOC_PROFILE",
        "RESULTS_COSMOS_URI",
        "RESULTS_COSMOS_DATABASE",
        "RESULTS_COSMOS_CONTAINER",
    )
    for name in required:
        if not environ.get(name):
            raise ValueError(f"Restoration requires explicit {name}")
    selected = target(
        environ["COSMOS_URI"], environ["COSMOS_DATABASE"], environ["COSMOS_CONTAINER"]
    )
    if selected != target(*confirmed):
        raise ValueError("Confirmed target differs from the selected workload target")
    results = target(
        environ["RESULTS_COSMOS_URI"],
        environ["RESULTS_COSMOS_DATABASE"],
        environ["RESULTS_COSMOS_CONTAINER"],
    )
    if selected == results:
        raise ValueError("Restoration must not target the results container")
    if (
        environ["WORKLOAD_DOC_PROFILE"] != "orders"
        or environ["COSMOS_PARTITION_KEY"] != "id"
    ):
        raise ValueError(
            "Restoration supports only the orders profile with partition key /id"
        )
    max_index = int(environ["COSMOS_MAX_ITEM_INDEX"])
    if max_index < 0:
        raise ValueError("COSMOS_MAX_ITEM_INDEX must be nonnegative")
    return {
        "target": selected,
        "max_item_index": max_index,
        "profile": "orders",
        "partition_key": "/id",
    }


def load_manifest(path, config):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {*config, "namespace"}:
        raise ValueError("Invalid restoration manifest")
    if any(manifest[name] != value for name, value in config.items()):
        raise ValueError(
            "Restoration manifest differs from the selected target or dataset"
        )
    namespace = manifest["namespace"]
    if not isinstance(namespace, str) or not re.fullmatch(r"[0-9a-f]{32}", namespace):
        raise ValueError("Invalid restoration namespace")
    return manifest


def inventory(container):
    rows = {}
    for item in container.query_items(
        "SELECT * FROM c", enable_cross_partition_query=True
    ):
        item_id = item["id"]
        if item_id in rows:
            raise ValueError(f"Duplicate item identity during restoration: {item_id}")
        rows[item_id] = item
    return rows


def restore_orders(container, manifest):
    properties = container.read()
    if properties.get("partitionKey", {}).get("paths") != ["/id"]:
        raise ValueError(
            "Restoration requires the actual container partition key to be /id"
        )
    if properties.get("defaultTtl") is not None:
        raise ValueError("Restoration requires a container without TTL")

    expected = {}
    for index in range(manifest["max_item_index"] + 1):
        body = create_seed_item(index)
        if body["id"] != f"order-{index}" or body.get("quantity") != 2:
            raise ValueError(
                "The active workload does not generate the agreed orders dataset"
            )
        expected[body["id"]] = body

    before = inventory(container)
    owned_pattern = re.compile(
        rf"order-{manifest['namespace']}-[0-9a-f]{{8}}-[0-9a-f]{{4}}-"
        rf"[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}"
    )
    extras = []
    for item_id, item in before.items():
        if item_id in expected:
            continue
        if not owned_pattern.fullmatch(item_id):
            raise ValueError(
                f"Unexpected item; no restoration writes performed: {item_id}"
            )
        if item.get("customerId") != "customer-" + item_id.removeprefix(
            "order-"
        ) or not item.get("_etag"):
            raise ValueError(f"Cannot safely identify workload-created item: {item_id}")
        extras.append(item)

    # Finish inventory validation before writing; never infer ownership from an
    # order- prefix alone. The ETag prevents deleting a changed inventory entry.
    for item in extras:
        container.delete_item(
            item["id"],
            partition_key=item["id"],
            etag=item["_etag"],
            match_condition=MatchConditions.IfNotModified,
        )
    for body in expected.values():
        container.upsert_item(body)

    after = inventory(container)
    if set(after) != set(expected):
        raise ValueError(
            "Restoration verification failed: unexpected or missing item identities"
        )
    for item_id, body in expected.items():
        actual = {
            key: value
            for key, value in after[item_id].items()
            if key not in _SYSTEM_FIELDS
        }
        if actual != body:
            raise ValueError(
                f"Restoration verification failed: body mismatch for {item_id}"
            )
    return {
        "status": "verified",
        "restored_orders": len(expected),
        "removed_owned_items": len(extras),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="Save a fresh ownership namespace; no service calls",
    )
    parser.add_argument(
        "--confirm-target",
        nargs=3,
        required=True,
        metavar=("ENDPOINT", "DATABASE", "CONTAINER"),
    )
    args = parser.parse_args()
    config = restoration_config(os.environ, args.confirm_target)
    if args.initialize:
        manifest = {**config, "namespace": uuid.uuid4().hex}
        with args.manifest.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
        print(manifest["namespace"])
        return
    manifest = load_manifest(args.manifest, config)
    active_namespace = os.environ.get("WORKLOAD_ITEM_NAMESPACE", "")
    if active_namespace and active_namespace != manifest["namespace"]:
        raise ValueError(
            "Active workload namespace differs from the restoration manifest"
        )
    if not os.environ.get("COSMOS_KEY"):
        raise ValueError("Restoration requires COSMOS_KEY")

    from azure.cosmos import CosmosClient

    with CosmosClient(
        os.environ["COSMOS_URI"], os.environ["COSMOS_KEY"], _backend="core-python"
    ) as client:
        container = client.get_database_client(
            config["target"]["database"]
        ).get_container_client(
            config["target"]["container"],
        )
        result = restore_orders(container, manifest)
    print(
        json.dumps(
            {**result, "target": config["target"], "namespace": manifest["namespace"]}
        )
    )


if __name__ == "__main__":
    main()
