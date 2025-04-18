from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
import os
import logging
import sys
import uuid
from azure.identity import get_bearer_token_provider
from pathlib import Path
from datetime import datetime
from azure.ai.evaluation import GroundednessEvaluator
from pylint.lint import Run

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)
# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=os.environ["AZURE_OPENAI_VERSION"], # Update this to the latest API version
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
)

EVAL_RESULTS = {}
PYLINT_SCORES = {}

FILE_PROMPT = """
# Pylint

## Running Pylint

## Fixing Pylint Warnings

### Dos and Don'ts
- DO use the table in https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md and the code examples as a guide on how to fix each rule. 
- DO refer to the pylint documentation: https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html.


- DO NOT solve a pylint warning if you are not 100% confident about the answer. If you think your approach might not be the best, stop trying to fix the warning and leave it as is.
- DO NOT create a new file when solving a pylint error, all solutions must remain in the current file.
- DO NOT import a module or modules that do not exist to solve a pylint warning.
- DO NOT add new dependencies or imports to the project to solve a pylint warning.
- DO NOT make larger changes where a smaller change would fix the issue.
- DO NOT change the code style or formatting of the code unless it is necessary to fix a pylint warning.
- DO NOT delete code or files unless it is necessary to fix a warning.

YOU MUST output ONLY the fixed code, and nothing else. no comments, no explanations, no additional text.
"""

def my_custom_logger(logger_name, level=logging.DEBUG):
    """
    Method to return a custom logger with the given name and level
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    format_string = ("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:"
                    "%(lineno)d — %(message)s")
    log_format = logging.Formatter(format_string)

    # Creating and adding the console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Creating and adding the file handler
    file_handler = logging.FileHandler(logger_name, mode='a')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger

def ensure_directories():
    """Create necessary directories for file organization."""
    base_dir = Path(__file__).parent
    dirs = ['test_files', 'fixed_files', 'backup_files', 'output_logs']
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(exist_ok=True)
    return base_dir

def get_test_cases():
    """
    Read test cases from local test_files directory.
    Returns:
        list: A list of dictionaries containing file name and content
    """
    test_cases = []
    test_files_dir = Path(__file__).parent / 'test_files'

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

    return test_cases

def fix_file(file_path: str, logger) -> dict:
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
        fixed_path = base_dir / 'fixed_files' / f"{file_name}_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"

        # Read the original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        logger.debug(f"MODEL: {os.environ['AZURE_OPENAI_MODEL']}")
        

        # Get fixed content from Azure OpenAI
        response = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_MODEL"],
            messages=[
                {"role": "system", "content": FILE_PROMPT},
                {"role": "user", "content": f"Fix pylint issues in this code:\n\n{original_content}"}
            ],
        )
        
        fixed_content = response.choices[0].message.content.strip()
        
        # Remove any markdown code blocks if they exist
        fixed_content = fixed_content.replace('```python', '').replace('```', '').strip()

        logger.debug(f"FIXED CONTENT: {fixed_content}")

        # Write fixed content to fixed_files directory
        with open(fixed_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
            f.write("\n")  # Ensure a newline at the end of the file

        return {
            'status': 'success',
            'original_file': file_path,
            'fixed_file': fixed_path,
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

def run_pylint(file_path: str, logger) -> dict:
    """
    Run pylint on the given file using the project's pylintrc configuration.
    Args:
        file_path: Path to the file to analyze
    Returns:
        dict: Pylint analysis results including score and messages
    """
    try:
        

        # Get path to pylintrc
        pylintrc_path = Path(__file__).parent / '.pylintrc'
        
        if not pylintrc_path.exists():
            raise FileNotFoundError(f"pylintrc not found at {pylintrc_path}")

        # Run pylint with configuration
        results = Run(
            [
                str(file_path),
                f'--rcfile={pylintrc_path}',
                '--output-format=json'
            ],
            exit=False
        )

        messages = results.linter.reporter.messages
        logger.debug(f"PYLINT MESSAGES: {messages}")

        logger.debug(f"PYLINT SCORE: {results.linter.stats.global_note}")
        pylint_name = file_path.split("/")[-1].split(".py")[0]
        try:
            PYLINT_SCORES[pylint_name].append(results.linter.stats.global_note)
        except:
            PYLINT_SCORES[pylint_name] = [results.linter.stats.global_note]

        return results.linter.stats.global_note

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file': file_path
        }

def evaluate_fixes(file_path, original_content, fixed_content):
    """
    Use azure-ai-evaluation to compare the original and fixed content.
    Args:
        file_path (str): The path of the file being evaluated.
        original_content (str): The original file content.
        fixed_content (str): The fixed file content.
    Returns:
        dict: Evaluation results.
    """

    model_config = {
    "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
    "azure_deployment": os.environ['AZURE_OPENAI_MODEL'],
    "api_version": os.environ["AZURE_OPENAI_VERSION"],
    "api_key": os.environ.get("AZURE_OPENAI_KEY"),
    }

    pylint_name = file_path.split("/")[-1].split(".py")[0]

    # Use the evaluate function with the JSONL file
    eval = GroundednessEvaluator(model_config=model_config)

    evaluation_result = eval(context=FILE_PROMPT + f"Fix pylint issues in this code:\n\n{original_content}", response=fixed_content) 
    EVAL_RESULTS[pylint_name] = evaluation_result

# Example usage
if __name__ == "__main__":
    ensure_directories()
    test_cases = get_test_cases()
    next = uuid.uuid4()
    try:
        for test_case in test_cases:
            logger = my_custom_logger(f"Logger_{test_case['name']}_{next}.log")
            logger.debug(test_case['name'])
            file_path = Path(__file__).parent / 'test_files' / test_case['name']
        
            print(f"Processing file: {file_path}")
                
            # Run pylint on both original file
            logger.debug("Running pylint on original file...")
            original_pylint = run_pylint(str(file_path), logger)
            logger.debug("-----"*80)

            fixed_pylint = original_pylint
            counter = 0
            while fixed_pylint != 10 and counter < 3:
                # Fix the file and get results
                logger.debug("Fixing file...")
                result = fix_file(str(file_path), logger)
                logger.debug("Running pylint on fixed file...")
                fixed_pylint = run_pylint(str(result['fixed_file']), logger)

                # Evaluate the fixes
                evaluate_fixes(str(result['fixed_file']), result['original_content'], result['fixed_content'])
    
                # Update file_path for next iteration
                logger.debug("-----"*80)
                file_path = str(result['fixed_file'])
                counter += 1
            logger.debug("-----"*80)
            logger.debug("\n\n\n")
        base_dir = Path(__file__).parent
        with open(f"{base_dir}/output_logs/final_{next}", 'w', encoding='utf-8') as f:
            for key, value in PYLINT_SCORES.items():
                f.write(f"{key}: {value}")
                f.write("\n")
                # Add corresponding evaluation scores if available
                if key in EVAL_RESULTS:
                    f.write(f"Evaluation Results for {key}:")
                    f.write("\n")
                    f.write(f"Groundedness Score: {EVAL_RESULTS[key]}")
                    f.write("\n")
                f.write("\n")
                f.write("-----"*80)
                f.write("\n")
    except Exception as e:
        raise e
