import io
import json

import pytest

from capital_gains.cli import run
from capital_gains.money import Money
from capital_gains.tax import Operation, process_operations_batch
from tests.helpers import brl

CASES = [
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=100),
            Operation(kind="sell", unit_cost=brl("15.00"), quantity=50),
            Operation(kind="sell", unit_cost=brl("15.00"), quantity=50),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
        ],
        id="case-1",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("5.00"), quantity=5_000),
        ],
        [
            Money.zero(),
            brl("10000.00"),
            Money.zero(),
        ],
        id="case-2",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("5.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=3_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            brl("1000.00"),
        ],
        id="case-3",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="buy", unit_cost=brl("25.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("15.00"), quantity=10_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
        ],
        id="case-4",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="buy", unit_cost=brl("25.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("15.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("25.00"), quantity=5_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            brl("10000.00"),
        ],
        id="case-5",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("2.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=2_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=2_000),
            Operation(kind="sell", unit_cost=brl("25.00"), quantity=1_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            brl("3000.00"),
        ],
        id="case-6",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("2.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=2_000),
            Operation(kind="sell", unit_cost=brl("20.00"), quantity=2_000),
            Operation(kind="sell", unit_cost=brl("25.00"), quantity=1_000),
            Operation(kind="buy", unit_cost=brl("20.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("15.00"), quantity=5_000),
            Operation(kind="sell", unit_cost=brl("30.00"), quantity=4_350),
            Operation(kind="sell", unit_cost=brl("30.00"), quantity=650),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            brl("3000.00"),
            Money.zero(),
            Money.zero(),
            brl("3700.00"),
            Money.zero(),
        ],
        id="case-7",
    ),
    pytest.param(
        [
            Operation(kind="buy", unit_cost=brl("10.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("50.00"), quantity=10_000),
            Operation(kind="buy", unit_cost=brl("20.00"), quantity=10_000),
            Operation(kind="sell", unit_cost=brl("50.00"), quantity=10_000),
        ],
        [
            Money.zero(),
            brl("80000.00"),
            Money.zero(),
            brl("60000.00"),
        ],
        id="case-8",
    ),
]


@pytest.mark.parametrize(("operations_batch", "expected_taxes"), CASES)
def test_process_operations_taxes(
    operations_batch: list[Operation], expected_taxes: list[Money]
) -> None:
    results_list = list(process_operations_batch(operations_batch))
    actual_taxes = [result.tax for result in results_list]

    assert len(actual_taxes) == len(operations_batch)
    assert actual_taxes == expected_taxes


CASE_1_INPUT = (
    '[{"operation":"buy", "unit-cost":10.00, "quantity": 100}, '
    '{"operation":"sell", "unit-cost":15.00, "quantity": 50}, '
    '{"operation":"sell", "unit-cost":15.00, "quantity": 50}]\n'
)
CASE_1_OUTPUT = '[{"tax": 0.00},{"tax": 0.00},{"tax": 0.00}]\n'

CASE_2_INPUT = (
    '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
    '{"operation":"sell", "unit-cost":20.00, "quantity": 5000}, '
    '{"operation":"sell", "unit-cost":5.00, "quantity": 5000}]\n'
)
CASE_2_OUTPUT = '[{"tax": 0.00},{"tax": 10000.00},{"tax": 0.00}]\n'

# Input and output text copied from the specification, each input ending
# with the empty line that closes it.
SPEC_EXAMPLES = [
    pytest.param(CASE_1_INPUT + "\n", CASE_1_OUTPUT, id="case-1"),
    pytest.param(CASE_2_INPUT + "\n", CASE_2_OUTPUT, id="case-2"),
    pytest.param(
        CASE_1_INPUT + CASE_2_INPUT + "\n",
        CASE_1_OUTPUT + CASE_2_OUTPUT,
        id="case-1-and-2",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":5.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":20.00, "quantity": 3000}]\n'
        "\n",
        '[{"tax": 0.00},{"tax": 0.00},{"tax": 1000.00}]\n',
        id="case-3",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"buy", "unit-cost":25.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":15.00, "quantity": 10000}]\n'
        "\n",
        '[{"tax": 0.00},{"tax": 0.00},{"tax": 0.00}]\n',
        id="case-4",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"buy", "unit-cost":25.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":15.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":25.00, "quantity": 5000}]\n'
        "\n",
        '[{"tax": 0.00},{"tax": 0.00},{"tax": 0.00},{"tax": 10000.00}]\n',
        id="case-5",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":2.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
        '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
        '{"operation":"sell", "unit-cost":25.00, "quantity": 1000}]\n'
        "\n",
        '[{"tax": 0.00},{"tax": 0.00},{"tax": 0.00},{"tax": 0.00},{"tax": 3000.00}]\n',
        id="case-6",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":2.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
        '{"operation":"sell", "unit-cost":20.00, "quantity": 2000}, '
        '{"operation":"sell", "unit-cost":25.00, "quantity": 1000}, '
        '{"operation":"buy", "unit-cost":20.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":15.00, "quantity": 5000}, '
        '{"operation":"sell", "unit-cost":30.00, "quantity": 4350}, '
        '{"operation":"sell", "unit-cost":30.00, "quantity": 650}]\n'
        "\n",
        '[{"tax":0.00}, {"tax":0.00}, {"tax":0.00}, {"tax":0.00}, {"tax":3000.00}, '
        '{"tax":0.00}, {"tax":0.00}, {"tax":3700.00}, {"tax":0.00}]\n',
        id="case-7",
    ),
    pytest.param(
        '[{"operation":"buy", "unit-cost":10.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":50.00, "quantity": 10000}, '
        '{"operation":"buy", "unit-cost":20.00, "quantity": 10000}, '
        '{"operation":"sell", "unit-cost":50.00, "quantity": 10000}]\n'
        "\n",
        '[{"tax":0.00},{"tax":80000.00},{"tax":0.00},{"tax":60000.00}]\n',
        id="case-8",
    ),
]


@pytest.mark.parametrize(("stdin", "expected_stdout"), SPEC_EXAMPLES)
def test_run_matches_spec_examples(stdin: str, expected_stdout: str) -> None:
    output = io.StringIO()

    run(io.StringIO(stdin), output)

    # Compared as parsed JSON, since the output prints 0.0 where the
    # specification shows 0.00 (see NOTES.md).
    assert [json.loads(line) for line in output.getvalue().splitlines()] == [
        json.loads(line) for line in expected_stdout.splitlines()
    ]
