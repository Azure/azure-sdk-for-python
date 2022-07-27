from ast import Assert, parse
from ci_tools.parsing import parse_require, ParsedSetup
from packaging.specifiers import SpecifierSet

def test_parse_require():
   test_scenarios = [
      "ConfigArgParse>=0.12.0",
      "msrest>=0.6.10",
      "azure-core<2.0.0,>=1.2.2",
      "msrest==0.6.10",
      "msrest<0.6.10",
      "msrest>0.6.9",
   ]

   for scenario in test_scenarios:
      result = parse_require(scenario)

      Assert(result[0] is not None)
      Assert(result[1] is not None)
      Assert(result[1] is SpecifierSet)

def test_parse_require_with_no_spec():
   spec_scenarios = [
      "readme_renderer"
   ]

   for scenario in spec_scenarios:
      result = parse_require(scenario)

      Assert(result[0] == scenario)
      Assert(result[1] is None)