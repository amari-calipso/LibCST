# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import Any, Callable

import libcst as cst
from libcst import CodeRange, parse_expression, parse_statement
from libcst._nodes.tests.base import CSTNodeTest
from libcst.testing.utils import data_provider


class TupleTest(CSTNodeTest):
    @data_provider(
        [
            # zero-element tuple
            {"node": cst.Tuple([]), "code": "()", "parser": parse_expression},
            # one-element tuple, sentinel comma value
            {
                "node": cst.Tuple([cst.Element(cst.Name("single_element"))]),
                "code": "(single_element,)",
                "parser": None,
            },
            {
                "node": cst.Tuple([cst.StarredElement(cst.Name("single_element"))]),
                "code": "(*single_element,)",
                "parser": None,
            },
            # two-element tuple, sentinel comma value
            {
                "node": cst.Tuple(
                    [cst.Element(cst.Name("one")), cst.Element(cst.Name("two"))]
                ),
                "code": "(one, two)",
                "parser": None,
            },
            # remove parenthesis
            {
                "node": cst.Tuple(
                    [cst.Element(cst.Name("one")), cst.Element(cst.Name("two"))],
                    lpar=[],
                    rpar=[],
                ),
                "code": "one, two",
                "parser": None,
            },
            # add extra parenthesis
            {
                "node": cst.Tuple(
                    [cst.Element(cst.Name("one")), cst.Element(cst.Name("two"))],
                    lpar=[cst.LeftParen(), cst.LeftParen()],
                    rpar=[cst.RightParen(), cst.RightParen()],
                ),
                "code": "((one, two))",
                "parser": None,
            },
            # starred element
            {
                "node": cst.Tuple(
                    [
                        cst.StarredElement(cst.Name("one")),
                        cst.StarredElement(cst.Name("two")),
                    ]
                ),
                "code": "(*one, *two)",
                "parser": None,
            },
            # custom comma on Element
            {
                "node": cst.Tuple(
                    [
                        cst.Element(cst.Name("one"), comma=cst.Comma()),
                        cst.Element(cst.Name("two"), comma=cst.Comma()),
                    ]
                ),
                "code": "(one,two,)",
                "parser": parse_expression,
            },
            # custom comma on StarredElement
            {
                "node": cst.Tuple(
                    [
                        cst.StarredElement(cst.Name("one"), comma=cst.Comma()),
                        cst.StarredElement(cst.Name("two"), comma=cst.Comma()),
                    ]
                ),
                "code": "(*one,*two,)",
                "parser": parse_expression,
                "expected_position": CodeRange.create((1, 1), (1, 11)),
            },
            # custom parenthesis on StarredElement
            {
                "node": cst.Tuple(
                    [
                        cst.StarredElement(
                            cst.Name("abc"),
                            lpar=[cst.LeftParen()],
                            rpar=[cst.RightParen()],
                            comma=cst.Comma(),
                        )
                    ]
                ),
                "code": "((*abc),)",
                "parser": parse_expression,
                "expected_position": CodeRange.create((1, 1), (1, 8)),
            },
            # custom whitespace on StarredElement
            {
                "node": cst.Tuple(
                    [
                        cst.Element(cst.Name("one"), comma=cst.Comma()),
                        cst.StarredElement(
                            cst.Name("two"),
                            whitespace_before_value=cst.SimpleWhitespace("  "),
                            lpar=[cst.LeftParen()],
                            rpar=[cst.RightParen()],
                        ),
                    ],
                    lpar=[],
                    rpar=[],  # rpar can't own the trailing whitespace if it's not there
                ),
                "code": "one,(*  two)",
                "parser": parse_expression,
                "expected_position": CodeRange.create((1, 0), (1, 12)),
            },
            # missing spaces around tuple, okay with parenthesis
            {
                "node": cst.For(
                    target=cst.Tuple(
                        [
                            cst.Element(cst.Name("k"), comma=cst.Comma()),
                            cst.Element(cst.Name("v")),
                        ]
                    ),
                    iter=cst.Name("abc"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_after_for=cst.SimpleWhitespace(""),
                    whitespace_before_in=cst.SimpleWhitespace(""),
                ),
                "code": "for(k,v)in abc: pass\n",
                "parser": parse_statement,
            },
            # no spaces around tuple, but using values that are parenthesized
            {
                "node": cst.For(
                    target=cst.Tuple(
                        [
                            cst.Element(
                                cst.Name(
                                    "k", lpar=[cst.LeftParen()], rpar=[cst.RightParen()]
                                ),
                                comma=cst.Comma(),
                            ),
                            cst.Element(
                                cst.Name(
                                    "v", lpar=[cst.LeftParen()], rpar=[cst.RightParen()]
                                )
                            ),
                        ],
                        lpar=[],
                        rpar=[],
                    ),
                    iter=cst.Name("abc"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_after_for=cst.SimpleWhitespace(""),
                    whitespace_before_in=cst.SimpleWhitespace(""),
                ),
                "code": "for(k),(v)in abc: pass\n",
                "parser": parse_statement,
            },
            # starred elements are safe to use without a space before them
            {
                "node": cst.For(
                    target=cst.Tuple(
                        [cst.StarredElement(cst.Name("foo"), comma=cst.Comma())],
                        lpar=[],
                        rpar=[],
                    ),
                    iter=cst.Name("bar"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_after_for=cst.SimpleWhitespace(""),
                ),
                "code": "for*foo, in bar: pass\n",
                "parser": parse_statement,
            },
            # a trailing comma doesn't mess up TrailingWhitespace
            {
                "node": cst.SimpleStatementLine(
                    [
                        cst.Expr(
                            cst.Tuple(
                                [
                                    cst.Element(cst.Name("one"), comma=cst.Comma()),
                                    cst.Element(cst.Name("two"), comma=cst.Comma()),
                                ],
                                lpar=[],
                                rpar=[],
                            )
                        )
                    ],
                    trailing_whitespace=cst.TrailingWhitespace(
                        whitespace=cst.SimpleWhitespace("  "),
                        comment=cst.Comment("# comment"),
                    ),
                ),
                "code": "one,two,  # comment\n",
                "parser": parse_statement,
            },
        ]
    )
    def test_valid(self, **kwargs: Any) -> None:
        self.validate_node(**kwargs)

    @data_provider(
        (
            (
                lambda: cst.Tuple([], lpar=[], rpar=[]),
                "A zero-length tuple must be wrapped in parentheses.",
            ),
            (
                lambda: cst.Tuple(
                    [cst.Element(cst.Name("mismatched"))],
                    lpar=[cst.LeftParen(), cst.LeftParen()],
                    rpar=[cst.RightParen()],
                ),
                "unbalanced parens",
            ),
            (
                lambda: cst.For(
                    target=cst.Tuple([cst.Element(cst.Name("el"))], lpar=[], rpar=[]),
                    iter=cst.Name("it"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_after_for=cst.SimpleWhitespace(""),
                ),
                "Must have at least one space after 'for' keyword.",
            ),
            (
                lambda: cst.For(
                    target=cst.Tuple([cst.Element(cst.Name("el"))], lpar=[], rpar=[]),
                    iter=cst.Name("it"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_before_in=cst.SimpleWhitespace(""),
                ),
                "Must have at least one space before 'in' keyword.",
            ),
            # an additional check for StarredElement, since it's a separate codepath
            (
                lambda: cst.For(
                    target=cst.Tuple(
                        [cst.StarredElement(cst.Name("el"))], lpar=[], rpar=[]
                    ),
                    iter=cst.Name("it"),
                    body=cst.SimpleStatementSuite([cst.Pass()]),
                    whitespace_before_in=cst.SimpleWhitespace(""),
                ),
                "Must have at least one space before 'in' keyword.",
            ),
        )
    )
    def test_invalid(
        self, get_node: Callable[[], cst.CSTNode], expected_re: str
    ) -> None:
        self.assert_invalid(get_node, expected_re)
