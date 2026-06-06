"""One-shot audit scan over the files my branch touched.

Reports:
  1. Inline imports (any `import ...` / `from ... import ...` line
     that is indented, i.e. lives inside a def / if / try block
     instead of at module top).
  2. References to design-doc filenames in comments / docstrings
     (we want plain-English explanations, not breadcrumbs).
  3. Long comment / docstring blocks (>= 8 consecutive lines), so
     I can quickly find prose that needs tightening.

Reads file list from _py_changed.txt. Run with `python _audit_scan.py`.
"""
import ast
import re
import sys
from pathlib import Path

# Phrases / filenames that indicate "design-doc breadcrumb" comments.
DOC_REF_PATTERNS = [
    r"REQUEST_OPTIONS\.md",
    r"PYTHON_BUILD_PIPELINE",
    r"PYTHON_HEALTH_CHECKS",
    r"PYTHON_ARCHITECTURE",
    r"PYTHON_CACHING",
    r"OPENAI_",
    r"PYO3-BASICS",
    r"PY03-BASICS",
    r"RUST_BASICS",
    r"QUERY_PIPELINE_CORE",
    r"docs/V5",
    r"V5/",
    r"V5_",
    r"docs/",
    r"PartitionKeys\.md",
    r"TIMEOUTS\.md",
    r"TimeoutAndRetriesConfig\.md",
    r"ErrorCodesAndRetries\.md",
    r"BENCHMARKING\.md",
    r'see\s+`?docs/',
    r'per\s+REQUEST_OPTIONS',
    r'as\s+documented\s+in\s+',
    r'per\s+the\s+"[^"]+"\s+section',
    r'see\s+the\s+"[^"]+"\s+section',
    r'as\s+the\s+doc\s+',
    r'the\s+doc\s+calls\s+',
    r'design\s+doc',
]
DOC_REF_RE = re.compile("|".join(DOC_REF_PATTERNS), re.IGNORECASE)


def scan_inline_imports(path: Path) -> list[tuple[int, str]]:
    """Return [(lineno, line)] for every import that's not at module top."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    out = []
    src_lines = path.read_text(encoding="utf-8").splitlines()
    top_lines = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                top_lines.add(ln)
        # Top-level `if TYPE_CHECKING:` blocks are also fine
        if isinstance(node, ast.If):
            for sub in ast.walk(node):
                if isinstance(sub, (ast.Import, ast.ImportFrom)):
                    for ln in range(sub.lineno, (sub.end_lineno or sub.lineno) + 1):
                        top_lines.add(ln)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if node.lineno not in top_lines:
                line = src_lines[node.lineno - 1] if node.lineno - 1 < len(src_lines) else ""
                out.append((node.lineno, line.rstrip()))
    return out


def scan_doc_refs(path: Path) -> list[tuple[int, str]]:
    """Return [(lineno, line)] for every comment/docstring line that
    references a design-doc filename or section."""
    out = []
    src = path.read_text(encoding="utf-8")
    for i, line in enumerate(src.splitlines(), start=1):
        # Skip URLs in production code attribution blocks for tests
        if DOC_REF_RE.search(line):
            # Only flag if it looks like a comment or docstring text,
            # not a real import path / code reference.
            stripped = line.strip()
            if (stripped.startswith("#")
                    or stripped.startswith('"""')
                    or stripped.startswith("'''")
                    or stripped.startswith("*")
                    or stripped.startswith(":")
                    or (stripped and not stripped.startswith(("import ", "from ", "@", "def ", "class ", "return ", "raise ", "if ", "with ", "for ", "while ", "try:", "except ", "elif ", "else:")))):
                # crude: only catch if NOT a Python statement we recognize
                # Specifically docstring or comment text.
                # Filter out lines that are clearly Python identifiers (no spaces, has `=`).
                if "=" in stripped and " " not in stripped.split("=")[0]:
                    continue
                out.append((i, stripped))
    return out


def scan_long_blocks(path: Path, min_len: int = 8) -> list[tuple[int, int]]:
    """Return [(start, len)] for runs of >=min_len consecutive comment
    or in-docstring lines. Heuristic for prose that may need tightening."""
    src_lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    i = 0
    while i < len(src_lines):
        s = src_lines[i].strip()
        # comment run
        if s.startswith("#"):
            j = i
            while j < len(src_lines) and src_lines[j].strip().startswith("#"):
                j += 1
            if j - i >= min_len:
                out.append((i + 1, j - i))
            i = j
            continue
        i += 1
    # docstring runs: find triple-quoted blocks
    in_doc = False
    doc_start = 0
    doc_quote = None
    for i, line in enumerate(src_lines, start=1):
        if not in_doc:
            m = re.search(r'(?P<q>"""|\'\'\')', line)
            if m:
                doc_start = i
                doc_quote = m.group("q")
                in_doc = True
                # if closes on same line, skip
                if line.count(doc_quote) >= 2:
                    in_doc = False
        else:
            if doc_quote in line:
                in_doc = False
                if i - doc_start + 1 >= min_len:
                    out.append((doc_start, i - doc_start + 1))
    return out


def main():
    files = [Path(p.strip()) for p in Path("_py_changed.txt").read_text().splitlines() if p.strip()]
    files = [f for f in files if f.suffix == ".py" and f.name != "__init__.py"]

    print(f"# Audit scan over {len(files)} files")
    print()

    print("## 1. Inline imports (must be moved to top of file)")
    print()
    total_inline = 0
    for f in sorted(files):
        results = scan_inline_imports(f)
        if results:
            print(f"### {f}")
            for ln, line in results:
                print(f"  L{ln}: {line.strip()}")
                total_inline += 1
            print()
    print(f"TOTAL inline imports: {total_inline}")
    print()

    print("## 2. Design-doc references in comments/docstrings")
    print()
    total_refs = 0
    for f in sorted(files):
        results = scan_doc_refs(f)
        if results:
            print(f"### {f}")
            for ln, line in results[:20]:
                print(f"  L{ln}: {line[:140]}")
                total_refs += 1
            if len(results) > 20:
                print(f"  ...and {len(results) - 20} more")
                total_refs += len(results) - 20
            print()
    print(f"TOTAL doc-ref lines: {total_refs}")
    print()

    print("## 3. Long prose blocks (>=12 consecutive comment/docstring lines)")
    print()
    total_long = 0
    for f in sorted(files):
        results = scan_long_blocks(f, min_len=12)
        if results:
            print(f"### {f}")
            for start, length in results:
                print(f"  L{start}..{start + length - 1}: {length} lines")
                total_long += 1
            print()
    print(f"TOTAL long-prose blocks: {total_long}")


if __name__ == "__main__":
    main()

