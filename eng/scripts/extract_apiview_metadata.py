import argparse
import hashlib
import pathlib
import re
from typing import Dict, List


_METADATA_PATTERN = re.compile(
    r"^# Package is parsed using apiview-stub-generator\(version:([^\)]+)\), Python version:\s*([^\s]+)\s*$"
)


def extract_metadata(api_markdown_path: pathlib.Path) -> Dict[str, str]:
    file_text = api_markdown_path.read_text(encoding="utf-8-sig")
    line_ending = "\r\n" if "\r\n" in file_text else "\n"
    lines = re.split(r"\r?\n", file_text)

    metadata: Dict[str, str] = {}
    filtered: List[str] = []
    for line in lines:
        match = _METADATA_PATTERN.match(line)
        if match:
            metadata["parserVersion"] = match.group(1)
            metadata["pythonVersion"] = match.group(2)
        else:
            filtered.append(line)

    if filtered and filtered[0].startswith("```"):
        body = filtered[1:]
        while body and not body[0].strip():
            body.pop(0)
        filtered = [filtered[0], *body]
    else:
        while filtered and not filtered[0].strip():
            filtered.pop(0)

    normalized_text = "\n".join(line.rstrip() for line in filtered)
    metadata["apiMdSha256"] = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    api_markdown_path.write_text(line_ending.join(filtered), encoding="utf-8", newline="")
    metadata_path = api_markdown_path.parent / "api.metadata.yml"
    metadata_text = line_ending.join(f"{key}: {metadata[key]}" for key in sorted(metadata)) + line_ending
    metadata_path.write_text(metadata_text, encoding="utf-8", newline="")
    print(f"Updated markdown: {api_markdown_path}")
    print(f"Generated metadata: {metadata_path}")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Python APIView metadata from API markdown")
    parser.add_argument("--api-markdown-path")
    parser.add_argument("--output-path", default=".")
    args = parser.parse_args()

    api_markdown_path = pathlib.Path(args.api_markdown_path) if args.api_markdown_path else pathlib.Path(args.output_path) / "api.md"
    if not api_markdown_path.is_file():
        parser.error(f"API markdown file not found: {api_markdown_path}")
    extract_metadata(api_markdown_path)


if __name__ == "__main__":
    main()
