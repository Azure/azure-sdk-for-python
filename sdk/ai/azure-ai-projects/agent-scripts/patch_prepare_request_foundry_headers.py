# pylint: disable=line-too-long,useless-suppression
from pathlib import Path


def patch_file(path: Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    changed = False

    while i < len(lines):
        if lines[i].strip() != "def prepare_request(next_link=None):":
            i += 1
            continue

        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]

        method_indent = indent[:-4] if len(indent) >= 4 else ""
        method_start = i - 1
        while method_start >= 0 and not lines[method_start].startswith(method_indent + "def "):
            method_start -= 1
        if method_start < 0:
            i += 1
            continue

        method_block_lines = lines[method_start:i]
        method_block = "\n".join(method_block_lines)

        if "foundry_features" not in method_block:
            i += 1
            continue

        prepare_indent = indent
        j = i + 1
        while j < len(lines):
            current = lines[j]
            stripped = current.strip()
            current_indent = current[: len(current) - len(current.lstrip())]

            if stripped and len(current_indent) <= len(prepare_indent):
                break

            if stripped == "_request = HttpRequest(":
                end = j + 1
                while end < len(lines):
                    if lines[end].strip() == ")":
                        break
                    end += 1

                if end < len(lines):
                    call_block = "\n".join(lines[j : end + 1])
                    if "params=_next_request_params" in call_block and "Foundry-Features" not in call_block:
                        for k in range(j + 1, end):
                            if "params=_next_request_params" in lines[k]:
                                lines[k] = lines[k].replace(
                                    "params=_next_request_params",
                                    'params=_next_request_params, headers={"Foundry-Features": self._serialize.header("foundry_features", foundry_features, "str")}',
                                )
                                changed = True
                                break
                        j = end

            j += 1

        i += 1

    if changed:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return changed


def main() -> None:
    files = [
        Path("azure/ai/projects/operations/_operations.py"),
        Path("azure/ai/projects/aio/operations/_operations.py"),
    ]

    patched = []
    for file in files:
        if patch_file(file):
            patched.append(str(file))

    if patched:
        print("Patched prepare_request headers in:")
        for item in patched:
            print(f"- {item}")
    else:
        print("No prepare_request header patches were necessary.")


if __name__ == "__main__":
    main()
