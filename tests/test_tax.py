from decimal import Decimal

from capital_gains.money import Money
from capital_gains.tax import (
    TAX_RATE,
    InvestmentState,
    Operation,
    process_operation,
    process_operations_batch,
)


def test_first_buy_sets_initial_weighted_average() -> None:
    # arrange
    initial_state = InvestmentState()
    unit_price = Money("20.00")
    quantity = 10

    operation = Operation(
        operation="buy",
        unit_cost=unit_price,
        quantity=quantity,
    )

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == Money.zero(), "Tax on purchase must be zero."
    assert result.new_state.quantity == 10, (
        "Quantity after purchase should match operation."
    )
    assert result.new_state.weighted_average_price == Money("20.00"), (
        "Weighted average price should match unit cost on first buy."
    )
    assert result.new_state.accumulated_loss == Money.zero(), (
        "Accumulated loss should remain zero after purchase."
    )


def test_multiple_buys_calculate_weighted_average() -> None:
    # arrange
    initial_state = InvestmentState(quantity=5, weighted_average_price=Money("20.00"))
    operation = Operation(
        operation="buy",
        unit_cost=Money("10.00"),
        quantity=5,
    )
    expected_average = Money("15.00")

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.new_state.quantity == 10
    assert result.new_state.weighted_average_price == expected_average
    assert result.tax == Money.zero()


def test_sell_with_simple_profit_above_exemption_limit() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=1000, weighted_average_price=Money("30.00")
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("35.00"),
        quantity=1000,
    )
    gross_profit_amount = Decimal("5000.00")  # (35.00 - 30.00) * 1000
    expected_tax_amount = gross_profit_amount * TAX_RATE
    expected_tax = Money(expected_tax_amount)  # R$ 1,000.00

    # act
    result = process_operation(initial_state, operation)

    # Assert
    assert result.new_state.quantity == 0
    assert result.new_state.weighted_average_price == Money("30.00")
    assert result.new_state.accumulated_loss == Money.zero()
    # A verificação usa o resultado do cálculo dinâmico:
    assert result.tax == expected_tax, (
        f"Tax must be {TAX_RATE * 100}% ({expected_tax_amount}) of the profit."
    )


def test_sell_with_exemption_due_to_low_volume() -> None:
    # arrange
    initial_state = InvestmentState(quantity=100, weighted_average_price=Money("50.00"))
    operation = Operation(
        operation="sell",
        unit_cost=Money("60.00"),
        quantity=100,
    )
    expected_tax = Money.zero()

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.new_state.quantity == 0, (
        "Share quantity should be zero after the sale."
    )
    assert result.new_state.accumulated_loss == Money.zero(), (
        "Accumulated loss should remain zero."
    )
    assert result.tax == expected_tax, "Tax must be zero due to the exemption rule."


def test_sell_with_loss_generates_accumulated_loss() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=100,
        weighted_average_price=Money("50.00"),
        accumulated_loss=Money.zero(),
    )

    # arrange
    operation = Operation(
        operation="sell",
        unit_cost=Money("45.00"),
        quantity=100,
    )
    expected_loss = Money("500.00")

    # Act
    result = process_operation(initial_state, operation)

    # Assert
    assert result.new_state.quantity == 0, "Share quantity should be reduced."
    assert result.tax == Money.zero(), (
        "Tax must be zero when operation results in a loss."
    )
    assert result.new_state.accumulated_loss == expected_loss, (
        "Gross loss must be recorded as accumulated loss."
    )
    assert result.new_state.weighted_average_price == Money("50.00"), (
        "WAP should not change."
    )


def test_sell_with_profit_fully_compensated_by_accumulated_loss() -> None:
    # arrange
    initial_loss = Money("2000.00")
    initial_state = InvestmentState(
        quantity=500,
        weighted_average_price=Money("10.00"),
        accumulated_loss=initial_loss,
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("12.00"),
        quantity=500,
    )
    expected_remaining_loss = Money("1000.00")

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == Money.zero(), (
        "Tax must be zero when profit is fully compensated by loss carryforward."
    )
    assert result.new_state.accumulated_loss == expected_remaining_loss, (
        "Accumulated loss must be correctly reduced."
    )
    assert result.new_state.quantity == 0, (
        "Share quantity should be zero after the sale."
    )
    assert result.new_state.weighted_average_price == Money("10.00"), (
        "WAP should not change."
    )


