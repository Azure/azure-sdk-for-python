'use strict';

/**
@typedef {line: number, column: number} Position

Get the location of the given class node for reporting.

@param {Node} node - The class node to get.
@param {SourceCode} sourceCode - The source code object to get tokens.
@returns {{start: Position, end: Position}} The location of the class node for reporting.
*/
function getClassHeadLocation(node, sourceCode) {
	const {loc, body} = node;
	const tokenBeforeBody = sourceCode.getTokenBefore(body);

	const {start} = loc;
	const {end} = tokenBeforeBody.loc;

	return {start, end};
}

module.exports = getClassHeadLocation;
