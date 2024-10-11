#Install flake8 and flake8-annotations
pip install flake8 flake8-annotations
#Create a flake8 Configuration
[flake8]
max-line-length = 88
exclude = .git,__pycache__,build,dist
select = ANN
#Write a Python Script to Automatically Find and Replace Type Comments
import ast
import re

def find_type_comments(code):
    """Find type comments using regex."""
    pattern = re.compile(r'# type: \((.*?)\) -> (.*?)\n')
    return pattern.findall(code)

def replace_type_comments(code):
    """Replace type comments with Python 3 inline type annotations."""
    # Matches lines like: # type: (int, str) -> None
    pattern = re.compile(r'# type: \((.*?)\) -> (.*?)\n')

    def replacer(match):
        arg_types = match.group(1).split(", ")
        return_type = match.group(2)

        # Assuming function definition is right above the type comment
        func_def = re.search(r'def (.*?):\n', code[:match.start()])
        if func_def:
            func_header = code[func_def.start():func_def.end()]

            # Parse the function signature
            tree = ast.parse(func_header)
            func = tree.body[0]
            args = func.args.args
            new_func_header = func_header

            # Add type annotations to function parameters
            for i, arg in enumerate(args):
                if i < len(arg_types):
                    arg_type = arg_types[i]
                    # Replace the argument with a type annotation
                    new_func_header = re.sub(
                        r'(?<=\b' + arg.arg + r'\b)',
                        f': {arg_type}',
                        new_func_header
                    )

            # Add return type annotation
            new_func_header = new_func_header.rstrip(":\n") + f" -> {return_type}:\n"
            return new_func_header

        return match.group(0)

    # Replace all type comments
    return pattern.sub(replacer, code)

def process_file(filename):
    """Read, process, and write the modified file."""
    with open(filename, 'r') as f:
        code = f.read()

    # Find and replace type comments
    new_code = replace_type_comments(code)

    with open(filename, 'w') as f:
        f.write(new_code)

if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python replace_type_comments.py <directory_or_file>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        process_file(target)
    else:
        for dirpath, _, filenames in os.walk(target):
            for filename in filenames:
                if filename.endswith(".py"):
                    process_file(os.path.join(dirpath, filename))
#find_type_comments(code): Uses regex to find the old-style type comments (# type: (args) -> return_type).
replace_type_comments(code): Replaces old-style type comments with Python 3 inline annotations by parsing the function signature and modifying it.
process_file(filename): Reads the code from a file, applies the replacement, and writes the updated code back to the file.
Main function: You can run the script on a specific file or a directory containing Python files, and it will automatically process each file.
#Usage- Run the script like this
python replace_type_comments.py <directory_or_file>
#python replace_type_comments.py src/
#Before running the script, you might have this code:def function(self, max_wait_time, **kwargs):
    # type: (int, Any) -> None
    pass
#After running the script, it will be automatically transformed into:def function(self, max_wait_time: int, **kwargs: Any) -> None:
    pass




  
