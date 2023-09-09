import { __awaiter } from "tslib";
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { MessageChannel, Worker, receiveMessageOnPort, workerData, parentPort, } from 'node:worker_threads';
import { findUp, tryExtensions } from '@pkgr/utils';
export * from './types.js';
export const TsRunner = {
    TsNode: 'ts-node',
    EsbuildRegister: 'esbuild-register',
    EsbuildRunner: 'esbuild-runner',
    SWC: 'swc',
    TSX: 'tsx',
};
const { SYNCKIT_BUFFER_SIZE, SYNCKIT_TIMEOUT, SYNCKIT_EXEC_ARGV, SYNCKIT_TS_RUNNER, NODE_OPTIONS, } = process.env;
export const DEFAULT_BUFFER_SIZE = SYNCKIT_BUFFER_SIZE
    ? +SYNCKIT_BUFFER_SIZE
    : undefined;
export const DEFAULT_TIMEOUT = SYNCKIT_TIMEOUT ? +SYNCKIT_TIMEOUT : undefined;
export const DEFAULT_WORKER_BUFFER_SIZE = DEFAULT_BUFFER_SIZE || 1024;
export const DEFAULT_EXEC_ARGV = (SYNCKIT_EXEC_ARGV === null || SYNCKIT_EXEC_ARGV === void 0 ? void 0 : SYNCKIT_EXEC_ARGV.split(',')) || [];
export const DEFAULT_TS_RUNNER = (SYNCKIT_TS_RUNNER ||
    TsRunner.TsNode);
export const MTS_SUPPORTED_NODE_VERSION = 16;
const syncFnCache = new Map();
export function extractProperties(object) {
    if (object && typeof object === 'object') {
        const properties = {};
        for (const key in object) {
            properties[key] = object[key];
        }
        return properties;
    }
}
export function createSyncFn(workerPath, bufferSizeOrOptions, timeout) {
    if (!path.isAbsolute(workerPath)) {
        throw new Error('`workerPath` must be absolute');
    }
    const cachedSyncFn = syncFnCache.get(workerPath);
    if (cachedSyncFn) {
        return cachedSyncFn;
    }
    const syncFn = startWorkerThread(workerPath, typeof bufferSizeOrOptions === 'number'
        ? { bufferSize: bufferSizeOrOptions, timeout }
        : bufferSizeOrOptions);
    syncFnCache.set(workerPath, syncFn);
    return syncFn;
}
const cjsRequire = typeof require === 'undefined'
    ? createRequire(import.meta.url)
    : require;
