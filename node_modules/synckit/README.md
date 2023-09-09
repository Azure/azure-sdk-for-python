# synckit

[![GitHub Actions](https://github.com/un-ts/synckit/workflows/CI/badge.svg)](https://github.com/un-ts/synckit/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/un-ts/synckit.svg)](https://codecov.io/gh/un-ts/synckit)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/un-ts/synckit.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/un-ts/synckit/context:javascript)
[![type-coverage](https://img.shields.io/badge/dynamic/json.svg?label=type-coverage&prefix=%E2%89%A5&suffix=%&query=$.typeCoverage.atLeast&uri=https%3A%2F%2Fraw.githubusercontent.com%2Fun-ts%2Fsynckit%2Fmain%2Fpackage.json)](https://github.com/plantain-00/type-coverage)
[![npm](https://img.shields.io/npm/v/synckit.svg)](https://www.npmjs.com/package/synckit)
[![GitHub Release](https://img.shields.io/github/release/un-ts/synckit)](https://github.com/un-ts/synckit/releases)

[![Conventional Commits](https://img.shields.io/badge/conventional%20commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![JavaScript Style Guide](https://img.shields.io/badge/code_style-standard-brightgreen.svg)](https://standardjs.com)
[![Code Style: Prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

Perform async work synchronously in Node.js using `worker_threads` with first-class TypeScript support.

## TOC <!-- omit in toc -->

- [Usage](#usage)
  - [Install](#install)
  - [API](#api)
  - [Options](#options)
  - [Envs](#envs)
  - [TypeScript](#typescript)
    - [`ts-node`](#ts-node)
    - [`esbuild-register`](#esbuild-register)
    - [`esbuild-runner`](#esbuild-runner)
    - [`swc`](#swc)
    - [`tsx`](#tsx)
- [Benchmark](#benchmark)
- [Sponsors](#sponsors)
- [Backers](#backers)
- [Changelog](#changelog)
- [License](#license)

## Usage

### Install

```sh
# yarn
yarn add synckit

# npm
npm i synckit
```

### API

```js
// runner.js
import { createSyncFn } from 'synckit'

// the worker path must be absolute
const syncFn = createSyncFn(require.resolve('./worker'), {
  tsRunner: 'tsx', // optional, can be `'ts-node' | 'esbuild-register' | 'esbuild-runner' | 'tsx'`
})

// do whatever you want, you will get the result synchronously!
const result = syncFn(...args)
```

```js
// worker.js
import { runAsWorker } from 'synckit'

runAsWorker(async (...args) => {
  // do expensive work
  return result
})
```

You must make sure, the `result` is serializable by [`Structured Clone Algorithm`](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm)

### Options

1. `bufferSize` same as env `SYNCKIT_BUFFER_SIZE`
2. `timeout` same as env `SYNCKIT_TIMEOUT`
3. `execArgv` same as env `SYNCKIT_EXEC_ARGV`
4. `tsRunner` same as env `SYNCKIT_TS_RUNNER`

### Envs

1. `SYNCKIT_BUFFER_SIZE`: `bufferSize` to create `SharedArrayBuffer` for `worker_threads` (default as `1024`)
2. `SYNCKIT_TIMEOUT`: `timeout` for performing the async job (no default)
3. `SYNCKIT_EXEC_ARGV`: List of node CLI options passed to the worker, split with comma `,`. (default as `[]`), see also [`node` docs](https://nodejs.org/api/worker_threads.html)
4. `SYNCKIT_TS_RUNNER`: Which TypeScript runner to be used, it could be very useful for development, could be `'ts-node' | 'esbuild-register' | 'esbuild-runner' | 'swc' | 'tsx'`, `'ts-node'` is used by default, make sure you have installed them already

### TypeScript

#### `ts-node`

If you want to use `ts-node` for worker file (a `.ts` file), it is supported out of box!

If you want to use a custom tsconfig as project instead of default `tsconfig.json`, use `TS_NODE_PROJECT` env. Please view [ts-node](https://github.com/TypeStrong/ts-node#tsconfig) for more details.

If you want to integrate with [tsconfig-paths](https://www.npmjs.com/package/tsconfig-paths), please view [ts-node](https://github.com/TypeStrong/ts-node#paths-and-baseurl) for more details.

#### `esbuild-register`

Please view [`esbuild-register`][] for its document

#### `esbuild-runner`

Please view [`esbuild-runner`][] for its document

#### `swc`

Please view [`@swc-node/register`][] for its document

#### `tsx`

Please view [`tsx`][] for its document

## Benchmark

It is about 20x faster than [`sync-threads`](https://github.com/lambci/sync-threads) but 3x slower than native for reading the file content itself 1000 times during runtime, and 18x faster than `sync-threads` but 4x slower than native for total time.

And it's almost same as [`deasync`](https://github.com/abbr/deasync) but requires no native bindings or `node-gyp`.

See [benchmark.cjs](./benchmarks/benchmark.cjs.txt) and [benchmark.esm](./benchmarks/benchmark.esm.txt) for more details.

You can try it with running `yarn benchmark` by yourself. [Here](./benchmarks/benchmark.js) is the benchmark source code.

## Sponsors

| 1stG                                                                                                                               | RxTS                                                                                                                               | UnTS                                                                                                                               |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| [![1stG Open Collective backers and sponsors](https://opencollective.com/1stG/organizations.svg)](https://opencollective.com/1stG) | [![RxTS Open Collective backers and sponsors](https://opencollective.com/rxts/organizations.svg)](https://opencollective.com/rxts) | [![UnTS Open Collective backers and sponsors](https://opencollective.com/unts/organizations.svg)](https://opencollective.com/unts) |

## Backers

| 1stG                                                                                                                             | RxTS                                                                                                                             | UnTS                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| [![1stG Open Collective backers and sponsors](https://opencollective.com/1stG/individuals.svg)](https://opencollective.com/1stG) | [![RxTS Open Collective backers and sponsors](https://opencollective.com/rxts/individuals.svg)](https://opencollective.com/rxts) | [![UnTS Open Collective backers and sponsors](https://opencollective.com/unts/individuals.svg)](https://opencollective.com/unts) |

## Changelog

Detailed changes for each release are documented in [CHANGELOG.md](./CHANGELOG.md).

## License

[MIT][] © [JounQin][]@[1stG.me][]

[`esbuild-register`]: https://github.com/egoist/esbuild-register
[`esbuild-runner`]: https://github.com/folke/esbuild-runner
[`@swc-node/register`]: https://github.com/swc-project/swc-node/tree/master/packages/register
[`tsx`]: https://github.com/esbuild-kit/tsx
[1stg.me]: https://www.1stg.me
[jounqin]: https://GitHub.com/JounQin
[mit]: http://opensource.org/licenses/MIT
