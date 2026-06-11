# `.github/shared`

Shared JavaScript helper library (`@azure-tools/specs-shared`) used by tooling and GitHub Actions
across the `Azure/azure-rest-api-specs` repository. The code is plain ESM JavaScript annotated with
JSDoc, so it can be consumed from both JavaScript and TypeScript without a build step.

This document has two audiences:

- **[API reference](#api-reference)** — for _users_ of the shared code, a catalog of the APIs
  exported from `src` so you can reuse existing helpers instead of reinventing the wheel.
- **[Folder structure & contributing](#folder-structure--contributing)** — for _developers_ of the
  shared code, how the folder is organized and how to make changes.

## API reference

Each module is published as a subpath export in [`package.json`](./package.json) (for example
`@azure-tools/specs-shared/array`). Import directly from the subpath, e.g.:

```js
import { mapAsync } from "@azure-tools/specs-shared/array";
```

> The list below is generated from the `export` statements under [`src`](./src). When in doubt, read
> the JSDoc on the function/class itself — it is the source of truth for parameters and return types.

### `array` — async array helpers

- `filterAsync(array, asyncPredicate)` — `Array.prototype.filter` with an async predicate.
- `flatMapAsync(array, asyncMapper)` — `Array.prototype.flatMap` with an async mapper.
- `mapAsync(array, asyncMapper)` — `Array.prototype.map` with an async mapper.
- `includesEvery(array, values)` — true if `array` includes every value in `values`.
- `includesNone(array, values)` — true if `array` includes none of the values in `values`.

### `breaking-change` — breaking-change / versioning approval labels

Single source of truth for breaking-change and versioning approval label names and helpers.

- `VERSIONING_APPROVALS`, `BREAKING_CHANGE_APPROVALS`, `REVIEW_REQUIRED_LABELS` — label-name maps.
- `versioningApprovalValues`, `breakingChangeApprovalValues`, `reviewRequiredLabelValues` — value
  arrays for the maps above.
- `isValidVersioningApproval(value)`, `isValidBreakingChangeApproval(value)`,
  `isReviewRequiredLabel(value)` — label classification helpers.
- `breakingChangesCheckType`, `BREAKING_CHANGES_CHECK_TYPES` — breaking-change check type constants.

### `cache` — in-memory caches

- `KeyedCache` — cache keyed by a single value; `getOrCreate(key, factory)`.
- `KeyedPairCache` — cache keyed by a pair of values; `getOrCreate(key1, key2, factory)`.

### `changed-files` — git changed files & path predicates

- `getChangedFiles(options)` — list changed files (posix paths relative to repo root) between two
  commitishes via `git diff`.
- `getChangedFilesStatuses(options)` — same as above, but grouped by change status
  (added/modified/deleted/renamed).
- Path predicate filters (each takes a file path and returns a boolean): `json`, `markdown`,
  `readme`, `dataPlane`, `resourceManager`, `preview`, `stable`, `example`, `typespec`,
  `quickstartTemplate`, `swagger`, `scenario`.

### `console` — console output

- `log(...args)` — async wrapper around `console.log`.

### `exec` — child-process execution

- `isExecError(error)` — type guard for errors thrown by the exec helpers.
- `execFile(file, args, options)` — promisified `child_process.execFile`.
- `execNpm(args, options)` — run an `npm` command.
- `execNpmExec(args, options)` — run an `npm exec` command.

### `git` — git helpers

- `isFullGitSha(string)` — true if the string is a full 40-character git SHA.

### `github` — GitHub API constants

- `PER_PAGE_MAX` — maximum page size (100) for GitHub REST list APIs.
- `CheckStatus`, `CheckConclusion`, `CommitStatusState` — frozen enums mirroring GitHub check/commit
  status values.

### `logger` — logging

- `ILogger` (JSDoc typedef) — the logger interface (`debug`/`error`/`info`/`warning`/`isDebug`).
- `ConsoleLogger` — `ILogger` implementation backed by the console.
- `defaultLogger` — shared non-debug logger instance.
- `debugLogger` — shared debug-enabled logger instance.

### `math` — math helpers

- `toPercent(value, decimals)` — format a `0..1` ratio as a percentage string.

### `path` — path helpers (with caching)

- `includesSegment(path, segment)` — true if the path contains the given path segment.
- `resolveCached(path)` — cached `path.resolve` (hot path; much faster than uncached `resolve`).
- `resolvePairCached(from, to)` — cached `path.resolve(from, to)`.
- `untilLastSegment(path, segment)` — substring up to the last occurrence of `segment`.
- `untilLastSegmentWithParent(path, segment)` — like above, including the parent of the segment.

### `readme` — autorest readme model

- `TagMatchRegex` — regex matching `$(tag) == "..."` conditions in a readme.
- `Readme` — model of an autorest `readme.md`: `getGlobalConfig()`, `getTags()`, `path`,
  `specModel`, `toJSONAsync(options)`, `toString()`.

### `sdk-types` — SDK language types & schemas

- `SdkName` — frozen enum of SDK language identifiers (Go/Java/Js/Net/Python/Rust).
- `SdkNameSchema`, `APIViewRequestDataSchema`, `SpecGenSdkArtifactInfoSchema` — zod schemas (plus
  inferred typedefs) for SDK tooling payloads.
- `sdkLabels` — per-language SDK label configuration.

### `set` — set helpers

- `equals(set1, set2)` — true if the two sets contain the same elements.
- `intersect(a, b)` — the intersection of two sets.

### `simple-git` — git repo helpers

- `getRootFolder(inputPath)` — resolve the git repository root for a path.

### `sleep` — timers

- `sleep(ms)` — promise that resolves after `ms` milliseconds.

### `sort` — comparators

- `byDate(getDate)` — comparator sorting by a date extracted from each element.
- `invert(comparator)` — reverse an existing comparator.

### `spec-model` — spec folder model

- `SpecModel` — model of a specification folder: `folder`, `getAffectedReadmeTags(swaggerPath)`,
  `getAffectedSwaggers(swaggerPath)`, `getReadmes()`, `getSwaggers()`, `toJSONAsync(options)`,
  `toString()`.
- `embedError(fn, options)` — wrap an async function so thrown errors are embedded in the result.

### `spec-model-error` — errors

- `SpecModelError` — `Error` subclass carrying `source`, `readme`, and `tag` context.

### `swagger` — swagger document model

- `Swagger` — model of a swagger/OpenAPI document: `getRefs()`, `getExamples()`, `getOperations()`,
  `getTypeSpecGenerated()`, `path`, `tag`, `versionKind`, `toJSONAsync(options)`, `toString()`.
- `API_VERSION_LIFECYCLE_STAGES` — frozen enum of API-version lifecycle stages.

### `tag` — autorest tag model

- `Tag` — model of an autorest tag: `inputFiles`, `name`, `readme`, `toJSONAsync(options)`,
  `toString()`.

### `time` — time/duration helpers

- `Duration` — frozen map of common durations in milliseconds.
- `add(date, ms)` / `subtract(date, ms)` — date arithmetic.
- `formatDuration(ms)` — human-readable duration string.
- `getDuration(from, to)` — milliseconds between two dates.

## Folder structure & contributing

```
.github/shared
├── cmd/      # Executable CLI entry points (exposed via package.json "bin")
├── perf/     # Performance benchmarks (tinybench)
├── src/      # The shared library source (one module per file)
├── test/     # Vitest unit tests + fixtures and test helpers
├── package.json        # Subpath "exports", "bin", scripts, dependencies
├── tsconfig.json       # Type-checking config (lint:tsc)
├── eslint.config.js    # ESLint config (also re-exported as eslint-base-config)
└── vitest.config.js    # Test + coverage config
```

### `src`

The shared library. Each file is a focused module (see the [API reference](#api-reference)) and is
exposed to consumers through a subpath in [`package.json`](./package.json)'s `exports`. See
[`src/README.md`](./src/README.md) for notes on consuming the code from TypeScript.

Conventions:

- Plain ESM JavaScript annotated with JSDoc — no separate `.ts` sources or build step. Types are
  inferred from JSDoc, so keep annotations accurate.
- Runtime dependencies are kept to an absolute minimum (ideally zero transitive dependencies) for
  performance, and must be a subset of the parent [`../package.json`](../package.json).

### `test`

[Vitest](https://vitest.dev/) unit tests. Each `src/<module>.js` has a matching
`test/<module>.test.js`. Supporting assets live alongside the tests:

- `test/fixtures/` — sample specs/swaggers/readmes used by the tests.
- `test/examples.js` — shared example data (also exported publicly as
  `@azure-tools/specs-shared/test/examples`).
- `test/repo.js`, `test/sdk-types.js` — local test helpers.

### `perf`

[`perf/perf.js`](./perf/perf.js) contains [tinybench](https://github.com/tinylibs/tinybench)
micro-benchmarks (for example comparing `resolve()` vs `resolveCached()`). Run with `npm run perf`.

### `cmd`

CLI entry points exposed via `package.json` `"bin"`. [`cmd/spec-model.js`](./cmd/spec-model.js)
backs `npx spec-model` for dumping a `SpecModel` to JSON.

### Contributing

When adding or changing shared code:

1. **Add the module** under `src` as a single-responsibility file with JSDoc-annotated exports.
2. **Export it** by adding a subpath entry to the `exports` map in [`package.json`](./package.json).
3. **Test it** by adding/updating `test/<module>.test.js`; add fixtures under `test/fixtures` if
   needed.
4. **Keep dependencies minimal** — avoid new runtime dependencies; any you add must already exist in
   [`../package.json`](../package.json).
5. **Document new APIs** by updating the [API reference](#api-reference) above.

Useful scripts (run from `.github/shared`):

| Command                | Description                                        |
| ---------------------- | -------------------------------------------------- |
| `npm test`             | Run tests in watch mode (vitest).                  |
| `npm run test:ci`      | Run tests once with coverage.                      |
| `npm run lint`         | Run ESLint and `tsc` type-checking.                |
| `npm run format`       | Auto-format with prettier.                         |
| `npm run format:check` | Check formatting without writing.                  |
| `npm run perf`         | Run performance benchmarks.                        |
| `npm run check`        | Run tests, lint, and format check (the full gate). |
