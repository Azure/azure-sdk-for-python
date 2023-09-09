'use strict';
const hasSameRange = require('./has-same-range.js');

const isShorthandImportLocal = node => {
	const {type, local, imported} = node.parent;
	return type === 'ImportSpecifier' && hasSameRange(local, imported) && local === node;
};

module.exports = isShorthandImportLocal;
