'use strict';
const isShadowed = require('./utils/is-shadowed.js');
const {matches} = require('./selectors/index.js');
const {
	addParenthesizesToReturnOrThrowExpression,
} = require('./fix/index.js');
const {removeSpacesAfter} = require('./fix/index.js');
const isOnSameLine = require('./utils/is-on-same-line.js');
const needsSemicolon = require('./utils/needs-semicolon.js');
const {
	isParenthesized,
} = require('./utils/parentheses.js');

const MESSAGE_ID_ERROR = 'no-typeof-undefined/error';
const MESSAGE_ID_SUGGESTION = 'no-typeof-undefined/suggestion';
const messages = {
	[MESSAGE_ID_ERROR]: 'Compare with `undefined` directly instead of using `typeof`.',
	[MESSAGE_ID_SUGGESTION]: 'Switch to `… {{operator}} undefined`.',
};

const selector = [
	'BinaryExpression',
	matches(['===', '!==', '==', '!='].map(operator => `[operator="${operator}"]`)),
	'[left.type="UnaryExpression"]',
	'[left.operator="typeof"]',
	'[left.prefix]',
	'[right.type="Literal"]',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const {
		checkGlobalVariables,
	} = {
		checkGlobalVariables: false,
		...context.options[0],
	};
	const sourceCode = context.getSourceCode();

	return {
		[selector](binaryExpression) {
			const {left: typeofNode, right: undefinedString, operator} = binaryExpression;
			if (undefinedString.value !== 'undefined') {
				return;
			}

			const valueNode = typeofNode.argument;
			const isGlobalVariable = valueNode.type === 'Identifier'
				&& !isShadowed(sourceCode.getScope(valueNode), valueNode);

			if (!checkGlobalVariables && isGlobalVariable) {
				return;
			}

			const [typeofToken, secondToken] = sourceCode.getFirstTokens(typeofNode, 2);

			const fix = function * (fixer) {
				// Change `==`/`!=` to `===`/`!==`
				if (operator === '==' || operator === '!=') {
					const operatorToken = sourceCode.getTokenAfter(
						typeofNode,
						token => token.type === 'Punctuator' && token.value === operator,
					);

					yield fixer.insertTextAfter(operatorToken, '=');
				}

				yield fixer.replaceText(undefinedString, 'undefined');

				yield fixer.remove(typeofToken);
				yield removeSpacesAfter(typeofToken, sourceCode, fixer);

				const {parent} = binaryExpression;
				if (
					(parent.type === 'ReturnStatement' || parent.type === 'ThrowStatement')
					&& parent.argument === binaryExpression
					&& !isOnSameLine(typeofToken, secondToken)
					&& !isParenthesized(binaryExpression, sourceCode)
					&& !isParenthesized(typeofNode, sourceCode)
				) {
					yield * addParenthesizesToReturnOrThrowExpression(fixer, parent, sourceCode);
					return;
				}

				const tokenBefore = sourceCode.getTokenBefore(binaryExpression);
				if (needsSemicolon(tokenBefore, sourceCode, secondToken.value)) {
					yield fixer.insertTextBefore(binaryExpression, ';');
				}
			};

			const problem = {
				node: binaryExpression,
				loc: typeofToken.loc,
				messageId: MESSAGE_ID_ERROR,
			};

			if (isGlobalVariable) {
				problem.suggest = [
					{
						messageId: MESSAGE_ID_SUGGESTION,
						data: {operator: operator.startsWith('!') ? '!==' : '==='},
						fix,
					},
				];
			} else {
				problem.fix = fix;
			}

			return problem;
		},
	};
};

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			checkGlobalVariables: {
				type: 'boolean',
				default: false,
			},
		},
	},
];

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow comparing `undefined` using `typeof`.',
		},
		fixable: 'code',
		hasSuggestions: true,
		schema,
		messages,
	},
};
