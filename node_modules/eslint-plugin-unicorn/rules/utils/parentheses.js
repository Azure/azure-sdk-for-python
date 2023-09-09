'use strict';
const {isParenthesized, isOpeningParenToken, isClosingParenToken} = require('@eslint-community/eslint-utils');

/*
Get how many times the node is parenthesized.

@param {Node} node - The node to be checked.
@param {SourceCode} sourceCode - The source code object.
@returns {number}
*/
function getParenthesizedTimes(node, sourceCode) {
	let times = 0;

	while (isParenthesized(times + 1, node, sourceCode)) {
		times++;
	}

	return times;
}

/*
Get all parentheses tokens around the node.

@param {Node} node - The node to be checked.
@param {SourceCode} sourceCode - The source code object.
@returns {Token[]}
*/
function getParentheses(node, sourceCode) {
	const count = getParenthesizedTimes(node, sourceCode);

	if (count === 0) {
		return [];
	}

	return [
		...sourceCode.getTokensBefore(node, {count, filter: isOpeningParenToken}),
		...sourceCode.getTokensAfter(node, {count, filter: isClosingParenToken}),
	];
}

/*
Get the parenthesized range of the node.

@param {Node} node - The node to be checked.
@param {SourceCode} sourceCode - The source code object.
@returns {number[]}
*/
function getParenthesizedRange(node, sourceCode) {
	const parentheses = getParentheses(node, sourceCode);
	const [start] = (parentheses[0] || node).range;
	const [, end] = (parentheses[parentheses.length - 1] || node).range;
	return [start, end];
}

/*
Get the parenthesized text of the node.

@param {Node} node - The node to be checked.
@param {SourceCode} sourceCode - The source code object.
@returns {string}
*/
function getParenthesizedText(node, sourceCode) {
	const [start, end] = getParenthesizedRange(node, sourceCode);
	return sourceCode.text.slice(start, end);
}

module.exports = {
	isParenthesized,
	getParenthesizedTimes,
	getParentheses,
	getParenthesizedRange,
	getParenthesizedText,
};
