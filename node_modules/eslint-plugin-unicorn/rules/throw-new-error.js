'use strict';
const {matches} = require('./selectors/index.js');
const {switchCallExpressionToNewExpression} = require('./fix/index.js');

const messageId = 'throw-new-error';
const messages = {
	[messageId]: 'Use `new` when throwing an error.',
};

const customError = /^(?:[A-Z][\da-z]*)*Error$/;

const selector = [
	'ThrowStatement',
	' > ',
	'CallExpression.argument',
	matches([
		// `throw FooError()`
		[
			'[callee.type="Identifier"]',
			`[callee.name=/${customError.source}/]`,
		].join(''),
		// `throw lib.FooError()`
		[
			'[callee.type="MemberExpression"]',
			'[callee.computed!=true]',
			'[callee.property.type="Identifier"]',
			`[callee.property.name=/${customError.source}/]`,
		].join(''),
	]),
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector]: node => ({
		node,
		messageId,
		fix: fixer => switchCallExpressionToNewExpression(node, context.getSourceCode(), fixer),
	}),
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Require `new` when throwing an error.',
		},
		fixable: 'code',
		messages,
	},
};
