from os import listdir, walk
import re
from os.path import join, exists

print("| Package                                | Coverage   |")
print("|----------------------------------------|------------|")

pattern = ".\/sdk\/[a-z]+\/azure-mgmt-[a-z-]+$"
dirs = [x[0] for x in walk(".") if re.match(pattern, x[0])]
dirs.sort(key=lambda x: x.split("/").pop())
total_rps = 0
total_packages = 0
manual = 0
auto = 0
none = 0
all = {}
for d in dirs:
    total_packages += 1
    coverage = "-"
    test_dir = join(d, "tests")
    if exists(test_dir):
        test_files = [f for f in listdir(test_dir) if re.match("^test_[a-z_]+.py$", f)]
        has_manual = False
        has_auto = False
        for t in test_files:
            coverage = "M"
            if t.startswith("test_cli_"):
                coverage = "A"
                with open(join(test_dir, t)) as f:
                    content = f.readlines()
                    coverage = [
                        x for x in content if x.startswith("# Coverage %      :")
                    ]
                    coverage = (
                        0 if not coverage else float(coverage[0].split(":").pop())
                    )
                has_auto = True
            else:
                has_manual = True
        manual += 1 if has_manual else 0
        auto += 1 if has_auto else 0
    else:
        none += 1
    all[d.split("/").pop()] = coverage

if exists("../azure-rest-api-specs/specification"):
    pattern = ".+/resource-manager$"
    dirs = [
        x[0]
        for x in walk("../azure-rest-api-specs/specification")
        if re.match(pattern, x[0])
    ]
    total = 0
    have_python = 0
    packages = []
    missing = []
    for d in dirs:
        rp_name = d.split("/")[-2]
        total_rps += 1
        readme_files = [f for f in listdir(d) if f in ["readme.md", "readme.python.md"]]
        readme_file = None
        if "readme.python.md" in readme_files:
            readme_file = join(d, "readme.python.md")
        elif "readme.md" in readme_files:
            readme_file = join(d, "readme.md")

        if readme_file is None:
            all[rp_name] = "- (R)"
        else:
            with open(readme_file, encoding="utf8") as f:
                content = f.readlines()
                package_name = [
                    x for x in content if x.strip().startswith("package-name: ")
                ]
                if len(package_name) > 0:
                    have_python += 1
                    package_name = package_name[0].split(": ")[1].rstrip()
                    if package_name not in all:
                        all[package_name] = "- (S)"
                else:
                    all[rp_name] = "- (R)"

packages = sorted([x for x in all.keys()])
for p in packages:
    coverage = all[p]
    print(
        "| {:38} | {:10} |".format(
            p,
            coverage
            if coverage in ["- (R)", "- (S)", "-", "A", "M"]
            else "{:4.2f}".format(coverage),
        )
    )

print("| {:38} | {:10} |".format("", ""))
print("| {:38} | {:10} |".format("**TOTAL RPS**", "**{}**".format(total_rps)))
print("| {:38} | {:10} |".format("**TOTAL PACKAGES**", "**{}**".format(total_packages)))
print("| {:38} | {:10} |".format("**MANUAL**", "**{}**".format(manual)))
print(
    "| {:38} | {:10} |".format(
        "**MANUAL %**", "**{:4.2f}**".format(100 * manual / total_packages)
    )
)
print("| {:38} | {:10} |".format("**AUTO**", "**{}**".format(auto)))
print(
    "| {:38} | {:10} |".format(
        "**AUTO %**", "**{:4.2f}**".format(100 * auto / total_packages)
    )
)
print("| {:38} | {:10} |".format("**NONE**", "**{}**".format(none)))
print(
    "| {:38} | {:10} |".format(
        "**NONE %**", "**{:4.2f}**".format(100 * none / total_packages)
    )
)
