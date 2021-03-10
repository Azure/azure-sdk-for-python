# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import logging
import json
import os
from azure.iot.modelsrepository import resolver

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def dtmi():
    return "dtmi:com:somedomain:example:FooDTDL;1"


@pytest.fixture
def dtdl():
    return {
        "@context": "dtmi:dtdl:context;1",
        "@id": "dtmi:com:somedomain:example:FooDTDL;1",
        "@type": "Interface",
        "displayName": "Foo",
        "contents": [
            {
                "@type": "Property",
                "name": "fooproperty",
                "displayName": "Foo Property",
                "schema": "string",
                "description": "A string representing some value. This isn't real",
            },
        ],
    }


# NOTE: maybe move this to a fetcher specific class
@pytest.fixture
def path():
    return "some/path/to/a/dtdl.json"


#################################################################


@pytest.fixture
def foo_dtmi():
    return "dtmi:com:somedomain:example:FooDTDL;1"


# @pytest.fixture
# def foo_dtdl_json():
#     # Testing Notes:
#     #   - Contains a single property
#     #   - Contains multiple components
#     #   - Contains an extension of an interface
#     #   - Contains two different components with the same model
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:FooDTDL;1",
#         "@type": "Interface",
#         "displayName": "Foo",
#         "extends": "dtmi:com:somedomain:example:BazDTDL;1",
#         "contents": [
#             {
#                 "@type": "Property",
#                 "name": "fooproperty",
#                 "displayName": "Foo Property",
#                 "schema": "string",
#                 "description": "A string representing some value. This isn't real",
#             },
#             {
#                 "@type": "Component",
#                 "name": "bar",
#                 "displayName": "Bar 1",
#                 "schema": "dtmi:com:somedomain:example:BarDTDL;1",
#                 "description": "Bar component 1",
#             },
#             {
#                 "@type": "Component",
#                 "name": "bar",
#                 "displayName": "Bar 2",
#                 "schema": "dtmi:com:somedomain:example:BarDTDL;1",
#                 "description": "Bar component 2",
#             },
#             {
#                 "@type": "Component",
#                 "name": "buzz",
#                 "displayName": "Buzz",
#                 "schema": "dtmi:com:somedomain:example:BuzzDTDL;1",
#             },
#         ],
#     }


# @pytest.fixture
# def bar_dtdl_json():
#     # Testing Notes:
#     #   - Contains a telemetry
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:BarDTDL;1",
#         "@type": "Interface",
#         "displayName": "Bar",
#         "contents": [
#             {
#                 "@type": "Property",
#                 "name": "barproperty",
#                 "displayName": "Bar Property",
#                 "schema": "string",
#                 "description": "A string representing some value. This isn't real",
#             },
#             {"@type": "Telemetry", "name": "bartelemetry", "schema": "double"},
#         ],
#     }


# @pytest.fixture
# def buzz_dtdl_json():
#     # Testing Notes:
#     #   - Contains two extensions of interfaces (maximum value)
#     #   - Contains a single property
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:BuzzDTDL;1",
#         "@type": "Interface",
#         "displayName": "Buzz",
#         "extends": [
#             "dtmi:com:somedomain:example:QuxDTDL;1",
#             "dtmi:com:somedomain:example:QuzDTDL;1",
#         ],
#         "contents": [
#             {
#                 "@type": "Property",
#                 "name": "buzzproperty",
#                 "displayName": "Buzz Property",
#                 "schema": "string",
#                 "description": "A string representing some value. This isn't real",
#             },
#         ],
#     }


# @pytest.fixture
# def baz_dtdl_json():
#     # Testing Notes:
#     #   - Contains multiple properties
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:BazDTDL;1",
#         "@type": "Interface",
#         "displayName": "Baz",
#         "contents": [
#             {
#                 "@type": "Property",
#                 "name": "bazproperty1",
#                 "displayName": "Baz Property 1",
#                 "schema": "string",
#                 "description": "A string representing some value. This isn't real",
#             },
#             {
#                 "@type": "Property",
#                 "name": "bazproperty2",
#                 "displayName": "Baz Property 2",
#                 "schema": "string",
#                 "description": "A string representing some value. This isn't real",
#             },
#         ],
#     }


# @pytest.fixture
# def qux_dtdl_json():
#     # Testing Notes:
#     #   - Contains a Command
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:QuxDTDL;1",
#         "@type": "Interface",
#         "displayName": "Qux",
#         "contents": [
#             {
#                 "@type": "Command",
#                 "name": "quxcommand",
#                 "request": {
#                     "name": "quxcommandtime",
#                     "displayName": "Qux Command Time",
#                     "description": "It's a command. For Qux.",
#                     "schema": "dateTime",
#                 },
#                 "response": {"name": "quxresponsetime", "schema": "dateTime"},
#             }
#         ],
#     }


