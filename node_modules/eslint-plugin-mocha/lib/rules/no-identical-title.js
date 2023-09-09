'use strict';

const createAstUtils = require('../util/ast');

function newLayer() {
    return {
        describeTitles: [],
        testTitles: []
    };
}

function isFirstArgLiteral(node) {
    return (
        node.arguments &&
        node.arguments[0] &&
        node.arguments[0].type === 'Literal'
    );
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Disallow identical titles',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-identical-title.md'
        },
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const isTestCase = astUtils.buildIsTestCaseAnswerer();
        const isDescribe = astUtils.buildIsDescribeAnswerer();

        const titleLayers = [ newLayer() ];

        function handlTestCaseTitles(titles, node, title) {
            if (isTestCase(node)) {
                if (titles.includes(title)) {
                    context.report({
                        node,
                        message:
                            'Test title is used multiple times in the same test suite.'
                    });
                }
                titles.push(title);
            }
        }

        function handlTestSuiteTitles(titles, node, title) {
            if (!isDescribe(node)) {
                return;
            }
            if (titles.includes(title)) {
                context.report({
                    node,
                    message: 'Test suite title is used multiple times.'
                });
            }
            titles.push(title);
        }

        return {
            CallExpression(node) {
                const currentLayer = titleLayers[titleLayers.length - 1];

                if (isDescribe(node)) {
                    titleLayers.push(newLayer());
                }
                if (!isFirstArgLiteral(node)) {
                    return;
                }

                const title = node.arguments[0].value;
                handlTestCaseTitles(currentLayer.testTitles, node, title);
                handlTestSuiteTitles(currentLayer.describeTitles, node, title);
            },
            'CallExpression:exit'(node) {
                if (isDescribe(node)) {
                    titleLayers.pop();
                }
            }
        };
    }
};
