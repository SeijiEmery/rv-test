#!/usr/bin/env python3
from pathlib import Path
import os
import re

test_begin_regex = re.compile(r'test\s*(?:"([^"]*)")?\s*{{\s*\n')
test_end_regex = re.compile(r'}}')
test_inputs_regex = re.compile(r'inputs\s*{{([^}]+)}}')
test_outputs_regex = re.compile(r'outputs\s*{{([^}]+)}}')


def count_lines (s):
    return len(list(re.finditer(r'\n', s)))

def process_test_file (filepath):
    path = Path(filepath)
    if not path.is_file():
        raise Exception("Cannot load '%s' (file does not exist)"%filepath)
    with open(path, 'r') as f:
        lines = f.read()

    def parse_testcases (lines, line_num = 0):
        while True:
            # Search for begin test statement (test_begin_regex)
            match = re.search(test_begin_regex, lines)
            if not match:
                print("No match found in '%s'"%lines)
                return
            test_name = match.group(1)
            line_num += count_lines(lines[:match.end()])
            lines = lines[match.end():]

            # Search for end test statement (test_end_regex)
            end_match = re.search(test_end_regex, lines)
            if not match:
                raise Exception("Expected '}}' in %s:%s"%(
                    filepath, line_num))

            # Separate out test body
            body = lines[:end_match.start()]
            print("Got match on %s:%s:\n%s\n"%(
                filepath, line_num, body))

            # Return parsed testcase info
            yield None
            line_num += count_lines(lines[:end_match.end()])
            lines = lines[end_match.end():]

    testcases = list(parse_testcases(lines))

if __name__ == '__main__':
    filepath = 'tests/add.test.s'
    process_test_file(filepath)
