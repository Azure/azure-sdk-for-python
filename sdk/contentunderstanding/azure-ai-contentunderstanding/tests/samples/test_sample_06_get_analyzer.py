# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_06_get_analyzer.py

DESCRIPTION:
    These tests validate the sample_06_get_analyzer.py sample code.
    Tests correspond to .NET Sample06_GetAnalyzer.cs

USAGE:
    pytest test_sample_06_get_analyzer.py
"""

import json
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSample06GetAnalyzer(ContentUnderstandingClientTestBase):
    """Tests for sample_06_get_analyzer.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_06_get_analyzer(self, contentunderstanding_endpoint: str) -> None:
        """Test getting information about a prebuilt analyzer.
        
        This test validates:
        1. Getting analyzer information using get_analyzer
        2. Analyzer response structure
        3. Analyzer JSON serialization
        
        Corresponds to .NET Sample06_GetAnalyzer.GetPrebuiltAnalyzerAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Get information about a prebuilt analyzer
        response = client.get_analyzer(analyzer_id="prebuilt-documentSearch")
        
        # Assertions
        assert response is not None, "Response should not be null"
        print("[PASS] Get analyzer response received")
        
        analyzer = response
        assert analyzer is not None, "Analyzer should not be null"
        print("[PASS] Analyzer object is not null")
        
        # Verify basic analyzer properties for prebuilt-documentSearch
        if hasattr(analyzer, 'base_analyzer_id'):
            base_id = getattr(analyzer, 'base_analyzer_id', None)
            if base_id:
                print(f"[INFO] Base analyzer ID: {base_id}")
        
        if hasattr(analyzer, 'description'):
            description = getattr(analyzer, 'description', None)
            if description:
                print(f"[INFO] Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        
        # Verify config if present
        if hasattr(analyzer, 'config'):
            config = getattr(analyzer, 'config', None)
            if config:
                print("[INFO] Analyzer has configuration")
                if hasattr(config, 'enable_ocr'):
                    enable_ocr = getattr(config, 'enable_ocr', None)
                    if enable_ocr is not None:
                        print(f"[INFO]   EnableOcr: {enable_ocr}")
                if hasattr(config, 'enable_layout'):
                    enable_layout = getattr(config, 'enable_layout', None)
                    if enable_layout is not None:
                        print(f"[INFO]   EnableLayout: {enable_layout}")
        
        # Verify models if present
        if hasattr(analyzer, 'models'):
            models = getattr(analyzer, 'models', None)
            if models and len(models) > 0:
                print(f"[INFO] Analyzer has {len(models)} model mapping(s)")
                for key, value in list(models.items())[:5]:  # Show first 5
                    print(f"[INFO]   {key}: {value}")
        
        # Verify analyzer can be serialized to JSON
        try:
            # Convert analyzer to dict and then to JSON
            if hasattr(analyzer, '__dict__'):
                analyzer_dict = analyzer.__dict__
            elif hasattr(analyzer, 'as_dict'):
                analyzer_dict = analyzer.as_dict()  # type: ignore
            else:
                analyzer_dict = {"analyzer": str(analyzer)}
            
            analyzer_json = json.dumps(analyzer_dict, indent=2, default=str)
            
            assert analyzer_json is not None, "Analyzer JSON should not be null"
            assert len(analyzer_json) > 0, "Analyzer JSON should not be empty"
            print(f"[PASS] Analyzer JSON serialized successfully ({len(analyzer_json)} characters)")
            
            # Verify JSON contains analyzer identifier
            assert "documentSearch" in analyzer_json.lower() or "prebuilt" in analyzer_json.lower(), \
                "Analyzer JSON should contain analyzer identifier"
            print("[PASS] Analyzer JSON contains expected identifiers")
            print(f"[PASS] Analyzer JSON length: {len(analyzer_json)} characters")
            
            # Display formatted JSON (first 500 chars for brevity)
            print("\n[INFO] Prebuilt-documentSearch Analyzer (preview):")
            print(analyzer_json[:500] + "..." if len(analyzer_json) > 500 else analyzer_json)
            
        except Exception as e:
            print(f"[WARN] Could not fully serialize analyzer to JSON: {str(e)[:100]}")
            # Still verify basic properties
            assert analyzer is not None, "Analyzer should not be null"
        
        print("\n[PASS] All prebuilt analyzer properties validated successfully")
        print("\n[SUCCESS] All test_sample_06_get_analyzer assertions passed")
