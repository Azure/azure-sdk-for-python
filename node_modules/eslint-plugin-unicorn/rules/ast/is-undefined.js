'use strict';

function isUndefined(node) {
	return node.type === 'Identifier' && node.name === 'undefined';
}

module.exports = isUndefined;
