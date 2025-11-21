#!/usr/bin/env python3
"""
Multi-Project Test Orchestrator

Run the same test suite across multiple Azure AI projects in parallel.
Each project uses its own .env file for configuration.

Usage:
    python run_multi_project_tests.py [--config CONFIG_FILE]
    
Example:
    python run_multi_project_tests.py --config multi_project_test_config.json
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from collections import defaultdict
import argparse


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(message: str, color: str = Colors.ENDC):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.ENDC}")


def load_env_file(env_file_path: str) -> Dict[str, str]:
    """Load environment variables from a .env file."""
    env_vars = {}
    
    if not os.path.exists(env_file_path):
        print_colored(f"⚠️  Warning: .env file not found: {env_file_path}", Colors.WARNING)
        return env_vars
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def get_project_from_env(env_file: str) -> str:
    """
    Extract project endpoint from .env file to identify unique projects.
    This is used to group env files that point to the same project.
    """
    env_vars = load_env_file(env_file)
    # Use AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT as the project identifier
    project_endpoint = env_vars.get("AZURE_AI_PROJECTS_TESTS_PROJECT_ENDPOINT", env_file)
    return project_endpoint


def group_env_files_by_project(env_files: List[str]) -> Dict[str, List[str]]:
    """
    Group env files by their project endpoint.
    
    Env files pointing to the same project must run serially to avoid
    conflicts (tests use non-unique agent names). Different projects
    can run in parallel.
    
    Returns:
        Dict mapping project_endpoint -> list of env files for that project
    """
    project_groups = defaultdict(list)
    for env_file in env_files:
        project = get_project_from_env(env_file)
        project_groups[project].append(env_file)
    return dict(project_groups)


def run_project_group_tests(
    env_configs: List[Dict[str, Any]],
    test_suites: List[str],
    output_dir: str,
    pytest_args: List[str],
    timeout_seconds: int
) -> List[Dict[str, Any]]:
    """
    Run tests for all env configs in a project group serially.
    
    This prevents conflicts when running the same tests on the same project
    with different configurations (e.g., different models).
    
    Args:
        env_configs: List of dicts with 'env_file' and optional 'model' keys
    """
    results = []
    for config in env_configs:
        env_file = config["env_file"]
        model = config.get("model")
        result = run_test_suite(env_file, test_suites, output_dir, pytest_args, timeout_seconds, model)
        results.append(result)
    return results


def run_test_suite(
    env_file: str,
    test_suites: List[str],
    output_dir: str,
    pytest_args: List[str],
    timeout_seconds: int = 300,
    model_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run test suite with environment variables from specified .env file.
    
    Args:
        model_override: If specified, overrides AZURE_AI_MODEL_DEPLOYMENT_NAME
    
    Returns a dict with test results.
    """
    # Extract name from env file (e.g., ".env.usw21" -> "usw21", ".env" -> "default")
    env_path = Path(env_file)
    if env_path.name == ".env":
        env_name = "default"
    else:
        # Remove all ".env" prefixes to get the actual name
        env_name = env_path.name.replace(".env.", "").replace(".env", "")
        # Remove "generated." prefix if present for cleaner display
        if env_name.startswith("generated."):
            env_name = env_name.replace("generated.", "", 1)
        if not env_name:
            env_name = "default"
    
    # Append model name if overriding
    if model_override:
        env_name = f"{env_name}.{model_override}"
    
    print_colored(f"\n{'='*80}", Colors.OKBLUE)
    print_colored(f"🚀 Starting test run: {env_name}", Colors.OKBLUE)
    print_colored(f"{'='*80}", Colors.OKBLUE)
    
    start_time = time.time()
    
    # Load environment variables
    env_vars = load_env_file(env_file)
    print_colored(f"✅ Loaded {len(env_vars)} environment variables from {env_file}", Colors.OKGREEN)
    
    # Create output directory for this run (output_dir is already the timestamped run folder)
    run_output_dir = os.path.join(output_dir, env_name)
    os.makedirs(run_output_dir, exist_ok=True)
    
    # Define paths for structured test reports
    html_report_path = os.path.join(run_output_dir, "report.html")
    json_report_path = os.path.join(run_output_dir, "report.json")
    
    # Build pytest command with structured report outputs
    pytest_cmd = [
        "uv", "run", "pytest"
    ] + test_suites + [
        f"--html={html_report_path}",
        "--self-contained-html",  # Embed assets in HTML for portability
        f"--json={json_report_path}",
    ] + pytest_args
    
    print_colored(f"📝 Command: {' '.join(pytest_cmd)}", Colors.OKCYAN)
    print_colored(f"📁 Output: {run_output_dir}", Colors.OKCYAN)
    
    # Merge current environment with loaded env vars
    test_env = os.environ.copy()
    test_env.update(env_vars)
    
    # Override model deployment name if specified
    if model_override:
        test_env["AZURE_AI_MODEL_DEPLOYMENT_NAME"] = model_override
        test_env["AZURE_AI_PROJECTS_TESTS_MODEL_DEPLOYMENT_NAME"] = model_override
    
    # Tell conftest.py to skip loading .env file
    # This is critical for parallel test runs where each run has its own env vars.
    # Without this, conftest.py would load the .env file and override our env vars,
    # causing all parallel runs to use the same project (whichever is in .env).
    test_env["AZURE_AI_PROJECTS_SKIP_DOTENV"] = "true"
    
    # Force UTF-8 encoding for subprocess output
    # This prevents UnicodeEncodeError on Windows when tests print Unicode characters
    # (like checkmarks ✓) and output is redirected to files.
    test_env["PYTHONIOENCODING"] = "utf-8"
    
    # Run pytest
    result = {
        "env_file": env_file,
        "env_name": env_name,
        "output_dir": run_output_dir,
        "html_report": html_report_path,
        "json_report": json_report_path,
        "start_time": start_time,
        "command": " ".join(pytest_cmd)
    }
    
    # Write output directly to files to avoid subprocess deadlock
    stdout_path = os.path.join(run_output_dir, "stdout.log")
    stderr_path = os.path.join(run_output_dir, "stderr.log")
    
    try:
        with open(stdout_path, 'w') as stdout_f, open(stderr_path, 'w') as stderr_f:
            process = subprocess.run(
                pytest_cmd,
                env=test_env,
                stdout=stdout_f,
                stderr=stderr_f,
                timeout=timeout_seconds
            )
        
        result["exit_code"] = process.returncode
        result["success"] = process.returncode == 0
        
        # Read back the output for parsing (use UTF-8 encoding)
        with open(stdout_path, 'r', encoding='utf-8') as f:
            stdout_content = f.read()
            result["stdout"] = stdout_content
        
        with open(stderr_path, 'r', encoding='utf-8') as f:
            result["stderr"] = f.read()
        
        # Parse test counts from pytest output
        # Look for lines like "1 passed, 2 failed in 10.5s"
        stdout_lines = stdout_content.strip().split('\n')
        for line in reversed(stdout_lines):  # Start from end
            if 'passed' in line or 'failed' in line:
                # Try to extract counts
                import re
                passed_match = re.search(r'(\d+) passed', line)
                failed_match = re.search(r'(\d+) failed', line)
                skipped_match = re.search(r'(\d+) skipped', line)
                
                # Initialize all counts to 0
                result["tests_passed"] = 0
                result["tests_failed"] = 0
                result["tests_skipped"] = 0
                
                if passed_match:
                    result["tests_passed"] = int(passed_match.group(1))
                if failed_match:
                    result["tests_failed"] = int(failed_match.group(1))
                if skipped_match:
                    result["tests_skipped"] = int(skipped_match.group(1))
                
                result["tests_total"] = result["tests_passed"] + result["tests_failed"] + result["tests_skipped"]
                break
        
    except subprocess.TimeoutExpired:
        result["success"] = False
        result["error"] = "Test run timed out after 1 hour"
        print_colored(f"⏱️  Timeout: {env_name}", Colors.FAIL)
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        print_colored(f"❌ Error in {env_name}: {e}", Colors.FAIL)
    
    result["duration"] = time.time() - start_time
    
    # Print summary
    if result["success"]:
        print_colored(f"\n✅ {env_name} - PASSED", Colors.OKGREEN)
        if "tests_passed" in result:
            print_colored(
                f"   Tests: {result['tests_passed']}/{result['tests_total']} passed "
                f"({result.get('tests_failed', 0)} failed, {result.get('tests_skipped', 0)} skipped)",
                Colors.OKGREEN
            )
    else:
        print_colored(f"\n❌ {env_name} - FAILED", Colors.FAIL)
        if "error" in result:
            print_colored(f"   Error: {result['error']}", Colors.FAIL)
    
    print_colored(f"   Duration: {result['duration']:.2f}s", Colors.OKCYAN)
    print_colored(f"   Output: {run_output_dir}", Colors.OKCYAN)
    print_colored(f"   HTML Report: {html_report_path}", Colors.OKCYAN)
    print_colored(f"   JSON Report: {json_report_path}", Colors.OKCYAN)
    
    return result


