/// <reference types="node" />
export declare const DEV: "development";
export declare const PROD: "production";
export declare const NODE_ENV: string;
export declare const __DEV__: boolean;
export declare const __PROD__: boolean;
export declare const NODE_MODULES_REG: RegExp;
export declare const CWD: string;
export declare const cjsRequire: NodeRequire;
export declare const EXTENSIONS: string[];
export declare const SCRIPT_RUNNERS: {
    readonly npm: "npx";
    readonly pnpm: "pnpm";
    readonly yarn: "yarn";
};
export declare const SCRIPT_EXECUTORS: {
    readonly npm: "npx";
    readonly pnpm: "pnpx";
    readonly yarn: "yarn dlx";
};
