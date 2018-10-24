#!/usr/bin/env python3
from pathlib import Path
import os
import re

test_begin_regex = re.compile(r'test\s*(?:"([^"]*)")?\s*{{\s*\n')
test_stmt_regex = re.compile(r'\s*(?:(inputs|outputs)\s*{{([^}]+)}}|(}}))\s*')
register_assignment_expr_regex = re.compile(r'([a-z][a-z0-9]*)\s+(\-?[0-9]+)')

def parse_register_assignment (statements, register_dict):
    def parse_and_execute_assignment (match):
        name, value = match.group(1, 2)
        value = int(value)
        if name in register_dict:
            raise Exception("Already defined '%s' = %d; attempting to override with %d!"%(
                name, register_dict[name], value))
        register_dict[name] = value
        return ''
    rest = re.sub(
        register_assignment_expr_regex, 
        parse_and_execute_assignment, 
        statements
    ).strip()
    if rest:
        raise Exception("Failed to parse all of '%s': '%s'"%(statements, rest))


def count_lines (s):
    return len(list(re.finditer(r'\n', s)))

def process_test_file (filepath):
    path = Path(filepath)
    if not path.is_file():
        raise Exception("Cannot load '%s' (file does not exist)"%filepath)
    with open(path, 'r') as f:
        lines = f.read()

    def parse_testcases (lines, line_num = 0):
        # Try matching all statements:
        matches = list(re.finditer(test_begin_regex, lines))
        testcases = [
            (matches[i].group(1), 
                lines [
                    matches[i].end() : 
                    (matches[i+1].start() if i + 1 < len(matches) else -1)
                ],
                matches[i].end())
            for i in range(len(matches))
        ]
        for i, (name, body, start_index) in enumerate(testcases):
            inputs = {}
            outputs = {}
            def parse_stmt (match):
                # print(match)
                if match.group(1) == 'inputs':
                    parse_register_assignment(match.group(2), inputs)
                elif match.group(1) == 'outputs':
                    parse_register_assignment(match.group(2), outputs)
                return ''
            body = re.sub(test_stmt_regex, parse_stmt, body)

            # strip indentation
            body = '\n'.join([
                line.strip()
                for line in body.split('\n')
            ]) + '\n'

            yield i, name, body, inputs, outputs

    testcases = list(parse_testcases(lines))
    for testcase in testcases:
        print(testcase)

if __name__ == '__main__':
    filepath = 'tests/add.test.s'
    process_test_file(filepath)
