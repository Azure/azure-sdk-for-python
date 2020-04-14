from os import listdir, walk
import re
from os.path import join, exists

pattern = ".+/resource-manager$"
dirs = [x[0] for x in walk("../azure-rest-api-specs/specification") if re.match(pattern, x[0])]
# dirs.sort(key=lambda x: x.split("/").pop())
total = 0
have_python = 0
packages = []
missing = []
for d in dirs:
  total += 1
  readme_files = [f for f in listdir(d) if f in ['readme.md', 'readme.python.md']]
  readme_file = None
  if 'readme.python.md' in readme_files:
    readme_file = join(d, 'readme.python.md')
  elif 'readme.md' in readme_files:
    readme_file = join(d, 'readme.md')

  if readme_file is None:
    missing.append(d)
  if readme_file is not None:
    with open(readme_file, encoding='utf8') as f:
      content = f.readlines()
      package_name = [x for x in content if x.strip().startswith("package-name: ")]
      if len(package_name) > 0:
        have_python += 1
        packages.append(package_name[0].split(': ')[1].rstrip())
      else:
        missing.append(d)

print('MGMT SPECS: ' + str(total))
print('MGMT PKGS : ' + str(have_python))

print('PACKAGES:')
for p in packages:
  print(p)

print('MISSING:')
for m in missing:
  print(m)

