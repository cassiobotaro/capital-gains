import io
from unittest import TestCase

from capital_gains.cli import dump_json, parse_json_line, readlines
from capital_gains.tax import process_operations_batch


class CliTest(TestCase):
    def test_common_scenario(self):
        # given a_json_formatted_input
        input = io.StringIO(
            (
                '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
                '{"operation":"sell", "unit-cost":20.00, "quantity": 5000}]\n'
                '[{"operation":"buy", "unit-cost":20.00, "quantity": 10000}, '
                '{"operation":"sell", "unit-cost":10.00, "quantity": 5000}]\n'
                "\n"
            )
        )

        # then read lines of the input
        lines = readlines(input)

        # and parse as Operation
        parsed_lines = map(parse_json_line, lines)

        obtained_output = io.StringIO()
        for line in parsed_lines:
            taxes = process_operations_batch(line)
            dump_json(taxes, obtained_output)

        # then output should be correct and formatted as json
        expected_output = ""
        self.assertEqual(obtained_output.read(), expected_output)