# @pytest.fixture
# def quz_dtdl_json():
#     # Testing Notes:
#     #   - Contains no contents (doesn't make much sense, but an edge case to test nontheless)
#     return {
#         "@context": "dtmi:dtdl:context;1",
#         "@id": "dtmi:com:somedomain:example:QuzDTDL;1",
#         "@type": "Interface",
#         "displayName": "Quz",
#     }


# @pytest.fixture
# def foo_dtdl_expanded_json(
#     foo_dtdl_json, bar_dtdl_json, buzz_dtdl_json, qux_dtdl_json, quz_dtdl_json, baz_dtdl_json
# ):
#     return [
#         foo_dtdl_json,
#         bar_dtdl_json,
#         buzz_dtdl_json,
#         qux_dtdl_json,
#         quz_dtdl_json,
#         baz_dtdl_json,
#     ]


# @pytest.fixture
# def dtmi_to_path_mappings():
#     # NOTE: Does not include .exapnded.json paths.
#     # Manually replace .json with .expanded.json if necessary
#     path_map = {}
#     path_map["dtmi:com:somedomain:example:FooDTDL;1"] = "dtmi/com/somedomain/example/foodtdl-1.json"
#     path_map["dtmi:com:somedomain:example:BarDTDL;1"] = "dtmi/com/somedomain/example/bardtdl-1.json"
#     path_map[
#         "dtmi:com:somedomain:example:BuzzDTDL;1"
#     ] = "dtmi/com/somedomain/example/buzzdtdl-1.json"
#     path_map["dtmi:com:somedomain:example:QuxDTDL;1"] = "dtmi/com/somedomain/example/quxdtdl-1.json"
#     path_map["dtmi:com:somedomain:example:QuzDTDL;1"] = "dtmi/com/somedomain/example/quzdtdl-1.json"
#     path_map["dtmi:com:somedomain:example:BazDTDL;1"] = "dtmi/com/somedomain/example/bazdtdl-1.json"
#     return path_map


# @pytest.fixture
# def path_to_dtdl_mappings(
#     foo_dtdl_json,
#     bar_dtdl_json,
#     buzz_dtdl_json,
#     qux_dtdl_json,
#     quz_dtdl_json,
#     baz_dtdl_json,
#     foo_dtdl_expanded_json,
#     dtmi_to_path_mappings,
# ):
#     # NOTE: Keep this fixture updated with any new models added for testing
#     dtdl_map = {}
#     dtdl_list = [
#         # (Regular DTDL, Expanded DTDL)
#         (foo_dtdl_json, foo_dtdl_expanded_json),
#         (bar_dtdl_json, None),
#         (buzz_dtdl_json, None),
#         (qux_dtdl_json, None),
#         (quz_dtdl_json, None),
#         (baz_dtdl_json, None),
#     ]
#     for dtdl_tuple in dtdl_list:
#         dtdl = dtdl_tuple[0]
#         expanded_dtdl = dtdl_tuple[1]
#         path = dtmi_to_path_mappings[dtdl["@id"]]
#         dtdl_map[path] = dtdl
#         if expanded_dtdl:
#             expanded_path = path.replace(".json", ".expanded.json")
#             dtdl_map[expanded_path] = expanded_dtdl
#     return dtdl_map


# class DtmiResolverResolveSharedTests(object):
#     @pytest.fixture
#     def fetcher(self, mocker, path_to_dtdl_mappings):
#         fetcher_mock = mocker.MagicMock()
#         fetcher_mock.cached_mock_fetch_returns = []
#         fetcher_mock.fail_expanded = False

#         def mocked_fetch(path):
#             if path.endswith(".expanded.json") and fetcher_mock.fail_expanded:
#                 raise resolver.FetcherError()
#             try:
#                 dtdl = path_to_dtdl_mappings[path]
#             except KeyError:
#                 raise resolver.FetcherError()
#             fetcher_mock.cached_mock_fetch_returns.append(dtdl)
#             return dtdl

#         fetcher_mock.fetch.side_effect = mocked_fetch
#         return fetcher_mock

#     @pytest.fixture
#     def dtmi_resolver(self, mocker, fetcher):
#         return resolver.DtmiResolver(fetcher)

