'use strict';

function getIndentString(node, sourceCode) {
	const {line, column} = sourceCode.getLocFromIndex(node.range[0]);
	const lines = sourceCode.getLines();
	const before = lines[line - 1].slice(0, column);

	return before.match(/\s*$/)[0];
}

module.exports = getIndentString;
