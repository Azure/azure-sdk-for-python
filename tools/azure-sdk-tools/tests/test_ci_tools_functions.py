from ci_tools.functions import sort_spec_list, SortableSpecifierSet
from packaging.specifiers import SpecifierSet
from unittest.mock import patch

def test_spec_list_scenarios_ascending():
    scenarios = [
        ['>=0.7.1', '>=0.6.21', '>=0.6.18', '>=0.6.10', '<2.0.0,>=0.6.17'],
        ['>=0.7.1', '!=0.6.1', '!=0.8.3', '>=0.6.10', '>=0.6.17,<2.0.0'],
        ['!=0.7.7', '!=0.7.6', '>=0.16.1,!=0.16.3,!=0.16.4'],
        # we should never encounter this in the wild but better to test for it here
        # (multiple conflicting valid > specs)
        ['!=0.7.7', '>=0.6.2,>=0.6.1,!=0.6.2,!=0.6.2'],
        # this case is another diabolical one. forcing us to internally sort the possible return versions
        ['!=0.6.2', '>=0.6.2,>=0.6.1,!=0.6.3,!=0.6.4'],
        ['!=0.7.7', '~=1.1', '>=0.16.1']
    ]

    success_results = [
        ['>=0.6.10', '<2.0.0,>=0.6.17', '>=0.6.18',  '>=0.6.21', '>=0.7.1'],
        ['!=0.6.1', '>=0.6.10', '>=0.6.17,<2.0.0', '>=0.7.1', '!=0.8.3'],
        ['!=0.7.6', '!=0.7.7','>=0.16.1,!=0.16.3,!=0.16.4'],
        ['>=0.6.2,>=0.6.1,!=0.6.2,!=0.6.2', '!=0.7.7'],
        ['>=0.6.2,>=0.6.1,!=0.6.3,!=0.6.4', '!=0.6.2'],
        ['!=0.7.7', '>=0.16.1', '~=1.1']
    ]

    for index, scenario in enumerate(scenarios):
        result = [spec.full_spec for spec in sort_spec_list(scenario)]
        assert(result == success_results[index])
