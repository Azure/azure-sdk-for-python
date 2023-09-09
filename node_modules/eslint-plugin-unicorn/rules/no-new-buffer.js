'use strict';
const {getStaticValue} = require('@eslint-community/eslint-utils');
const {newExpressionSelector} = require('./selectors/index.js');
const {switchNewExpressionToCallExpression} = require('./fix/index.js');
const isNumber = require('./utils/is-number.js');

const ERROR = 'error';
const ERROR_UNKNOWN = 'error-unknown';
const SUGGESTION = 'suggestion';
const messages = {
	[ERROR]: '`new Buffer()` is deprecated, use `Buffer.{{method}}()` instead.',
	[ERROR_UNKNOWN]: '`new Buffer()` is deprecated, use `Buffer.alloc()` or `Buffer.from()` instead.',
	[SUGGESTION]: 'Switch to `Buffer.{{replacement}}()`.',
};

const inferMethod = (bufferArguments, scope) => {
	if (bufferArguments.length !== 1) {
		return 'from';
	}

	const [firstArgument] = bufferArguments;
	if (firstArgument.type === 'SpreadElement') {
		return;
	}

	if (firstArgument.type === 'ArrayExpression' || firstArgument.type === 'TemplateLiteral') {
		return 'from';
	}

	if (isNumber(firstArgument, scope)) {
		return 'alloc';
	}

	const staticResult = getStaticValue(firstArgument, scope);
	if (staticResult) {
		const {value} = staticResult;
		if (
			typeof value === 'string'
			|| Array.isArray(value)
		) {
			return 'from';
		}
	}
};

function fix(node, sourceCode, method) {
	return function * (fixer) {
		yield fixer.insertTextAfter(node.callee, `.${method}`);
		yield * switchNewExpressionToCallExpression(node, sourceCode, fixer);
	};
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();
	return {
		[newExpressionSelector('Buffer')](node) {
			const method = inferMethod(node.arguments, sourceCode.getScope(node));

			if (method) {
				return {
					node,
					messageId: ERROR,
					data: {method},
					fix: fix(node, sourceCode, method),
				};
			}

			return {
				node,
				messageId: ERROR_UNKNOWN,
				suggest: ['from', 'alloc'].map(replacement => ({
					messageId: SUGGESTION,
					data: {replacement},
					fix: fix(node, sourceCode, replacement),
				})),
			};
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Enforce the use of `Buffer.from()` and `Buffer.alloc()` instead of the deprecated `new Buffer()`.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages,
	},
};
