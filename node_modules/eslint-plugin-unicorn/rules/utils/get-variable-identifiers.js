'use strict';

// Get identifiers of given variable
module.exports = ({identifiers, references}) => [...new Set([
	...identifiers,
	...references.map(({identifier}) => identifier),
])];
