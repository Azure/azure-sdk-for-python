'use strict';

function removeSpacesAfter(indexOrNodeOrToken, sourceCode, fixer) {
	let index = indexOrNodeOrToken;
	if (typeof indexOrNodeOrToken === 'object' && Array.isArray(indexOrNodeOrToken.range)) {
		index = indexOrNodeOrToken.range[1];
	}

	const textAfter = sourceCode.text.slice(index);
	const [leadingSpaces] = textAfter.match(/^\s*/);
	return fixer.removeRange([index, index + leadingSpaces.length]);
}

module.exports = removeSpacesAfter;