def merge_pytest_json_reports(output_dir: str, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Merge all individual pytest JSON reports into a consolidated report.
    
    This function is resilient to failures - it will merge whatever reports
    exist, even if some test runs failed or timed out.
    
    Args:
        output_dir: The run output directory containing subdirectories with report.json files
        results: List of test run results containing json_report paths
        
    Returns:
        Merged report dict, or None if no valid reports found
    """
    merged_report = {
        "created_at": datetime.now().isoformat(),
        "environments": {},
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
            "total_duration": 0.0
        },
        "all_tests": []
    }
    
    reports_found = 0
    
    for result in results:
        json_report_path = result.get("json_report")
        env_name = result.get("env_name", "unknown")
        
        # Check if report file exists
        if not json_report_path or not os.path.exists(json_report_path):
            print_colored(f"⚠️  JSON report not found for {env_name}: {json_report_path}", Colors.WARNING)
            continue
        
        try:
            # Load the pytest-json report
            with open(json_report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            reports_found += 1
            
            # Extract the report data (pytest-json uses "report" as root key)
            if "report" in report_data:
                report = report_data["report"]
            else:
                report = report_data
            
            # Add environment-specific data
            merged_report["environments"][env_name] = {
                "summary": report.get("summary", {}),
                "created_at": report.get("created_at"),
                "test_count": report.get("summary", {}).get("num_tests", 0)
            }
            
            # Add all tests with environment prefix
            tests = report.get("tests", [])
            for test in tests:
                # Add environment identifier to test
                test_copy = test.copy()
                test_copy["environment"] = env_name
                merged_report["all_tests"].append(test_copy)
            
            # Accumulate summary statistics
            summary = report.get("summary", {})
            merged_report["summary"]["total_tests"] += summary.get("num_tests", 0)
            merged_report["summary"]["passed"] += summary.get("passed", 0)
            merged_report["summary"]["failed"] += summary.get("failed", 0)
            merged_report["summary"]["skipped"] += summary.get("skipped", 0)
            merged_report["summary"]["error"] += summary.get("error", 0)
            merged_report["summary"]["total_duration"] += summary.get("duration", 0.0)
            
            print_colored(f"✅ Merged report from {env_name} ({len(tests)} tests)", Colors.OKGREEN)
            
        except Exception as e:
            print_colored(f"⚠️  Failed to merge report from {env_name}: {e}", Colors.WARNING)
            continue
    
    if reports_found == 0:
        print_colored("⚠️  No valid JSON reports found to merge", Colors.WARNING)
        return None
    
    print_colored(f"✅ Successfully merged {reports_found} JSON report(s)", Colors.OKGREEN)
    return merged_report


def generate_summary_report(results: List[Dict[str, Any]], output_dir: str, orchestration_duration: float):
    """Generate a summary report of all test runs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = os.path.join(output_dir, "summary.json")
    
    # Remove stdout/stderr from results for summary (keep in individual log files)
    clean_results = []
    for r in results:
        clean_result = {k: v for k, v in r.items() if k not in ["stdout", "stderr"]}
        clean_results.append(clean_result)
    
    # Calculate totals
    total_passed = sum(r.get("tests_passed", 0) for r in results)
    total_failed = sum(r.get("tests_failed", 0) for r in results)
    total_skipped = sum(r.get("tests_skipped", 0) for r in results)
    # Use actual orchestration wall-clock time
    total_duration = orchestration_duration
    
    summary = {
        "timestamp": timestamp,
        "total_runs": len(results),
        "total_tests_passed": total_passed,
        "total_tests_failed": total_failed,
        "total_tests_skipped": total_skipped,
        "total_duration": total_duration,
        "results": clean_results
    }
    
    # Save summary JSON
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Merge all pytest JSON reports into consolidated report
    print_colored(f"\n{'='*80}", Colors.HEADER)
    print_colored("📊 Merging pytest JSON reports...", Colors.HEADER)
    print_colored(f"{'='*80}", Colors.HEADER)
    
    merged_json = merge_pytest_json_reports(output_dir, results)
    if merged_json:
        merged_json_file = os.path.join(output_dir, "merged_pytest_report.json")
        with open(merged_json_file, 'w', encoding='utf-8') as f:
            json.dump(merged_json, f, indent=2)
        print_colored(f"✅ Merged pytest report: {merged_json_file}", Colors.OKGREEN)
    
    # Print summary table
    print_colored(f"\n{'='*80}", Colors.HEADER)
    print_colored("📊 SUMMARY REPORT", Colors.HEADER)
    print_colored(f"{'='*80}", Colors.HEADER)
    
    print(f"\n{'Environment':<20} {'Passed':<10} {'Failed':<10} {'Skipped':<10} {'Duration':<15}")
    print("-" * 80)
    
    for result in results:
        env_name = result.get("env_name", "unknown")
        passed = result.get("tests_passed", 0)
        failed = result.get("tests_failed", 0)
        skipped = result.get("tests_skipped", 0)
        duration = f"{result.get('duration', 0):.2f}s"
        
        # Use color based on whether tests failed
        color = Colors.OKGREEN if failed == 0 else Colors.FAIL
        print_colored(
            f"{env_name:<20} {passed:<10} {failed:<10} {skipped:<10} {duration:<15}",
            color
        )
    
    # Add totals row
    print("-" * 80)
    print_colored(
        f"{'TOTAL':<20} {total_passed:<10} {total_failed:<10} {total_skipped:<10} {summary['total_duration']:.2f}s",
        Colors.BOLD
    )
    
    print(f"\n📄 Summary: {summary_file}")
    if merged_json:
        merged_json_file = os.path.join(output_dir, "merged_pytest_report.json")
        print(f"📄 Merged pytest report: {merged_json_file}")
    print_colored(f"{'='*80}\n", Colors.HEADER)
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run tests across multiple Azure AI projects in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config',
        default='multi_project_test_config.json',
        help='Path to configuration JSON file (default: multi_project_test_config.json)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if not os.path.exists(args.config):
        print_colored(f"❌ Configuration file not found: {args.config}", Colors.FAIL)
        sys.exit(1)
    
    # Get the directory of the script (not config) to resolve relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # Parent of scripts/ is project root
    config_dir = os.path.dirname(os.path.abspath(args.config))
    
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    # Resolve both env files and test suites relative to project directory
    # This allows configs to be in subdirectories while env files and tests stay in project root
    env_files = [os.path.join(project_dir, ef) if not os.path.isabs(ef) else ef 
                 for ef in config.get("env_files", [])]
    test_suites = [os.path.join(project_dir, ts) if not os.path.isabs(ts) else ts 
                   for ts in config.get("test_suites", [])]
    
    # Resolve output dir relative to project directory (parent of scripts/)
    output_dir_rel = config.get("output_dir", "test_output")
    output_dir_base = os.path.join(project_dir, output_dir_rel) if not os.path.isabs(output_dir_rel) else output_dir_rel
    
    # Create timestamped run folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = os.path.join(output_dir_base, f"run_{timestamp}")
    
    max_parallel = config.get("max_parallel", 4)
    timeout_seconds = config.get("timeout_seconds", 300)
    pytest_args = config.get("pytest_args", ["-v"])
    models = config.get("models", [])
    
    # Expand env files by models if specified
    # Each env_file × model combination becomes a separate test run
    if models:
        env_configs = []
        for env_file in env_files:
            for model in models:
                env_configs.append({"env_file": env_file, "model": model})
    else:
        # No models specified, use env files as-is
        env_configs = [{"env_file": ef, "model": None} for ef in env_files]
    
    print_colored(f"\n{'='*80}", Colors.HEADER)
    print_colored("MULTI-PROJECT TEST ORCHESTRATOR", Colors.HEADER)
    print_colored(f"{'='*80}", Colors.HEADER)
    print(f"\n📋 Configuration: {args.config}")
    print(f"🗂️  Base environments: {len(env_files)}")
    if models:
        print(f"🤖 Models: {len(models)}")
        print(f"📊 Total test runs: {len(env_configs)} ({len(env_files)} envs × {len(models)} models)")
    else:
        print(f"📊 Total test runs: {len(env_configs)}")
    print(f"🧪 Test suites: {len(test_suites)}")
    print(f"⚡ Max parallel: {max_parallel}")
    print(f"⏱️  Timeout per project: {timeout_seconds}s")
    print(f"📁 Output directory: {run_folder}")
    print(f"\n📝 Environment files:")
    for env_file in env_files:
        print(f"   - {env_file}")
    if models:
        print(f"\n� Models:")
        for model in models:
            print(f"   - {model}")
    print(f"\n�🧪 Test suites:")
    for suite in test_suites:
        print(f"   - {suite}")
    
    # Create output directory
    os.makedirs(run_folder, exist_ok=True)
    
    # Group env configs by project to prevent conflicts
    # Extract unique projects and group configs by project
    project_to_configs = defaultdict(list)
    for config_item in env_configs:
        project = get_project_from_env(config_item["env_file"])
        project_to_configs[project].append(config_item)
    project_groups = dict(project_to_configs)
    
    print(f"\n📊 Project grouping:")
    for project_endpoint, group_configs in project_groups.items():
        project_name = project_endpoint.split('/')[-1] if '/' in project_endpoint else project_endpoint
        print(f"   {project_name}: {len(group_configs)} configuration(s)")
        for cfg in group_configs:
            env_base = os.path.basename(cfg["env_file"])
            if cfg.get("model"):
                print(f"      - {env_base} + {cfg['model']}")
            else:
                print(f"      - {env_base}")
    
    # Run tests in parallel (by project, serialized within each project)
    print_colored(f"\n{'='*80}", Colors.OKBLUE)
    print_colored(f"🚀 Starting parallel test execution...", Colors.OKBLUE)
    print_colored(f"   (Projects run in parallel, configs within same project run serially)", Colors.OKBLUE)
    print_colored(f"{'='*80}", Colors.OKBLUE)
    
    # Track wall-clock time for the entire orchestration
    orchestration_start_time = time.time()
    results = []
    
    with ProcessPoolExecutor(max_workers=max_parallel) as executor:
        # Submit one job per project group (each group runs its configs serially)
        future_to_project = {
            executor.submit(
                run_project_group_tests,
                group_configs,
                test_suites,
                run_folder,
                pytest_args,
                timeout_seconds
            ): project_endpoint
            for project_endpoint, group_configs in project_groups.items()
        }
        
        # Collect results as they complete (flatten list of lists)
        for future in as_completed(future_to_project):
            project_endpoint = future_to_project[future]
            try:
                group_results = future.result()  # Returns list of results
                results.extend(group_results)
            except Exception as e:
                print_colored(f"❌ Exception for project {project_endpoint}: {e}", Colors.FAIL)
                # Mark all configs in this group as failed
                group_configs = project_groups[project_endpoint]
                for cfg in group_configs:
                    results.append({
                        "env_file": cfg["env_file"],
                        "success": False,
                        "error": str(e)
                    })
    
    # Calculate actual wall-clock time
    orchestration_duration = time.time() - orchestration_start_time
    
    # Generate summary report
    summary = generate_summary_report(results, run_folder, orchestration_duration)
    
    # Exit with appropriate code - exit with 1 if any tests failed
    if summary["total_tests_failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
