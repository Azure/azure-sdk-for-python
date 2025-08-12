#!/usr/bin/env python3
"""
Azure AI Content Understanding SDK - Sample Test Runner

This script runs all samples in the samples directory and reports success/failure status.
Useful for validation, testing, and ensuring all samples work correctly.

Prerequisites:
- Azure AI Content Understanding service endpoint configured
- Proper authentication (Azure CLI, key, or DefaultAzureCredential)
- All required dependencies installed

Usage:
    cd sdk/contentunderstanding/azure-ai-contentunderstanding/samples
    python run_all_samples.py
"""

import asyncio
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Sample files to run (excluding helper files, demos, and this script)
SAMPLES_TO_RUN = [
    # Content Analyzers
    "content_analyzers_list.py",
    "content_analyzers_analyze_binary.py", 
    "content_analyzers_analyze.py",
    "content_analyzers_create_or_replace.py",
    "content_analyzers_get_analyzer.py",
    "content_analyzers_update.py",
    "content_analyzers_get_operation_status.py",
    "content_analyzers_get_result.py",
    "content_analyzers_get_result_file.py",
    "content_analyzers_delete_analyzer.py",
    
    # Content Classifiers
    "content_classifiers_list.py",
    "content_classifiers_classify_binary.py",
    "content_classifiers_classify.py", 
    "content_classifiers_create_or_replace.py",
    "content_classifiers_get_classifier.py",
    "content_classifiers_update.py",
    "content_classifiers_get_operation_status.py",
    "content_classifiers_get_result.py",
    "content_classifiers_delete_classifier.py",
    
    # Face Detection
    "faces_detect.py",
    
    # Person Directories - Basic Operations
    "person_directories_create.py",
    "person_directories_list.py",
    "person_directories_get.py", 
    "person_directories_update.py",
    "person_directories_delete.py",
    
    # Person Management
    "person_directories_add_person.py",
    "person_directories_list_persons.py",
    "person_directories_get_person.py",
    "person_directories_update_person.py", 
    "person_directories_delete_person.py",
    
    # Face Management
    "person_directories_get_face.py",
    "person_directories_list_faces.py",
    "person_directories_update_face.py",
    "person_directories_delete_face.py",
    
    # Face Recognition (Enhanced Demo)
    "person_directories_find_similar_faces.py",
]




class SampleRunner:
    """Runs samples and tracks results."""
    
    def __init__(self):
        self.results: List[Tuple[str, bool, float, str]] = []
        self.start_time = time.time()
        
    def check_prerequisites(self) -> bool:
        """Check if basic prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check if we're in the right directory
        if not Path("sample_helper.py").exists():
            print("❌ Error: sample_helper.py not found. Please run from samples directory.")
            return False
            
        # Check environment configuration
        endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT")
        if not endpoint:
            print("❌ Error: AZURE_CONTENT_UNDERSTANDING_ENDPOINT not set.")
            print("   Please configure your .env file or set environment variables.")
            return False
            
        print(f"✅ Endpoint configured: {endpoint}")
        
        # Check for authentication
        key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
        if key:
            print("✅ Key-based authentication configured")
        else:
            print("✅ Using DefaultAzureCredential (recommended)")
            
        return True
        
    def run_sample(self, sample_file: str) -> Tuple[bool, float, str]:
        """Run a single sample and return (success, duration, output/error)."""
        print(f"\n🔧 Running {sample_file}...")
        
        start_time = time.time()
        try:
            # Run the sample with timeout
            result = subprocess.run(
                [sys.executable, sample_file],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout per sample
                cwd=os.getcwd()
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {sample_file} completed successfully ({duration:.1f}s)")
                return True, duration, result.stdout
            else:
                print(f"❌ {sample_file} failed ({duration:.1f}s)")
                print(f"   Error: {result.stderr.strip()}")
                return False, duration, result.stderr
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Timeout after {duration:.1f}s"
            print(f"⏰ {sample_file} timed out ({duration:.1f}s)")
            return False, duration, error_msg
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            print(f"💥 {sample_file} crashed ({duration:.1f}s): {error_msg}")
            return False, duration, error_msg
            
    def run_all_samples(self) -> None:
        """Run all samples and collect results."""
        if not self.check_prerequisites():
            return
            
        print(f"\n🚀 Starting sample test run at {datetime.now(timezone.utc).isoformat()}")
        print(f"📋 Found {len(SAMPLES_TO_RUN)} samples to test")
        print("=" * 60)
        
        for i, sample_file in enumerate(SAMPLES_TO_RUN, 1):
            if not Path(sample_file).exists():
                print(f"⚠️  Skipping {sample_file} (file not found)")
                self.results.append((sample_file, False, 0.0, "File not found"))
                continue
                
            print(f"\n[{i}/{len(SAMPLES_TO_RUN)}] {sample_file}")
            success, duration, output = self.run_sample(sample_file)
            self.results.append((sample_file, success, duration, output))
            
            # Small delay between samples to avoid rate limiting
            time.sleep(1)
            
    def print_summary(self) -> None:
        """Print detailed summary of all results."""
        total_time = time.time() - self.start_time
        successful = [r for r in self.results if r[1]]
        failed = [r for r in self.results if not r[1]]
        
        print("\n" + "=" * 80)
        print("📊 SAMPLE TEST SUMMARY")
        print("=" * 80)
        
        print(f"🕐 Total execution time: {total_time:.1f}s")
        print(f"✅ Successful samples: {len(successful)}")
        print(f"❌ Failed samples: {len(failed)}")
        print(f"📈 Success rate: {len(successful)/len(self.results)*100:.1f}%")
        
        if successful:
            print(f"\n✅ SUCCESSFUL SAMPLES ({len(successful)}):")
            for sample, _, duration, _ in successful:
                print(f"   ✓ {sample:<45} ({duration:.1f}s)")
                
        if failed:
            print(f"\n❌ FAILED SAMPLES ({len(failed)}):")
            for sample, _, duration, error in failed:
                print(f"   ✗ {sample:<45} ({duration:.1f}s)")
                # Show first line of error for quick diagnosis
                first_error_line = error.split('\n')[0] if error else "Unknown error"
                print(f"     └─ {first_error_line}")
                
        print("\n" + "=" * 80)
        
        if failed:
            print("💡 TROUBLESHOOTING TIPS:")
            print("   • Check your Azure AI Content Understanding endpoint and authentication")
            print("   • Ensure you have sufficient quota and permissions")
            print("   • Verify test data files exist in ../samples/test_data/")
            print("   • Check for network connectivity issues")
            print("   • Review individual sample error messages above")
            
        # Exit with non-zero code if any samples failed
        if failed:
            print(f"\n❌ {len(failed)} samples failed. Exiting with error code 1.")
            sys.exit(1)
        else:
            print(f"\n🎉 All {len(successful)} samples completed successfully!")
            sys.exit(0)


def main():
    """Main entry point."""
    print("🧪 Azure AI Content Understanding SDK - Sample Test Runner")
    print("=" * 60)
    
    runner = SampleRunner()
    try:
        runner.run_all_samples()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        runner.print_summary()


if __name__ == "__main__":
    main()
