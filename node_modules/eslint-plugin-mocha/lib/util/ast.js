'use strict';

const { complement, both, isNil, propEq, pathEq, find } = require('rambda');
const { getTestCaseNames, getSuiteNames } = require('./names');
const { getAddtionalNames } = require('./settings');

const isDefined = complement(isNil);
const isCallExpression = both(isDefined, propEq('type', 'CallExpression'));

const hooks = [
    'before',
    'after',
    'beforeEach',
    'afterEach',
    'beforeAll',
    'afterAll',
    'setup',
    'teardown',
    'suiteSetup',
    'suiteTeardown'
];
const suiteConfig = [ 'timeout', 'slow', 'retries' ];

const findReturnStatement = find(propEq('type', 'ReturnStatement'));

function getPropertyName(property) {
    return property.name || property.value;
}

function getNodeName(node) {
    if (node.type === 'ThisExpression') {
        return 'this';
    }
    if (node.type === 'MemberExpression') {
        return `${getNodeName(node.object)}.${getPropertyName(node.property)}`;
    }
    return node.name;
}

function isHookIdentifier(node) {
    return node && node.type === 'Identifier' && hooks.includes(node.name);
}

function isHookCall(node) {
    return isCallExpression(node) && isHookIdentifier(node.callee);
}

function findReference(scope, node) {
    const hasSameRangeAsNode = pathEq([ 'identifier', 'range' ], node.range);

    return find(hasSameRangeAsNode, scope.references);
}

function isShadowed(scope, identifier) {
    const reference = findReference(scope, identifier);

    return (
        reference && reference.resolved && reference.resolved.defs.length > 0
    );
}

function isCallToShadowedReference(node, scope) {
    const identifier =
        node.callee.type === 'MemberExpression' ?
            node.callee.object :
            node.callee;

    return isShadowed(scope, identifier);
}

function isFunctionCallWithName(node, names) {
    return isCallExpression(node) && names.includes(getNodeName(node.callee));
}

// eslint-disable-next-line max-statements
function createAstUtils(settings) {
    const additionalCustomNames = getAddtionalNames(settings);

    function buildIsDescribeAnswerer(options = {}) {
        const { modifiers = [ 'skip', 'only' ], modifiersOnly = false } = options;
        const describeAliases = getSuiteNames({
            modifiersOnly,
            modifiers,
            additionalCustomNames
        });

        return (node) => isFunctionCallWithName(node, describeAliases);
    }

    function isDescribe(node, options = {}) {
        return buildIsDescribeAnswerer(options)(node);
    }

    function buildIsTestCaseAnswerer(options = {}) {
        const { modifiers = [ 'skip', 'only' ], modifiersOnly = false } = options;
        const testCaseNames = getTestCaseNames({
            modifiersOnly,
            modifiers,
            additionalCustomNames
        });

        return (node) => isFunctionCallWithName(node, testCaseNames);
    }

    function isTestCase(node, options = {}) {
        return buildIsTestCaseAnswerer(options)(node);
    }

    function isSuiteConfigExpression(node) {
        if (node.type !== 'MemberExpression') {
            return false;
        }

        const usingThis = node.object.type === 'ThisExpression';

        if (usingThis || isTestCase(node.object)) {
            return suiteConfig.includes(getPropertyName(node.property));
        }

        return false;
    }

    function isSuiteConfigCall(node) {
        return isCallExpression(node) && isSuiteConfigExpression(node.callee);
    }

    function buildIsMochaFunctionCallAnswerer(_isTestCase, _isDescribe) {
        function isMochaFunctionCall(node) {
            return _isTestCase(node) || _isDescribe(node) || isHookCall(node);
        }

        return (node, context) => {
            if (isMochaFunctionCall(node)) {
                const scope = context.getScope();

                if (!isCallToShadowedReference(node, scope)) {
                    return true;
                }
            }

            return false;
        };
    }

    function hasParentMochaFunctionCall(functionExpression, options) {
        return (
            isTestCase(functionExpression.parent, options) ||
            isHookCall(functionExpression.parent)
        );
    }

    function isExplicitUndefined(node) {
        return node && node.type === 'Identifier' && node.name === 'undefined';
    }

    function isReturnOfUndefined(node) {
        const argument = node.argument;
        const isImplicitUndefined = argument === null;

        return isImplicitUndefined || isExplicitUndefined(argument);
    }

    return {
        isDescribe,
        isHookIdentifier,
        isTestCase,
        getPropertyName,
        getNodeName,
        isHookCall,
        isSuiteConfigCall,
        hasParentMochaFunctionCall,
        findReturnStatement,
        isReturnOfUndefined,
        buildIsDescribeAnswerer,
        buildIsTestCaseAnswerer,
        buildIsMochaFunctionCallAnswerer
    };
}

module.exports = createAstUtils;
