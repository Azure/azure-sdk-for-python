export type Browser = {
	/**
	Human-readadable name of the browser.
	*/
	name: string;

	/**
	Unique ID for the browser on the current platform:
	- On macOS, it's the ID in LaunchServices.
	- On Linux, it's the desktop file ID (from `xdg-mime`).
	- On Windows, it's an invented ID as Windows doesn't have IDs.
	*/
	id: string;
};

/**
Get the default browser for the current platform.

@returns A promise for the browser.

```
import defaultBrowser from 'default-browser';

console.log(await defaultBrowser());
//=> {name: 'Safari', id: 'com.apple.Safari'}
```
*/
export default function defaultBrowser(): Promise<Browser>;
