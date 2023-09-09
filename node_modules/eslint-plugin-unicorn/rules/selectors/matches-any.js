'use strict';

function matches(selectors) {
	switch (selectors.length) {
		case 0: {
			return '';
		}

		case 1: {
			// Make selectors more readable
			return selectors[0];
		}

		default: {
			return `:matches(${selectors.join(', ')})`;
		}
	}
}

module.exports = matches;
