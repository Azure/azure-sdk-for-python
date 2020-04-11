from os import listdir, walk
import re
from os.path import join, exists

pattern = ".\/sdk\/[a-z]+\/azure-mgmt-[a-z-]+$" 
dirs = [x[0] for x in walk(".") if re.match(pattern, x[0])]

for d in dirs:
  coverage = "NONE"
  test_dir = join(d, "tests")
  if exists(test_dir):
    test_files = [f for f in listdir(test_dir) if re.match("^test_[a-z_]+.py$", f)]
    for t in test_files:
      coverage = "MANUAL"
      if t.startswith("test_cli_"):
        coverage = "AUTO"
        with open(join(test_dir, t)) as f:
          content = f.readlines()
          coverage = str([x for x in content if x.startswith("# Coverage %      :")])
  print("{:65} : {}".format(d, coverage))
