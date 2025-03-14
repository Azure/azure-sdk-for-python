import os
import re
import subprocess
from github import Github, Auth

def get_issues_with_title(title):
    # Github
    GIT_TOKEN = os.environ["GH_TOKEN"]
    auth = Auth.Token(GIT_TOKEN)
    github = Github(auth=auth)
    repo = github.get_repo("Azure/azure-sdk-for-python")
    issues = list(repo.get_issues(state="open"))
    
    # Filter issues based on title
    filtered_issues = [issue for issue in issues if title in issue.title]
    return filtered_issues
def parse_service_directory(issue_body):
    # Use regex to find the service directory
    match = re.search(r'Library name:\s*(.*)', issue_body)
    if match:
        return match.group(1).strip()
    return None


title_keyword = "needs linting updates for pylint version 3.2.7"

# Get the issues
issues = get_issues_with_title(title_keyword)

# Initialize a list to store service directories
service_directories = []

# Initialize a list to store service directories and their pylint scores
service_directories_scores = []

# Print the issues and parse the service directory
for issue in issues:
    
    # TODO: For right now we will just do the library name
    # Parse and print the service directory
    service_directory = parse_service_directory(issue.body)
    if service_directory:
        print(f"Service Directory: {service_directory}\n")
        service_directories.append(service_directory)
    else:
        print("Service Directory not found.\n")

# Print the list of service directories
print("List of Service Directories:")
print(service_directories)

# Iterate through the list of service directories and run pip install command
for directory in service_directories:
    try:
        directory = directory.split(" ")[1]
        # Install needed packages
        setup_command = f'pip install tox'
        subprocess.run(setup_command, shell=True)
        
        # Run tox next-pylint command from the project root directory
        command = f'cd /home/llawrence/repos/azure-sdk-for-python && python -m tox -e next-pylint --root sdk/{directory.split("-")[1]}/{directory}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Extract and print the pylint score
        score_match = re.search(r'Your code has been rated at ([\d\.]+)/10', result.stdout)
        if score_match:
            pylint_score = score_match.group(1)
            print(f"Pylint score: {pylint_score}/10")
            service_directories_scores.append((directory, pylint_score))
        else:
            print("Pylint score not found in output.")
            service_directories_scores.append((directory, "N/A"))

    except Exception as e:
        print(f"Error running command for {directory}: {e}")
        service_directories_scores.append((directory, "Error"))

# Write the results to a file
with open("pylint_scores.txt", "w") as file:
    file.write("Service Directory | Pylint Score\n")
    file.write("-----------------|--------------\n")
    for directory, score in service_directories_scores:
        file.write(f"{directory} | {score}\n")
