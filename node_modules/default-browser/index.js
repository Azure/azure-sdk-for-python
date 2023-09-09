import process from 'node:process';
import defaultBrowserId from 'default-browser-id';
import bundleName from 'bundle-name';
import titleize from 'titleize';
import {execa} from 'execa';
import windows from './windows.js';

export default async function defaultBrowser() {
	if (process.platform === 'linux') {
		const {stdout} = await execa('xdg-mime', ['query', 'default', 'x-scheme-handler/http']);
		const name = titleize(stdout.trim().replace(/.desktop$/, '').replace('-', ' '));

		return {
			name,
			id: stdout,
		};
	}

	if (process.platform === 'darwin') {
		const id = await defaultBrowserId();
		const name = await bundleName(id);
		return {name, id};
	}

	if (process.platform === 'win32') {
		return windows();
	}

	throw new Error('Only macOS, Linux, and Windows are supported');
}
