# Python TypeSpec Code Generation Tooling
# Targets: generate-models, generate-validators, generate-openapi,
#          generate-contracts, clean, install-typespec-deps
#
# Dependencies are resolved from eng/emitter-package.json (via tsp-client sync)
# which creates TempTypeSpecFiles/package.json with pinned versions.
# Do NOT override versions with npm install --no-save.

OUTPUT_DIR  ?= azure/ai/agentserver/responses/models/_generated
TYPESPEC_DIR ?= type_spec
TEMP_TSP_DIR := $(TYPESPEC_DIR)/TempTypeSpecFiles
OPENAPI_SPEC ?= $(TEMP_TSP_DIR)/Foundry/openapi.virtual-public-preview.yaml
VALIDATORS_OUTPUT ?= $(OUTPUT_DIR)/_validators.py
ROOT_SCHEMAS ?= CreateResponse
OVERLAY ?= _scripts/validation-overlay.yaml
TEMP_OUTPUT_DIR := $(OUTPUT_DIR)/.tmp_codegen
MODEL_PACKAGE_DIR := $(TEMP_OUTPUT_DIR)/azure/ai/agentserver/responses/models
CONTRACTS_DIR := $(TEMP_TSP_DIR)/sdk-service-agentserver-contracts
SDK_ROOT ?= ../../..
EXTENSION_OPENAI_DIR ?= $(SDK_ROOT)/sdk/ai/azure-ai-extensions-openai

.PHONY: generate-models generate-validators generate-openapi generate-contracts clean install-typespec-deps

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
	@if not exist "$(OPENAPI_SPEC)" (echo Error: OpenAPI spec not found at $(OPENAPI_SPEC). Run 'make generate-openapi' first. 1>&2 && exit /b 1)
	@echo Generating payload validators from $(OPENAPI_SPEC)...
	python _scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)" --overlay "$(OVERLAY)"
	@echo Generated validators at $(VALIDATORS_OUTPUT)
else
generate-validators:
	@command -v python >/dev/null 2>&1 || { \
		echo "Error: python is required and was not found on PATH." >&2; \
		exit 1; \
	}
	@test -f "$(OPENAPI_SPEC)" || { \
		echo "Error: OpenAPI spec not found at $(OPENAPI_SPEC)." >&2; \
		echo "Run 'make generate-openapi' first." >&2; \
		exit 1; \
	}
	@echo "Generating payload validators from $(OPENAPI_SPEC)..."
	python _scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)" --overlay "$(OVERLAY)"
	@echo "Generated validators at $(VALIDATORS_OUTPUT)"
endif

# --------------------------------------------------------------------------
# generate-openapi: Compile TypeSpec → OpenAPI spec (for validator generation)
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-openapi:
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	@if not exist "$(CONTRACTS_DIR)\client.tsp" ( \
		echo Error: TypeSpec sources not found. Run 'make install-typespec-deps' first. 1>&2 && exit /b 1 \
	)
	@echo Compiling TypeSpec to OpenAPI spec...
	cd /d $(TEMP_TSP_DIR) && npx tsp compile sdk-service-agentserver-contracts\client.tsp --emit @typespec/openapi3 --option "@typespec/openapi3.emitter-output-dir=$(abspath $(dir $(OPENAPI_SPEC)))"
	@if not exist "$(OPENAPI_SPEC)" (echo Error: OpenAPI spec was not generated at $(OPENAPI_SPEC). 1>&2 && exit /b 1)
	@echo OpenAPI spec generated at $(OPENAPI_SPEC)
else
generate-openapi:
	@command -v npm >/dev/null 2>&1 || { \
		echo "Error: npm is required. Install Node.js (v18+) from https://nodejs.org/" >&2; \
		exit 1; \
	}
	@test -f "$(CONTRACTS_DIR)/client.tsp" || { \
		echo "Error: TypeSpec sources not found. Run 'make install-typespec-deps' first." >&2; \
		exit 1; \
	}
	@echo "Compiling TypeSpec → OpenAPI spec..."
	cd $(TEMP_TSP_DIR) && npx tsp compile sdk-service-agentserver-contracts/client.tsp --emit @typespec/openapi3 --option "@typespec/openapi3.emitter-output-dir=$(abspath $(dir $(OPENAPI_SPEC)))"
	@test -f "$(OPENAPI_SPEC)" || { \
		echo "Error: OpenAPI spec was not generated at $(OPENAPI_SPEC)." >&2; \
		exit 1; \
	}
	@echo "OpenAPI spec generated at $(OPENAPI_SPEC)"
endif

# --------------------------------------------------------------------------
# generate-contracts: Generate models + OpenAPI spec + validators
# --------------------------------------------------------------------------
generate-contracts: generate-models generate-openapi generate-validators

# --------------------------------------------------------------------------
# generate-models: Compile TypeSpec definitions into Python model classes
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-models:
	@where tsp-client >NUL 2>NUL || (echo Error: tsp-client is not installed. 1>&2 && echo Run 'make install-typespec-deps' to install it. 1>&2 && exit /b 1)
	@echo Generating extension-owned OpenAI Responses models...
	cd /d $(EXTENSION_OPENAI_DIR) && $(MAKE) generate-responses-models
	@if exist "$(OUTPUT_DIR)" rmdir /s /q "$(OUTPUT_DIR)"
	python _scripts\write_extension_model_shims.py --local-generated-root "$(OUTPUT_DIR)"
else
generate-models:
	@command -v tsp-client >/dev/null 2>&1 || { \
		echo "Error: tsp-client is not installed." >&2; \
		echo "Run 'make install-typespec-deps' to install it." >&2; \
		exit 1; \
	}
	@echo "Generating extension-owned OpenAI Responses models..."
	$(MAKE) -C $(EXTENSION_OPENAI_DIR) generate-responses-models
	rm -rf $(OUTPUT_DIR)
	python _scripts/write_extension_model_shims.py --local-generated-root "$(OUTPUT_DIR)"
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
	cd /d $(TYPESPEC_DIR) && tsp-client sync
	cd /d $(TEMP_TSP_DIR) && npm install --silent
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
	cd $(TYPESPEC_DIR) && tsp-client sync
	cd $(TEMP_TSP_DIR) && npm install --silent
endif
