import io
import json

import pytest

from capital_gains.cli import dump_json, lines_until_blank, parse_json_line, run
from capital_gains.money import Money
from capital_gains.tax import INITIAL_INVESTMENT, Operation, OperationResult
from tests.helpers import brl


@pytest.mark.parametrize(
    ("input_data", "expected_output"),
    [
        (
            # Lines after the first blank line are not read
            ["op1\n", "op2\n", "\n", "op3\n"],
            ["op1\n", "op2\n"],
        ),
        (
            # A whitespace-only line also ends the input
            ["op1\n", " \t\n", "op2\n"],
            ["op1\n"],
        ),
        (
            # Input without a blank line is read until EOF
            ["line A\n", "line B"],
            ["line A\n", "line B"],
        ),
        (
            # Input starting with a blank line is empty
            ["\n", "op1\n"],
            [],
        ),
    ],
)
def test_lines_until_blank_stops_at_first_blank_line(
    input_data: list[str], expected_output: list[str]
) -> None:
    assert list(lines_until_blank(input_data)) == expected_output


def test_parse_json_line_converts_to_domain_objects() -> None:
    input_json = '[{"operation":"buy", "unit-cost":15.50, "quantity": 100}]'

    operations = parse_json_line(input_json)

    assert operations == [Operation(kind="buy", unit_cost=brl("15.50"), quantity=100)]


def test_parse_json_line_accepts_integer_unit_cost() -> None:
    input_json = '[{"operation":"buy", "unit-cost":10, "quantity": 100}]'

    operations = parse_json_line(input_json)

    assert operations == [Operation(kind="buy", unit_cost=brl("10.00"), quantity=100)]


def test_dump_json_serializes_and_adds_newline() -> None:
    tax_result_1 = OperationResult(INITIAL_INVESTMENT, tax=brl("123.456"))
    tax_result_2 = OperationResult(INITIAL_INVESTMENT, tax=Money.zero())
    tax_list = [tax_result_1, tax_result_2]

    output_stream = io.StringIO()

    dump_json(tax_list, output_stream)

    output_stream.seek(0)
    output_content = output_stream.read()

    assert output_content.endswith("\n")

    output_data = json.loads(output_content)
    assert output_data == [
        {"tax": 123.46},
        {"tax": 0.0},
    ]


def test_process_operations_integrates_full_pipeline() -> None:
    input_data = [
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 1000}]\n',
        '[{"operation":"sell", "unit-cost":50.00, "quantity": 10}]\n',
        "\n",  # blank line, ends the input
        "not json, never parsed\n",
    ]
    reader_stream = io.StringIO("".join(input_data))
    writer_stream = io.StringIO()

    run(reader_stream, writer_stream)

    writer_stream.seek(0)
    output_content = writer_stream.read()

    assert output_content == '[{"tax": 0.0}]\n[{"tax": 0.0}]\n'
