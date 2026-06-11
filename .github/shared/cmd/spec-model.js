#!/usr/bin/env node

import { debugLogger } from "../src/logger.js";
import { SpecModel } from "../src/spec-model.js";

const USAGE =
  "Usage: npx spec-model path/to/spec [--debug] [--include-operations] [--include-refs] [--relative-paths] [--no-embed-errors]\n" +
  "Examples:\n" +
  "  npx spec-model specification/widget\n" +
  "  npx spec-model specification --include-operations --include-refs > out.txt; grep out.txt '\"error\":'";

// Exclude first two args (node, script file)
let args = process.argv.slice(2);

const debug = args.includes("--debug");
args = args.filter((a) => a != "--debug");

const includeOperations = args.includes("--include-operations");
args = args.filter((a) => a != "--include-operations");

const includeRefs = args.includes("--include-refs");
args = args.filter((a) => a != "--include-refs");

const relativePaths = args.includes("--relative-paths");
args = args.filter((a) => a != "--relative-paths");

const noEmbedErrors = args.includes("--no-embed-errors");
args = args.filter((a) => a != "--no-embed-errors");

if (args.length < 1) {
  console.error(USAGE);
  process.exit(1);
}

if (args.length > 1) {
  console.error("ERROR: Too many arguments\n");
  console.error(USAGE);
  process.exit(1);
}

const specPath = args[0];

// Default to 'undefined' instead of 'defaultLogger', so output is always a valid JSON object (no logging)
const logger = debug ? debugLogger : undefined;

const specModel = new SpecModel(specPath, { logger });

console.log(
  JSON.stringify(
    await specModel.toJSONAsync({
      embedErrors: !noEmbedErrors,
      includeOperations,
      includeRefs,
      relativePaths,
    }),
    null,
    2,
  ),
);
