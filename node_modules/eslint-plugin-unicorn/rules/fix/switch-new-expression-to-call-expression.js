'use strict';
const isNewExpressionWithParentheses = require('../utils/is-new-expression-with-parentheses.js');
const {isParenthesized} = require('../utils/parentheses.js');
const isOnSameLine = require('../utils/is-on-same-line.js');
const addParenthesizesToReturnOrThrowExpression = require('./add-parenthesizes-to-return-or-throw-expression.js');
const removeSpaceAfter = require('./remove-spaces-after.js');

function * switchNewExpressionToCallExpression(newExpression, sourceCode, fixer) {
	const newToken = sourceCode.getFirstToken(newExpression);
	yield fixer.remove(newToken);
	yield removeSpaceAfter(newToken, sourceCode, fixer);

	if (!isNewExpressionWithParentheses(newExpression, sourceCode)) {
		yield fixer.insertTextAfter(newExpression, '()');
	}

	/*
		Remove `new` from this code will makes the function return `undefined`

		```js
			() => {
				return new // comment
					Foo()
			}
		```
	*/
	if (!isOnSameLine(newToken, newExpression.callee) && !isParenthesized(newExpression, sourceCode)) {
		// Ideally, we should use first parenthesis of the `callee`, and should check spaces after the `new` token
		// But adding extra parentheses is harmless, no need to be too complicated
		yield * addParenthesizesToReturnOrThrowExpression(fixer, newExpression.parent, sourceCode);
	}
}

module.exports = switchNewExpressionToCallExpression;
