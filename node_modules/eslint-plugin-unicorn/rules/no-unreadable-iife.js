'use strict';
const {
	isParenthesized,
	getParenthesizedRange,
} = require('./utils/parentheses.js');
const toLocation = require('./utils/to-location.js');

const MESSAGE_ID_ERROR = 'no-unreadable-iife';
const messages = {
	[MESSAGE_ID_ERROR]: 'IIFE with parenthesized arrow function body is considered unreadable.',
};

const selector = [
	'CallExpression',
	' > ',
	'ArrowFunctionExpression.callee',
	' > ',
	':not(BlockStatement).body',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](node) {
		const sourceCode = context.getSourceCode();
		if (!isParenthesized(node, sourceCode)) {
			return;
		}

		return {
			node,
			loc: toLocation(getParenthesizedRange(node, sourceCode), sourceCode),
			messageId: MESSAGE_ID_ERROR,
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow unreadable IIFEs.',
		},
		hasSuggestions: false,
		messages,
	},
};
