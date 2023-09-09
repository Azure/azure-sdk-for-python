'use strict';
const {isParenthesized} = require('../utils/parentheses.js');
const shouldAddParenthesesToNewExpressionCallee = require('../utils/should-add-parentheses-to-new-expression-callee.js');

function * switchCallExpressionToNewExpression(node, sourceCode, fixer) {
	yield fixer.insertTextBefore(node, 'new ');

	const {callee} = node;
	if (
		!isParenthesized(callee, sourceCode)
		&& shouldAddParenthesesToNewExpressionCallee(callee)
	) {
		yield fixer.insertTextBefore(callee, '(');
		yield fixer.insertTextAfter(callee, ')');
	}
}

module.exports = switchCallExpressionToNewExpression;
