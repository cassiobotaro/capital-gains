import io
import json

import pytest

from capital_gains.cli import dump_json, parse_json_line, process_operations, readlines
from capital_gains.money import Money
from capital_gains.tax import INITIAL_INVESTMENT, Operation, OperationResult


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            # Input with empty and whitespace-only lines
            ["op1\n", "  \n", "op2\n", "\t", "op3"],
            ["op1\n", "op2\n", "op3"],
        ),
        (
            # Simple input
            ["line A", "line B"],
            ["line A", "line B"],
        ),
        (
            # Input with garbage lines
            ["\n", " "],
            [],
        ),
    ],
)
def test_readlines_filters_empty_and_whitespace(
    input_data: list[str], expected_output: list[str]
) -> None:
    assert list(readlines(input_data)) == expected_output


def test_parse_json_line_converts_to_domain_objects() -> None:
    input_json = '[{"operation":"buy", "unit-cost":15.50, "quantity": 100}]'

    operations = parse_json_line(input_json)

    assert operations == [
        Operation(operation="buy", unit_cost=Money("15.50"), quantity=100)
    ]


def test_dump_json_serializes_and_adds_newline() -> None:
    tax_result_1 = OperationResult(INITIAL_INVESTMENT, tax=Money(123.456))
    tax_result_2 = OperationResult(INITIAL_INVESTMENT, tax=Money(0))
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
        "\n",  # Linha ignorada
        '[{"operation":"sell", "unit-cost":50.00, "quantity": 10}]\n',
    ]
    reader_stream = io.StringIO("".join(input_data))
    writer_stream = io.StringIO()

    process_operations(reader_stream, writer_stream)

    writer_stream.seek(0)
    output_content = writer_stream.read()

    assert output_content == '[{"tax": 0.0}]\n[{"tax": 0.0}]\n'
