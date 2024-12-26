#!/usr/bin/env python3
"""
snark_linter.py
A Python "linter" that provides sarcastic, unhelpful messages about your code.

Step 6: JSON Output Mode
- We add a '--json' flag. If present, we output the comedic issues as a JSON array.
- Otherwise, we continue the usual plain-text output.

Existing checks:
- Syntax errors (single comedic message if parse fails)
- AST-based:
  - Class name CapWords
  - Function name snake_case
  - Docstrings (presence, length, format)
  - Single-letter variables
  - Nested loops
- Comments (token-based)
- Line-length checks
- Import checks
"""

import ast
import sys
import os
import re
import json
import tokenize

CAPWORDS_REGEX = re.compile(r'^[A-Z][a-zA-Z0-9]+(?:[A-Z0-9][a-zA-Z0-9]*)*$')
SNAKE_CASE_REGEX = re.compile(r'^[a-z_][a-z0-9_]*$')


class SnarkLinter(ast.NodeVisitor):
    """
    A custom AST visitor that complains about normal code constructs,
    plus naming conventions for classes and functions,
    plus docstring checks.
    """

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.issues = []
        self.loop_depth = 0  # Track loop depth for nested loops

    def visit_ClassDef(self, node):
        # Class naming
        if not CAPWORDS_REGEX.match(node.name):
            message = (
                f"Class '{node.name}' at line {node.lineno} is not in CapWords style. "
                "Do you even PEP 8, bro?"
            )
            self.issues.append((node.lineno, message))

        # Docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            msg = (
                f"Class '{node.name}' at line {node.lineno} has no docstring. "
                "Why bother writing code if no one knows what it does?"
            )
            self.issues.append((node.lineno, msg))
        else:
            self._check_docstring_rules(docstring, node.lineno, f"Class '{node.name}'")

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Snark about functions existing at all
        basic_message = (
            f"Found a function named '{node.name}' at line {node.lineno}. "
            "Is this your attempt at structured programming? How quaint."
        )
        self.issues.append((node.lineno, basic_message))

        # Function name snake_case
        if not SNAKE_CASE_REGEX.match(node.name):
            name_msg = (
                f"Function '{node.name}' at line {node.lineno} is not snake_case. "
                "We only speak underscores around here."
            )
            self.issues.append((node.lineno, name_msg))

        # Docstring
        docstring = ast.get_docstring(node)
        if not docstring:
            msg = (
                f"Function '{node.name}' at line {node.lineno} has no docstring. "
                "Don't keep secrets from your future self!"
            )
            self.issues.append((node.lineno, msg))
        else:
            self._check_docstring_rules(docstring, node.lineno, f"Function '{node.name}'")

        self.generic_visit(node)

    def _check_docstring_rules(self, docstring, lineno, entity_name):
        # Check length
        if len(docstring) < 10:
            short_msg = (
                f"{entity_name} at line {lineno} has a docstring with only "
                f"{len(docstring)} characters. That's barely a grunt, not a docstring."
            )
            self.issues.append((lineno, short_msg))

        # Capital letter at start
        first_char = docstring[0]
        if not first_char.isupper():
            cap_msg = (
                f"{entity_name} at line {lineno} has a docstring that doesn't start with a capital letter. "
                "Where's your sense of grammar?"
            )
            self.issues.append((lineno, cap_msg))

        # End with punctuation
        last_char = docstring[-1]
        if last_char not in ('.', '!', '?'):
            end_msg = (
                f"{entity_name} at line {lineno} has a docstring that doesn't end with punctuation. "
                "Finish your sentence, please."
            )
            self.issues.append((lineno, end_msg))

    def visit_Assign(self, node):
        # Single-letter variable check
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if len(var_name) == 1 and var_name.isalpha():
                    message = (
                        f"Single-letter variable '{var_name}' at line {node.lineno}. "
                        "Oh sure, I'd never guess what it means, but I'm sure it's clear to YOU."
                    )
                    self.issues.append((node.lineno, message))
        self.generic_visit(node)

    def visit_For(self, node):
        # Nested loops
        self.loop_depth += 1
        if self.loop_depth > 1:
            message = (
                f"Nested loop at line {node.lineno}. "
                "You do realize we invented break and return statements, right?"
            )
            self.issues.append((node.lineno, message))

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        # Nested loops
        self.loop_depth += 1
        if self.loop_depth > 1:
            message = (
                f"Nested loop at line {node.lineno}. "
                "Yikes, a while loop inside another loop? Are you allergic to simplicity?"
            )
            self.issues.append((node.lineno, message))

        self.generic_visit(node)
        self.loop_depth -= 1


