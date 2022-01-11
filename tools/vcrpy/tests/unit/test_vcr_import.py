import sys


def test_vcr_import_deprecation(recwarn):

    if "vcr" in sys.modules:
        # Remove imported module entry if already loaded in another test
        del sys.modules["vcr"]

    import vcr  # noqa: F401

    if sys.version_info[0] == 2:
        assert len(recwarn) == 1
        assert issubclass(recwarn[0].category, DeprecationWarning)
    else:
        assert len(recwarn) == 0
