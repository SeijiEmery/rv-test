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
        # Try matching all statements:
        begin_stmts = list(re.finditer(test_begin_regex, lines))
        input_stmts = list(re.finditer(test_inputs_regex, lines))
        output_stmts = list(re.finditer(test_outputs_regex, lines))

        def find_non_overlapping_end_stmts ():
            def overlaps (m1, m2):
                return m1.end() <= m2.end()

            input_index, output_index = 0, 0
            for match in re.finditer(test_end_regex, lines):
                while input_index < len(input_stmts) and input_stmts[input_index].end() < match.start():
                    input_index += 1
                while output_index < len(output_stmts) and output_stmts[output_index].end() < match.start():
                    output_index += 1
                # print("Comparing %s %s to %s"%(input_index, input_stmts[input_index] if input_index < len(input_stmts) else None, match))
                # print("Comparing %s %s to %s"%(output_index, output_stmts[output_index] if output_index < len(output_stmts) else None, match))

                if input_index < len(input_stmts) and overlaps(input_stmts[input_index], match):
                    # print("Discarding %s"%match)
                    continue
                if output_index < len(output_stmts) and overlaps(output_stmts[output_index], match):
                    # print("Discarding %s"%match)
                    continue
                # print("Emitting %s"%match)
                yield match
        end_stmts = list(find_non_overlapping_end_stmts())

        if len(begin_stmts) != len(end_stmts):
            raise Exception("Mismatched {{ ... }}! in %s"%filepath)

        for match_start in begin_stmts:
            # Validate end statement
            if len(end_stmts) == 0 or end_stmts[0].start() > match_start.end():
                raise Exception("Missing '}}' in testcase at %s:%s!"%(
                    filepath, count_lines(lines[:match_start.end()])))
            match_end = end_stmts.pop(0)

            # Validate input statement(s)
            if len(input_stmts) > 0 and (
                input_stmts[0].start() < match_start.end() or 
                input_stmts[0].end() > match_end.start()):
                raise Exception("Unused input statement (not in a testcase) at %s:%s!"%(
                    filepath, count_lines(lines[:input_stmts[0].start()])))
            if len(input_stmts) == 0:
                raise Exception("No input statements in testcase at %s:%s!"%(
                    filepath, count_lines(lines[:match_start.end()])))

            # Validate output statement(s)
            if len(output_stmts) > 0 and (
                output_stmts[0].start() < match_start.end() or 
                output_stmts[0].end() > match_end.start()):
                raise Exception("Unused output statement (not in a testcase) at %s:%s!"%(
                    filepath, count_lines(lines[:output_stmts[0].start()])))
            if len(output_stmts) == 0:
                raise Exception("No output statements in testcase at %s:%s!"%(
                    filepath, count_lines(lines[:match_start.end()])))

            # Read input + output statements
            inputs = []
            while len(input_stmts) > 0 and input_stmts[0].end() <= match_end.start():
                inputs += input_stmts.pop(0).group(1) + '\n'
            outputs = ''
            while len(output_stmts) > 0 and output_stmts[0].end() <= match_end.start():
                inputs += output_stmts.pop(0).group(1) + '\n'

            print(inputs)
            print(outputs)




        # def overlaps (m1, mlist):
        #     for m2 in mlist:
        #         if not (
        #             (m1.start() >= m2.start() and m1.end() >= m2.end()) or
        #             (m1.start() <= m2.start() and m1.end() <= m2.end())
        #         ):
        #             return False
        #     return True
        # end_stmts = [
        #     m for m in re.finditer(test_end_regex, lines)
        #     if not overlaps(m, input_stmts) and not overlaps(m, output_stmts)
        # ]
        print(begin_stmts)
        print(input_stmts)
        print(output_stmts)
        print(end_stmts)
        return

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
