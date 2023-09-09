'use strict';
const {getParenthesizedRange} = require('../utils/parentheses.js');

function replaceArgument(fixer, node, text, sourceCode) {
	return fixer.replaceTextRange(getParenthesizedRange(node, sourceCode), text);
}

module.exports = replaceArgument;