def find_comment_issues(file_path):
    """
    Token-based check for comments. We mock the presence of comments
    and also mock if they're too long (>72 chars).
    """
    issues = []
    if not os.path.exists(file_path):
        return issues

    with open(file_path, 'rb') as f:
        tokens = tokenize.tokenize(f.readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                line_num = token.start[0]
                comment_text = token.string.strip()
                if len(comment_text) > 72:
                    message = (
                        f"This comment at line {line_num} is {len(comment_text)} characters long. "
                        "Way to kill the readability. 72 was too short for you?"
                    )
                else:
                    message = (
                        f"Extraneous comment at line {line_num}. "
                        f"Real developers keep it all in their heads: {comment_text}"
                    )
                issues.append((line_num, message))

    return issues


def find_line_length_issues(file_path):
    """
    Checks each line:
    - If it's a comment-only line (#...), limit is 72
    - Otherwise, limit is 79
    """
    issues = []
    if not os.path.exists(file_path):
        return issues

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, start=1):
            raw_line = line.rstrip('\n')
            if not raw_line.strip():
                continue
            if raw_line.lstrip().startswith('#'):
                if len(raw_line) > 72:
                    msg = (
                        f"Line {line_no} has {len(raw_line)} characters in a comment. "
                        "72 is the limit, but apparently your brilliance needed more space?"
                    )
                    issues.append((line_no, msg))
            else:
                if len(raw_line) > 79:
                    msg = (
                        f"Line {line_no} has {len(raw_line)} characters. "
                        "Trying to write the next War and Peace in one line?"
                    )
                    issues.append((line_no, msg))

    return issues


def find_import_issues(file_path):
    """
    We complain if multiple modules are imported on the same line.
    e.g. 'import sys, os' or 'from foo import bar, baz'.
    """
    issues = []
    if not os.path.exists(file_path):
        return issues

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if stripped.startswith('import '):
                after_import = stripped[len('import '):]
                if ',' in after_import:
                    msg = (
                        f"Multiple imports on one line at {line_no}. "
                        "You think we can read two modules in one breath?"
                    )
                    issues.append((line_no, msg))
            elif stripped.startswith('from ') and ' import ' in stripped:
                parts = stripped.split(' import ', maxsplit=1)
                if len(parts) == 2:
                    to_import = parts[1]
                    if ',' in to_import:
                        msg = (
                            f"Multiple imports on one line at {line_no}. "
                            "One import statement per line, please. Our tiny eyes can't parse multiple."
                        )
                        issues.append((line_no, msg))

    return issues


def run_snark_linter(file_path):
    """
    Collect all comedic issues from the various checks.
    If there's a SyntaxError, produce one comedic complaint and skip everything else.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Syntax parse check
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        line_number = e.lineno if e.lineno else 1
        message = (
            f"Wow, syntax error at line {line_number}. "
            "Did you even try to run this code yourself? I can't parse this nonsense."
        )
        return [(line_number, message)]

    # AST-based checks
    linter = SnarkLinter(file_path)
    linter.visit(tree)
    ast_issues = linter.issues

    # Additional checks
    comment_issues = find_comment_issues(file_path)
    length_issues = find_line_length_issues(file_path)
    import_issues = find_import_issues(file_path)

    all_issues = ast_issues + comment_issues + length_issues + import_issues
    all_issues.sort(key=lambda x: x[0])
    return all_issues


def main():
    """
    Main entry point for the command line.
    If '--json' is specified, we output JSON.
    Otherwise, we do the usual text-based output.
    """
    import argparse
    parser = argparse.ArgumentParser(description="A comedic Python linter.")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("filepath", nargs="?", help="Path to the Python file to lint")
    args = parser.parse_args()

    if not args.filepath:
        print("Usage: python snark_linter.py [--json] path/to/your_file.py")
        sys.exit(1)

    file_path = args.filepath
    try:
        issues = run_snark_linter(file_path)
        if not issues:
            if args.json:
                print(json.dumps([]))
            else:
                print("No comedic issues found. Your code is evidently too normal.")
        else:
            if args.json:
                # We’ll output a JSON array, each item containing line and message
                output = []
                for line_num, message in issues:
                    output.append({
                        "line": line_num,
                        "message": message
                    })
                print(json.dumps(output, indent=2))
            else:
                # Plain-text output, as before
                for line_num, message in issues:
                    print(f"{file_path}:{line_num}: {message}")

    except Exception as e:
        print(f"Error analyzing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()