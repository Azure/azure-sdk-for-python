# Python TypeSpec Code Generation Tooling
# Targets: generate-models, clean, install-typespec-deps

OUTPUT_DIR  ?= azure/ai/responses/server/_generated
TYPESPEC_DIR ?= type_spec
OPENAPI_SPEC ?= type_spec/TempTypeSpecFiles/Foundry/openapi3/v1/microsoft-foundry-openapi3.yaml
VALIDATORS_OUTPUT ?= azure/ai/responses/server/_generated/_validators.py
ROOT_SCHEMAS ?= CreateResponse
LOCAL_TYPESPEC_PACKAGES := @typespec/compiler @typespec/http @typespec/openapi @typespec/openapi3 @typespec/versioning @typespec/events @typespec/sse @azure-tools/typespec-python @azure-tools/typespec-azure-core @azure-tools/typespec-client-generator-core @azure-tools/openai-typespec
TEMP_OUTPUT_DIR := $(OUTPUT_DIR)/.tmp_codegen
MODEL_FILES_DIR := $(TEMP_OUTPUT_DIR)/azure/ai/responses/server/sdk/models/models

.PHONY: generate-models generate-validators generate-contracts clean install-typespec-deps

ifeq ($(OS),Windows_NT)
SHELL := cmd
.SHELLFLAGS := /c
endif

# --------------------------------------------------------------------------
# generate-validators: Generate JSON payload validators from OpenAPI
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-validators:
	@where python >NUL 2>NUL || (echo Error: python is required and was not found on PATH. 1>&2 && exit /b 1)
	@if not exist "$(OPENAPI_SPEC)" (echo Error: OpenAPI spec not found at $(OPENAPI_SPEC). 1>&2 && exit /b 1)
	@echo Generating payload validators from $(OPENAPI_SPEC)...
	python scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)"
	@echo Generated validators at $(VALIDATORS_OUTPUT)
else
generate-validators:
	@command -v python >/dev/null 2>&1 || { \
		echo "Error: python is required and was not found on PATH." >&2; \
		exit 1; \
	}
	@test -f "$(OPENAPI_SPEC)" || { \
		echo "Error: OpenAPI spec not found at $(OPENAPI_SPEC)." >&2; \
		exit 1; \
	}
	@echo "Generating payload validators from $(OPENAPI_SPEC)..."
	python scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)"
	@echo "Generated validators at $(VALIDATORS_OUTPUT)"
endif

# --------------------------------------------------------------------------
# generate-contracts: Generate models + validators artifacts
# --------------------------------------------------------------------------
generate-contracts: generate-models generate-validators

TYPESPEC_OUTPUT_DIR := {cwd}/../$(TEMP_OUTPUT_DIR)

# --------------------------------------------------------------------------
# generate-models: Compile TypeSpec definitions into Python model classes
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-models:
	@where tsp-client >NUL 2>NUL || (echo Error: tsp-client is not installed. 1>&2 && echo Run 'make install-typespec-deps' to install it. 1>&2 && exit /b 1)
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	@echo Syncing upstream TypeSpec sources...
	cd /d $(TYPESPEC_DIR) && tsp-client sync
	@echo Installing local TypeSpec compiler dependencies...
	npm install --prefix $(TYPESPEC_DIR) --no-save $(LOCAL_TYPESPEC_PACKAGES)
	@echo Generating Python models...
	@if exist "$(OUTPUT_DIR)" rmdir /s /q "$(OUTPUT_DIR)"
	cd /d $(TYPESPEC_DIR) && npx tsp compile . --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(TYPESPEC_OUTPUT_DIR)"
	@if not exist "$(MODEL_FILES_DIR)" (echo Error: generated model files were not found. 1>&2 && exit /b 1)
	@move /y "$(MODEL_FILES_DIR)\__init__.py" "$(OUTPUT_DIR)\__init__.py" >NUL
	@move /y "$(MODEL_FILES_DIR)\_enums.py" "$(OUTPUT_DIR)\_enums.py" >NUL
	@move /y "$(MODEL_FILES_DIR)\_models.py" "$(OUTPUT_DIR)\_models.py" >NUL
	@move /y "$(MODEL_FILES_DIR)\_patch.py" "$(OUTPUT_DIR)\_patch.py" >NUL
	@if exist "$(TEMP_OUTPUT_DIR)" rmdir /s /q "$(TEMP_OUTPUT_DIR)"
else
generate-models:
	@command -v tsp-client >/dev/null 2>&1 || { \
		echo "Error: tsp-client is not installed." >&2; \
		echo "Run 'make install-typespec-deps' to install it." >&2; \
		exit 1; \
	}
	@command -v npm >/dev/null 2>&1 || { \
		echo "Error: npm is required. Install Node.js (v18+) from https://nodejs.org/" >&2; \
		exit 1; \
	}
	@echo "Syncing upstream TypeSpec sources..."
	cd $(TYPESPEC_DIR) && tsp-client sync
	@echo "Installing local TypeSpec compiler dependencies..."
	npm install --prefix $(TYPESPEC_DIR) --no-save $(LOCAL_TYPESPEC_PACKAGES)
	@echo "Generating Python models..."
	rm -rf $(OUTPUT_DIR)
	cd $(TYPESPEC_DIR) && npx tsp compile . --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(TYPESPEC_OUTPUT_DIR)"
	@test -d $(MODEL_FILES_DIR)
	mv $(MODEL_FILES_DIR)/__init__.py $(OUTPUT_DIR)/__init__.py
	mv $(MODEL_FILES_DIR)/_enums.py $(OUTPUT_DIR)/_enums.py
	mv $(MODEL_FILES_DIR)/_models.py $(OUTPUT_DIR)/_models.py
	mv $(MODEL_FILES_DIR)/_patch.py $(OUTPUT_DIR)/_patch.py
	rm -rf $(TEMP_OUTPUT_DIR)
endif

# --------------------------------------------------------------------------
# clean: Remove all previously generated Python model files
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
clean:
	@if exist "$(OUTPUT_DIR)" rmdir /s /q "$(OUTPUT_DIR)"
else
clean:
	rm -rf $(OUTPUT_DIR)
endif

# --------------------------------------------------------------------------
# install-typespec-deps: Install tsp-client CLI and sync TypeSpec sources
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
install-typespec-deps:
	@where node >NUL 2>NUL || (echo Error: Node.js ^(v18+^) is required. Install from https://nodejs.org/ 1>&2 && exit /b 1)
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	npm install -g @azure-tools/typespec-client-generator-cli
	npm install --prefix $(TYPESPEC_DIR) --no-save $(LOCAL_TYPESPEC_PACKAGES)
	cd /d $(TYPESPEC_DIR) && tsp-client sync
else
install-typespec-deps:
	@command -v node >/dev/null 2>&1 || { \
		echo "Error: Node.js (v18+) is required. Install from https://nodejs.org/" >&2; \
		exit 1; \
	}
	@command -v npm >/dev/null 2>&1 || { \
		echo "Error: npm is required. Install Node.js (v18+) from https://nodejs.org/" >&2; \
		exit 1; \
	}
	npm install -g @azure-tools/typespec-client-generator-cli
	npm install --prefix $(TYPESPEC_DIR) --no-save $(LOCAL_TYPESPEC_PACKAGES)
	cd $(TYPESPEC_DIR) && tsp-client sync
endif
