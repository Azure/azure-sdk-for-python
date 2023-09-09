var _a;
import { createRequire } from 'node:module';
export const DEV = 'development';
export const PROD = 'production';
export const NODE_ENV = (_a = process.env.NODE_ENV) !== null && _a !== void 0 ? _a : DEV;
export const __DEV__ = NODE_ENV === DEV;
export const __PROD__ = NODE_ENV === PROD;
export const NODE_MODULES_REG = /[/\\]node_modules[/\\]/;
export const CWD = process.cwd();
export const cjsRequire = typeof require === 'undefined' ? createRequire(import.meta.url) : require;
export const EXTENSIONS = ['.ts', '.tsx', ...Object.keys(cjsRequire.extensions)];
export const SCRIPT_RUNNERS = {
    npm: 'npx',
    pnpm: 'pnpm',
    yarn: 'yarn',
};
export const SCRIPT_EXECUTORS = {
    npm: 'npx',
    pnpm: 'pnpx',
    yarn: 'yarn dlx',
};
//# sourceMappingURL=constants.js.map