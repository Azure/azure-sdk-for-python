'use strict';
const {getParenthesizedRange} = require('../utils/parentheses.js');
const removeMemberExpressionProperty = require('./remove-member-expression-property.js');

function * removeMethodCall(fixer, callExpression, sourceCode) {
	const memberExpression = callExpression.callee;

	// `(( (( foo )).bar ))()`
	//              ^^^^
	yield removeMemberExpressionProperty(fixer, memberExpression, sourceCode);

	// `(( (( foo )).bar ))()`
	//                     ^^
	const [, start] = getParenthesizedRange(memberExpression, sourceCode);
	const [, end] = callExpression.range;

	yield fixer.removeRange([start, end]);
}

module.exports = removeMethodCall;
