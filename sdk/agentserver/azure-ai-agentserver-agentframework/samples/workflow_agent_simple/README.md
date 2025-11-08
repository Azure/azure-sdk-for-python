## Workflow Agent Reflection Sample (Python)

This sample demonstrates how to wrap an Agent Framework workflow (with iterative review + improvement) as an agent using the Container Agents Adapter. It implements a "reflection" pattern consisting of two executors:

- Worker: Produces an initial answer (and revised answers after feedback)
- Reviewer: Evaluates the answer against quality criteria and either approves or returns constructive feedback

The workflow cycles until the Reviewer approves the response. Only approved content is emitted externally (streamed the same way as a normal agent response). This pattern is useful for quality‑controlled assistance, gated tool use, evaluative chains, or iterative refinement.

### Key Concepts Shown
- `WorkflowBuilder` + `.as_agent()` to expose a workflow as a standard agent
- Bidirectional edges enabling cyclical review (Worker ↔ Reviewer)
- Structured output parsing (Pydantic model) for review feedback
- Emitting `AgentRunUpdateEvent` to stream only approved messages
- Managing pending requests and re‑submission with incorporated feedback

File: `workflow_agent_simple.py`

---

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

Dependencies used by `workflow_agent_simple.py`:
- agent-framework-azure-ai (published package with workflow abstractions)
- agents_adapter
- azure-identity (for `DefaultAzureCredential`)
- python-dotenv (loads `.env` for local credentials)
- pydantic (pulled transitively; listed for clarity)

Install from PyPI (from the repo root: `container_agents/`):
```bash
pip install agent-framework-azure-ai azure-identity python-dotenv

pip install -e src/adapter/python
```

---

## Additional Requirements

1. Azure AI project with a model deployment (supports Microsoft hosted, Azure OpenAI, or custom models exposed via Azure AI Foundry).

---

## Configuration

Copy `.envtemplate` to `.env` and fill in real values:
```
AZURE_AI_PROJECT_ENDPOINT=<foundry-project-endpoint>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
AGENT_PROJECT_NAME=<agent-project-name-optional>
```
`AGENT_PROJECT_NAME` lets you override the default Azure AI agent project for this workflow; omit it to fall back to the SDK default.

---

## Run the Workflow Agent

From this folder:

```bash
python workflow_agent_simple.py
```
The server (via the adapter) will start on `0.0.0.0:8088` by default.

---

## Send a Non‑Streaming Request

```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/runs \
  -d '{"input":"Explain the concept of reflection in this workflow sample.","stream":false}'
```

Sample output (non‑streaming):

```
Processing 1 million files in parallel and writing their contents into a sorted output file can be a computationally and resource-intensive task. To handle it effectively, you can use Python with libraries like `concurrent.futures` for parallelism and `heapq` for the sorting and merging.

Below is an example implementation:

import os
from concurrent.futures import ThreadPoolExecutor
import heapq

def read_file(file_path):
    """Read the content of a single file and return it as a list of lines."""
    with open(file_path, 'r') as file:
        return file.readlines()

def parallel_read_files(file_paths, max_workers=8):
    """
    Read files in parallel and return all the lines in memory.
    :param file_paths: List of file paths to read.
    :param max_workers: Number of worker threads to use for parallelism.
    """
    all_lines = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to read each file in parallel
        results = executor.map(read_file, file_paths)
        # Collect the results
        for lines in results:
            all_lines.extend(lines)
    return all_lines

def write_sorted_output(lines, output_file_path):
    """
    Write sorted lines to the output file.
    :param lines: List of strings to be sorted and written.
    :param output_file_path: File path to write the sorted result.
    """
    sorted_lines = sorted(lines)
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(sorted_lines)

def main(directory_path, output_file_path):
    """
    Main function to read files in parallel and write sorted output.
    :param directory_path: Path to the directory containing input files.
    :param output_file_path: File path to write the sorted output.
    """
    # Get a list of all the file paths in the given directory
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    print(f"Found {len(file_paths)} files. Reading files in parallel...")
    
    # Read all lines from the files in parallel
    all_lines = parallel_read_files(file_paths)
    
    print(f"Total lines read: {len(all_lines)}. Sorting and writing to output file...")
    
    # Write the sorted lines to the output file
    write_sorted_output(all_lines, output_file_path)
    
    print(f"Sorted output written to: {output_file_path}")

if __name__ == "__main__":
    # Replace these paths with the appropriate input directory and output file path
    input_directory = "path/to/input/directory"  # Directory containing 1 million files
    output_file = "path/to/output/sorted_output.txt"  # Output file path
    
    main(input_directory, output_file)

### Key Features and Steps:

1. **Parallel Reading with `ThreadPoolExecutor`**:
   - Files are read in parallel using threads to improve I/O performance since reading many files is mostly I/O-bound.

2. **Sorting and Writing**:
   - Once all lines are aggregated into memory, they are sorted using Python's `sorted()` function and written to the output file in one go.

3. **Handles Large Number of Files**:
   - The program uses threads to manage the potentially massive number of files in parallel, saving time instead of processing them serially.

### Considerations:
- **Memory Usage**: This script reads all file contents into memory. If the total size of the files is too large, you may encounter memory issues. In such cases, consider processing the files in smaller chunks.
- **Sorting**: For extremely large data, consider using an external/merge sort technique to handle sorting in smaller chunks.
- **I/O Performance**: Ensure that your I/O subsystem and disk can handle the load.

Let me know if you'd like an optimized version to handle larger datasets with limited memory!

Usage (if provided): None
```

