'use strict';
const typedArray = require('../shared/typed-array.js');

const enforceNew = [
	'Object',
	'Array',
	'ArrayBuffer',
	'DataView',
	'Date',
	'Error',
	'Function',
	'Map',
	'WeakMap',
	'Set',
	'WeakSet',
	'Promise',
	'RegExp',
	'SharedArrayBuffer',
	'Proxy',
	'WeakRef',
	'FinalizationRegistry',
	...typedArray,
];

const disallowNew = [
	'BigInt',
	'Boolean',
	'Number',
	'String',
	'Symbol',
];

module.exports = {
	enforceNew,
	disallowNew,
};
