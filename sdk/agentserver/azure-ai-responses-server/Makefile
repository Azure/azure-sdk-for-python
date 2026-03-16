# Python TypeSpec Code Generation Tooling
# Targets: generate-models, clean, install-typespec-deps

OUTPUT_DIR  ?= azure/ai/responses/server/_generated
TYPESPEC_DIR ?= type_spec

.PHONY: generate-models clean install-typespec-deps

ifeq ($(OS),Windows_NT)
SHELL := cmd
.SHELLFLAGS := /c
TYPESPEC_OUTPUT_DIR := ..\$(OUTPUT_DIR)
else
TYPESPEC_OUTPUT_DIR := ../$(OUTPUT_DIR)
endif

# --------------------------------------------------------------------------
# generate-models: Compile TypeSpec definitions into Python model classes
# --------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
generate-models:
	@where tsp-client >NUL 2>NUL || (echo Error: tsp-client is not installed. 1>&2 && echo Run 'make install-typespec-deps' to install it. 1>&2 && exit /b 1)
	cd /d $(TYPESPEC_DIR) && tsp-client generate --emitter-options "emitter-output-dir=$(TYPESPEC_OUTPUT_DIR)"
else
generate-models:
	@command -v tsp-client >/dev/null 2>&1 || { \
		echo "Error: tsp-client is not installed." >&2; \
		echo "Run 'make install-typespec-deps' to install it." >&2; \
		exit 1; \
	}
	cd $(TYPESPEC_DIR) && tsp-client generate --emitter-options "emitter-output-dir=$(TYPESPEC_OUTPUT_DIR)"
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
endif
