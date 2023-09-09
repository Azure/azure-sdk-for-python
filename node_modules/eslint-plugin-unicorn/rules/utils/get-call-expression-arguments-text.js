'use strict';
const {isOpeningParenToken} = require('@eslint-community/eslint-utils');

/**
Get the text of the arguments list of `CallExpression`.

@param {Node} node - The `CallExpression` node.
@param {SourceCode} sourceCode - The source code object.
@returns {string}
*/
const getCallExpressionArgumentsText = (node, sourceCode) => {
	const openingParenthesisToken = sourceCode.getTokenAfter(node.callee, isOpeningParenToken);
	const closingParenthesisToken = sourceCode.getLastToken(node);

	return sourceCode.text.slice(
		openingParenthesisToken.range[1],
		closingParenthesisToken.range[0],
	);
};

module.exports = getCallExpressionArgumentsText;
