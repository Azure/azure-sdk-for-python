# AZURE SDK FOR PYTHON - COPILOT INSTRUCTIONS

---

## GETTING STARTED

### FIRST: ALWAYS VERIFY ENVIRONMENT
**BEFORE any commands:** Use `verify_setup` tool and ensure Python virtual environment is active

### THEN: IDENTIFY THE TASK
Determine which workflow the user needs based on their request:

| **User Request** | **Workflow** | **Expected Time** |
|---|---|---|
| Generate SDK from TypeSpec | TypeSpec SDK Generation | 5-6 minutes |
| Run pylint, mypy, pyright validation | Static Validation Operations | 3-5 minutes per step |
| Fix specific pylint warnings | Pylint Warning Resolution | Variable |
| Set up or verify environment | Environment Setup | 2-3 minutes |
| Commit, push, or manage PRs | Git and PR Operations | 2-4 minutes |

---

## CORE PRINCIPLES

### RULE 1: EFFICIENT GUIDANCE
**Provide concise guidance without repeating detailed step-by-step instructions. Reference the appropriate workflow and let users follow the detailed steps independently.**

### RULE 2: REFERENCE OFFICIAL DOCUMENTATION
**ALWAYS** reference the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- Link to specific pages when answering guidelines questions
- Use this as the authoritative source for SDK development guidance

### RULE 3: PROVIDE TIME EXPECTATIONS
**ALWAYS inform users** of expected completion time before starting any workflow

---

## WORKFLOWS

### TypeSpec SDK Generation
**When to use:** User requests SDK generation from TypeSpec  
**What to do:** 
1. First use `read_file` tool to load `.github/prompts/typespec-sdk-generation.prompt.md`
2. Execute each step sequentially as outlined in the prompt file
3. If any step fails, inform user and provide guidance on resolution
**Expected time:** 5-6 minutes

### Static Validation Operations
**When to use:** User needs pylint, mypy, pyright, or verifytypes validation  
**What to do:** Load and execute steps from `.github/prompts/static-validation.prompt.md`  
**Expected time:** 3-5 minutes per validation step

### Pylint Warning Resolution
**When to use:** User has specific pylint warnings to fix  
**What to do:** Load and execute steps from `.github/prompts/next-pylint.prompt.md`  
**Expected time:** Variable based on warnings

### Environment Setup
**When to use:** User needs environment verification or setup  
**What to do:** Load and execute steps from `.github/prompts/environment-setup.prompt.md`  
**Expected time:** 2-3 minutes

### Git and PR Operations
**When to use:** User needs to commit, push, or manage pull requests  
**What to do:** Load and execute steps from `.github/prompts/git-operations.prompt.md`  
**Expected time:** 2-4 minutes

---

## AZURE DEVELOPMENT BEST PRACTICES
When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_best_practices` tool if available.