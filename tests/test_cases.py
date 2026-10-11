from decimal import Decimal

import pytest

from capital_gains.money import Money
from capital_gains.tax import Operation, process_operations_batch

test_cases = [
    (
        # case 1
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=100),
            Operation(kind="sell", unit_cost=Money(Decimal("15.00")), quantity=50),
            Operation(kind="sell", unit_cost=Money(Decimal("15.00")), quantity=50),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
        ],
    ),
    (
        # case 2
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("5.00")), quantity=5_000),
        ],
        [
            Money.zero(),
            Money(Decimal("10000.00")),
            Money.zero(),
        ],
    ),
    (
        # case 3
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("5.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=3_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money(Decimal("1000.00")),
        ],
    ),
    (
        # case 4
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="buy", unit_cost=Money(Decimal("25.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("15.00")), quantity=10_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
        ],
    ),
    (
        # case 5
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="buy", unit_cost=Money(Decimal("25.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("15.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("25.00")), quantity=5_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money(Decimal("10000.00")),
        ],
    ),
    (
        # case 6
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("2.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=2_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=2_000),
            Operation(kind="sell", unit_cost=Money(Decimal("25.00")), quantity=1_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money(Decimal("3000.00")),
        ],
    ),
    (
        # case 7
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("2.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=2_000),
            Operation(kind="sell", unit_cost=Money(Decimal("20.00")), quantity=2_000),
            Operation(kind="sell", unit_cost=Money(Decimal("25.00")), quantity=1_000),
            Operation(kind="buy", unit_cost=Money(Decimal("20.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("15.00")), quantity=5_000),
            Operation(kind="sell", unit_cost=Money(Decimal("30.00")), quantity=4_350),
            Operation(kind="sell", unit_cost=Money(Decimal("30.00")), quantity=650),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money(Decimal("3000.00")),
            Money.zero(),
            Money.zero(),
            Money(Decimal("3700.00")),
            Money.zero(),
        ],
    ),
    (
        # case 8
        [
            Operation(kind="buy", unit_cost=Money(Decimal("10.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("50.00")), quantity=10_000),
            Operation(kind="buy", unit_cost=Money(Decimal("20.00")), quantity=10_000),
            Operation(kind="sell", unit_cost=Money(Decimal("50.00")), quantity=10_000),
        ],
        [
            Money.zero(),
            Money(Decimal("80000.00")),
            Money.zero(),
            Money(Decimal("60000.00")),
        ],
    ),
]


@pytest.mark.parametrize("operations_batch, expected_taxes", test_cases)
def test_process_operations_taxes(
    operations_batch: list[Operation], expected_taxes: list[Money]
) -> None:
    # act
    results_list = process_operations_batch(operations_batch)
    actual_taxes = [result.tax for result in results_list]

    # assert
    assert len(actual_taxes) == len(operations_batch)
    assert actual_taxes == expected_taxes
