import { __awaiter } from "tslib";
import { execSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import spawn from 'cross-spawn';
import picocolors from 'picocolors';
const OSX_CHROME = 'google chrome';
var Action;
(function (Action) {
    Action[Action["NONE"] = 0] = "NONE";
    Action[Action["BROWSER"] = 1] = "BROWSER";
    Action[Action["SCRIPT"] = 2] = "SCRIPT";
})(Action || (Action = {}));
function getBrowserEnv() {
    const value = process.env.BROWSER;
    const args = process.env.BROWSER_ARGS
        ? process.env.BROWSER_ARGS.split(' ')
        : [];
    let action;
    if (!value) {
        action = Action.BROWSER;
    }
    else if (value.toLowerCase().endsWith('.js')) {
        action = Action.SCRIPT;
    }
    else if (value.toLowerCase() === 'none') {
        action = Action.NONE;
    }
    else {
        action = Action.BROWSER;
    }
    return { action, value, args };
}
function executeNodeScript(scriptPath, url) {
    const extraArgs = process.argv.slice(2);
    const child = spawn(process.execPath, [scriptPath, ...extraArgs, url], {
        stdio: 'inherit',
    });
    child.on('close', code => {
        if (code !== 0) {
            console.log();
            console.log(picocolors.red('The script specified as BROWSER environment variable failed.'));
            console.log(`${picocolors.cyan(scriptPath)} exited with code ${code}`);
            console.log();
        }
    });
    return true;
}
function startBrowserProcess(browser, url, args) {
    return __awaiter(this, void 0, void 0, function* () {
        const shouldTryOpenChromiumWithAppleScript = process.platform === 'darwin' &&
            (typeof browser !== 'string' || browser === OSX_CHROME);
        if (shouldTryOpenChromiumWithAppleScript) {
            const supportedChromiumBrowsers = [
                'Google Chrome Canary',
                'Google Chrome',
                'Microsoft Edge',
                'Brave Browser',
                'Vivaldi',
                'Chromium',
            ];
            const _dirname = typeof __dirname === 'undefined'
                ? path.dirname(fileURLToPath(import.meta.url))
                : __dirname;
            for (const chromiumBrowser of supportedChromiumBrowsers) {
                try {
                    execSync('ps cax | grep "' + chromiumBrowser + '"');
                    execSync('osascript ../openChrome.applescript "' +
                        encodeURI(url) +
                        '" "' +
                        chromiumBrowser +
                        '"', {
                        cwd: _dirname,
                        stdio: 'ignore',
                    });
                    return true;
                }
                catch (_a) {
                }
            }
        }
        if (process.platform === 'darwin' && browser === 'open') {
            browser = undefined;
        }
        try {
            const open = (yield import('open')).default;
            open(url, {
                app: browser
                    ? {
                        name: browser,
                        arguments: args,
                    }
                    : undefined,
                wait: false,
            }).catch(() => { });
            return true;
        }
        catch (_b) {
            return false;
        }
    });
}
export function openBrowser(url) {
    return __awaiter(this, void 0, void 0, function* () {
        const { action, value, args } = getBrowserEnv();
        switch (action) {
            case Action.NONE: {
                return false;
            }
            case Action.SCRIPT: {
                return executeNodeScript(value, url);
            }
            case Action.BROWSER: {
                return startBrowserProcess(value, url, args);
            }
            default: {
                throw new Error('Not implemented.');
            }
        }
    });
}
//# sourceMappingURL=browser.js.map