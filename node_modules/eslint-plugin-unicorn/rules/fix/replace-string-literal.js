'use strict';

function replaceStringLiteral(fixer, node, text, relativeRangeStart, relativeRangeEnd) {
	const firstCharacterIndex = node.range[0] + 1;
	const start = Number.isInteger(relativeRangeEnd) ? relativeRangeStart + firstCharacterIndex : firstCharacterIndex;
	const end = Number.isInteger(relativeRangeEnd) ? relativeRangeEnd + firstCharacterIndex : node.range[1] - 1;

	return fixer.replaceTextRange([start, end], text);
}

module.exports = replaceStringLiteral;
