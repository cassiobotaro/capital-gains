import pytest

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
