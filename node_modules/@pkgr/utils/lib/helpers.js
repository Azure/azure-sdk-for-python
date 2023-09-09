import fs from 'node:fs';
import path from 'node:path';
import isGlob from 'is-glob';
import { CWD, EXTENSIONS, cjsRequire, SCRIPT_RUNNERS, SCRIPT_EXECUTORS, } from './constants.js';
export const tryPkg = (pkg) => {
    try {
        return cjsRequire.resolve(pkg);
    }
    catch (_a) { }
};
export const tryRequirePkg = (pkg) => {
    try {
        return cjsRequire(pkg);
    }
    catch (_a) { }
};
export const isPkgAvailable = (pkg) => !!tryPkg(pkg);
export const isTsAvailable = isPkgAvailable('typescript');
export const isAngularAvailable = isPkgAvailable('@angular/core/package.json');
export const isMdxAvailable = isPkgAvailable('@mdx-js/mdx/package.json') ||
    isPkgAvailable('@mdx-js/react/package.json');
export const isReactAvailable = isPkgAvailable('react');
export const isSvelteAvailable = isPkgAvailable('svelte');
export const isVueAvailable = isPkgAvailable('vue');
export const tryFile = (filePath, includeDir = false) => {
    if (typeof filePath === 'string') {
        return fs.existsSync(filePath) &&
            (includeDir || fs.statSync(filePath).isFile())
            ? filePath
            : '';
    }
    for (const file of filePath !== null && filePath !== void 0 ? filePath : []) {
        if (tryFile(file, includeDir)) {
            return file;
        }
    }
    return '';
};
export const tryExtensions = (filepath, extensions = EXTENSIONS) => {
    const ext = [...extensions, ''].find(ext => tryFile(filepath + ext));
    return ext == null ? '' : filepath + ext;
};
export const tryGlob = (paths, options = {}) => {
    const { absolute = true, baseDir = CWD, ignore = ['**/node_modules/**'], } = typeof options === 'string' ? { baseDir: options } : options;
    return paths.reduce((acc, pkg) => [
        ...acc,
        ...(isGlob(pkg)
            ? tryRequirePkg('fast-glob')
                .sync(pkg, {
                cwd: baseDir,
                ignore,
                onlyFiles: false,
            })
                .map(file => (absolute ? path.resolve(baseDir, file) : file))
            : [tryFile(path.resolve(baseDir, pkg), true)]),
    ].filter(Boolean), []);
};
export const identify = (_) => !!_;
export const findUp = (searchEntry, searchFile = 'package.json') => {
    console.assert(path.isAbsolute(searchEntry));
    if (!tryFile(searchEntry, true) ||
        (searchEntry !== CWD && !searchEntry.startsWith(CWD + path.sep))) {
        return '';
    }
    searchEntry = path.resolve(fs.statSync(searchEntry).isDirectory()
        ? searchEntry
        : path.resolve(searchEntry, '..'));
    do {
        const searched = tryFile(path.resolve(searchEntry, searchFile));
        if (searched) {
            return searched;
        }
        searchEntry = path.resolve(searchEntry, '..');
    } while (searchEntry === CWD || searchEntry.startsWith(CWD + path.sep));
    return '';
};
export const arrayify = (...args) => args.reduce((arr, curr) => {
    arr.push(...(Array.isArray(curr) ? curr : curr == null ? [] : [curr]));
    return arr;
}, []);
export const getPackageManager = () => {
    const execPath = process.env.npm_execpath;
    if (!execPath) {
        return;
    }
    if (/\byarn\b/.test(execPath)) {
        return 'yarn';
    }
    if (/\bpnpm\b/.test(execPath)) {
        return 'pnpm';
    }
    if (/\bnpm\b/.test(execPath)) {
        return 'npm';
    }
    console.warn('unknown package manager:', execPath);
};
export const getScriptRunner = () => {
    const pm = getPackageManager();
    if (!pm) {
        return;
    }
    return SCRIPT_RUNNERS[pm];
};
export const getScriptExecutor = () => {
    const pm = getPackageManager();
    if (!pm) {
        return;
    }
    return SCRIPT_EXECUTORS[pm];
};
//# sourceMappingURL=helpers.js.map