#     @pytest.mark.it("Raises a ValueError if the provided DTMI is invalid")
#     @pytest.mark.parametrize(
#         "dtmi",
#         [
#             pytest.param("", id="Empty string"),
#             pytest.param("not a dtmi", id="Not a DTMI"),
#             pytest.param("com:somedomain:example:FooDTDL;1", id="DTMI missing scheme"),
#             pytest.param("dtmi:com:somedomain:example:FooDTDL", id="DTMI missing version"),
#             pytest.param("dtmi:foo_bar:_16:baz33:qux;12", id="System DTMI"),
#         ],
#     )
#     def test_invalid_dtmi(self, dtmi_resolver, dtmi):
#         with pytest.raises(ValueError):
#             dtmi_resolver.resolve(dtmi)

#     @pytest.mark.it("Raises a ResolverError if the Fetcher is unable to fetch a DTDL")
#     def test_fetcher_failure(self, dtmi_resolver, foo_dtmi):
#         my_fetcher_error = resolver.FetcherError("Some arbitrary fetcher error")
#         dtmi_resolver.fetcher.fetch.side_effect = my_fetcher_error
#         with pytest.raises(resolver.ResolverError) as e_info:
#             dtmi_resolver.resolve(foo_dtmi)
#         assert e_info.value.__cause__ is my_fetcher_error

#     # @pytest.mark.it("Raises a ResolverError if provided an invalid resolve mode")
#     # def test_invalid_resolve_mode(self, dtmi_resolver, dtmi):
#     #     with pytest.raises(resolver.ResolverError):
#     #         dtmi_resolver.resolve(dtmi=dtmi, resolve_mode="invalid_mode")


# @pytest.mark.describe("DtmiResolver = .resolve() -- Dependency Mode: Disabled")
# class TestDtmiResolverResolveDependencyModeDisabled(DtmiResolverResolveSharedTests):
#     @pytest.mark.it(
#         "Uses the Fetcher to fetch a model DTDL from a path that corresponds to the provided DTMI"
#     )
#     def test_fetcher(self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings, mocker):
#         dtmi_resolver.resolve(foo_dtmi)

#         assert dtmi_resolver.fetcher.fetch.call_count == 1
#         expected_path = dtmi_to_path_mappings[foo_dtmi]
#         assert dtmi_resolver.fetcher.fetch.call_args == mocker.call(expected_path)

#     @pytest.mark.it(
#         "Returns a dictionary mapping the provided DTMI the corresponding model DTDL that was returned by the Fetcher"
#     )
#     def test_returned_dict(self, dtmi_resolver, foo_dtmi):
#         d = dtmi_resolver.resolve(foo_dtmi)

#         assert isinstance(d, dict)
#         assert len(d) == 1 == dtmi_resolver.fetcher.fetch.call_count
#         assert d[foo_dtmi] == dtmi_resolver.fetcher.cached_mock_fetch_returns[0]


# @pytest.mark.describe("DtmiResolver - .resolve() -- Dependency Mode: Enabled")
# class TestDtmiResolverResolveDependencyModeEnabled(DtmiResolverResolveSharedTests):
#     @pytest.mark.it(
#         "Uses the Fetcher to fetch model DTDLs from paths corresponding to the provided DTMI, as well as the DTMIs of all its dependencies"
#     )
#     def test_fetcher(self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings, mocker):
#         dtmi_resolver.resolve(foo_dtmi, dependency_mode=constant.DEPENDENCY_MODE_ENABLED)

#         # NOTE: there are 6 calls because we only fetch for each UNIQUE component or interface.
#         # There are two components in FooDTDL that are of type BarDTDL, but that DTDL only has
#         # to be fetched once.
#         assert dtmi_resolver.fetcher.fetch.call_count == 6
#         expected_path1 = dtmi_to_path_mappings["dtmi:com:somedomain:example:FooDTDL;1"]
#         expected_path2 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BarDTDL;1"]
#         expected_path3 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BuzzDTDL;1"]
#         expected_path4 = dtmi_to_path_mappings["dtmi:com:somedomain:example:QuxDTDL;1"]
#         expected_path5 = dtmi_to_path_mappings["dtmi:com:somedomain:example:QuzDTDL;1"]
#         expected_path6 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BazDTDL;1"]
#         assert dtmi_resolver.fetcher.fetch.call_args_list[0] == mocker.call(expected_path1)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[1] == mocker.call(expected_path2)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[2] == mocker.call(expected_path3)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[3] == mocker.call(expected_path4)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[4] == mocker.call(expected_path5)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[5] == mocker.call(expected_path6)

