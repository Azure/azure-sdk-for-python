'use strict';
const path = require('node:path');
const packageJson = require('../../package.json');

const repoUrl = 'https://github.com/sindresorhus/eslint-plugin-unicorn';

module.exports = filename => {
	const ruleName = path.basename(filename, '.js');
	return `${repoUrl}/blob/v${packageJson.version}/docs/rules/${ruleName}.md`;
};
