# TypeSpec Code Generation Tooling for storage request/response models
# Targets: generate-models, clean, install-typespec-deps
#
# See type_spec/README.md for why this compiles main.tsp locally instead of
# `tsp-client sync`-ing from Azure/azure-rest-api-specs (no upstream
# state-stores directory exists there yet).

OUTPUT_DIR   ?= azure/ai/agentserver/core/storage/_generated
TYPESPEC_DIR ?= type_spec
TEMP_OUTPUT_DIR := $(TYPESPEC_DIR)/.tmp_codegen

.PHONY: generate-models clean install-typespec-deps

ifeq ($(OS),Windows_NT)
SHELL := cmd
.SHELLFLAGS := /c
endif

# --------------------------------------------------------------------------
# install-typespec-deps: Install the pinned TypeSpec toolchain (one-time)
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
install-typespec-deps:
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	cd /d $(TYPESPEC_DIR) && npm install --silent
else
install-typespec-deps:
	@command -v npm >/dev/null 2>&1 || { \
		echo "Error: npm is required. Install Node.js (v18+) from https://nodejs.org/" >&2; \
		exit 1; \
	}
	cd $(TYPESPEC_DIR) && npm install --silent
endif

# --------------------------------------------------------------------------
# generate-models: Compile type_spec/main.tsp into Python model classes
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-models:
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	@if not exist "$(TYPESPEC_DIR)\node_modules" (echo Error: TypeSpec toolchain not installed. Run 'make install-typespec-deps' first. 1>&2 && exit /b 1)
	@echo Compiling TypeSpec into Python models...
	cd /d $(TYPESPEC_DIR) && npx tsp compile main.tsp --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(abspath $(TEMP_OUTPUT_DIR))"
	@if not exist "$(OUTPUT_DIR)" mkdir "$(OUTPUT_DIR)"
	@if not exist "$(OUTPUT_DIR)\_utils" mkdir "$(OUTPUT_DIR)\_utils"
	@for /f "delims=" %%d in ('dir /b /s /ad "$(TEMP_OUTPUT_DIR)\models"') do @copy /Y "%%d\_models.py" "$(OUTPUT_DIR)\_models.py" >NUL & copy /Y "%%d\_enums.py" "$(OUTPUT_DIR)\_enums.py" >NUL
	@for /f "delims=" %%d in ('dir /b /s /ad "$(TEMP_OUTPUT_DIR)\_utils"') do @copy /Y "%%d\model_base.py" "$(OUTPUT_DIR)\_utils\model_base.py" >NUL
	@powershell -NoProfile -Command "(Get-Content '$(OUTPUT_DIR)\_models.py') -replace 'from \.\.\._utils\.model_base', 'from ._utils.model_base' | Set-Content '$(OUTPUT_DIR)\_models.py'"
	@echo Generated models at $(OUTPUT_DIR)
	@if exist "$(TEMP_OUTPUT_DIR)" rmdir /s /q "$(TEMP_OUTPUT_DIR)"
else
generate-models:
	@command -v npm >/dev/null 2>&1 || { \
		echo "Error: npm is required. Install Node.js (v18+) from https://nodejs.org/" >&2; \
		exit 1; \
	}
	@test -d "$(TYPESPEC_DIR)/node_modules" || { \
		echo "Error: TypeSpec toolchain not installed. Run 'make install-typespec-deps' first." >&2; \
		exit 1; \
	}
	@echo "Compiling TypeSpec into Python models..."
	cd $(TYPESPEC_DIR) && npx tsp compile main.tsp --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(abspath $(TEMP_OUTPUT_DIR))"
	mkdir -p $(OUTPUT_DIR)/_utils
	find $(TEMP_OUTPUT_DIR) -path "*/models/_models.py" -exec cp {} $(OUTPUT_DIR)/_models.py \;
	find $(TEMP_OUTPUT_DIR) -path "*/models/_enums.py" -exec cp {} $(OUTPUT_DIR)/_enums.py \;
	find $(TEMP_OUTPUT_DIR) -path "*/_utils/model_base.py" -exec cp {} $(OUTPUT_DIR)/_utils/model_base.py \;
	sed -i 's/from \.\.\._utils\.model_base/from ._utils.model_base/' $(OUTPUT_DIR)/_models.py
	@echo "Generated models at $(OUTPUT_DIR)"
	rm -rf $(TEMP_OUTPUT_DIR)
endif

# --------------------------------------------------------------------------
# clean: Remove all previously generated Python model files
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
clean:
	@if exist "$(OUTPUT_DIR)\_models.py" del /q "$(OUTPUT_DIR)\_models.py"
	@if exist "$(OUTPUT_DIR)\_enums.py" del /q "$(OUTPUT_DIR)\_enums.py"
	@if exist "$(OUTPUT_DIR)\_utils\model_base.py" del /q "$(OUTPUT_DIR)\_utils\model_base.py"
else
clean:
	rm -f $(OUTPUT_DIR)/_models.py $(OUTPUT_DIR)/_enums.py $(OUTPUT_DIR)/_utils/model_base.py
endif