const dataUrl = (code) => new URL(`data:text/javascript,${encodeURIComponent(code)}`);
export const isFile = (path) => {
    try {
        return fs.statSync(path).isFile();
    }
    catch (_a) {
        return false;
    }
};
const setupTsRunner = (workerPath, { execArgv, tsRunner }) => {
    let ext = path.extname(workerPath);
    if (!/[/\\]node_modules[/\\]/.test(workerPath) &&
        (!ext || /^\.[cm]?js$/.test(ext))) {
        const workPathWithoutExt = ext
            ? workerPath.slice(0, -ext.length)
            : workerPath;
        let extensions;
        switch (ext) {
            case '.cjs':
                extensions = ['.cts', '.cjs'];
                break;
            case '.mjs':
                extensions = ['.mts', '.mjs'];
                break;
            default:
                extensions = ['.ts', '.js'];
                break;
        }
        const found = tryExtensions(workPathWithoutExt, extensions);
        let differentExt;
        if (found && (!ext || (differentExt = found !== workPathWithoutExt))) {
            workerPath = found;
            if (differentExt) {
                ext = path.extname(workerPath);
            }
        }
    }
    const isTs = /\.[cm]?ts$/.test(workerPath);
    let tsUseEsm = workerPath.endsWith('.mts');
    if (isTs) {
        if (!tsUseEsm) {
            const pkg = findUp(workerPath);
            if (pkg) {
                tsUseEsm =
                    cjsRequire(pkg).type ===
                        'module';
            }
        }
        switch (tsRunner) {
            case TsRunner.TsNode: {
                if (tsUseEsm) {
                    if (!execArgv.includes('--loader')) {
                        execArgv = ['--loader', `${TsRunner.TsNode}/esm`, ...execArgv];
                    }
                }
                else if (!execArgv.includes('-r')) {
                    execArgv = ['-r', `${TsRunner.TsNode}/register`, ...execArgv];
                }
                break;
            }
            case TsRunner.EsbuildRegister: {
                if (!execArgv.includes('-r')) {
                    execArgv = ['-r', TsRunner.EsbuildRegister, ...execArgv];
                }
                break;
            }
            case TsRunner.EsbuildRunner: {
                if (!execArgv.includes('-r')) {
                    execArgv = ['-r', `${TsRunner.EsbuildRunner}/register`, ...execArgv];
                }
                break;
            }
            case TsRunner.SWC: {
                if (!execArgv.includes('-r')) {
                    execArgv = ['-r', `@${TsRunner.SWC}-node/register`, ...execArgv];
                }
                break;
            }
            case TsRunner.TSX: {
                if (!execArgv.includes('--loader')) {
                    execArgv = ['--loader', TsRunner.TSX, ...execArgv];
                }
                break;
            }
            default: {
                throw new Error(`Unknown ts runner: ${String(tsRunner)}`);
            }
        }
    }
    if (process.versions.pnp) {
        const nodeOptions = NODE_OPTIONS === null || NODE_OPTIONS === void 0 ? void 0 : NODE_OPTIONS.split(/\s+/);
        let pnpApiPath;
        try {
            pnpApiPath = cjsRequire.resolve('pnpapi');
        }
        catch (_a) { }
        if (pnpApiPath &&
            !(nodeOptions === null || nodeOptions === void 0 ? void 0 : nodeOptions.some((option, index) => ['-r', '--require'].includes(option) &&
                pnpApiPath === cjsRequire.resolve(nodeOptions[index + 1]))) &&
            !execArgv.includes(pnpApiPath)) {
            execArgv = ['-r', pnpApiPath, ...execArgv];
            const pnpLoaderPath = path.resolve(pnpApiPath, '../.pnp.loader.mjs');
            if (isFile(pnpLoaderPath)) {
                const experimentalLoader = pathToFileURL(pnpLoaderPath).toString();
                execArgv = ['--experimental-loader', experimentalLoader, ...execArgv];
            }
        }
    }
    return {
        ext,
        isTs,
        tsUseEsm,
        workerPath,
        execArgv,
    };
};
function startWorkerThread(workerPath, { bufferSize = DEFAULT_WORKER_BUFFER_SIZE, timeout = DEFAULT_TIMEOUT, execArgv = DEFAULT_EXEC_ARGV, tsRunner = DEFAULT_TS_RUNNER, } = {}) {
    const { port1: mainPort, port2: workerPort } = new MessageChannel();
    const { isTs, ext, tsUseEsm, workerPath: finalWorkerPath, execArgv: finalExecArgv, } = setupTsRunner(workerPath, { execArgv, tsRunner });
    const workerPathUrl = pathToFileURL(finalWorkerPath);
    if (/\.[cm]ts$/.test(finalWorkerPath)) {
        const isTsxSupported = !tsUseEsm ||
            Number.parseFloat(process.versions.node) >= MTS_SUPPORTED_NODE_VERSION;
        if ([
            TsRunner.EsbuildRegister,
            TsRunner.EsbuildRunner,
            TsRunner.SWC,
            ...(isTsxSupported ? [] : [TsRunner.TSX]),
        ].includes(tsRunner)) {
            throw new Error(`${tsRunner} is not supported for ${ext} files yet` +
                (isTsxSupported
                    ? ', you can try [tsx](https://github.com/esbuild-kit/tsx) instead'
                    : ''));
        }
    }
    const useEval = isTs && !tsUseEsm;
    const worker = new Worker(tsUseEsm && tsRunner === TsRunner.TsNode
        ? dataUrl(`import '${String(workerPathUrl)}'`)
        : useEval
            ? `require('${finalWorkerPath.replace(/\\/g, '\\\\')}')`
            : workerPathUrl, {
        eval: useEval,
        workerData: { workerPort },
        transferList: [workerPort],
        execArgv: finalExecArgv,
    });
    let nextID = 0;
    const syncFn = (...args) => {
        const id = nextID++;
        const sharedBuffer = new SharedArrayBuffer(bufferSize);
        const sharedBufferView = new Int32Array(sharedBuffer);
        const msg = { sharedBuffer, id, args };
        worker.postMessage(msg);
        const status = Atomics.wait(sharedBufferView, 0, 0, timeout);
        if (!['ok', 'not-equal'].includes(status)) {
            throw new Error('Internal error: Atomics.wait() failed: ' + status);
        }
        const { id: id2, result, error, properties, } = receiveMessageOnPort(mainPort)
            .message;
        if (id !== id2) {
            throw new Error(`Internal error: Expected id ${id} but got id ${id2}`);
        }
        if (error) {
            throw Object.assign(error, properties);
        }
        return result;
    };
    worker.unref();
    return syncFn;
}
export function runAsWorker(fn) {
    if (!workerData) {
        return;
    }
    const { workerPort } = workerData;
    try {
        parentPort.on('message', ({ sharedBuffer, id, args }) => {
            ;
            (() => __awaiter(this, void 0, void 0, function* () {
                const sharedBufferView = new Int32Array(sharedBuffer);
                let msg;
                try {
                    msg = { id, result: yield fn(...args) };
                }
                catch (error) {
                    msg = { id, error, properties: extractProperties(error) };
                }
                workerPort.postMessage(msg);
                Atomics.add(sharedBufferView, 0, 1);
                Atomics.notify(sharedBufferView, 0);
            }))();
        });
    }
    catch (error) {
        parentPort.on('message', ({ sharedBuffer, id }) => {
            const sharedBufferView = new Int32Array(sharedBuffer);
            workerPort.postMessage({
                id,
                error,
                properties: extractProperties(error),
            });
            Atomics.add(sharedBufferView, 0, 1);
            Atomics.notify(sharedBufferView, 0);
        });
    }
}
//# sourceMappingURL=index.js.map