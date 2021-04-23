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
            pytest.param("com:somedomain:example:FooDTDL;1", id="DTMI missing scheme"),
            pytest.param("dtmi:com:somedomain:example:FooDTDL", id="DTMI missing version"),
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
                "https://myrepository/",
                "https://myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="HTTPS repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myrepository/",
                "http://myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="HTTP repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file:///myrepository/",
                "file:///myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="POSIX Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://c:/myrepository/",
                "file://c:/myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Drive Letter Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://server/myrepository",
                "file://server/myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Windows UNC Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://localhost/myrepository/",
                "file://localhost/myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Filesystem URI w/ host",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myrepository",
                "http://myrepository/dtmi/com/somedomain/example/foodtdl-1.json",
                id="Repository URI without trailing '/'",
            ),
        ],
    )
    def test_uri(self, dtmi, repository_uri, expected_model_uri):
        model_uri = dtmi_conventions.get_model_uri(dtmi, repository_uri)
        assert model_uri == expected_model_uri

    @pytest.mark.it("Returns the URI for a specified expanded model at a specified repository")
    @pytest.mark.parametrize(
        "dtmi, repository_uri, expected_model_uri",
        [
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "https://myfakerepository.com/",
                "https://myfakerepository.com/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="HTTPS repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myfakerepository.com/",
                "http://myfakerepository.com/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="HTTP repository URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file:///myrepository/",
                "file:///myrepository/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="POSIX Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://c:/myrepository/",
                "file://c:/myrepository/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="Drive Letter Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://server/myrepository",
                "file://server/myrepository/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="Windows UNC Filesystem URI",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "file://localhost/myrepository/",
                "file://localhost/myrepository/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="Filesystem URI w/ host",
            ),
            pytest.param(
                "dtmi:com:somedomain:example:FooDTDL;1",
                "http://myrepository.com",
                "http://myrepository.com/dtmi/com/somedomain/example/foodtdl-1.expanded.json",
                id="Repository URI without trailing '/'",
            ),
        ],
    )
    def test_uri_expanded(self, dtmi, repository_uri, expected_model_uri):
        model_uri = dtmi_conventions.get_model_uri(dtmi, repository_uri, expanded=True)
        assert model_uri == expected_model_uri

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
        with pytest.raises(ValueError):
            dtmi_conventions.get_model_uri(dtmi, "https://myrepository/")
