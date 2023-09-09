'use strict';

const isShorthandPropertyValue = identifier =>
	identifier.parent.type === 'Property'
	&& identifier.parent.shorthand
	&& identifier === identifier.parent.value;

module.exports = isShorthandPropertyValue;
