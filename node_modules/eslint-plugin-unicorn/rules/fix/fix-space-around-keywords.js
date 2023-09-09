'use strict';
const {getParenthesizedRange} = require('../utils/parentheses.js');

const isProblematicToken = ({type, value}) => (
	(type === 'Keyword' && /^[a-z]*$/.test(value))
	// ForOfStatement
	|| (type === 'Identifier' && value === 'of')
	// AwaitExpression
	|| (type === 'Identifier' && value === 'await')
);

function * fixSpaceAroundKeyword(fixer, node, sourceCode) {
	const range = getParenthesizedRange(node, sourceCode);
	const tokenBefore = sourceCode.getTokenBefore({range}, {includeComments: true});

	if (
		tokenBefore
		&& range[0] === tokenBefore.range[1]
		&& isProblematicToken(tokenBefore)
	) {
		yield fixer.insertTextAfter(tokenBefore, ' ');
	}

	const tokenAfter = sourceCode.getTokenAfter({range}, {includeComments: true});

	if (
		tokenAfter
		&& range[1] === tokenAfter.range[0]
		&& isProblematicToken(tokenAfter)
	) {
		yield fixer.insertTextBefore(tokenAfter, ' ');
	}
}

module.exports = fixSpaceAroundKeyword;
