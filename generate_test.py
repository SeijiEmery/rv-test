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
        # pre-search + replace all test input + test output cases
        # since parsing is done w/ regexes, this is the only, uh...
        # sane way to do this (can't parse recursive '{{ ... }}'
        # statements, but by parsing + removing the inner ones first,
        # a 2-depth nesting is possible)

        # Store parsed input + output statements as in-order lists of
        # match objects
        input_stmts  = []
        output_stmts = []

        def process_input (match):
            input_stmts.append(match)
            return ''

        def process_output (match):
            output_stmts.append(match)
            return ''

        lines = re.sub(test_inputs_regex, process_input, lines)
        lines = re.sub(test_outputs_regex, process_output, lines)

        print("got %s input statements: %s"%(
            len(input_stmts), ', '.join(map(str, input_stmts))))
        print("got %s output statements: %s"%(
            len(output_stmts), ', '.join(map(str, output_stmts))))

        while True:
            # Search for begin test statement (test_begin_regex)
            start_match = re.search(test_begin_regex, lines)
            if not start_match:
                print("No match found in '%s'"%lines.strip())
                return
            test_name = start_match.group(1)
            line_num += count_lines(lines[:start_match.end()])
            lines = lines[start_match.end():]

            # Search for end test statement (test_end_regex)
            end_match = re.search(test_end_regex, lines)
            if not end_match:
                raise Exception("Expected '}}' in %s:%s"%(
                    filepath, line_num))

            # Separate out test body
            body = lines[:end_match.start()]
            print("Got match on %s:%s:\n%s\n"%(
                filepath, line_num, body))

            # find input + output statements that are within this test body
            inputs = [
                m.group(1)
                for m in input_stmts
                if m.start() >= start_match.end() and m.end() <= end_match.start()
            ]
            outputs = [
                m.group(1)
                for m in output_stmts
                if m.start() >= start_match.end() and m.end() <= end_match.start()
            ]
            if len(inputs) == 0:
                raise Exception("Testcase '%s' is missing 'inputs' statement! %s:%s"%(
                    test_name, filepath, line_num))
            if len(outputs) == 0:
                raise Exception("Testcase '%s' is missing 'outputs' statement! %s:%s"%(
                    test_name, filepath, line_num))



            # Return parsed testcase info
            yield None
            line_num += count_lines(lines[:end_match.end()])
            lines = lines[end_match.end():]

    testcases = list(parse_testcases(lines))

if __name__ == '__main__':
    filepath = 'tests/add.test.s'
    process_test_file(filepath)