#     @pytest.mark.it(
#         "Returns a dictionary mapping DTMIs to model DTDLs returned by the Fetcher, for the provided DTMI, as well as the DTMIs of all dependencies"
#     )
#     def test_returned_dict(
#         self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings, path_to_dtdl_mappings
#     ):
#         d = dtmi_resolver.resolve(foo_dtmi, dependency_mode=constant.DEPENDENCY_MODE_ENABLED)

#         assert isinstance(d, dict)
#         assert len(d) == 6 == dtmi_resolver.fetcher.fetch.call_count
#         for model in dtmi_resolver.fetcher.cached_mock_fetch_returns:
#             dtmi = model["@id"]
#             assert dtmi in d.keys()
#             assert d[dtmi] == model


# @pytest.mark.describe("DtmiResolver - .resolve() -- Dependency Mode: Try From Expanded")
# class TestDtmiResolverResolveDependencyModeTryFromExpanded(DtmiResolverResolveSharedTests):
#     @pytest.mark.it(
#         "Attempts to use the Fetcher to fetch an expanded model DTDL from a path that corresponds to the provided DTMI"
#     )
#     def test_fetcher(self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings, mocker):
#         dtmi_resolver.resolve(foo_dtmi, dependency_mode=constant.DEPENDENCY_MODE_TRY_FROM_EXPANDED)

#         assert dtmi_resolver.fetcher.fetch.call_count == 1
#         expected_path = dtmi_to_path_mappings[foo_dtmi].replace(".json", ".expanded.json")
#         assert dtmi_resolver.fetcher.fetch.call_args == mocker.call(expected_path)

#     @pytest.mark.it(
#         "Returns a dictionary mapping DTMIs to model DTDLs for all models contained within the expanded DTDL that was returned by the Fetcher"
#     )
#     def test_returned_dict_expanded(self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings):
#         d = dtmi_resolver.resolve(
#             foo_dtmi, dependency_mode=constant.DEPENDENCY_MODE_TRY_FROM_EXPANDED
#         )

#         assert isinstance(d, dict)
#         assert len(d) == 6
#         assert dtmi_resolver.fetcher.fetch.call_count == 1
#         expanded_dtdl = dtmi_resolver.fetcher.cached_mock_fetch_returns[0]
#         assert len(expanded_dtdl) == 6
#         for model in expanded_dtdl:
#             dtmi = model["@id"]
#             assert dtmi in d.keys()
#             assert d[dtmi] == model

#     @pytest.mark.it(
#         "Uses the Fetcher to fetch model DTDLs from paths corresponding to the provided DTMI, as well as the DTMIs of all its dependencies, for each expanded DTDL that cannot be fetched"
#     )
#     def test_fetcher_fallback(self, dtmi_resolver, foo_dtmi, dtmi_to_path_mappings, mocker):
#         dtmi_resolver.fetcher.fail_expanded = True
#         dtmi_resolver.resolve(foo_dtmi, dependency_mode=constant.DEPENDENCY_MODE_TRY_FROM_EXPANDED)

#         # NOTE: There are 7 calls. 1 attempted expanded fetch + 6 regular fetches. The expanded
#         # fetch will fail, and then as a fallback it will do the regular fetch procedure.
#         #
#         # There are 6 regular fetch calls because we only fetch for each UNIQUE component or
#         # interface. There are two components in FooDTDL that are of type BarDTDL, but that
#         # DTDL only has to be fetched once.
#         assert dtmi_resolver.fetcher.fetch.call_count == 12
#         expected_path1 = dtmi_to_path_mappings["dtmi:com:somedomain:example:FooDTDL;1"]
#         expected_path2 = dtmi_to_path_mappings["dtmi:com:somedomain:example:FooDTDL;1"]
#         expected_path3 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BarDTDL;1"]
#         expected_path4 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BuzzDTDL;1"]
#         expected_path5 = dtmi_to_path_mappings["dtmi:com:somedomain:example:QuxDTDL;1"]
#         expected_path6 = dtmi_to_path_mappings["dtmi:com:somedomain:example:QuzDTDL;1"]
#         expected_path7 = dtmi_to_path_mappings["dtmi:com:somedomain:example:BazDTDL;1"]
#         assert dtmi_resolver.fetcher.fetch.call_args_list[0] == mocker.call(expected_path1)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[1] == mocker.call(expected_path2)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[2] == mocker.call(expected_path3)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[3] == mocker.call(expected_path4)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[4] == mocker.call(expected_path5)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[5] == mocker.call(expected_path6)
#         assert dtmi_resolver.fetcher.fetch.call_args_list[6] == mocker.call(expected_path7)


