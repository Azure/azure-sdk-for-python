'use strict';
const {matches} = require('./selectors/index.js');

const MESSAGE_ID = 'prefer-event-target';
const messages = {
	[MESSAGE_ID]: 'Prefer `EventTarget` over `EventEmitter`.',
};

const selector = [
	'Identifier',
	'[name="EventEmitter"]',
	matches([
		'ClassDeclaration > .superClass',
		'ClassExpression > .superClass',
		'NewExpression > .callee',
	]),
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	[selector](node) {
		return {
			node,
			messageId: MESSAGE_ID,
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `EventTarget` over `EventEmitter`.',
		},
		messages,
	},
};
