import sys
from pathlib import Path
import re

snippets = {}
not_up_to_date = False

target_snippet_sources = ["samples/*.py", "samples/*/*.py"]
target_md_files = ["README.md"]

def get_snippet(file):
    with open(file, 'r') as f:
        content = f.read()
    pattern = "# \\[START[A-Z a-z0-9_]+\\][\\s\\S]+?# \\[END[A-Z a-z0-9_]+\\]"
    matches = re.findall(pattern, content)
    for match in matches:
        s = match
        pos1 = s.index("[START")
        pos2 = s.index("]")
        name = s[pos1 + 6:pos2].strip()
        s = s[pos2 + 1:]
        pos1 = s.index("# [END")
        snippet = s[:pos1-1]
        # Remove extra spaces
        spaces = ""
        for char in snippet[1:]:
            if char == " ":
                spaces += char
            else:
                break
        snippet = snippet.replace("\n" + spaces, "\n")
        # Remove first newline
        snippet = snippet[1:].rstrip()
        if snippet[-1] == "\n":
            snippet = snippet[:-1]

        file_name = str(file.name)[:-3]
        identifier = ".".join([file_name, name])
        if identifier in snippets.keys():
            print(f'Warning: found duplicated snippet name "{identifier}".')
            print(file)
        # print(f"Found: {file.name}.{name}")
        snippets[identifier] = snippet


def update_snippet(file):
    with open(file, 'r') as f:
        content = f.read()
    pattern = "<!-- SNIPPET:[A-Z a-z0-9_.]+-->[\\s\\S]*?<!-- END SNIPPET -->"
    matches = re.findall(pattern, content)
    for match in matches:
        s = match
        pos1 = s.index("-->")
        header = s[:pos1+3]
        name = s[13:pos1].strip()
        # print(f"Info: found name: {name}")
        if name not in snippets.keys():
            print(f'Warning: cannot found snippet name "{name}".')
            exit(1)
        target = "".join([header, "\n```python\n", snippets[name], "\n```\n", "<!-- END SNIPPET -->"])
        if s != target:
            print(f'Warning: snippet "{name}" is not up to date.')
            global not_up_to_date
            not_up_to_date = True
            content = content.replace(s, target)
    with open(file, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    arg_len = len(sys.argv)
    if arg_len < 2:
        print(f"Usage: PythonSnippetUpdater <path>")
        exit(1)
    path = sys.argv[1]
    print(f"Path: {path}")
    for source in target_snippet_sources:
        for py_file in Path(path).rglob(source):
            try:
                get_snippet(py_file)
            except UnicodeDecodeError:
                pass
    # for key in snippets.keys():
    #     print(f"Info: found snippet: {key}")
    for target in target_md_files:
        for md_file in Path(path).rglob(target):
            try:
                update_snippet(md_file)
            except UnicodeDecodeError:
                pass
    if not_up_to_date:
        print(f'Error: code snippets are out of sync. Please run Python PythonSnippetUpdater.py "{path}" to fix it.')
        exit(1)
    print(f"README.md under {path} is up to date.")