def test_sell_with_profit_partially_compensated_by_accumulated_loss() -> None:
    # arrange
    initial_loss = Money("500.00")
    initial_state = InvestmentState(
        quantity=2000,
        weighted_average_price=Money("30.00"),
        accumulated_loss=initial_loss,
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("32.50"),
        quantity=2000,
    )
    expected_tax = Money("900.00")

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, (
        "Tax must be 20% of the net profit (after partial compensation)."
    )
    assert result.new_state.accumulated_loss == Money.zero(), (
        "Accumulated loss must be reset to zero when profit is taxable."
    )
    assert result.new_state.quantity == 0
    assert result.new_state.weighted_average_price == Money("30.00")


def test_sell_with_profit_exempt_but_compensating_loss() -> None:
    # arrange
    initial_loss = Money("1000.00")
    initial_state = InvestmentState(
        quantity=200,
        weighted_average_price=Money("40.00"),
        accumulated_loss=initial_loss,
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("42.50"),
        quantity=200,
    )
    expected_tax = Money.zero()
    expected_remaining_loss = Money("500.00")

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, "Tax must be zero due to the exemption limit."
    assert result.new_state.accumulated_loss == expected_remaining_loss, (
        "Accumulated loss must be reduced by the exempt profit."
    )
    assert result.new_state.quantity == 0


def test_sell_above_exemption_limit_but_net_profit_is_zero() -> None:
    # arrange
    initial_loss = Money("5000.00")
    initial_state = InvestmentState(
        quantity=1000,
        weighted_average_price=Money("30.00"),
        accumulated_loss=initial_loss,
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("33.00"),
        quantity=1000,
    )
    expected_tax = Money.zero()
    expected_remaining_loss = Money("2000.00")

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, (
        "Tax must be zero if net profit is zero/negative, regardless of sale volume."
    )
    assert result.new_state.accumulated_loss == expected_remaining_loss, (
        "Accumulated loss must be correctly reduced by the gross profit."
    )
    assert result.new_state.quantity == 0


def test_full_sequence_of_operations_and_state_management() -> None:
    current_state = InvestmentState()
    total_tax_paid = Money.zero()

    op1 = Operation(operation="buy", unit_cost=Money("10.00"), quantity=100)
    result1 = process_operation(current_state, op1)

    assert result1.new_state.quantity == 100
    assert result1.new_state.weighted_average_price == Money("10.00")
    assert result1.tax == Money.zero()
    current_state = result1.new_state

    op2 = Operation(operation="buy", unit_cost=Money("20.00"), quantity=100)
    result2 = process_operation(current_state, op2)

    assert result2.new_state.quantity == 200
    assert result2.new_state.weighted_average_price == Money("15.00")
    assert result2.tax == Money.zero()
    current_state = result2.new_state

    op3 = Operation(operation="sell", unit_cost=Money("12.00"), quantity=100)
    result3 = process_operation(current_state, op3)

    assert result3.new_state.quantity == 100
    assert result3.new_state.accumulated_loss == Money("300.00")
    assert result3.tax == Money.zero()
    current_state = result3.new_state

    op4 = Operation(operation="sell", unit_cost=Money("30.00"), quantity=100)
    result4 = process_operation(current_state, op4)

    assert result4.tax == Money.zero(), "Tax must be zero due to low volume exemption."
    assert result4.new_state.accumulated_loss == Money.zero(), (
        "Accumulated loss must be compensated/zeroed by the exempt profit."
    )

    total_tax_paid += result1.tax + result2.tax + result3.tax + result4.tax

    assert total_tax_paid == Money.zero()


def test_process_operations_batch_extracts_taxes() -> None:
    # arrange
    operations_batch = [
        Operation(operation="buy", unit_cost=Money("10.00"), quantity=100),
        Operation(operation="buy", unit_cost=Money("20.00"), quantity=100),
        Operation(operation="sell", unit_cost=Money("12.00"), quantity=100),
        Operation(operation="sell", unit_cost=Money("30.00"), quantity=100),
    ]
    expected_taxes = [
        Money.zero(),
        Money.zero(),
        Money.zero(),
        Money.zero(),
    ]

    # act
    results_list = process_operations_batch(operations_batch)
    actual_taxes = [result.tax for result in results_list]

    # assert
    assert len(actual_taxes) == len(operations_batch)
    assert actual_taxes == expected_taxes


