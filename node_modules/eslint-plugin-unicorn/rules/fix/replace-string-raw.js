'use strict';

// Replace `StringLiteral` or `TemplateLiteral` node with raw text
const replaceStringRaw = (fixer, node, raw) =>
	fixer.replaceTextRange(
		// Ignore quotes and backticks
		[
			node.range[0] + 1,
			node.range[1] - 1,
		],
		raw,
	);

module.exports = replaceStringRaw;
