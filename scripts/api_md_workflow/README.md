# API Review PR Helper

This folder contains the standalone Python helper used to create API review PRs from generated `api.md` files.

## Purpose

`create_api_review_pr.py` compares a baseline package release tag with a target API surface, creates or reuses dedicated API review branches, and opens a draft PR that shows the `api.md` diff.

The API consistency workflow helpers live under `.github/workflows/src/api-md-consistency`.

## Usage

The script includes Python package discovery, version parsing, `api.md` generation, git branch orchestration, and GitHub PR creation in one file.

`create_api_review_pr.py` compares a baseline package release tag with a target API surface. The target can be a package release tag, an `origin` branch, or an `owner:branch` fork reference. When the target is a tag, the generated PR body identifies it as a target tag instead of a working branch.

Example comparing two package release tags:

```bash
python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-ai-projects --base azure-ai-projects_2.1.0 --target azure-ai-projects_2.2.0
```
