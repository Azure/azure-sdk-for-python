var _a, _b, _c, _d;
import path from 'node:path';
import { tryGlob, tryRequirePkg } from './helpers.js';
const pkg = (_a = tryRequirePkg(path.resolve('package.json'))) !== null && _a !== void 0 ? _a : {};
const lernaConfig = (_b = tryRequirePkg(path.resolve('lerna.json'))) !== null && _b !== void 0 ? _b : {};
const pkgsPath = (_d = (_c = lernaConfig.packages) !== null && _c !== void 0 ? _c : pkg.workspaces) !== null && _d !== void 0 ? _d : [];
export const isMonorepo = Array.isArray(pkgsPath) && pkgsPath.length > 0;
export const monorepoPkgs = isMonorepo
    ? tryGlob(pkgsPath.map(pkg => pkg.endsWith('/package.json') ? pkg : `${pkg}/package.json`))
    : [];
//# sourceMappingURL=monorepo.js.map