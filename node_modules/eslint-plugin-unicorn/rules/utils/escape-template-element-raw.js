'use strict';

module.exports = string => string.replace(
	/(?<=(?:^|[^\\])(?:\\\\)*)(?<symbol>(?:`|\$(?={)))/g,
	'\\$<symbol>',
);
