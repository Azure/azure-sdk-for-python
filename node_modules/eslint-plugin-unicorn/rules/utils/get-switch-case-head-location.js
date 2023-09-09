'use strict';

const {isColonToken} = require('@eslint-community/eslint-utils');

/**
@typedef {line: number, column: number} Position

Get the location of the given `SwitchCase` node for reporting.

@param {Node} node - The `SwitchCase` node to get.
@param {SourceCode} sourceCode - The source code object to get tokens from.
@returns {{start: Position, end: Position}} The location of the class node for reporting.
*/
function getSwitchCaseHeadLocation(node, sourceCode) {
	const startToken = node.test || sourceCode.getFirstToken(node);
	const colonToken = sourceCode.getTokenAfter(startToken, isColonToken);

	return {start: node.loc.start, end: colonToken.loc.end};
}

module.exports = getSwitchCaseHeadLocation;
