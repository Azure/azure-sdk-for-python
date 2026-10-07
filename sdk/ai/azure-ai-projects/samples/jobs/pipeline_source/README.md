# Source-backed Python pipeline components

`sample_pipeline_source.py` builds a native two-node Foundry PipelineJob from
`steps/components.py`. Both components use `@component(code="..")`, so the Code
snapshot includes the sibling `helpers.py` module and `greeting.txt` resource.
The pipeline is built locally; component bodies run on the selected compute.
Both nodes share the same uploaded Code asset.

Set `FOUNDRY_PROJECT_ENDPOINT`, `JOB_COMPUTE_ID`, `JOB_ENVIRONMENT_IMAGE`,
`JOB_NODE_UAI_RESOURCE_ID`, and `JOB_INSTANCE_TYPE` before running
`python sample_pipeline_source.py` from this directory. **Running the sample
uploads Code and submits a live job.** The container image must have a matching
`azure-ai-projects` version and all imports used by your components installed;
the source snapshot does not install Python dependencies. Keep component modules
import-safe: do not submit jobs or rely on submitter-only environment variables at
module import time.

The code root is resolved relative to the file defining each component, not the
working directory. `.amlignore` takes precedence over `.gitignore` within each
directory; neither ignore file is uploaded. Common local artifacts and `.env`
files are excluded. Include only files intended for remote execution in the
code root; included symlinks cause an error rather than copying files outside it.
