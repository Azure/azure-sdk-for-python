'use strict';
const {methodCallSelector} = require('./selectors/index.js');

const MESSAGE_ID = 'prefer-string-trim-start-end';
const messages = {
	[MESSAGE_ID]: 'Prefer `String#{{replacement}}()` over `String#{{method}}()`.',
};

const selector = [
	methodCallSelector({
		methods: ['trimLeft', 'trimRight'],
		argumentsLength: 0,
		includeOptionalMember: true,
	}),
	' > .callee',
	' > .property',
].join(' ');

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	[selector](node) {
		const method = node.name;
		const replacement = method === 'trimLeft' ? 'trimStart' : 'trimEnd';

		return {
			node,
			messageId: MESSAGE_ID,
			data: {method, replacement},
			fix: fixer => fixer.replaceText(node, replacement),
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `String#trimStart()` / `String#trimEnd()` over `String#trimLeft()` / `String#trimRight()`.',
		},
		fixable: 'code',
		messages,
	},
};
