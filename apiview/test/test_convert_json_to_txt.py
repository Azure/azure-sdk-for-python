import os
import sys
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convert_json_to_txt import process_tokens, process_review_lines, convert_json_to_txt


class TestConvertJsonToTxt(unittest.TestCase):
    
    def setUp(self):
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.json_file = os.path.join(self.test_data_dir, "azure-keyvault-secrets_python.json")
        self.reference_txt = os.path.join(self.test_data_dir, "keyvault_secrets_4.10.0b1.txt")
    
    def test_process_tokens_basic(self):
        tokens = [
            {"Value": "class", "HasPrefixSpace": False, "HasSuffixSpace": True},
            {"Value": "MyClass", "HasPrefixSpace": False, "HasSuffixSpace": False}
        ]
        result = process_tokens(tokens)
        self.assertEqual(result, "class MyClass")
    
    def test_process_tokens_with_spacing(self):
        tokens = [
            {"Value": "def", "HasPrefixSpace": False, "HasSuffixSpace": True},
            {"Value": "method", "HasPrefixSpace": False, "HasSuffixSpace": False},
            {"Value": "(", "HasPrefixSpace": False, "HasSuffixSpace": False},
            {"Value": "self", "HasPrefixSpace": False, "HasSuffixSpace": False},
            {"Value": ")", "HasPrefixSpace": False, "HasSuffixSpace": False}
        ]
        result = process_tokens(tokens)
        self.assertEqual(result, "def method(self)")
    
    def test_process_tokens_empty(self):
        tokens = []
        result = process_tokens(tokens)
        self.assertEqual(result, "")
    
    def test_process_review_lines_single_line(self):
        lines = [
            {"Tokens": [{"Value": "namespace", "HasPrefixSpace": False, "HasSuffixSpace": True},
                       {"Value": "test", "HasPrefixSpace": False, "HasSuffixSpace": False}]}
        ]
        result = process_review_lines(lines)
        self.assertEqual(result, ["namespace test"])
    
    def test_process_review_lines_with_indentation(self):
        lines = [
            {
                "Tokens": [{"Value": "class", "HasPrefixSpace": False, "HasSuffixSpace": True},
                          {"Value": "Test", "HasPrefixSpace": False, "HasSuffixSpace": False}],
                "Children": [
                    {"Tokens": [{"Value": "def", "HasPrefixSpace": False, "HasSuffixSpace": True},
                               {"Value": "method", "HasPrefixSpace": False, "HasSuffixSpace": False}]}
                ]
            }
        ]
        result = process_review_lines(lines)
        self.assertEqual(result, ["class Test", "\tdef method"])
    
    def test_process_review_lines_empty_lines(self):
        lines = [
            {"Tokens": [{"Value": "test", "HasPrefixSpace": False, "HasSuffixSpace": False}]},
            {"Tokens": []},
            {"Tokens": [{"Value": "test2", "HasPrefixSpace": False, "HasSuffixSpace": False}]}
        ]
        result = process_review_lines(lines)
        self.assertEqual(result, ["test", "", "test2"])
    
    def test_convert_json_to_txt_with_real_data(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            convert_json_to_txt(self.json_file, tmp_path)
            
            with open(tmp_path, 'r', encoding='utf-8') as f:
                generated_content = f.read()
            
            with open(self.reference_txt, 'r', encoding='utf-8') as f:
                reference_content = f.read()
            
            generated_lines = generated_content.split('\n')
            reference_lines = reference_content.split('\n')
            
            self.assertEqual(len(generated_lines), len(reference_lines))
            
            self.assertTrue(generated_lines[0].startswith("# Package is parsed using"))
            self.assertTrue("namespace azure.keyvault.secrets" in generated_content)
            self.assertTrue("class azure.keyvault.secrets.ApiVersion" in generated_content)
        
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_convert_json_to_txt_auto_filename(self):
        original_dir = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                convert_json_to_txt(self.json_file)
                
                expected_file = "azure_keyvault_secrets_4.10.0b1.txt"
                self.assertTrue(os.path.exists(expected_file))
                
                with open(expected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertTrue(len(content) > 0)
                    self.assertTrue("namespace azure.keyvault.secrets" in content)
            
            finally:
                os.chdir(original_dir)
    
    def test_json_structure_validation(self):
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("PackageName", data)
        self.assertIn("PackageVersion", data)
        self.assertIn("ReviewLines", data)
        self.assertEqual(data["PackageName"], "azure-keyvault-secrets")
        self.assertEqual(data["PackageVersion"], "4.10.0b1")
        self.assertIsInstance(data["ReviewLines"], list)


if __name__ == "__main__":
    unittest.main()
