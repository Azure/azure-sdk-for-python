'use strict';
const {getParenthesizedRange} = require('../utils/parentheses.js');

function removeMemberExpressionProperty(fixer, memberExpression, sourceCode) {
	const [, start] = getParenthesizedRange(memberExpression.object, sourceCode);
	const [, end] = memberExpression.range;

	return fixer.removeRange([start, end]);
}

module.exports = removeMemberExpressionProperty;