---

## Send a Streaming Request (Server-Sent Events)

```bash
curl -N \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/runs \
  -d '{"input":"How does the reviewer decide to approve?","stream":true}'
```

Sample output (streaming):

```
Here is a Python script that demonstrates parallel reading of 1 million files using `concurrent.futures` for parallelism and `heapq` to write the outputs to a sorted file. This approach ensures efficiency when dealing with such a large number of files.


import os
import heapq
from concurrent.futures import ThreadPoolExecutor

def read_file(file_path):
    """
    Read the content of a single file and return it as a list of lines.
    """
    with open(file_path, 'r') as file:
        return file.readlines()

def parallel_read_files(file_paths, max_workers=4):
    """
    Read multiple files in parallel.
    """
    all_lines = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit reading tasks to the thread pool
        futures = [executor.submit(read_file, file_path) for file_path in file_paths]
        
        # Gather results as they are completed
        for future in futures:
            all_lines.extend(future.result())
    
    return all_lines

def write_sorted_output(lines, output_file):
    """
    Write sorted lines to an output file.
    """
    sorted_lines = sorted(lines)
    with open(output_file, 'w') as file:
        file.writelines(sorted_lines)

if __name__ == "__main__":
    # Set the directory containing your input files
    input_directory = 'path_to_your_folder_with_files'
    
    # Get the list of all input files
    file_paths = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
    
    # Specify the number of threads for parallel processing
    max_threads = 8  # Adjust according to your system's capabilities
    
    # Step 1: Read all files in parallel
    print("Reading files in parallel...")
    all_lines = parallel_read_files(file_paths, max_workers=max_threads)
    
    # Step 2: Write the sorted data to the output file
    output_file = 'sorted_output.txt'
    print(f"Writing sorted output to {output_file}...")
    write_sorted_output(all_lines, output_file)
    
    print("Operation complete.")

[comment]: # ( cspell:ignore pysort )

### Key Points:
1. **Parallel Read**: The reading of files is handled using `concurrent.futures.ThreadPoolExecutor`, allowing multiple files to be processed simultaneously.

2. **Sorted Output**: After collecting all lines from the files, the `sorted()` function is used to sort the content in memory. This ensures that the final output file will have all data in sorted order.

3. **Adjustable Parallelism**: The `max_threads` parameter can be modified to control the number of threads used for file reading. The value should match your system's capabilities for optimal performance.

4. **Large Data Handling**: If the data from 1 million files is too large to fit into memory, consider using an external merge sort algorithm or a library like `pysort` for efficient external sorting.

Let me know if you'd like improvements or adjustments for more specific scenarios!
Final usage (if provided): None
```

> Only the final approved assistant content is emitted as normal output deltas; intermediate review feedback stays internal.

---

## How the Reflection Loop Works
1. User query enters the workflow (Worker start executor)
2. Worker produces an answer with model call
3. Reviewer evaluates using a structured schema (`feedback`, `approved`)
4. If not approved: Worker augments context with feedback + regeneration instruction, then re‑answers
5. Loop continues until `approved=True`
6. Approved content is emitted as `AgentRunResponseUpdate` (streamed externally)

---

## Troubleshooting
| Issue | Resolution |
|-------|------------|
| `DefaultAzureCredential` errors | Run `az login` or configure a service principal. |
| Empty / no streaming | Confirm `stream` flag in request JSON and that the event loop is healthy. |
| Model 404 / deployment error | Verify `AZURE_AI_MODEL_DEPLOYMENT_NAME` exists in the Azure AI project configured by `AZURE_AI_PROJECT_ENDPOINT`. |
| `.env` not loading | Ensure `.env` sits beside the script (or set `dotenv_path`) and that `python-dotenv` is installed. |

---

## Related Resources
- Agent Framework repo: https://github.com/microsoft/agent-framework
- Basic simple sample README (same folder structure) for installation reference

---

## License & Support
This sample follows the repository's LICENSE. For questions about unreleased Agent Framework features, contact the Agent Framework team via its GitHub repository.
