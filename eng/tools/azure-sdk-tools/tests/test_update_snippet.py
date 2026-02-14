import tempfile
from pathlib import Path

from azpysdk.update_snippet import (
    get_snippets_from_directory,
    update_snippets_in_file,
)


def test_get_snippets_from_directory():
    """Test that snippets are correctly extracted from sample files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create samples directory
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()

        # Create a sample file with a snippet
        sample_content = """
# [START trio]
from azure.core.pipeline.transport import TrioRequestsTransport

async with AsyncPipeline(TrioRequestsTransport(), policies=policies) as pipeline:
    return await pipeline.run(request)
# [END trio]
"""
        sample_file = samples_dir / "sample_trio.py"
        sample_file.write_text(sample_content, encoding="utf-8")

        # Extract snippets
        snippets = get_snippets_from_directory(temp_dir)

        # Verify
        assert len(snippets) == 1
        assert "sample_trio.trio" in snippets
        expected_snippet = """from azure.core.pipeline.transport import TrioRequestsTransport

async with AsyncPipeline(TrioRequestsTransport(), policies=policies) as pipeline:
    return await pipeline.run(request)"""
        assert snippets["sample_trio.trio"] == expected_snippet


def test_update_snippets_in_file():
    """Test that README snippets are correctly updated from extracted snippets."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create samples directory with a snippet
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()

        sample_content = """
# [START trio]
from azure.core.pipeline.transport import TrioRequestsTransport

async with AsyncPipeline(TrioRequestsTransport(), policies=policies) as pipeline:
    return await pipeline.run(request)
# [END trio]
"""
        sample_file = samples_dir / "sample_trio.py"
        sample_file.write_text(sample_content, encoding="utf-8")

        # Extract snippets
        snippets = get_snippets_from_directory(temp_dir)

        # Create README with outdated snippet
        readme_content = """# My Package

<!-- SNIPPET:sample_trio.trio-->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
```

<!-- END SNIPPET -->

Some other content.
"""
        readme_file = Path(temp_dir) / "README.md"
        readme_file.write_text(readme_content, encoding="utf-8")

        # Update snippets
        out_of_date = update_snippets_in_file(str(readme_file), snippets)

        # Verify
        assert out_of_date is True

        updated_content = readme_file.read_text(encoding="utf-8")
        assert "from azure.core.pipeline.transport import TrioRequestsTransport" in updated_content
        assert "TextAnalyticsClient" not in updated_content


def test_update_snippets_already_up_to_date():
    """Test that no update is flagged when snippets are already current."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create samples directory with a snippet
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()

        sample_content = """
# [START example]
print("hello world")
# [END example]
"""
        sample_file = samples_dir / "sample_example.py"
        sample_file.write_text(sample_content, encoding="utf-8")

        # Extract snippets
        snippets = get_snippets_from_directory(temp_dir)

        # Create README with up-to-date snippet
        readme_content = """# My Package

<!-- SNIPPET:sample_example.example-->

```python
print("hello world")
```

<!-- END SNIPPET -->
"""
        readme_file = Path(temp_dir) / "README.md"
        readme_file.write_text(readme_content, encoding="utf-8")

        # Update snippets
        out_of_date = update_snippets_in_file(str(readme_file), snippets)

        # Verify - should not be flagged as out of date
        assert out_of_date is False


def test_multiple_snippets():
    """Test handling of multiple snippets in a single file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create samples directory
        samples_dir = Path(temp_dir) / "samples"
        samples_dir.mkdir()

        sample_content = """
# [START first]
code_one = 1
# [END first]

# [START second]
code_two = 2
# [END second]
"""
        sample_file = samples_dir / "multi.py"
        sample_file.write_text(sample_content, encoding="utf-8")

        # Extract snippets
        snippets = get_snippets_from_directory(temp_dir)

        # Verify
        assert len(snippets) == 2
        assert "multi.first" in snippets
        assert "multi.second" in snippets
        assert snippets["multi.first"] == "code_one = 1"
        assert snippets["multi.second"] == "code_two = 2"


if __name__ == "__main__":
    test_get_snippets_from_directory()
    test_update_snippets_in_file()
    test_update_snippets_already_up_to_date()
    test_multiple_snippets()
    print("All tests passed!")
