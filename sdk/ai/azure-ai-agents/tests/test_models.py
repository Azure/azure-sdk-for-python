# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import azure.ai.agents.models as _models


class TestModels:
    """Unit tests for models."""

    _FILES = ["file1", "file2"]
    _DATA_SOURCES = [
        _models.VectorStoreDataSource(
            asset_identifier="azureai:/123", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
        ),
        _models.VectorStoreDataSource(
            asset_identifier="azureai:/456", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
        ),
    ]

    def _assert_data_sources_are_the_same(self, one, other):
        """Convenience method to compare lists."""
        one_list = [ds.asset_identifier for ds in one]
        other_list = [ds.asset_identifier for ds in other]
        assert sorted(one_list) == sorted(other_list)

    @pytest.mark.parametrize(
        "files,ds",
        [
            (_FILES, None),
            (_FILES, []),
            (None, _DATA_SOURCES),
            ([], _DATA_SOURCES),
            ([], []),
            ([], None),
            (None, []),
            (None, None),
        ],
    )
    def test_create_code_interpreter_tool(self, files, ds):
        """Test The created ToolResources."""
        code_interpreter = _models.CodeInterpreterTool(file_ids=files, data_sources=ds)
        tool_resources = code_interpreter.resources
        if not files and not ds:
            assert tool_resources.code_interpreter is None
        if files:
            assert sorted(tool_resources.code_interpreter.file_ids) == sorted(files)
            assert tool_resources.code_interpreter.data_sources is None
        if ds:
            assert tool_resources.code_interpreter.file_ids is None
            self._assert_data_sources_are_the_same(tool_resources.code_interpreter.data_sources, ds)

    def test_assert_code_interpreter_tool_raises(self):
        """Test that if both file_ids and data sources are provided the error is raised."""
        with pytest.raises(ValueError) as e:
            _models.CodeInterpreterTool(file_ids=TestModels._FILES, data_sources=TestModels._DATA_SOURCES)
        assert _models.CodeInterpreterTool._INVALID_CONFIGURATION == e.value.args[0]

    @pytest.mark.parametrize(
        "file_id,expected",
        [
            (_FILES[0], _FILES),
            ("file3", _FILES + ["file3"]),
        ],
    )
    def test_add_files(self, file_id, expected):
        """Test addition of files to code interpreter tool."""
        code_interpreter = _models.CodeInterpreterTool(file_ids=TestModels._FILES)
        code_interpreter.add_file(file_id)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is not None
        assert sorted(tool_resources.code_interpreter.file_ids) == sorted(expected)

    @pytest.mark.parametrize(
        "ds,expected",
        [
            (_DATA_SOURCES[0], _DATA_SOURCES),
            (
                _models.VectorStoreDataSource(
                    asset_identifier="azureai://789", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
                ),
                _DATA_SOURCES
                + [
                    _models.VectorStoreDataSource(
                        asset_identifier="azureai://789", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
                    )
                ],
            ),
        ],
    )
    def test_add_data_sources(self, ds, expected):
        """Test addition of data sources."""
        code_interpreter = _models.CodeInterpreterTool(data_sources=TestModels._DATA_SOURCES)
        code_interpreter.add_data_source(ds)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is not None
        self._assert_data_sources_are_the_same(tool_resources.code_interpreter.data_sources, expected)

    def test_add_files_raises(self):
        """Test that addition of file to the CodeInterpreter with existing data sources raises the exception."""
        code_interpreter = _models.CodeInterpreterTool(data_sources=TestModels._DATA_SOURCES)
        with pytest.raises(ValueError) as e:
            code_interpreter.add_file("123")
        assert _models.CodeInterpreterTool._INVALID_CONFIGURATION == e.value.args[0]

    def test_add_data_source_raises(self):
        """Test that addition of a data source to CodeInterpreter with file IDs raises the exception."""
        code_interpreter = _models.CodeInterpreterTool(file_ids=TestModels._FILES)
        with pytest.raises(ValueError) as e:
            code_interpreter.add_data_source(
                _models.VectorStoreDataSource(
                    asset_identifier="azureai://789", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
                )
            )
        assert _models.CodeInterpreterTool._INVALID_CONFIGURATION == e.value.args[0]

    @pytest.mark.parametrize(
        "file_id,expected",
        [
            (_FILES[0], [_FILES[1]]),
            ("file3", _FILES),
        ],
    )
    def test_remove_fie_id(self, file_id, expected):
        """Test removal of a file ID."""
        code_interpreter = _models.CodeInterpreterTool(file_ids=TestModels._FILES)
        code_interpreter.remove_file(file_id)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is not None
        assert sorted(tool_resources.code_interpreter.file_ids) == sorted(expected)

    def test_remove_all_ids(
        self,
    ):
        """Test removal of all file IDs."""
        code_interpreter = _models.CodeInterpreterTool(file_ids=TestModels._FILES)
        for file_id in TestModels._FILES:
            code_interpreter.remove_file(file_id)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is None

    @pytest.mark.parametrize(
        "ds,expected",
        [
            (_DATA_SOURCES[0], [_DATA_SOURCES[1]]),
            (
                _models.VectorStoreDataSource(
                    asset_identifier="azureai://789", asset_type=_models.VectorStoreDataSourceAssetType.URI_ASSET
                ),
                _DATA_SOURCES,
            ),
        ],
    )
    def test_remode_data_source(self, ds, expected):
        """Test removal of a data source."""
        code_interpreter = _models.CodeInterpreterTool(data_sources=TestModels._DATA_SOURCES)
        code_interpreter.remove_data_source(ds.asset_identifier)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is not None
        self._assert_data_sources_are_the_same(tool_resources.code_interpreter.data_sources, expected)

    def test_remove_all_data_sources(self):
        """Test removal of all data sources."""
        code_interpreter = _models.CodeInterpreterTool(data_sources=TestModels._DATA_SOURCES)
        for ds in TestModels._DATA_SOURCES:
            code_interpreter.remove_data_source(ds.asset_identifier)
        tool_resources = code_interpreter.resources
        assert tool_resources.code_interpreter is None
