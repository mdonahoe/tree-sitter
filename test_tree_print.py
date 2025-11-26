#!/usr/bin/env python3
"""
Test suite for tree_print tool.
Tests various query patterns against example.c and validates output.
"""

import subprocess
import sys
from typing import List, Tuple

def run_tree_print(filename: str, query: str) -> Tuple[str, str, int]:
    """Run tree_print and return (stdout, stderr, returncode)"""
    result = subprocess.run(
        ['./tree_print', filename, query],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode

def test_case(name: str, filename: str, query: str, expected: List[str], should_contain_all: bool = True) -> bool:
    """
    Run a test case and validate output.

    Args:
        name: Test name
        filename: Source file to parse
        query: Tree-sitter query pattern
        expected: List of expected strings in output
        should_contain_all: If True, all expected strings must be present.
                           If False, at least one must be present.

    Returns:
        True if test passes, False otherwise
    """
    print(f"Testing: {name}...", end=" ")

    stdout, stderr, returncode = run_tree_print(filename, query)

    if returncode != 0:
        print(f"FAIL (exit code {returncode})")
        print(f"  Output: {stdout}")
        print(f"  Error: {stderr}")
        return False

    # Check if expected strings are in output
    matches = [exp in stdout for exp in expected]

    if should_contain_all:
        if all(matches):
            print("PASS")
            return True
        else:
            print("FAIL")
            print(f"  Expected all of: {expected}")
            print(f"  Got: {stdout[:200]}...")
            missing = [exp for exp, match in zip(expected, matches) if not match]
            print(f"  Missing: {missing}")
            return False
    else:
        if any(matches):
            print("PASS")
            return True
        else:
            print("FAIL")
            print(f"  Expected at least one of: {expected}")
            print(f"  Got: {stdout[:200]}...")
            return False

def test_error_case(name: str, filename: str, query: str) -> bool:
    """Test that a query fails as expected"""
    print(f"Testing: {name}...", end=" ")

    stdout, stderr, returncode = run_tree_print(filename, query)

    if returncode != 0:
        print("PASS (failed as expected)")
        return True
    else:
        print("FAIL (should have failed)")
        print(f"  Got output: {stdout[:200]}")
        print(f"  Got error: {stderr[:200]}")
        return False

def main():
    """Run all tests"""
    subprocess.run(["make", "tree_print"])
    print("=" * 60)
    print("tree_print Test Suite")
    print("=" * 60)
    print()

    tests_passed = 0
    tests_failed = 0

    # Test 1: Find all string literals
    if test_case(
        "String literals",
        "example.c",
        "(string_literal) @str",
        [
            '"Tree-sitter minimal API example\\n"',
            '"Failed to create parser\\n"',
            '"✓ Parser created successfully\\n"'
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 2: Find function definitions
    if test_case(
        "Function definitions",
        "example.c",
        "(function_definition) @func",
        [
            "int main()",
            "return 0;"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 3: Find function call names
    if test_case(
        "Function call names",
        "example.c",
        "(call_expression function: (identifier) @name)",
        [
            "printf",
            "ts_parser_new",
            "fprintf",
            "ts_parser_delete"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 4: Find comments
    if test_case(
        "Comments",
        "example.c",
        "(comment) @c",
        [
            "// Create a parser",
            "// Clean up"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 5: Find if statements
    if test_case(
        "If statements",
        "example.c",
        "(if_statement) @if",
        [
            "if (!parser)",
            "return 1;"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 6: Find declarations
    if test_case(
        "Declarations",
        "example.c",
        "(declaration) @decl",
        [
            "TSParser *parser"
        ],
        should_contain_all=False  # Just need to find at least one
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 7: Find pointer declarators
    if test_case(
        "Pointer types",
        "example.c",
        "(pointer_declarator) @ptr",
        [
            "*parser"
        ],
        should_contain_all=False
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 8: Find identifiers with specific name
    if test_case(
        "Specific identifier (parser)",
        "example.c",
        '(identifier) @id (#eq? @id "parser")',
        [
            "parser"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 9: Find return statements
    if test_case(
        "Return statements",
        "example.c",
        "(return_statement) @ret",
        [
            "return 1;",
            "return 0;"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 10: Find type identifiers
    if test_case(
        "Type identifiers",
        "example.c",
        "(type_identifier) @type",
        [
            "TSParser"
        ],
        should_contain_all=False
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 11: Find printf calls specifically
    if test_case(
        "Printf calls with arguments",
        "example.c",
        '(call_expression function: (identifier) @fn (#eq? @fn "printf"))',
        [
            "printf"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 12: Field access in call expression
    if test_case(
        "Call expressions with arguments",
        "example.c",
        "(call_expression arguments: (argument_list) @args)",
        [
            "(stderr",
            '("Tree-sitter minimal API example\\n")'
        ],
        should_contain_all=False
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 13: Find all macros/preprocessor directives
    if test_case(
        "Preprocessor includes",
        "example.c",
        "(preproc_include) @inc",
        [
            "#include <stdio.h>",
            "#include <tree_sitter/api.h>"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 14: Find number literals
    if test_case(
        "Number literals",
        "example.c",
        "(number_literal) @num",
        [
            "1",
            "0"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test 15: Complex nested query
    if test_case(
        "Nested query - if with return",
        "example.c",
        "(if_statement consequence: (compound_statement (return_statement) @ret))",
        [
            "return 1;"
        ]
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Edge cases
    print()
    print("Testing edge cases:")
    print("-" * 60)

    # Test E1: Query without capture (valid but produces no output)
    print(f"Testing: Query without capture (no output)...", end=" ")
    stdout, stderr, returncode = run_tree_print("example.c", "(string_literal)")
    if returncode == 0 and "No matches found" in stderr:
        print("PASS")
        tests_passed += 1
    else:
        print("FAIL")
        print(f"  stdout: {stdout}")
        print(f"  stderr: {stderr}")
        tests_failed += 1

    # Error cases
    print()
    print("Testing error cases:")
    print("-" * 60)

    # Test E2: Invalid query syntax
    if test_error_case(
        "Invalid query syntax",
        "example.c",
        "(invalid_node_type) @x"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Test E3: Non-existent file
    if test_error_case(
        "Non-existent file",
        "nonexistent.c",
        "(string_literal) @str"
    ):
        tests_passed += 1
    else:
        tests_failed += 1

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Total:  {tests_passed + tests_failed}")
    print()

    if tests_failed == 0:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {tests_failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
