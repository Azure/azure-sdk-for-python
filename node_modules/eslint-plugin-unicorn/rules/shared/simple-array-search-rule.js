'use strict';

const {hasSideEffect, isParenthesized, findVariable} = require('@eslint-community/eslint-utils');
const {matches, methodCallSelector} = require('../selectors/index.js');
const isFunctionSelfUsedInside = require('../utils/is-function-self-used-inside.js');

const getBinaryExpressionSelector = path => [
	`[${path}.type="BinaryExpression"]`,
	`[${path}.operator="==="]`,
	`:matches([${path}.left.type="Identifier"], [${path}.right.type="Identifier"])`,
].join('');
const getFunctionSelector = path => [
	`[${path}.generator!=true]`,
	`[${path}.async!=true]`,
	`[${path}.params.length=1]`,
	`[${path}.params.0.type="Identifier"]`,
].join('');
const callbackFunctionSelector = path => matches([
	// Matches `foo.findIndex(bar => bar === baz)`
	[
		`[${path}.type="ArrowFunctionExpression"]`,
		getFunctionSelector(path),
		getBinaryExpressionSelector(`${path}.body`),
	].join(''),
	// Matches `foo.findIndex(bar => {return bar === baz})`
	// Matches `foo.findIndex(function (bar) {return bar === baz})`
	[
		`:matches([${path}.type="ArrowFunctionExpression"], [${path}.type="FunctionExpression"])`,
		getFunctionSelector(path),
		`[${path}.body.type="BlockStatement"]`,
		`[${path}.body.body.length=1]`,
		`[${path}.body.body.0.type="ReturnStatement"]`,
		getBinaryExpressionSelector(`${path}.body.body.0.argument`),
	].join(''),
]);
const isIdentifierNamed = ({type, name}, expectName) => type === 'Identifier' && name === expectName;

function simpleArraySearchRule({method, replacement}) {
	// Add prefix to avoid conflicts in `prefer-includes` rule
	const MESSAGE_ID_PREFIX = `prefer-${replacement}-over-${method}/`;
	const ERROR = `${MESSAGE_ID_PREFIX}error`;
	const SUGGESTION = `${MESSAGE_ID_PREFIX}suggestion`;
	const ERROR_MESSAGES = {
		findIndex: 'Use `.indexOf()` instead of `.findIndex()` when looking for the index of an item.',
		findLastIndex: 'Use `.lastIndexOf()` instead of `findLastIndex() when looking for the index of an item.`',
		some: `Use \`.${replacement}()\` instead of \`.${method}()\` when checking value existence.`,
	};

	const messages = {
		[ERROR]: ERROR_MESSAGES[method],
		[SUGGESTION]: `Replace \`.${method}()\` with \`.${replacement}()\`.`,
	};

	const selector = [
		methodCallSelector({
			method,
			argumentsLength: 1,
		}),
		callbackFunctionSelector('arguments.0'),
	].join('');

	function createListeners(context) {
		const sourceCode = context.getSourceCode();
		const {scopeManager} = sourceCode;

		return {
			[selector](node) {
				const [callback] = node.arguments;
				const binaryExpression = callback.body.type === 'BinaryExpression'
					? callback.body
					: callback.body.body[0].argument;
				const [parameter] = callback.params;
				const {left, right} = binaryExpression;
				const {name} = parameter;

				let searchValueNode;
				let parameterInBinaryExpression;
				if (isIdentifierNamed(left, name)) {
					searchValueNode = right;
					parameterInBinaryExpression = left;
				} else if (isIdentifierNamed(right, name)) {
					searchValueNode = left;
					parameterInBinaryExpression = right;
				} else {
					return;
				}

				const callbackScope = scopeManager.acquire(callback);
				if (
					// `parameter` is used somewhere else
					findVariable(callbackScope, parameter).references.some(({identifier}) => identifier !== parameterInBinaryExpression)
					|| isFunctionSelfUsedInside(callback, callbackScope)
				) {
					return;
				}

				const method = node.callee.property;
				const problem = {
					node: method,
					messageId: ERROR,
					suggest: [],
				};

				const fix = function * (fixer) {
					let text = sourceCode.getText(searchValueNode);
					if (isParenthesized(searchValueNode, sourceCode) && !isParenthesized(callback, sourceCode)) {
						text = `(${text})`;
					}

					yield fixer.replaceText(method, replacement);
					yield fixer.replaceText(callback, text);
				};

				if (hasSideEffect(searchValueNode, sourceCode)) {
					problem.suggest.push({messageId: SUGGESTION, fix});
				} else {
					problem.fix = fix;
				}

				return problem;
			},
		};
	}

	return {messages, createListeners};
}

module.exports = simpleArraySearchRule;
