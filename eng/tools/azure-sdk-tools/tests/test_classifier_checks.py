import pytest

from ci_tools.functions import verify_package_classifiers


@pytest.mark.parametrize(
    "package_name, package_version, package_classifiers, expected_result",
    [
        ("a", "1.0.0", ["Development Status :: 4 - Beta"], False),
        ("b", "1.0.0", ["Development Status :: 5 - Production/Stable"], True),
        ("b", "1.0.0a1", ["Development Status :: 5 - Production/Stable"], False),
        ("b", "1.0.0a1", ["Development Status :: 4 - Beta"], True),
        ("c", "1.0.0b1", ["Development Status :: 4 - Beta"], True),
        ("c", "1.0.0b1", ["Development Status :: 4 - Beta", "Development Status :: 5 - Production/Stable"], False),
        ("c", "1.0.0", ["Development Status :: 4 - Beta", "Development Status :: 5 - Production/Stable"], False),
        ("c", "1.0.1", ["Development Status :: 7 - Inactive"], True),
        ("c", "1.0.1b1", ["Development Status :: 7 - Inactive"], False),
    ],
)
def test_classifier_enforcement(package_name, package_version, package_classifiers, expected_result):
    result = verify_package_classifiers(package_name, package_version, package_classifiers)
    assert result[0] is expected_result
