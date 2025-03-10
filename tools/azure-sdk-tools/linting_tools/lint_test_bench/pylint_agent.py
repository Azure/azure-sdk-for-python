from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
import os
import re
import base64
from azure.identity import get_bearer_token_provider
from pathlib import Path
from datetime import datetime
import shutil
import json

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=os.environ["AZURE_OPENAI_VERSION"], # Update this to the latest API version
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
)

pylint_scores = {}

def ensure_directories():
    """Create necessary directories for file organization."""
    base_dir = Path(__file__).parent
    dirs = ['test_files', 'fixed_files', 'backup_files', 'fixed_files_without_comments', 'test_files_without_comment']
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(exist_ok=True)
    return base_dir

def get_test_cases_from_github():
    """
    Read test cases from local test_files directory.
    Returns:
        list: A list of dictionaries containing file name and content
    """
    try:
        test_cases = []
        test_files_dir = Path(__file__).parent / 'test_files_without_comment'
        
        # Create test_files directory if it doesn't exist
        test_files_dir.mkdir(exist_ok=True)
        
        # Read all .py files from test_files directory
        for test_file in test_files_dir.glob('*.py'):
            with open(test_file, 'r', encoding='utf-8') as f:
                test_cases.append({
                    'name': test_file.name,
                    'content': f
                })
        
        if not test_cases:
            print("Warning: No test files found in test_files directory")
            # Fallback to default test case
        
        return test_cases
    except Exception as e:
        print(f"Error reading test cases from local directory: {e}")
        return []

def fix_file(file_path: str) -> dict:
    """
    Fix pylint issues in the given file and save the changes.
    Args:
        file_path: Path to the file that needs fixing
    Returns:
        dict: Status of the operation including original and fixed content
    """
    try:
        base_dir = ensure_directories()
        file_name = Path(file_path).name
        
        # Define output paths
        fixed_path = base_dir / 'fixed_files' / f"{file_name}_fixed.{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        # fixed_path = base_dir / 'fixed_files_without_comments' / f"{file_name}_fixed.{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        # backup_path = base_dir / 'backup_files' / f"{file_name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"

        # Read the original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Create backup
        # shutil.copy2(file_path, backup_path)

        # added "run pylint"
        fix_file_prompt = "You are a helpful assistant that fixes pylint warnings and custom pylint warnings from these rules: https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/pylint_guidelines_checker.py. \
                 Given a python file that has a pylint issue, you will identify the issue and output ONLY the fixed code. Any explainations need to be outputted as python comments."
        print(f"PROMPT FOR FIXING FILE: {fix_file_prompt}")
        

        # Get fixed content from Azure OpenAI
        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": fix_file_prompt},
                {"role": "user", "content": f"Fix pylint issues in this code:\n\n{original_content}"}
            ],
        )
        
        fixed_content = response.choices[0].message.content.strip()
        
        # Remove any markdown code blocks if they exist
        fixed_content = fixed_content.replace('```python', '').replace('```', '').strip()

        # Write fixed content to fixed_files directory
        with open(fixed_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return {
            'status': 'success',
            'original_file': file_path,
            'fixed_file': fixed_path,
            # 'backup_file': backup_path,
            'original_content': original_content,
            'fixed_content': fixed_content
        }

    except Exception as e:
        print(f"Error while fixing file: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'file': file_path
        }

def run_pylint(file_path: str) -> dict:
    """
    Run pylint on the given file using the project's pylintrc configuration.
    Args:
        file_path: Path to the file to analyze
    Returns:
        dict: Pylint analysis results including score and messages
    """
    try:
        from pylint.lint import Run
        from pylint.reporters import JSONReporter
        from io import StringIO
        import json

        # Get path to pylintrc
        pylintrc_path = Path(__file__).parent / '.pylintrc'
        
        if not pylintrc_path.exists():
            raise FileNotFoundError(f"pylintrc not found at {pylintrc_path}")

        # Create string buffer for JSON output
        output = StringIO()
        reporter = JSONReporter(output)

        # Run pylint with configuration
        results = Run(
            [
                str(file_path),
                f'--rcfile={pylintrc_path}',
                '--output-format=json'
            ],
            exit=False
        )

        print(f"PYLINT SCORE: {results.linter.stats.global_note}")
        try:
            pylint_scores[file_path.split("/")[-1]].append(results.linter.stats.global_note)
        except:
            pylint_scores[file_path.split("/")[-1]] = [results.linter.stats.global_note]

        # Parse JSON output
        # result = json.loads(output.getvalue())
        
        return {
            'status': 'success',
            'messages': results,
            'score': results[0]['message-id'] if result else 10.0,
            'file': file_path
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file': file_path
        }

def get_azure_llm_issue_creation(prompt: str) -> str:
    """
    Get a response from Azure OpenAI LLM using DefaultAzureCredential.
    """
    try:
        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_MODEL"],  # Update this to your deployed model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant that fixes pylint issues. \
                 You will be given a custom pylint rule and you will create a test case for it."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error while communicating with Azure OpenAI: {e}")
        return None

# Example usage
if __name__ == "__main__":
    ensure_directories()
    test_cases = get_test_cases_from_github()
    
    for test_case in test_cases:
        file_path = Path(__file__).parent / 'test_files' / test_case['name']
        # file_path = Path(__file__).parent / 'test_files_without_comment' / test_case['name']
        
        # Fix the file and get results
        result = fix_file(str(file_path))
      
        if result['status'] == 'success':
            print("-----"*80)
            print(f"Fixed file: {result['fixed_file']}")
            # print(f"Backup created at: {result['backup_file']}")
            print("-----"*80)
            
            # Run pylint on both original and fixed files
            print("Running pylint on original file...")
            original_pylint = run_pylint(str(file_path))
            print("-----"*80)
            print("Running pylint on fixed file...")
            fixed_pylint = run_pylint(str(result['fixed_file']))
            print("-----"*80)
            print("\n\n\n")     
        else:
            print(f"Error fixing file {file_path}: {result['error']}")
    
    for key, value in pylint_scores.items():
        print(f"{key}: {value}")
        print("-----"*80)
