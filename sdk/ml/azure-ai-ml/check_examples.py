import os
import re
import sys


def find_definitions_in_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Regular expression to find class and method definitions
    pattern = r"\b(class|def)\s+(\w+)\s*(\([^)]*\))?\s*:(?:(?![\w\s]*\bclass\b)[\s\S])*?"
    definitions = re.findall(pattern, content)
    return definitions


# Function to check if the given docstring contains ".. admonition:: Example:"
def missing_example_admonition(docstring):
    return ".. admonition:: Example:" not in docstring


def separate_docstring(data):
    pattern = r'("""(.*?)""",)'
    matches = re.findall(pattern, data, re.DOTALL)

    # Extract docstrings and create an iterable object
    docstrings = [match[0] for match in matches]

    return docstrings


# Function to process a Python file and check docstrings
def process_python_file(file_path, missing_examples):
    definitions = find_definitions_in_file(file_path)
    counter = 0

    with open(file_path, "r") as file:
        content = file.read()

    pattern = r'(["\']{3}(.*?)["\']{3}(?:.*?))(\n|$)'
    docstrings = [match[0] for match in re.findall(pattern, content, re.DOTALL)]

    for obj_type, name, _ in definitions:
        if docstrings:
            try:
                docstring = docstrings[counter]
                counter += 2
            except IndexError:
                docstring = docstrings[0]

            if obj_type == "class" and not name.startswith("_"):
                if missing_example_admonition(docstring):
                    if "ignore: no-inline-example" in content:
                        print(f"Ignoring {name} in {file_path} due to 'ignore: no-inline-example' comment.")
                    else:
                        missing_examples.append(f"Inline code example missing for class {name} in {file_path}")
            elif obj_type == "def" and not name.startswith("_"):
                if missing_example_admonition(docstring):
                    if "ignore: no-inline-example" in content:
                        print(f"Ignoring {name} in {file_path} due to 'ignore: no-inline-example' comment.")
                    else:
                        missing_examples.append(f"Inline code example missing for method {name}() in {file_path}")
            docstrings.pop()


# Main function to traverse the directory and analyze Python files
def main(directory):
    missing_examples = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                process_python_file(file_path, missing_examples)

    if missing_examples:
        print(f"Found {len(missing_examples)} objects missing reference documentation examples:")
        for example in missing_examples:
            print(f"  {example}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    main(directory)
