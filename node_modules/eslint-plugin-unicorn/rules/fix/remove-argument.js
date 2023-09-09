'use strict';
const {isCommaToken} = require('@eslint-community/eslint-utils');
const {getParentheses} = require('../utils/parentheses.js');

function removeArgument(fixer, node, sourceCode) {
	const callExpression = node.parent;
	const index = callExpression.arguments.indexOf(node);
	const parentheses = getParentheses(node, sourceCode);
	const firstToken = parentheses[0] || node;
	const lastToken = parentheses[parentheses.length - 1] || node;

	let [start] = firstToken.range;
	let [, end] = lastToken.range;

	if (index !== 0) {
		start = sourceCode.getTokenBefore(firstToken).range[0];
	}

	// If the removed argument is the only argument, the trailing comma must be removed too
	/* c8 ignore start */
	if (callExpression.arguments.length === 1) {
		const tokenAfter = sourceCode.getTokenBefore(lastToken);
		if (isCommaToken(tokenAfter)) {
			end = tokenAfter[1];
		}
	}
	/* c8 ignore end */

	return fixer.replaceTextRange([start, end], '');
}

module.exports = removeArgument;
