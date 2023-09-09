'use strict';
const {isParenthesized, hasSideEffect} = require('@eslint-community/eslint-utils');
const {methodCallSelector, notDomNodeSelector} = require('./selectors/index.js');
const needsSemicolon = require('./utils/needs-semicolon.js');
const isValueNotUsable = require('./utils/is-value-not-usable.js');
const {getParenthesizedText} = require('./utils/parentheses.js');
const shouldAddParenthesesToMemberExpressionObject = require('./utils/should-add-parentheses-to-member-expression-object.js');

const ERROR_MESSAGE_ID = 'error';
const SUGGESTION_MESSAGE_ID = 'suggestion';
const messages = {
	[ERROR_MESSAGE_ID]: 'Prefer `childNode.remove()` over `parentNode.removeChild(childNode)`.',
	[SUGGESTION_MESSAGE_ID]: 'Replace `parentNode.removeChild(childNode)` with `childNode.remove()`.',
};

const selector = [
	methodCallSelector({
		method: 'removeChild',
		argumentsLength: 1,
		includeOptionalMember: true,
	}),
	notDomNodeSelector('callee.object'),
	notDomNodeSelector('arguments.0'),
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		[selector](node) {
			const parentNode = node.callee.object;
			const childNode = node.arguments[0];

			const problem = {
				node,
				messageId: ERROR_MESSAGE_ID,
			};

			const fix = fixer => {
				let childNodeText = getParenthesizedText(childNode, sourceCode);
				if (
					!isParenthesized(childNode, sourceCode)
					&& shouldAddParenthesesToMemberExpressionObject(childNode, sourceCode)
				) {
					childNodeText = `(${childNodeText})`;
				}

				if (needsSemicolon(sourceCode.getTokenBefore(node), sourceCode, childNodeText)) {
					childNodeText = `;${childNodeText}`;
				}

				return fixer.replaceText(node, `${childNodeText}.remove()`);
			};

			if (!hasSideEffect(parentNode, sourceCode) && isValueNotUsable(node) && !node.callee.optional) {
				problem.fix = fix;
			} else {
				problem.suggest = [
					{
						messageId: SUGGESTION_MESSAGE_ID,
						fix,
					},
				];
			}

			return problem;
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `childNode.remove()` over `parentNode.removeChild(childNode)`.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages,
	},
};
