'use strict';
const {checkVueTemplate} = require('./utils/rule.js');
const {getParenthesizedRange} = require('./utils/parentheses.js');
const {replaceNodeOrTokenAndSpacesBefore, fixSpaceAroundKeyword} = require('./fix/index.js');

const isInstanceofToken = token => token.value === 'instanceof' && token.type === 'Keyword';

const MESSAGE_ID = 'no-instanceof-array';
const messages = {
	[MESSAGE_ID]: 'Use `Array.isArray()` instead of `instanceof Array`.',
};
const selector = [
	'BinaryExpression',
	'[operator="instanceof"]',
	'[right.type="Identifier"]',
	'[right.name="Array"]',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		[selector](node) {
			const {left, right} = node;
			let tokenStore = sourceCode;
			let instanceofToken = tokenStore.getTokenAfter(left, isInstanceofToken);
			if (!instanceofToken && context.parserServices.getTemplateBodyTokenStore) {
				tokenStore = context.parserServices.getTemplateBodyTokenStore();
				instanceofToken = tokenStore.getTokenAfter(left, isInstanceofToken);
			}

			return {
				node: instanceofToken,
				messageId: MESSAGE_ID,
				/** @param {import('eslint').Rule.RuleFixer} fixer */
				* fix(fixer) {
					yield * fixSpaceAroundKeyword(fixer, node, sourceCode);

					const range = getParenthesizedRange(left, tokenStore);
					yield fixer.insertTextBeforeRange(range, 'Array.isArray(');
					yield fixer.insertTextAfterRange(range, ')');

					yield * replaceNodeOrTokenAndSpacesBefore(instanceofToken, '', fixer, sourceCode, tokenStore);
					yield * replaceNodeOrTokenAndSpacesBefore(right, '', fixer, sourceCode, tokenStore);
				},
			};
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create: checkVueTemplate(create),
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Require `Array.isArray()` instead of `instanceof Array`.',
		},
		fixable: 'code',
		messages,
	},
};
