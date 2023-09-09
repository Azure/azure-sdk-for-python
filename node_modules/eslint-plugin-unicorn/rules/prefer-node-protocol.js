'use strict';
const isBuiltinModule = require('is-builtin-module');
const {matches, STATIC_REQUIRE_SOURCE_SELECTOR} = require('./selectors/index.js');
const {replaceStringLiteral} = require('./fix/index.js');

const MESSAGE_ID = 'prefer-node-protocol';
const messages = {
	[MESSAGE_ID]: 'Prefer `node:{{moduleName}}` over `{{moduleName}}`.',
};

const importExportSourceSelector = [
	':matches(ImportDeclaration, ExportNamedDeclaration, ImportExpression)',
	' > ',
	'Literal.source',
].join('');

const selector = matches([
	importExportSourceSelector,
	STATIC_REQUIRE_SOURCE_SELECTOR,
]);

const create = () => ({
	[selector](node) {
		const {value} = node;
		if (
			typeof value !== 'string'
			|| value.startsWith('node:')
			|| !isBuiltinModule(value)
		) {
			return;
		}

		return {
			node,
			messageId: MESSAGE_ID,
			data: {moduleName: value},
			/** @param {import('eslint').Rule.RuleFixer} fixer */
			fix: fixer => replaceStringLiteral(fixer, node, 'node:', 0, 0),
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer using the `node:` protocol when importing Node.js builtin modules.',
		},
		fixable: 'code',
		messages,
	},
};
