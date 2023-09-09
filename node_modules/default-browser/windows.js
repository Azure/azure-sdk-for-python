import {execa} from 'execa';

// Windows doesn't have browser IDs in the same way macOS/Linux does so we give fake
// ones that look real and match the macOS/Linux versions for cross-platform apps.
const windowsBrowserProgIds = {
	AppXq0fevzme2pys62n3e0fbqa7peapykr8v: {name: 'Edge', id: 'com.microsoft.edge.old'},
	MSEdgeDHTML: {name: 'Edge', id: 'com.microsoft.edge'}, // On macOS, it's "com.microsoft.edgemac"
	MSEdgeHTM: {name: 'Edge', id: 'com.microsoft.edge'}, // Newer Edge/Win10 releases
	'IE.HTTP': {name: 'Internet Explorer', id: 'com.microsoft.ie'},
	FirefoxURL: {name: 'Firefox', id: 'org.mozilla.firefox'},
	ChromeHTML: {name: 'Chrome', id: 'com.google.chrome'},
};

export class UnknownBrowserError extends Error {}

export default async function defaultBrowser(_execa = execa) {
	const result = await _execa('reg', [
		'QUERY',
		' HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice',
		'/v',
		'ProgId',
	]);

	const match = /ProgId\s*REG_SZ\s*(?<id>\S+)/.exec(result.stdout);
	if (!match) {
		throw new UnknownBrowserError(`Cannot find Windows browser in stdout: ${JSON.stringify(result.stdout)}`);
	}

	const {id} = match.groups;

	const browser = windowsBrowserProgIds[id];
	if (!browser) {
		throw new UnknownBrowserError(`Unknown browser ID: ${id}`);
	}

	return browser;
}
