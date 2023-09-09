'use strict';

const createAstUtils = require('../util/ast');

module.exports = {
    meta: {
        docs: {
            description: 'Disallow exports from test files',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-exports.md'
        },
        messages: {
            unexpectedExport: 'Unexpected export from a test file'
        },
        type: 'suggestion',
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const exportNodes = [];
        let hasTestCase = false;
        const isTestCase = astUtils.buildIsTestCaseAnswerer();
        const isDescribe = astUtils.buildIsDescribeAnswerer();
        const isMochaFunctionCall = astUtils.buildIsMochaFunctionCallAnswerer(
            isTestCase,
            isDescribe
        );

        function isCommonJsExport(node) {
            if (node.type === 'MemberExpression') {
                const name = astUtils.getNodeName(node);

                return name === 'module.exports' || name.startsWith('exports.');
            }

            return false;
        }

        return {
            'Program:exit'() {
                if (hasTestCase && exportNodes.length > 0) {
                    for (const node of exportNodes) {
                        context.report({ node, messageId: 'unexpectedExport' });
                    }
                }
            },

            CallExpression(node) {
                if (!hasTestCase && isMochaFunctionCall(node, context)) {
                    hasTestCase = true;
                }
            },

            'ExportNamedDeclaration, ExportDefaultDeclaration, ExportAllDeclaration'(
                node
            ) {
                exportNodes.push(node);
            },

            AssignmentExpression(node) {
                if (isCommonJsExport(node.left)) {
                    exportNodes.push(node);
                }
            }
        };
    }
};
