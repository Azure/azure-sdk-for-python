'use strict';

const {
    where,
    includes,
    intersection,
    pipe,
    isEmpty,
    complement,
    flip,
    filter,
    over,
    lensProp,
    map,
    view,
    assoc,
    allPass
} = require('rambda');
const { memoizeWith } = require('./memoizeWith');

const INTERFACES = {
    BDD: 'BDD',
    TDD: 'TDD',
    QUnit: 'QUnit'
};

const TYPES = {
    suite: 'suite',
    testCase: 'testCase',
    hook: 'hook'
};

const MODIFIERS = {
    skip: 'skip',
    only: 'only'
};

const baseNames = [
    { name: 'describe', interfaces: [ INTERFACES.BDD ], type: TYPES.suite },
    { name: 'context', interfaces: [ INTERFACES.BDD ], type: TYPES.suite },
    { name: 'suite', interfaces: [ INTERFACES.TDD, INTERFACES.QUnit ], type: TYPES.suite },
    { name: 'it', interfaces: [ INTERFACES.BDD ], type: TYPES.testCase },
    { name: 'specify', interfaces: [ INTERFACES.BDD ], type: TYPES.testCase },
    { name: 'test', interfaces: [ INTERFACES.TDD, INTERFACES.QUnit ], type: TYPES.testCase },
    { name: 'before', interfaces: [ INTERFACES.BDD, INTERFACES.QUnit ], type: TYPES.hook },
    { name: 'after', interfaces: [ INTERFACES.BDD, INTERFACES.QUnit ], type: TYPES.hook },
    { name: 'beforeEach', interfaces: [ INTERFACES.BDD, INTERFACES.QUnit ], type: TYPES.hook },
    { name: 'afterEach', interfaces: [ INTERFACES.BDD, INTERFACES.QUnit ], type: TYPES.hook },
    { name: 'suiteSetup', interfaces: [ INTERFACES.TDD ], type: TYPES.hook },
    { name: 'suiteTeardown', interfaces: [ INTERFACES.TDD ], type: TYPES.hook },
    { name: 'setup', interfaces: [ INTERFACES.TDD ], type: TYPES.hook },
    { name: 'teardown', interfaces: [ INTERFACES.TDD ], type: TYPES.hook }
];

const includesSublist = (sublist) => pipe(intersection(sublist), complement(isEmpty));
const isIncludedIn = flip(includes);
const hasMatchingType = (typesToMatch) => where({ type: isIncludedIn(typesToMatch) });
const hasMatchingInterfaces = (interfacesToMatch) => where({ interfaces: includesSublist(interfacesToMatch) });
const hasMatchingModifier = (modifierToMatch) => where({ modifier: isIncludedIn(modifierToMatch) });
const filterTestCasesAndSuites = filter(hasMatchingType([ TYPES.suite, TYPES.testCase ]));

const nameLens = lensProp('name');
const mapNames = (fn) => map(over(nameLens, fn));
const extractNames = map(view(nameLens));
const addModifier = (modifier) => map(assoc('modifier', modifier));

function formatXVariant(name) {
    return `x${name}`;
}

function formatSkipVariant(name) {
    return `${name}.${MODIFIERS.skip}`;
}

function formatExclusiveVariant(name) {
    return `${name}.${MODIFIERS.only}`;
}

const buildXVariants = pipe(
    filterTestCasesAndSuites,
    filter(hasMatchingInterfaces([ INTERFACES.BDD ])),
    mapNames(formatXVariant),
    addModifier(MODIFIERS.skip)
);

const buildSkipVariants = pipe(
    filterTestCasesAndSuites,
    mapNames(formatSkipVariant),
    addModifier(MODIFIERS.skip)
);

const buildExclusiveVariants = pipe(
    filterTestCasesAndSuites,
    mapNames(formatExclusiveVariant),
    addModifier(MODIFIERS.only)
);

function buildAllNames(additionalNames) {
    const names = addModifier(null)([ ...baseNames, ...additionalNames ]);

    return [
        ...names,
        ...buildSkipVariants(names),
        ...buildXVariants(names),
        ...buildExclusiveVariants(names)
    ];
}

function getNamesByType(type, filterOptions = {}) {
    const { modifiers = [], modifiersOnly = false, additionalCustomNames = [] } = filterOptions;
    const allNames = buildAllNames(additionalCustomNames);
    const predicates = [
        hasMatchingType([ type ]),
        hasMatchingModifier([ ...modifiers, ...modifiersOnly ? [] : [ null ] ])
    ];
    const filteredNames = filter(allPass(predicates), allNames);

    return extractNames(filteredNames);
}

const getNamesByTypeMemoized = memoizeWith((type, options) => JSON.stringify({ type, options }), getNamesByType);

function getTestCaseNames(options) {
    return getNamesByTypeMemoized(TYPES.testCase, options);
}

function getSuiteNames(options) {
    return getNamesByTypeMemoized(TYPES.suite, options);
}

module.exports = {
    getTestCaseNames,
    getSuiteNames
};

