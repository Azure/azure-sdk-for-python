'use strict';
const isMethodNamed = require('./utils/is-method-named.js');
const simpleArraySearchRule = require('./shared/simple-array-search-rule.js');
const {isLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'prefer-includes';
const messages = {
	[MESSAGE_ID]: 'Use `.includes()`, rather than `.indexOf()`, when checking for existence.',
};
// Ignore {_,lodash,underscore}.indexOf
const ignoredVariables = new Set(['_', 'lodash', 'underscore']);
const isIgnoredTarget = node => node.type === 'Identifier' && ignoredVariables.has(node.name);
const isNegativeOne = node => node.type === 'UnaryExpression' && node.operator === '-' && node.argument && node.argument.type === 'Literal' && node.argument.value === 1;
const isLiteralZero = node => isLiteral(node, 0);
const isNegativeResult = node => ['===', '==', '<'].includes(node.operator);

const getProblem = (context, node, target, argumentsNodes) => {
	const sourceCode = context.getSourceCode();
	const memberExpressionNode = target.parent;
	const dotToken = sourceCode.getTokenBefore(memberExpressionNode.property);
	const targetSource = sourceCode.getText().slice(memberExpressionNode.range[0], dotToken.range[0]);

	// Strip default `fromIndex`
	if (isLiteralZero(argumentsNodes[1])) {
		argumentsNodes = argumentsNodes.slice(0, 1);
	}

	const argumentsSource = argumentsNodes.map(argument => sourceCode.getText(argument));

	return {
		node: memberExpressionNode.property,
		messageId: MESSAGE_ID,
		fix(fixer) {
			const replacement = `${isNegativeResult(node) ? '!' : ''}${targetSource}.includes(${argumentsSource.join(', ')})`;
			return fixer.replaceText(node, replacement);
		},
	};
};

const includesOverSomeRule = simpleArraySearchRule({
	method: 'some',
	replacement: 'includes',
});

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	BinaryExpression(node) {
		const {left, right, operator} = node;

		if (!isMethodNamed(left, 'indexOf')) {
			return;
		}

		const target = left.callee.object;

		if (isIgnoredTarget(target)) {
			return;
		}

		const {arguments: argumentsNodes} = left;

		// Ignore something.indexOf(foo, 0, another)
		if (argumentsNodes.length > 2) {
			return;
		}

		if (
			(['!==', '!=', '>', '===', '=='].includes(operator) && isNegativeOne(right))
			|| (['>=', '<'].includes(operator) && isLiteralZero(right))
		) {
			return getProblem(
				context,
				node,
				target,
				argumentsNodes,
			);
		}
	},
	...includesOverSomeRule.createListeners(context),
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `.includes()` over `.indexOf()` and `Array#some()` when checking for existence or non-existence.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages: {
			...messages,
			...includesOverSomeRule.messages,
		},
	},
};
