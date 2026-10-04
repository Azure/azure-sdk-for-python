from azpysdk import _tool_reqs


def test_load_requirements_strips_comments_and_blanks():
    specs = _tool_reqs.load_requirements("mypy")
    assert "mypy==1.19.1" in specs
    # the locked type stubs travel with the mypy pin
    assert "types-requests==2.31.0.6" in specs
    # comment lines and blank lines are not returned
    assert all(not spec.startswith("#") for spec in specs)
    assert all(spec.strip() for spec in specs)


def test_pin_returns_single_specifier():
    assert _tool_reqs.pin("pylint", "pylint") == "pylint==4.0.4"
    assert _tool_reqs.pin("pylint", "azure-pylint-guidelines-checker") == "azure-pylint-guidelines-checker==0.5.7"


def test_pin_is_case_insensitive():
    assert _tool_reqs.pin("pylint", "PyLint") == "pylint==4.0.4"


def test_pin_missing_package_raises():
    try:
        _tool_reqs.pin("black", "not-a-real-tool")
    except KeyError:
        return
    raise AssertionError("expected KeyError for a package not listed in the file")


def test_pinned_version_returns_version_only():
    assert _tool_reqs.pinned_version("mypy", "mypy") == "1.19.1"
    assert _tool_reqs.pinned_version("sphinx", "sphinxcontrib-jquery") == "4.1"


def test_verifytypes_and_pyright_share_a_single_pin():
    # verifytypes intentionally reuses pyright.txt so the pin lives in one place
    assert _tool_reqs.load_requirements("pyright") == ["pyright==1.1.407"]
