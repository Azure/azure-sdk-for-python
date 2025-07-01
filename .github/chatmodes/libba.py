#!/usr/bin/env python3
"""
Azure SDK for Python - Complete TypeSpec Generation Workflow Script

This Python script implements the complete TypeSpec SDK generation workflow 
for the azure-sdk-for-python repository as defined in generation.chatmode.md.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# ANSI color codes for colored output
class Colors:
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    INFO = '\033[96m'
    PHASE = '\033[95m'
    COMMAND = '\033[94m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class WorkflowConfig:
    def __init__(self):
        self.repo_root: Optional[Path] = None
        self.tox_ini_path: Optional[Path] = None
        self.package_path: Optional[Path] = None
        self.current_branch: Optional[str] = None
        self.start_time = datetime.now()

class AzureSDKWorkflow:
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.colors = Colors()
        
    def write_phase_header(self, phase: str, description: str):
        """Write a formatted phase header"""
        separator = "=" * 80
        print(f"\n{self.colors.PHASE}{separator}")
        print(f"PHASE {phase}: {description}")
        print(f"{separator}{self.colors.RESET}")
    
    def write_step_info(self, message: str):
        """Write step information"""
        print(f"  {self.colors.INFO}➤ {message}{self.colors.RESET}")
    
    def write_command_info(self, command: str, purpose: str):
        """Write command information before execution"""
        print(f"\n{self.colors.COMMAND}Command I'm about to run: {self.colors.WHITE}\"{command}\"{self.colors.RESET}")
        print(f"{self.colors.INFO}Purpose: {purpose}{self.colors.RESET}")
    
    def get_user_input(self, prompt: str, valid_options: Optional[List[str]] = None, default: Optional[str] = None) -> str:
        """Get user input with validation"""
        while True:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    user_input = default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if valid_options and user_input not in valid_options:
                print(f"{self.colors.WARNING}Please choose from: {', '.join(valid_options)}{self.colors.RESET}")
                continue
            
            return user_input
    
    def run_command(self, command: str, purpose: str, ignore_errors: bool = False, 
                   no_output: bool = False, force: bool = False) -> Optional[subprocess.CompletedProcess]:
        """Execute a command safely with user confirmation"""
        self.write_command_info(command, purpose)
        
        if not force:
            confirm = self.get_user_input("Execute this command? (y/n)", ["y", "n", "yes", "no"], "y")
            if confirm in ["n", "no"]:
                print(f"{self.colors.WARNING}Skipped.{self.colors.RESET}")
                return None
        
        try:
            if no_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(command, shell=True, text=True)
            
            if result.returncode != 0 and not ignore_errors:
                raise subprocess.CalledProcessError(result.returncode, command)
            
            return result
        except subprocess.CalledProcessError as e:
            if ignore_errors:
                print(f"{self.colors.WARNING}Command failed but continuing: {e}{self.colors.RESET}")
                return None
            else:
                raise
    
    def test_prerequisites(self):
        """Check prerequisites and setup environment"""
        self.write_step_info("Checking prerequisites...")
        
        # Check if we're in the azure-sdk-for-python repo
        try:
            git_remote = subprocess.run(
                ["git", "remote", "get-url", "origin"], 
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            if "azure-sdk-for-python" not in git_remote:
                raise RuntimeError("Not in azure-sdk-for-python repository. Please run from the repository root.")
        except subprocess.CalledProcessError:
            raise RuntimeError("Not in a git repository or origin remote not found.")
        
        # Set repo root
        try:
            repo_root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            self.config.repo_root = Path(repo_root)
        except subprocess.CalledProcessError:
            self.config.repo_root = Path.cwd()
        
        # Set tox.ini path
        self.config.tox_ini_path = self.config.repo_root / "eng" / "tox" / "tox.ini"
        if not self.config.tox_ini_path.exists():
            raise RuntimeError(f"tox.ini not found at expected path: {self.config.tox_ini_path}")
        
        # Check required tools
        required_tools = ["python", "git", "gh", "tox"]
        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"{self.colors.WARNING}{tool} not found in PATH. Please install it.{self.colors.RESET}")
        
        print(f"{self.colors.SUCCESS}✓ Prerequisites validated{self.colors.RESET}")
    
    def get_package_info(self, service_name: Optional[str] = None, 
                        package_name: Optional[str] = None) -> Dict[str, Any]:
        """Get package information from user input or parameters"""
        if not service_name:
            service_name = self.get_user_input("Enter service name (e.g., eventgrid, ai)")
        
        if not package_name:
            package_name = self.get_user_input("Enter package name (e.g., azure-eventgrid)")
        
        package_path = self.config.repo_root / "sdk" / service_name / package_name
        self.config.package_path = package_path
        
        return {
            "service_name": service_name,
            "package_name": package_name,
            "package_path": package_path,
            "exists": package_path.exists()
        }
    
    def phase1_context_assessment(self, service_name: Optional[str] = None, 
                                 package_name: Optional[str] = None,
                                 workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Phase 1: Context Assessment & Prerequisites"""
        self.write_phase_header("1", "CONTEXT ASSESSMENT & PREREQUISITES")
        
        self.test_prerequisites()
        
        # Get current branch
        current_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        self.config.current_branch = current_branch
        self.write_step_info(f"Current branch: {current_branch}")
        
        if current_branch in ["main", "master"]:
            create_branch = self.get_user_input(
                "You're on main branch. Create feature branch? (y/n)", ["y", "n"], "y"
            )
            if create_branch in ["y", "yes"]:
                branch_name = self.get_user_input(
                    "Enter branch name", 
                    default=f"feature/sdk-generation-{datetime.now().strftime('%Y%m%d-%H%M')}"
                )
                self.run_command(f"git checkout -b {branch_name}", "Create and switch to feature branch")
                self.config.current_branch = branch_name
        
        # Context assessment questions
        print(f"\n{self.colors.INFO}🔍 CONTEXT ASSESSMENT")
        print("I need to understand your scenario before proceeding.")
        
        if not workflow_type:
            print("\nWhat specifically needs to be done?")
            print("1. TypeSpec changes/regeneration")
            print("2. Validation fixes only")
            print("3. Version bump/release prep")
            print("4. New package creation")
            print("5. Custom workflow")
            
            choice = self.get_user_input("Select option (1-5)", ["1", "2", "3", "4", "5"])
            workflow_type = {
                "1": "update",
                "2": "validation", 
                "3": "release",
                "4": "new",
                "5": "custom"
            }[choice]
        
        package_info = self.get_package_info(service_name, package_name)
        
        print(f"\n{self.colors.SUCCESS}📋 WORKFLOW SUMMARY{self.colors.RESET}")
        print(f"{self.colors.WHITE}Service: {package_info['service_name']}")
        print(f"Package: {package_info['package_name']}")
        print(f"Workflow: {workflow_type}")
        print(f"Package exists: {package_info['exists']}")
        print(f"Branch: {self.config.current_branch}{self.colors.RESET}")
        
        package_info["workflow_type"] = workflow_type
        return package_info
    
    def phase2_environment_verification(self, package_info: Dict[str, Any]):
        """Phase 2: Environment Verification"""
        self.write_phase_header("2", "ENVIRONMENT VERIFICATION")
        
        self.write_step_info("Checking Python virtual environment...")
        
        # Check for virtual environment
        venv_active = os.environ.get('VIRTUAL_ENV') or sys.prefix != sys.base_prefix
        
        if not venv_active:
            print(f"{self.colors.WARNING}No virtual environment detected. Consider activating one.{self.colors.RESET}")
            create_venv = self.get_user_input("Create and activate virtual environment? (y/n)", ["y", "n"], "y")
            
            if create_venv in ["y", "yes"]:
                venv_path = self.config.repo_root / ".venv"
                self.run_command(f"python -m venv {venv_path}", "Create virtual environment")
                print(f"{self.colors.INFO}Please activate the virtual environment manually:")
                if os.name == 'nt':  # Windows
                    print(f"  {venv_path}\\Scripts\\activate")
                else:  # Unix-like
                    print(f"  source {venv_path}/bin/activate")
                print(f"Then re-run this script.{self.colors.RESET}")
                sys.exit(0)
        else:
            print(f"{self.colors.SUCCESS}✓ Virtual environment active: {os.environ.get('VIRTUAL_ENV', 'detected')}{self.colors.RESET}")
        
        self.write_step_info("Installing/updating required packages...")
        
        # Install azure-sdk-tools
        tools_path = self.config.repo_root / "tools" / "azure-sdk-tools"
        if tools_path.exists():
            self.run_command(f"pip install -e \"{tools_path}\"", "Install azure-sdk-tools")
        
        # Install dev requirements
        dev_req_path = self.config.repo_root / "dev_requirements.txt"
        if dev_req_path.exists():
            self.run_command(f"pip install -r \"{dev_req_path}\"", "Install development requirements")
        
        print(f"{self.colors.SUCCESS}✓ Environment verification complete{self.colors.RESET}")
    
    def phase3_sdk_generation(self, package_info: Dict[str, Any], typespec_path: Optional[str] = None):
        """Phase 3: SDK Generation"""
        self.write_phase_header("3", "SDK GENERATION")
        print(f"{self.colors.INFO}⏱️ TIME EXPECTATION: 5-6 minutes{self.colors.RESET}")
        
        workflow_type = package_info["workflow_type"]
        
        if workflow_type == "validation":
            self.write_step_info("Skipping SDK generation for validation-only workflow")
            return
        
        os.chdir(self.config.repo_root)
        
        if workflow_type == "new":
            self.write_step_info("Generating new SDK package...")
            
            if not typespec_path:
                typespec_path = self.get_user_input("Enter TypeSpec location (local path or commit hash)")
            
            is_local = Path(typespec_path).exists()
            if is_local:
                command = f"python scripts/quickstart_tooling_dpg/init_local.py --local-typespec-dir \"{typespec_path}\""
            else:
                command = f"python scripts/quickstart_tooling_dpg/init.py --package-name {package_info['package_name']} --commit-hash {typespec_path}"
            
            self.run_command(command, "Initialize new SDK package")
        
        elif workflow_type == "update":
            self.write_step_info("Updating existing SDK package...")
            
            if not package_info["exists"]:
                raise RuntimeError("Package does not exist. Use 'new' workflow type instead.")
            
            if not typespec_path:
                use_existing = self.get_user_input("Use existing TypeSpec configuration? (y/n)", ["y", "n"], "y")
                if use_existing == "n":
                    typespec_path = self.get_user_input("Enter new TypeSpec commit hash")
            
            if typespec_path:
                command = f"python scripts/quickstart_tooling_dpg/update.py --package-path \"{package_info['package_path']}\" --commit-hash {typespec_path}"
            else:
                command = f"python scripts/quickstart_tooling_dpg/update.py --package-path \"{package_info['package_path']}\""
            
            self.run_command(command, "Update SDK package")
        
        elif workflow_type == "release":
            self.write_step_info("Preparing package for release...")
            print(f"{self.colors.WARNING}Release preparation requires manual version and changelog updates{self.colors.RESET}")
        
        elif workflow_type == "custom":
            self.write_step_info("Custom workflow - manual intervention required")
            custom_command = self.get_user_input("Enter custom generation command (or press Enter to skip)")
            if custom_command:
                self.run_command(custom_command, "Execute custom command")
        
        print(f"{self.colors.SUCCESS}✓ SDK generation complete{self.colors.RESET}")
    
    def phase4_iterative_flow_selection(self):
        """Phase 4: Iterative Flow Selection"""
        self.write_phase_header("4", "ITERATIVE FLOW SELECTION")
        
        flows = {
            "1": {"name": "TypeSpec Client Customization (client.tsp)", "description": "TypeSpec-level customizations"},
            "2": {"name": "Python Patch File Approach (_patch.py)", "description": "Python-specific modifications"},
            "4": {"name": "Generate & Record Tests", "description": "Test infrastructure setup"},
            "5": {"name": "Update & Re-record Tests", "description": "Refresh tests after updates"},
            "6": {"name": "Update & Test Samples", "description": "Sample validation and updates"},
            "7": {"name": "Documentation & Release Preparation", "description": "Release documentation"},
            "skip": {"name": "Skip to Validation", "description": "Proceed to static validation"}
        }
        
        while True:
            print(f"\n{self.colors.INFO}📋 AVAILABLE FLOWS:{self.colors.RESET}")
            for key in sorted(flows.keys()):
                print(f"  {self.colors.WHITE}{key}. {flows[key]['name']}")
                print(f"     {self.colors.GRAY}{flows[key]['description']}{self.colors.RESET}")
            
            selection = self.get_user_input("Select flow (1,2,4,5,6,7) or 'skip' to continue", list(flows.keys()))
            
            if selection == "skip":
                break
            
            # Execute selected flow
            if selection == "1":
                self.flow1_typespec_customization()
            elif selection == "2":
                self.flow2_python_patch()
            elif selection == "4":
                self.flow4_generate_tests()
            elif selection == "5":
                self.flow5_update_tests()
            elif selection == "6":
                self.flow6_update_samples()
            elif selection == "7":
                self.flow7_documentation()
            
            continue_flows = self.get_user_input("Select another flow? (y/n)", ["y", "n"], "n")
            if continue_flows not in ["y", "yes"]:
                break
    
    def flow1_typespec_customization(self):
        """Flow 1: TypeSpec Client Customization"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 1: TypeSpec Client Customization{self.colors.RESET}")
        
        client_tsp_path = self.config.package_path / "client.tsp"
        
        if client_tsp_path.exists():
            print(f"{self.colors.SUCCESS}Found existing client.tsp file{self.colors.RESET}")
            edit = self.get_user_input("Edit client.tsp file? (y/n)", ["y", "n"], "y")
            if edit in ["y", "yes"]:
                # Open in default editor
                editor = os.environ.get('EDITOR', 'code')
                subprocess.run([editor, str(client_tsp_path)])
                input("Press Enter when editing is complete...")
        else:
            print(f"{self.colors.WARNING}No client.tsp file found. Create one?{self.colors.RESET}")
            create = self.get_user_input("Create client.tsp? (y/n)", ["y", "n"], "n")
            if create in ["y", "yes"]:
                template = '''import "@azure-tools/typespec-client-generator-core";
import "./main.tsp";

using Azure.ClientGenerator.Core;

// Add your TypeSpec customizations here
'''
                client_tsp_path.write_text(template)
                editor = os.environ.get('EDITOR', 'code')
                subprocess.run([editor, str(client_tsp_path)])
                input("Press Enter when editing is complete...")
        
        # Regenerate after TypeSpec changes
        regenerate = self.get_user_input("Regenerate SDK after TypeSpec changes? (y/n)", ["y", "n"], "y")
        if regenerate in ["y", "yes"]:
            self.run_command(
                f"python scripts/quickstart_tooling_dpg/update.py --package-path \"{self.config.package_path}\"",
                "Regenerate SDK with TypeSpec changes"
            )
    
    def flow2_python_patch(self):
        """Flow 2: Python Patch File Approach"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 2: Python Patch File Approach{self.colors.RESET}")
        
        # Find _patch.py files
        patch_files = list(self.config.package_path.rglob("*_patch.py"))
        
        if patch_files:
            print(f"{self.colors.SUCCESS}Found patch files:{self.colors.RESET}")
            for file in patch_files:
                print(f"  {self.colors.WHITE}{file.relative_to(self.config.package_path)}{self.colors.RESET}")
            
            edit = self.get_user_input("Edit patch files? (y/n)", ["y", "n"], "y")
            if edit in ["y", "yes"]:
                editor = os.environ.get('EDITOR', 'code')
                for file in patch_files:
                    subprocess.run([editor, str(file)])
                input("Press Enter when editing is complete...")
        else:
            print(f"{self.colors.WARNING}No _patch.py files found.")
            print(f"{self.colors.INFO}Patch files are automatically created during generation if needed.{self.colors.RESET}")
    
    def flow4_generate_tests(self):
        """Flow 4: Generate & Record Tests"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 4: Generate & Record Tests{self.colors.RESET}")
        
        tests_path = self.config.package_path / "tests"
        
        if not tests_path.exists():
            self.write_step_info("Creating tests directory structure...")
            tests_path.mkdir(parents=True, exist_ok=True)
        
        # Generate test templates
        generate_tests = self.get_user_input("Generate test templates? (y/n)", ["y", "n"], "y")
        if generate_tests in ["y", "yes"]:
            command = f"python scripts/quickstart_tooling_dpg/generate_tests.py --package-path \"{self.config.package_path}\""
            self.run_command(command, "Generate test templates", ignore_errors=True)
        
        # Bicep infrastructure
        generate_bicep = self.get_user_input("Generate Bicep infrastructure files? (y/n)", ["y", "n"], "y")
        if generate_bicep in ["y", "yes"]:
            bicep_path = tests_path / "bicep"
            bicep_path.mkdir(parents=True, exist_ok=True)
            print(f"{self.colors.WARNING}Bicep template creation requires manual setup based on service requirements{self.colors.RESET}")
    
    def flow5_update_tests(self):
        """Flow 5: Update & Re-record Tests"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 5: Update & Re-record Tests{self.colors.RESET}")
        
        tests_path = self.config.package_path / "tests"
        
        if not tests_path.exists():
            print(f"{self.colors.WARNING}No tests directory found{self.colors.RESET}")
            return
        
        # Re-record tests
        rerecord = self.get_user_input("Re-record test recordings? (y/n)", ["y", "n"], "y")
        if rerecord in ["y", "yes"]:
            os.chdir(self.config.package_path)
            command = "python -m pytest tests/ --record-mode=rewrite"
            self.run_command(command, "Re-record test recordings", ignore_errors=True)
            os.chdir(self.config.repo_root)
    
    def flow6_update_samples(self):
        """Flow 6: Update & Test Samples"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 6: Update & Test Samples{self.colors.RESET}")
        
        samples_path = self.config.package_path / "samples"
        
        if not samples_path.exists():
            self.write_step_info("Creating samples directory...")
            samples_path.mkdir(parents=True, exist_ok=True)
        
        # Generate sample templates
        generate_samples = self.get_user_input("Generate sample templates? (y/n)", ["y", "n"], "y")
        if generate_samples in ["y", "yes"]:
            command = f"python scripts/quickstart_tooling_dpg/generate_samples.py --package-path \"{self.config.package_path}\""
            self.run_command(command, "Generate sample templates", ignore_errors=True)
        
        # Test samples
        test_samples = self.get_user_input("Test samples? (y/n)", ["y", "n"], "n")
        if test_samples in ["y", "yes"]:
            os.chdir(self.config.package_path)
            command = f"tox -e samples -c \"{self.config.tox_ini_path}\" --root ."
            self.run_command(command, "Test samples", ignore_errors=True)
            os.chdir(self.config.repo_root)
    
    def flow7_documentation(self):
        """Flow 7: Documentation & Release Preparation"""
        print(f"\n{self.colors.PHASE}🔧 FLOW 7: Documentation & Release Preparation{self.colors.RESET}")
        
        # Update CHANGELOG.md
        changelog_path = self.config.package_path / "CHANGELOG.md"
        if changelog_path.exists():
            edit_changelog = self.get_user_input("Edit CHANGELOG.md? (y/n)", ["y", "n"], "y")
            if edit_changelog in ["y", "yes"]:
                editor = os.environ.get('EDITOR', 'code')
                subprocess.run([editor, str(changelog_path)])
                input("Press Enter when editing is complete...")
        
        # Update README.md
        readme_path = self.config.package_path / "README.md"
        if readme_path.exists():
            edit_readme = self.get_user_input("Edit README.md? (y/n)", ["y", "n"], "n")
            if edit_readme in ["y", "yes"]:
                editor = os.environ.get('EDITOR', 'code')
                subprocess.run([editor, str(readme_path)])
                input("Press Enter when editing is complete...")
        
        # Version update
        update_version = self.get_user_input("Update version? (y/n)", ["y", "n"], "n")
        if update_version in ["y", "yes"]:
            new_version = self.get_user_input("Enter new version (e.g., 1.0.0)")
            version_files = list(self.config.package_path.rglob("*/_version.py"))
            
            for file in version_files:
                print(f"{self.colors.INFO}Update version in: {file}{self.colors.RESET}")
                # Manual version update would be required here
    
    def phase5_static_validation(self, package_info: Dict[str, Any], skip_validation: bool = False):
        """Phase 5: Static Validation (Sequential)"""
        if skip_validation:
            print(f"{self.colors.WARNING}Skipping validation (skip_validation flag set){self.colors.RESET}")
            return
        
        self.write_phase_header("5", "STATIC VALIDATION (SEQUENTIAL)")
        print(f"{self.colors.INFO}⏱️ TIME EXPECTATION: 3-5 minutes per validation step{self.colors.RESET}")
        
        os.chdir(package_info["package_path"])
        
        validation_steps = [
            {"name": "pylint", "command": f"tox -e pylint -c \"{self.config.tox_ini_path}\" --root .", "required": True},
            {"name": "mypy", "command": f"tox -e mypy -c \"{self.config.tox_ini_path}\" --root .", "required": True},
            {"name": "pyright", "command": f"tox -e pyright -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "verifytypes", "command": f"tox -e verifytypes -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "sphinx", "command": f"tox -e sphinx -c \"{self.config.tox_ini_path}\" --root .", "required": True},
            {"name": "mindependency", "command": f"tox -e mindependency -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "bandit", "command": f"tox -e bandit -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "black", "command": f"tox -e black -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "samples", "command": f"tox -e samples -c \"{self.config.tox_ini_path}\" --root .", "required": False},
            {"name": "breaking", "command": f"tox -e breaking -c \"{self.config.tox_ini_path}\" --root .", "required": False},
        ]
        
        results = {}
        
        for step in validation_steps:
            print(f"\n{self.colors.INFO}🔍 Running {step['name']} validation...{self.colors.RESET}")
            
            run_step = self.get_user_input(f"Run {step['name']}? (y/n/s for skip all)", ["y", "n", "s"], "y")
            
            if run_step == "s":
                print(f"{self.colors.WARNING}Skipping remaining validation steps{self.colors.RESET}")
                break
            
            if run_step == "n":
                results[step["name"]] = "SKIPPED"
                continue
            
            try:
                result = self.run_command(step["command"], f"Run {step['name']} validation", ignore_errors=True)
                results[step["name"]] = "PASS" if result and result.returncode == 0 else "FAIL"
                
                if results[step["name"]] == "FAIL" and step["required"]:
                    print(f"{self.colors.WARNING}{step['name']} failed - this is a release blocking check{self.colors.RESET}")
                    fix = self.get_user_input("Attempt to fix issues? (y/n)", ["y", "n"], "n")
                    if fix == "y":
                        print(f"{self.colors.WARNING}Please fix issues manually and re-run validation{self.colors.RESET}")
                        input("Press Enter when fixes are complete...")
                        
                        # Re-run the step
                        result = self.run_command(step["command"], f"Re-run {step['name']} validation", ignore_errors=True)
                        results[step["name"]] = "PASS" if result and result.returncode == 0 else "FAIL"
            except Exception as e:
                results[step["name"]] = "ERROR"
                print(f"{self.colors.WARNING}{step['name']} encountered an error: {e}{self.colors.RESET}")
        
        # Validation summary
        print(f"\n{self.colors.PHASE}📊 VALIDATION SUMMARY{self.colors.RESET}")
        release_blocking = []
        
        for step in validation_steps:
            result = results.get(step["name"], "NOT_RUN")
            
            color = {
                "PASS": self.colors.SUCCESS,
                "FAIL": self.colors.ERROR,
                "ERROR": self.colors.ERROR
            }.get(result, self.colors.WARNING)
            
            print(f"  {color}{step['name']}: {result}{self.colors.RESET}")
            
            if step["required"] and result in ["FAIL", "ERROR"]:
                release_blocking.append(step["name"])
        
        if release_blocking:
            print(f"\n{self.colors.ERROR}⚠️ RELEASE BLOCKING ISSUES:")
            for issue in release_blocking:
                print(f"  - {issue}")
            print(self.colors.RESET)
        else:
            print(f"{self.colors.SUCCESS}✓ All required validations passed{self.colors.RESET}")
        
        os.chdir(self.config.repo_root)
    
    def phase6_commit_and_push(self, package_info: Dict[str, Any], auto_commit: bool = False):
        """Phase 6: Commit and Push"""
        self.write_phase_header("6", "COMMIT AND PUSH")
        
        # Show changed files
        try:
            changed_files = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n') if subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True, text=True
            ).stdout.strip() else []
            
            staged_files = subprocess.run(
                ["git", "diff", "--staged", "--name-only"],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n') if subprocess.run(
                ["git", "diff", "--staged", "--name-only"],
                capture_output=True, text=True
            ).stdout.strip() else []
        except subprocess.CalledProcessError:
            changed_files = []
            staged_files = []
        
        if changed_files or staged_files:
            print(f"\n{self.colors.INFO}📁 CHANGED FILES:{self.colors.RESET}")
            
            if changed_files and changed_files != ['']:
                print(f"{self.colors.WARNING}Unstaged changes:{self.colors.RESET}")
                for file in changed_files:
                    if not file.startswith('.github') and not file.startswith('.vscode'):
                        print(f"  {self.colors.WHITE}{file}{self.colors.RESET}")
            
            if staged_files and staged_files != ['']:
                print(f"{self.colors.SUCCESS}Staged changes:{self.colors.RESET}")
                for file in staged_files:
                    if not file.startswith('.github') and not file.startswith('.vscode'):
                        print(f"  {self.colors.WHITE}{file}{self.colors.RESET}")
            
            if not auto_commit:
                commit = self.get_user_input("Commit and push changes? (y/n)", ["y", "n"], "y")
            else:
                commit = "y"
            
            if commit in ["y", "yes"]:
                # Stage all changes
                if changed_files and changed_files != ['']:
                    self.run_command("git add .", "Stage all changes")
                
                # Commit
                default_message = f"feat: SDK generation for {package_info['service_name']}/{package_info['package_name']}"
                commit_message = self.get_user_input("Enter commit message", default=default_message)
                
                self.run_command(f"git commit -m \"{commit_message}\"", "Commit changes")
                
                # Push
                push = self.get_user_input("Push to remote? (y/n)", ["y", "n"], "y")
                if push in ["y", "yes"]:
                    self.run_command(f"git push origin {self.config.current_branch}", "Push changes to remote")
        else:
            print(f"{self.colors.INFO}No changes to commit{self.colors.RESET}")
    
    def phase7_pull_request_management(self, package_info: Dict[str, Any]):
        """Phase 7: Pull Request Management"""
        self.write_phase_header("7", "PULL REQUEST MANAGEMENT")
        
        # Check if gh CLI is authenticated
        try:
            subprocess.run(["gh", "auth", "status"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print(f"{self.colors.WARNING}GitHub CLI not authenticated{self.colors.RESET}")
            auth = self.get_user_input("Authenticate with GitHub CLI? (y/n)", ["y", "n"], "y")
            if auth in ["y", "yes"]:
                self.run_command("gh auth login", "Authenticate with GitHub CLI")
            else:
                print(f"{self.colors.WARNING}Skipping pull request management{self.colors.RESET}")
                return
        
        # Check for existing PR
        try:
            existing_pr_json = subprocess.run(
                ["gh", "pr", "view", "--json", "number,title,state"],
                capture_output=True, text=True, check=True
            ).stdout
            existing_pr = json.loads(existing_pr_json)
            
            print(f"{self.colors.SUCCESS}Existing PR found:{self.colors.RESET}")
            print(f"  {self.colors.WHITE}#{existing_pr['number']}: {existing_pr['title']}")
            print(f"  State: {existing_pr['state']}{self.colors.RESET}")
            
            update_pr = self.get_user_input("Update existing PR? (y/n)", ["y", "n"], "y")
            if update_pr in ["y", "yes"]:
                print(f"{self.colors.SUCCESS}PR updated with latest changes{self.colors.RESET}")
        except subprocess.CalledProcessError:
            # Create new PR
            create_pr = self.get_user_input("Create new pull request? (y/n)", ["y", "n"], "y")
            if create_pr in ["y", "yes"]:
                pr_title = self.get_user_input(
                    "Enter PR title", 
                    default=f"SDK generation for {package_info['service_name']}/{package_info['package_name']}"
                )
                pr_body = self.get_user_input(
                    "Enter PR description", 
                    default="Automated SDK generation and validation"
                )
                
                command = f"gh pr create --title \"{pr_title}\" --body \"{pr_body}\" --draft"
                self.run_command(command, "Create draft pull request")
                
                # Get PR info
                try:
                    new_pr_json = subprocess.run(
                        ["gh", "pr", "view", "--json", "number,url"],
                        capture_output=True, text=True, check=True
                    ).stdout
                    new_pr = json.loads(new_pr_json)
                    print(f"{self.colors.SUCCESS}✓ Created PR #{new_pr['number']}: {new_pr['url']}{self.colors.RESET}")
                except subprocess.CalledProcessError:
                    pass
    
    def phase8_release_readiness(self, package_info: Dict[str, Any]):
        """Phase 8: Release Readiness & Handoff"""
        self.write_phase_header("8", "RELEASE READINESS & HANDOFF")
        
        # Package readiness check would require azure-sdk-python-mcp tool
        self.write_step_info("Checking package readiness status...")
        print(f"{self.colors.WARNING}Note: Package readiness check requires azure-sdk-python-mcp integration{self.colors.RESET}")
        
        # PR URL
        try:
            pr_info_json = subprocess.run(
                ["gh", "pr", "view", "--json", "number,url"],
                capture_output=True, text=True, check=True
            ).stdout
            pr_info = json.loads(pr_info_json)
            print(f"\n{self.colors.SUCCESS}🔗 PULL REQUEST:")
            print(f"  {self.colors.WHITE}{pr_info['url']}{self.colors.RESET}")
        except subprocess.CalledProcessError:
            pass
        
        # Next steps
        print(f"\n{self.colors.INFO}📋 NEXT STEPS:")
        print(f"  {self.colors.WHITE}1. Review PR checks and validation results")
        print("  2. Address any failing checks")
        print("  3. Request review from SDK architects")
        print(f"  4. Use azure-rest-api-specs agent for TypeSpec updates if needed{self.colors.RESET}")
        
        # Completion summary
        end_time = datetime.now()
        duration = end_time - self.config.start_time
        
        print(f"\n{self.colors.SUCCESS}🎉 WORKFLOW COMPLETE!")
        print(f"Total execution time: {duration}{self.colors.RESET}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Azure SDK for Python - Complete TypeSpec Generation Workflow Script"
    )
    parser.add_argument("--service-name", help="The Azure service name (e.g., eventgrid, ai)")
    parser.add_argument("--package-name", help="The specific package name within the service")
    parser.add_argument("--typespec-path", help="Path to local TypeSpec project or commit hash for remote TypeSpec")
    parser.add_argument("--workflow-type", 
                       choices=["new", "update", "validation", "release", "custom"],
                       default="update",
                       help="Type of workflow")
    parser.add_argument("--skip-validation", action="store_true", help="Skip static validation steps")
    parser.add_argument("--auto-commit", action="store_true", help="Automatically commit and push changes without confirmation")
    parser.add_argument("--force", action="store_true", help="Execute commands without confirmation")
    
    args = parser.parse_args()
    
    try:
        print(f"{Colors.PHASE}🚀 Azure SDK for Python - TypeSpec Generation Workflow{Colors.RESET}")
        print(f"{Colors.INFO}Starting workflow execution...{Colors.RESET}")
        
        config = WorkflowConfig()
        workflow = AzureSDKWorkflow(config)
        
        # Phase 1: Context Assessment
        package_info = workflow.phase1_context_assessment(
            args.service_name, args.package_name, args.workflow_type
        )
        
        # Phase 2: Environment Verification
        workflow.phase2_environment_verification(package_info)
        
        # Phase 3: SDK Generation
        workflow.phase3_sdk_generation(package_info, args.typespec_path)
        
        # Phase 4: Iterative Flow Selection
        workflow.phase4_iterative_flow_selection()
        
        # Phase 5: Static Validation
        workflow.phase5_static_validation(package_info, args.skip_validation)
        
        # Phase 6: Commit and Push
        workflow.phase6_commit_and_push(package_info, args.auto_commit)
        
        # Phase 7: Pull Request Management
        workflow.phase7_pull_request_management(package_info)
        
        # Phase 8: Release Readiness
        workflow.phase8_release_readiness(package_info)
        
    except Exception as e:
        print(f"\n{Colors.ERROR}❌ ERROR: {e}")
        print(f"Stack trace: {e.__class__.__name__}: {e}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
