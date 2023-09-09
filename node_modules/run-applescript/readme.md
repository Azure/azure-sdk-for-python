# run-applescript

> Run AppleScript and get the result

## Install

```
$ npm install run-applescript
```

## Usage

```js
import {runAppleScriptAsync} from 'run-applescript';

const result = await runAppleScriptAsync('return "unicorn"');

console.log(result);
//=> 'unicorn'
```

## API

### runAppleScriptAsync(script)

Returns a `Promise<string>` with the script result.

### runAppleScriptSync(script)

Returns a `string` with the script result.

## Related

- [run-jxa](https://github.com/sindresorhus/run-jxa) - Run JXA code and get the result
