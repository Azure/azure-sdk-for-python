'use strict';

const replaceTemplateElement = (fixer, node, replacement) => {
	const {range: [start, end], tail} = node;
	return fixer.replaceTextRange(
		[start + 1, end - (tail ? 1 : 2)],
		replacement,
	);
};

module.exports = replaceTemplateElement;
