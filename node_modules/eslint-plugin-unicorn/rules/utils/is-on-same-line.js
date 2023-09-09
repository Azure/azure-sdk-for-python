'use strict';

function isOnSameLine(nodeOrTokenA, nodeOrTokenB) {
	return nodeOrTokenA.loc.start.line === nodeOrTokenB.loc.start.line;
}

module.exports = isOnSameLine;