def test_sell_partial_with_loss_accumulates_loss() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=100,
        weighted_average_price=Money("50.00"),
        accumulated_loss=Money("100.00"),
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("45.00"),
        quantity=50,
    )
    expected_accumulated_loss = Money("350.00")
    expected_quantity = 50

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == Money.zero(), (
        "Tax must be zero when operation results in a loss."
    )
    assert result.new_state.quantity == expected_quantity, (
        "Remaining quantity must be correct."
    )
    assert (
        result.new_state.weighted_average_price == initial_state.weighted_average_price
    ), "Weighted average price must not change after a sell operation."
    assert result.new_state.accumulated_loss == expected_accumulated_loss, (
        "New loss must be correctly added to the accumulated loss."
    )


def test_sell_partial_with_profit_above_tax_limit() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=1000,
        weighted_average_price=Money("10.00"),
        accumulated_loss=Money.zero(),
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("60.00"),
        quantity=500,
    )
    expected_tax = Money("5000.00")
    expected_quantity = 500

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, "Tax must be 20% of the gross profit."
    assert result.new_state.quantity == expected_quantity, (
        "Remaining quantity must be correct."
    )
    assert (
        result.new_state.weighted_average_price == initial_state.weighted_average_price
    ), "Weighted average price must not change after a sell operation."
    assert result.new_state.accumulated_loss == Money.zero(), (
        "Accumulated loss must remain zero as there was profit."
    )


def test_sell_with_profit_exempt_and_accumulated_loss_fully_zeroed() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=100,
        weighted_average_price=Money("40.00"),
        accumulated_loss=Money("500.00"),
    )
    operation = Operation(
        operation="sell",
        unit_cost=Money("48.00"),
        quantity=100,
    )
    expected_tax = Money.zero()
    expected_remaining_loss = Money.zero()

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, (
        "Tax must be zero due to the exemption limit, despite net profit."
    )
    assert result.new_state.accumulated_loss == expected_remaining_loss, (
        "Accumulated loss must be fully zeroed by the exempt profit."
    )
    assert result.new_state.quantity == 0, (
        "Share quantity should be zero after the sale."
    )


def test_buy_zero_quantity_does_not_change_state() -> None:
    # arrange
    initial_state = InvestmentState(
        quantity=10,
        weighted_average_price=Money("20.00"),
        accumulated_loss=Money("500.00"),
    )
    operation = Operation(
        operation="buy",
        unit_cost=Money("100.00"),
        quantity=0,
    )

    expected_quantity = initial_state.quantity
    expected_wap = initial_state.weighted_average_price
    expected_loss = initial_state.accumulated_loss
    expected_tax = Money.zero()

    # act
    result = process_operation(initial_state, operation)

    # assert
    assert result.tax == expected_tax, "Tax must be zero on a buy operation."
    assert result.new_state.quantity == expected_quantity, (
        "Quantity must remain unchanged."
    )
    assert result.new_state.weighted_average_price == expected_wap, (
        "Weighted average price must remain unchanged when quantity bought is zero."
    )
    assert result.new_state.accumulated_loss == expected_loss, (
        "Accumulated loss must remain unchanged."
    )


def test_full_sequence_of_operations_with_final_taxable_sale() -> None:
    current_state = InvestmentState()

    op1 = Operation(operation="buy", unit_cost=Money("10.00"), quantity=100)
    result1 = process_operation(current_state, op1)
    current_state = result1.new_state

    op2 = Operation(operation="buy", unit_cost=Money("20.00"), quantity=100)
    result2 = process_operation(current_state, op2)
    current_state = result2.new_state

    op3 = Operation(operation="sell", unit_cost=Money("12.00"), quantity=100)
    result3 = process_operation(current_state, op3)
    current_state = result3.new_state
    assert current_state.accumulated_loss == Money("300.00")

    op4 = Operation(operation="sell", unit_cost=Money("30.00"), quantity=100)
    result4 = process_operation(current_state, op4)
    current_state = result4.new_state
    assert result4.tax == Money.zero(), "Tax must be zero due to low volume exemption."
    assert current_state.accumulated_loss == Money.zero(), (
        "Accumulated loss must be zeroed."
    )

    op5 = Operation(operation="buy", unit_cost=Money("20.00"), quantity=500)
    result5 = process_operation(current_state, op5)
    current_state = result5.new_state
    assert current_state.quantity == 500
    assert current_state.weighted_average_price == Money("20.00")

    op6 = Operation(operation="sell", unit_cost=Money("70.00"), quantity=500)
    result6 = process_operation(current_state, op6)

    expected_tax = Money("5000.00")

    assert result6.tax == expected_tax, "Final sale must be taxed due to volume > 20k."
    assert result6.new_state.quantity == 0
    assert result6.new_state.accumulated_loss == Money.zero()
