'use strict';

function not(selectors) {
	selectors = Array.isArray(selectors) ? selectors : [selectors];
	return `:not(${selectors.join(', ')})`;
}

module.exports = not;
