from os import listdir, walk
import re
from os.path import join, exists

print("| Package                                | Coverage   |")
print("|----------------------------------------|------------|")

pattern = ".\/sdk\/[a-z]+\/azure-mgmt-[a-z-]+$" 
dirs = [x[0] for x in walk(".") if re.match(pattern, x[0])]
dirs.sort(key=lambda x: x.split("/").pop())
total = 0
manual = 0
auto = 0
none = 0
for d in dirs:
  total += 1
  coverage = "-"
  test_dir = join(d, "tests")
  if exists(test_dir):
    test_files = [f for f in listdir(test_dir) if re.match("^test_[a-z_]+.py$", f)]
    has_manual = False
    has_auto = False
    for t in test_files:
      coverage = "MANUAL"
      if t.startswith("test_cli_"):
        coverage = "AUTO"
        with open(join(test_dir, t)) as f:
          content = f.readlines()
          coverage = [x for x in content if x.startswith("# Coverage %      :")]
          coverage = 0 if not coverage else float(coverage[0].split(":").pop())
        has_auto = True
      else:
        has_manual = True
    manual += 1 if has_manual else 0
    auto += 1 if has_auto else 0
  else:
    none += 1

  print("| {:38} | {:10} |".format(d.split("/").pop(), coverage if coverage in ["-" , "AUTO", "MANUAL"] else "{:4.2f}".format(coverage)))

print("| {:38} | {:10} |".format("", ""))
print("| {:38} | {:10} |".format("**TOTAL**", "**{}**".format(total)))
print("| {:38} | {:10} |".format("**MANUAL**", "**{}**".format(manual)))
print("| {:38} | {:10} |".format("**MANUAL %**", "**{:4.2f}**".format(100 * manual / total)))
print("| {:38} | {:10} |".format("**AUTO**", "**{}**".format(auto)))
print("| {:38} | {:10} |".format("**AUTO %**", "**{:4.2f}**".format(100 * auto / total)))
print("| {:38} | {:10} |".format("**NONE**", "**{}**".format(none)))
print("| {:38} | {:10} |".format("**NONE %**", "**{:4.2f}**".format(100 * none / total)))


