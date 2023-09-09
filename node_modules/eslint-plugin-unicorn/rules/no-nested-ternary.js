'use strict';
const {isParenthesized} = require('@eslint-community/eslint-utils');

const MESSAGE_ID_TOO_DEEP = 'too-deep';
const MESSAGE_ID_SHOULD_PARENTHESIZED = 'should-parenthesized';
const messages = {
	[MESSAGE_ID_TOO_DEEP]: 'Do not nest ternary expressions.',
	[MESSAGE_ID_SHOULD_PARENTHESIZED]: 'Nest ternary expression should be parenthesized.',
};

const nestTernarySelector = level => `:not(ConditionalExpression)${' > ConditionalExpression'.repeat(level)}`;

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		[nestTernarySelector(3)]: node =>
			// Nesting more than one level not allowed.
			({node, messageId: MESSAGE_ID_TOO_DEEP}),
		[nestTernarySelector(2)](node) {
			if (!isParenthesized(node, sourceCode)) {
				return {
					node,
					messageId: MESSAGE_ID_SHOULD_PARENTHESIZED,
					fix: fixer => [
						fixer.insertTextBefore(node, '('),
						fixer.insertTextAfter(node, ')'),
					],
				};
			}
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow nested ternary expressions.',
		},
		fixable: 'code',
		messages,
	},
};
