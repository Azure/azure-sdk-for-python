'use strict';
const {getParentheses} = require('../utils/parentheses.js');

function * removeParentheses(node, fixer, sourceCode) {
	const parentheses = getParentheses(node, sourceCode);
	for (const token of parentheses) {
		yield fixer.remove(token);
	}
}

module.exports = removeParentheses;
