# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.iot.modelsrepository import dtmi_conventions


@pytest.mark.describe(".is_valid_dtmi()")
class TestIsValidDTMI(object):
    @pytest.mark.it("Returns True if given a valid DTMI")
    @pytest.mark.parametrize(
        "dtmi",
        [
            pytest.param("dtmi:FooDTDL;1", id="Short DTMI"),
            pytest.param("dtmi:com:somedomain:example:FooDTDL;1", id="Long DTMI"),
            pytest.param("dtmi:com:example:Thermostat;1", id="Realistic Example 1"),
            pytest.param("dtmi:contoso:scope:entity;2", id="Realistic Example 2"),
        ],
    )
    def test_valid_dtmi(self, dtmi):
        assert dtmi_conventions.is_valid_dtmi(dtmi)

    @pytest.mark.it("Returns False if given an invalid DTMI")
    @pytest.mark.parametrize(
        "dtmi",
        [
            pytest.param("", id="Empty string"),
            pytest.param("not a dtmi", id="Not a DTMI"),
            pytest.param("dtmi;1", id="Only version"),
            pytest.param("com:somedomain:example:FooDTDL;1", id="DTMI missing scheme"),
            pytest.param("dtmi:com:somedomain:example:FooDTDL", id="DTMI missing version"),
            pytest.param("dtmi:com:example::Thermostat;1", id="DTMI extra :"),
            pytest.param("dtmi:foo_bar:_16:baz33:qux;12", id="System DTMI"),
        ],
    )
    def test_invalid_dtmi(self, dtmi):
        assert not dtmi_conventions.is_valid_dtmi(dtmi)


@pytest.mark.describe(".get_model_uri()")
class TestGetModelURI(object):
    @pytest.mark.it("Returns the URI for a specified model at a specified repository")
    @pytest.mark.parametrize(
        "dtmi, repository_uri, expected_model_uri",
        [
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "https://myrepository/local/",
                "https://myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="HTTPS repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myrepository/local/",
                "http://myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="HTTP repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "https://MYREPOSITORY/local/",
                "https://MYREPOSITORY/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Caps HTTPS repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file:///myrepository/local/",
                "file:///myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="POSIX Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file:///c:/myrepository/local/",
                "file:///c:/myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Drive Letter Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file:///c:/myrepoSitory/local/",
                "file:///c:/myrepoSitory/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Mixed case Drive Letter Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://server/myrepository/local",
                "file://server/myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Windows UNC Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://localhost/myrepository/local/",
                "file://localhost/myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Filesystem URI w/ host",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myrepository/local",
                "http://myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Repository URI without trailing '/'",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "/myrepository/local/",
                "file:///myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="POSIX Filesystem with no file scheme",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "c:/myrepository/local/",
                "file:///c:/myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Drive Letter Filesystem with no file scheme",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "\\\\myrepository\\local",
                "file://myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Forward slashes",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "c:\\myrepository\\local\\",
                "file:///c:/myrepository/local/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Drive Letter Filesystem with no file scheme and foward slashes",
            ),
        ],
    )
    def test_uri(self, dtmi, repository_uri, expected_model_uri):
        model_uri = dtmi_conventions.get_model_uri(dtmi, repository_uri)
        assert model_uri == expected_model_uri

        expanded_model_uri = dtmi_conventions.get_model_uri(dtmi, repository_uri, expanded=True)
        assert expanded_model_uri == expected_model_uri.replace(".json", ".expanded.json")

    @pytest.mark.it("Raises ValueError if given an invalid DTMI")
    @pytest.mark.parametrize(
        "dtmi",
        [
            pytest.param("", id="Empty string"),
            pytest.param("not a dtmi", id="Not a DTMI"),
            pytest.param("com:somedomain:example:FooDTDL;1", id="DTMI missing scheme"),
            pytest.param("dtmi:com:somedomain:example:FooDTDL", id="DTMI missing version"),
            pytest.param("dtmi:foo_bar:_16:baz33:qux;12", id="System DTMI"),
        ],
    )
    def test_invalid_dtmi(self, dtmi):
        # Remote repository
        with pytest.raises(ValueError):
            dtmi_conventions.get_model_uri(dtmi, "https://myrepository/local")
        # Remote repository, expanded
        with pytest.raises(ValueError):
            dtmi_conventions.get_model_uri(dtmi, "https://myrepository/local", expanded=True)
        # Local repository
        with pytest.raises(ValueError):
            dtmi_conventions.get_model_uri(dtmi, "file://path/to/repository/")
        # Local repository, expanded
        with pytest.raises(ValueError):
            dtmi_conventions.get_model_uri(dtmi, "file://path/to/repository/", expanded=True)

@pytest.mark.describe("._convert_dtmi_to_path()")
class TestConvertDTMIToPath(object):
    @pytest.mark.it("Returns a correct path for the specified DTMI")
    @pytest.mark.parametrize(
        "dtmi, expanded, expected_path",
        [
            pytest.param(
                "dtmi:com:example:Model;1",
                False,
                "dtmi/com/example/model-1.json",
                id="Example non-expanded DTMI"
            ),
            pytest.param(
                "dtmi:com:example:Model;1",
                True,
                "dtmi/com/example/model-1.expanded.json",
                id="Example expanded DTMI"
            ),
            pytest.param(
                "dtmi:com:Example:Model;1",
                False,
                "dtmi/com/example/model-1.json",
                id="Upper case non-expanded DTMI"
            ),
            pytest.param(
                "dtmi:com:Example:Model;1",
                True,
                "dtmi/com/example/model-1.expanded.json",
                id="Upper case expanded DTMI"
            ),
            pytest.param(
                "dtmi:com:Example:Model:1",
                False,
                "",
                id="Invalid DTMI"
            ),
            pytest.param(
                "",
                True,
                "",
                id="Empty String"
            ),
        ],
    )
    def test_valid_dtmi(self, dtmi, expanded, expected_path):
        assert dtmi_conventions._convert_dtmi_to_path(dtmi, expanded) == expected_path
