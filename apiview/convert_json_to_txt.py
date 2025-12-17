import sys
import json


def process_tokens(tokens):
    result = ""
    for token in tokens:
        value = token.get("Value", "")
        has_prefix_space = token.get("HasPrefixSpace", False)
        has_suffix_space = token.get("HasSuffixSpace", False)
        
        if has_prefix_space:
            result += " "
        result += value
        if has_suffix_space:
            result += " "
    
    return result


def process_review_lines(lines, indent_level=0):
    output = []
    indent = "\t" * indent_level
    
    for line in lines:
        tokens = line.get("Tokens", [])
        text = process_tokens(tokens)
        
        if text.strip():
            output.append(indent + text)
        else:
            output.append("")
        
        children = line.get("Children", [])
        if children:
            child_lines = process_review_lines(children, indent_level + 1)
            output.extend(child_lines)
    
    return output


def convert_json_to_txt(json_path, output_path=None):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if output_path is None:
        package_name = data.get("PackageName", "output").replace("-", "_")
        version = data.get("PackageVersion", "1.0.0")
        output_path = f"{package_name}_{version}.txt"
    
    review_lines = data.get("ReviewLines", [])
    output_lines = process_review_lines(review_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Converted {json_path} -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_txt.py <input.json> [output.txt]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_json_to_txt(input_file, output_file)