@pytest.mark.describe("HttpFetcher - .fetch()")
class TestHttpFetcherFetch(object):
    @pytest.fixture
    def fetcher(self, mocker, dtdl):
        mock_http_client = mocker.MagicMock()
        mock_response = mock_http_client._pipeline.run.return_value.http_response
        mock_response.status_code = 200
        mock_response.text.return_value = json.dumps(dtdl)
        mock_http_client._pipeline
        return resolver.HttpFetcher(mock_http_client)

    @pytest.mark.it(
        "Sends an HTTP GET request for the provided path, using the fetcher's HTTP client"
    )
    def test_request(self, fetcher, path, mocker):
        fetcher.fetch(path)

        assert fetcher.client.get.call_count == 1
        assert fetcher.client.get.call_args == mocker.call(url=path)
        request = fetcher.client.get.return_value
        assert fetcher.client._pipeline.run.call_count == 1
        assert fetcher.client._pipeline.run.call_args == mocker.call(request)

    @pytest.mark.it("Returns the GET response in JSON format, if the GET request is successful")
    def test_response_success(self, fetcher, path):
        dtdl_json = fetcher.fetch(path)

        assert isinstance(dtdl_json, dict)
        client_response = fetcher.client._pipeline.run.return_value.http_response
        assert client_response.status_code == 200
        assert dtdl_json == json.loads(client_response.text())

    @pytest.mark.it("Raises a FetcherError if the GET request is unsuccessful")
    def test_response_failure(self, fetcher, path):
        fetcher.client._pipeline.run.return_value.http_response.status_code = 400
        with pytest.raises(resolver.FetcherError):
            fetcher.fetch(path)


@pytest.mark.describe("FilesystemFetcher - .fetch()")
class TestFilesystemFetcherFetch(object):
    @pytest.fixture
    def mock_open(self, mocker, dtdl):
        return mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(dtdl)))

    @pytest.fixture
    def fetcher(self, mock_open, mocker):
        base_path = "C:/some/base/path"
        return resolver.FilesystemFetcher(base_path)

    @pytest.mark.it(
        "Formats and normalizes syntax of provided path to fetch, then opens and reads the file at that location"
    )
    def test_open_read_path(self, fetcher, path, mock_open, mocker):
        mocker.spy(os.path, "join")
        mocker.spy(os.path, "normcase")
        mocker.spy(os.path, "normpath")

        fetcher.fetch(path)

        # These three functions being called ensure that the path will be formatted correctly for
        # all cases (e.g. trailing slash, no trailing slash, leading slash, etc.)
        # Because we know how these builtin functions work, there's no need to explicitly test
        # these input variants - the logic is handled externally, and is not part of this unit
        assert os.path.join.call_count == 1
        assert os.path.normcase.call_count == 1
        assert os.path.normpath.call_count == 1

        # The expected formatted path was passed to the 'open()' function
        expected_absolute_path = os.path.normpath(
            os.path.normcase(os.path.join(fetcher.base_path, path))
        )
        assert mock_open.call_count == 1
        assert mock_open.call_args == mocker.call(expected_absolute_path)

        # The data was read from the file
        assert mock_open.return_value.read.call_count == 1
        assert mock_open.return_value.read.call_args == mocker.call()

    @pytest.mark.it(
        "Returns the data returned by the read operation in JSON format, if the read is successful"
    )
    def test_open_read_success(self, fetcher, path, mock_open, dtdl, mocker):
        dtdl_json = fetcher.fetch(path)

        assert isinstance(dtdl, dict)
        # Unfortunately, there isn't really a way to show that the returned value comes from the
        # file read due to how the mock of open/read builtins work. Best I can do is show that it
        # has the expected value (with the assumption that the mock returned that value)
        assert dtdl_json == dtdl

    @pytest.mark.it(
        "Raises a FetcherError if there is an error while opening the file at the provided path"
    )
    def test_open_failure(self, fetcher, mock_open, path, arbitrary_exception):
        mock_open.side_effect = arbitrary_exception
        with pytest.raises(resolver.FetcherError) as e_info:
            fetcher.fetch(path)
        assert e_info.value.__cause__ == arbitrary_exception

    @pytest.mark.it(
        "Raises a FetcherError if there is an error while reading the file at the provided path"
    )
    def test_read_failure(self, fetcher, mock_open, path, arbitrary_exception):
        mock_open.return_value.read.side_effect = arbitrary_exception
        with pytest.raises(resolver.FetcherError) as e_info:
            fetcher.fetch(path)
        assert e_info.value.__cause__ == arbitrary_exception
