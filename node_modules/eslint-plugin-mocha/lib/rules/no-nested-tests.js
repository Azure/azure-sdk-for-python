'use strict';

/* eslint "complexity": [ "error", 5 ] */

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        type: 'problem',
        docs: {
            description: 'Disallow tests to be nested within other tests ',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-nested-tests.md'
        },
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        let testNestingLevel = 0;
        let hookCallNestingLevel = 0;
        const isTestCase = astUtils.buildIsTestCaseAnswerer();
        const isDescribe = astUtils.buildIsDescribeAnswerer();

        function report(callExpression, message) {
            context.report({
                message,
                node: callExpression.callee
            });
        }

        function isNestedTest(_isTestCase, _isDescribe, nestingLevel) {
            const isNested = nestingLevel > 0;
            const isTest = _isTestCase || _isDescribe;

            return isNested && isTest;
        }

        function checkForAndReportErrors(
            node,
            _isTestCase,
            _isDescribe,
            isHookCall
        ) {
            if (isNestedTest(_isTestCase, _isDescribe, testNestingLevel)) {
                const message = _isDescribe ?
                    'Unexpected suite nested within a test.' :
                    'Unexpected test nested within another test.';
                report(node, message);
            } else if (
                isNestedTest(_isTestCase, isHookCall, hookCallNestingLevel)
            ) {
                const message = isHookCall ?
                    'Unexpected test hook nested within a test hook.' :
                    'Unexpected test nested within a test hook.';
                report(node, message);
            }
        }

        return {
            CallExpression(node) {
                const _isTestCase = isTestCase(node);
                const isHookCall = astUtils.isHookCall(node);
                const _isDescribe = isDescribe(node);

                checkForAndReportErrors(
                    node,
                    _isTestCase,
                    _isDescribe,
                    isHookCall
                );

                if (_isTestCase) {
                    testNestingLevel += 1;
                } else if (isHookCall) {
                    hookCallNestingLevel += 1;
                }
            },

            'CallExpression:exit'(node) {
                if (isTestCase(node)) {
                    testNestingLevel -= 1;
                } else if (astUtils.isHookCall(node)) {
                    hookCallNestingLevel -= 1;
                }
            }
        };
    }
};
