from pathlib import Path

from check_mgmt_sdk_data import main


def test_check_mgmt_sdk_data_writes_ordered_markdown(tmp_path):
    sdk_repo = tmp_path / "azure-sdk-for-python"
    rest_repo = tmp_path / "azure-rest-api-specs"
    data_file = sdk_repo / "data.txt"
    output_file = sdk_repo / "result.md"

    (sdk_repo / "sdk" / "foo" / "azure-mgmt-foo").mkdir(parents=True)
    (sdk_repo / "sdk" / "storageactions" / "azure-mgmt-storageactions").mkdir(parents=True)
    explicit_sdk = sdk_repo / "sdk" / "bar" / "azure-mgmt-explicit"
    explicit_sdk.mkdir(parents=True)
    (explicit_sdk / "tsp-location.yaml").write_text("directory: specification/bar\n", encoding="utf-8")

    tsp_dir = rest_repo / "specification" / "foo" / "resource-manager" / "Microsoft.Foo" / "Foo"
    tsp_dir.mkdir(parents=True)
    (tsp_dir / "tspconfig.yaml").write_text(
        "options:\n"
        "  '@azure-tools/typespec-python':\n"
        "    emitter-output-dir: '{project-root}/../azure-sdk-for-python/sdk/foo/azure-mgmt-foo'\n",
        encoding="utf-8",
    )
    direct_tsp_dir = rest_repo / "specification" / "storageactions" / "StorageAction.Management"
    direct_tsp_dir.mkdir(parents=True)
    (direct_tsp_dir / "tspconfig.yaml").write_text(
        "options:\n"
        "  '@azure-tools/typespec-python':\n"
        "    emitter-output-dir: '{output-dir}/{service-dir}/azure-mgmt-storageactions'\n",
        encoding="utf-8",
    )

    data_file.write_text(
        '"serivce folder 1" "service folder 2" sdk_name\n'
        "Microsoft.Foo\tfoo\n"
        "Microsoft.StorageActions\tstorageactions\n"
        'Microsoft.NoSpecs\tnospecs "no specs"\n'
        "Microsoft.Bar\tbar azure-mgmt-explicit\n"
        "Microsoft.Missing\tmissing\n",
        encoding="utf-8",
    )

    exit_code = main([str(rest_repo), "--data", str(data_file), "--output", str(output_file), "--sdk-repo", str(sdk_repo)])

    assert exit_code == 0
    assert output_file.read_text(encoding="utf-8").splitlines() == [
        "| id | service folder 1 | service folder 2 | sdk name (azure-mgmt-*) | path exist (Y/N) | tsp file (Y/N) |",
        "| --- | --- | --- | --- | --- | --- |",
        "| 1 | Microsoft.Foo | foo | azure-mgmt-foo | Y | N |",
        "| 2 | Microsoft.StorageActions | storageactions | azure-mgmt-storageactions | Y | N |",
        "| 3 | Microsoft.NoSpecs | nospecs | no specs | - | - |",
        "| 4 | Microsoft.Bar | bar | azure-mgmt-explicit | Y | Y |",
        "| 5 | Microsoft.Missing | missing |  | N | N |",
    ]
