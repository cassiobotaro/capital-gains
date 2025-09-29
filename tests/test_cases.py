import pytest

from capital_gains.money import Money
from capital_gains.tax import Operation, process_operations_batch

test_cases = [
    (
        # case 1
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=100),
            Operation(operation="sell", unit_cost=Money("15.00"), quantity=50),
            Operation(operation="sell", unit_cost=Money("15.00"), quantity=50),
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
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("5.00"), quantity=5_000),
        ],
        [
            Money.zero(),
            Money("10000.00"),
            Money.zero(),
        ],
    ),
    (
        # case 3
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("5.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=3_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money("1000.00"),
        ],
    ),
    (
        # case 4
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="buy", unit_cost=Money("25.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("15.00"), quantity=10_000),
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
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="buy", unit_cost=Money("25.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("15.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("25.00"), quantity=5_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money("10000.00"),
        ],
    ),
    (
        # case 6
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("2.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=2_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=2_000),
            Operation(operation="sell", unit_cost=Money("25.00"), quantity=1_000),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money("3000.00"),
        ],
    ),
    (
        # case 7
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("2.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=2_000),
            Operation(operation="sell", unit_cost=Money("20.00"), quantity=2_000),
            Operation(operation="sell", unit_cost=Money("25.00"), quantity=1_000),
            Operation(operation="buy", unit_cost=Money("20.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("15.00"), quantity=5_000),
            Operation(operation="sell", unit_cost=Money("30.00"), quantity=4_350),
            Operation(operation="sell", unit_cost=Money("30.00"), quantity=650),
        ],
        [
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money.zero(),
            Money("3000.00"),
            Money.zero(),
            Money.zero(),
            Money("3700.00"),
            Money.zero(),
        ],
    ),
    (
        # case 8
        [
            Operation(operation="buy", unit_cost=Money("10.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("50.00"), quantity=10_000),
            Operation(operation="buy", unit_cost=Money("20.00"), quantity=10_000),
            Operation(operation="sell", unit_cost=Money("50.00"), quantity=10_000),
        ],
        [
            Money.zero(),
            Money("80000.00"),
            Money.zero(),
            Money("60000.00"),
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
