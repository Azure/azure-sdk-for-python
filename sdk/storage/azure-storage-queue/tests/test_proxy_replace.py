
import os
import re
import sys

removes = [
    re.compile(r'@AsyncStorageTestCase.await_prepared_test')
]

replacements = {
    re.compile(r'self.assertTrue\((.*)\)'):                     r'assert \1',
    re.compile(r'self.assertIsNotNone\((.*)\)'):                r'assert \1 is not None',
    re.compile(r'self.assertEqual\((.*), (.*)\)'):              r'assert \1 == \2',
    re.compile(r'self.assertIn\((.*), (.*)\)'):                 r'assert \1 in \2',
    re.compile(r'self.assertIsNone\((.*)\)'):                   r'assert \1 is None',
    re.compile(r'self.assertFalse\((.*)\)'):                    r'assert not \1',
    re.compile(r'self.assertNotEqual\((.*), (.*)\)'):           r'assert \1 != \2',
    re.compile(r'self.assertIsInstance\((.*), (.*)\)'):         r'assert isinstance(\1, \2)',
    re.compile(r'self.assertRaises\('):                         r'pytest.raises(',
    re.compile(r'self.assertListEqual\((.*), (.*)\)'):          r'assert \1 == \2',
    re.compile(r'self.assertDictEqual\((.*), (.*)\)'):          r'assert \1 == \2',
    re.compile(r'self.assertGreaterEqual\((.*), (.*)\)'):       r'assert \1 >= \2',

    re.compile(r'^(\s*)(|async )def test_(\S*?)(?:_async)?\(self, (\S*), (\S*)(?:|, \*\*kwargs)\):'):          r'\1\2def test_\3(self, **kwargs):\n\1    \4 = kwargs.pop("\4")\n\1    \5 = kwargs.pop("\5")\n',
    re.compile(r'^(\s*)(|async )def test_(\S*?)(?:_async)?\(self, (\S*), (\S*), (\S*)(?:|, \*\*kwargs)\):'):   r'\1\2def test_\3(self, **kwargs):\n\1    \4 = kwargs.pop("\4")\n\1    \5 = kwargs.pop("\5")\n\1    \6 = kwargs.pop("\6")\n'
}

try:
    input_file = sys.argv[1]
except IndexError:
    print(f'Usage: python {os.path.basename(__file__)} <input-file>')
    exit()

def process_line(line):
    # Skip lines that should be removed entirely
    for remove in removes:
        if remove.search(line):
            return ""

    # Replace lines that need replacing
    for regex, replace in replacements.items():
        line = re.sub(regex, replace, line)
    return line

buffer = ""
with open (input_file, 'r') as input:
    for line in input:
       buffer += process_line(line)

with open (input_file, 'w') as output:
    output.write(buffer)
