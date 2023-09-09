'use strict';
const {getFunctionHeadLocation} = require('@eslint-community/eslint-utils');
const getDocumentationUrl = require('./utils/get-documentation-url.js');
const {methodCallSelector, matches} = require('./selectors/index.js');

const MESSAGE_ID = 'no-invalid-remove-event-listener';
const messages = {
	[MESSAGE_ID]: 'The listener argument should be a function reference.',
};

const removeEventListenerSelector = [
	methodCallSelector({
		method: 'removeEventListener',
		minimumArguments: 2,
	}),
	'[arguments.0.type!="SpreadElement"]',
	matches([
		'[arguments.1.type="FunctionExpression"]',
		'[arguments.1.type="ArrowFunctionExpression"]',
		methodCallSelector({method: 'bind', path: 'arguments.1'}),
	]),
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[removeEventListenerSelector](node) {
		const listener = node.arguments[1];
		if (['ArrowFunctionExpression', 'FunctionExpression'].includes(listener.type)) {
			return {
				node: listener,
				loc: getFunctionHeadLocation(listener, context.getSourceCode()),
				messageId: MESSAGE_ID,
			};
		}

		return {
			node: listener.callee.property,
			messageId: MESSAGE_ID,
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Prevent calling `EventTarget#removeEventListener()` with the result of an expression.',
			url: getDocumentationUrl(__filename),
		},
		messages,
	},
};
