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
OVERLAY ?= scripts/validation-overlay.yaml
TEMP_OUTPUT_DIR := $(OUTPUT_DIR)/.tmp_codegen
MODEL_PACKAGE_DIR := $(TEMP_OUTPUT_DIR)/azure/ai/agentserver/responses/models
MODEL_SHIMS_DIR := scripts/generated_shims
CONTRACTS_DIR := $(TEMP_TSP_DIR)/sdk-service-agentserver-contracts
MODEL_BASE    := $(OUTPUT_DIR)/sdk/models/_utils/model_base.py

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
	python scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)" --overlay "$(OVERLAY)"
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
	python scripts/generate_validators.py --input "$(OPENAPI_SPEC)" --output "$(VALIDATORS_OUTPUT)" --root-schemas "$(ROOT_SCHEMAS)" --overlay "$(OVERLAY)"
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
	@where npm >NUL 2>NUL || (echo Error: npm is required. Install Node.js ^(v18+^) from https://nodejs.org/ 1>&2 && exit /b 1)
	@echo Syncing upstream TypeSpec sources...
	cd /d $(TYPESPEC_DIR) && tsp-client sync
	@echo Installing TypeSpec dependencies from emitter-package.json...
	cd /d $(TEMP_TSP_DIR) && npm install --silent
	@echo Generating Python models...
	@if exist "$(OUTPUT_DIR)" rmdir /s /q "$(OUTPUT_DIR)"
	cd /d $(TEMP_TSP_DIR) && npx tsp compile sdk-service-agentserver-contracts\client.tsp --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(abspath $(TEMP_OUTPUT_DIR))"
	@if not exist "$(MODEL_PACKAGE_DIR)" (echo Error: generated model package was not found. 1>&2 && exit /b 1)
	@if not exist "$(OUTPUT_DIR)\sdk" mkdir "$(OUTPUT_DIR)\sdk"
	@xcopy /E /I /Y "$(MODEL_PACKAGE_DIR)" "$(OUTPUT_DIR)\sdk\models" >NUL
	@if exist "$(OUTPUT_DIR)\sdk\models\aio" rmdir /s /q "$(OUTPUT_DIR)\sdk\models\aio"
	@if exist "$(OUTPUT_DIR)\sdk\models\operations" rmdir /s /q "$(OUTPUT_DIR)\sdk\models\operations"
	@if exist "$(OUTPUT_DIR)\sdk\models\_client.py" del /q "$(OUTPUT_DIR)\sdk\models\_client.py"
	@if exist "$(OUTPUT_DIR)\sdk\models\_configuration.py" del /q "$(OUTPUT_DIR)\sdk\models\_configuration.py"
	@if exist "$(OUTPUT_DIR)\sdk\models\_version.py" del /q "$(OUTPUT_DIR)\sdk\models\_version.py"
	@copy /Y "$(MODEL_SHIMS_DIR)\sdk_models__init__.py" "$(OUTPUT_DIR)\sdk\models\__init__.py" >NUL
	@copy /Y "$(MODEL_SHIMS_DIR)\__init__.py" "$(OUTPUT_DIR)\__init__.py" >NUL
	@copy /Y "$(MODEL_SHIMS_DIR)\_enums.py" "$(OUTPUT_DIR)\_enums.py" >NUL
	@copy /Y "$(MODEL_SHIMS_DIR)\_models.py" "$(OUTPUT_DIR)\_models.py" >NUL
	@copy /Y "$(MODEL_SHIMS_DIR)\_patch.py" "$(OUTPUT_DIR)\_patch.py" >NUL
	@copy /Y "$(MODEL_SHIMS_DIR)\models_patch.py" "$(OUTPUT_DIR)\sdk\models\models\_patch.py" >NUL
	@REM Patch _deserialize_sequence: reject plain strings so union falls through to str branch
	@powershell -Command "(Get-Content '$(MODEL_BASE)') -replace 'return type\(obj\)\(_deserialize\(deserializer, entry, module\) for entry in obj\)','if isinstance(obj, str):\n        raise DeserializationError()\n    return type(obj)(_deserialize(deserializer, entry, module) for entry in obj)' | Set-Content '$(MODEL_BASE)'"
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
	@echo "Installing TypeSpec dependencies from emitter-package.json..."
	cd $(TEMP_TSP_DIR) && npm install --silent
	@echo "Generating Python models..."
	rm -rf $(OUTPUT_DIR)
	cd $(TEMP_TSP_DIR) && npx tsp compile sdk-service-agentserver-contracts/client.tsp --emit @azure-tools/typespec-python --option "@azure-tools/typespec-python.emitter-output-dir=$(abspath $(TEMP_OUTPUT_DIR))"
	@test -d $(MODEL_PACKAGE_DIR) || { \
		echo "Error: generated model package was not found." >&2; \
		exit 1; \
	}
	mkdir -p $(OUTPUT_DIR)/sdk
	cp -R $(MODEL_PACKAGE_DIR) $(OUTPUT_DIR)/sdk/models
	rm -rf $(OUTPUT_DIR)/sdk/models/aio
	rm -rf $(OUTPUT_DIR)/sdk/models/operations
	rm -f $(OUTPUT_DIR)/sdk/models/_client.py
	rm -f $(OUTPUT_DIR)/sdk/models/_configuration.py
	rm -f $(OUTPUT_DIR)/sdk/models/_version.py
	cp $(MODEL_SHIMS_DIR)/sdk_models__init__.py $(OUTPUT_DIR)/sdk/models/__init__.py
	cp $(MODEL_SHIMS_DIR)/__init__.py $(OUTPUT_DIR)/__init__.py
	cp $(MODEL_SHIMS_DIR)/_enums.py $(OUTPUT_DIR)/_enums.py
	cp $(MODEL_SHIMS_DIR)/_models.py $(OUTPUT_DIR)/_models.py
	cp $(MODEL_SHIMS_DIR)/_patch.py $(OUTPUT_DIR)/_patch.py
	cp $(MODEL_SHIMS_DIR)/models_patch.py $(OUTPUT_DIR)/sdk/models/models/_patch.py
	# Patch _deserialize_sequence: reject plain strings so union falls through to str branch
	sed -i 's/    return type(obj)(_deserialize(deserializer, entry, module) for entry in obj)/    if isinstance(obj, str):\n        raise DeserializationError()\n    return type(obj)(_deserialize(deserializer, entry, module) for entry in obj)/' $(MODEL_BASE)
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
