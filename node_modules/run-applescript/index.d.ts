/**
Run AppleScript asynchronously.

@param script - The script to run.
@returns The script result.

@example
```
import {runAppleScriptAsync} from 'run-applescript';

const result = await runAppleScriptAsync('return "unicorn"');

console.log(result);
//=> 'unicorn'
```
*/
export function runAppleScriptAsync(script: string): Promise<string>;

/**
Run AppleScript synchronously.

@param script - The script to run.
@returns The script result.

@example
```
import {runAppleScriptSync} from 'run-applescript';

const result = runAppleScriptSync('return "unicorn"');

console.log(result);
//=> 'unicorn'
```
*/
export function runAppleScriptSync(script: string): string;
