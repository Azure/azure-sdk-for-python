'use strict';
const {isOpeningBraceToken} = require('@eslint-community/eslint-utils');
const {matches} = require('./selectors/index.js');

const MESSAGE_ID = 'empty-brace-spaces';
const messages = {
	[MESSAGE_ID]: 'Do not add spaces between braces.',
};

const selector = matches([
	'BlockStatement[body.length=0]',
	'ClassBody[body.length=0]',
	'ObjectExpression[properties.length=0]',
	'StaticBlock[body.length=0]',
	// Experimental https://github.com/tc39/proposal-record-tuple
	'RecordExpression[properties.length=0]',
]);

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](node) {
		const sourceCode = context.getSourceCode();
		const filter = node.type === 'RecordExpression'
			? token => token.type === 'Punctuator' && (token.value === '#{' || token.value === '{|')
			: isOpeningBraceToken;
		const openingBrace = sourceCode.getFirstToken(node, {filter});
		const closingBrace = sourceCode.getLastToken(node);
		const [, start] = openingBrace.range;
		const [end] = closingBrace.range;
		const textBetween = sourceCode.text.slice(start, end);

		if (!/^\s+$/.test(textBetween)) {
			return;
		}

		return {
			loc: {
				start: openingBrace.loc.end,
				end: closingBrace.loc.start,
			},
			messageId: MESSAGE_ID,
			fix: fixer => fixer.removeRange([start, end]),
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'layout',
		docs: {
			description: 'Enforce no spaces between braces.',
		},
		fixable: 'whitespace',
		messages,
	},
};
