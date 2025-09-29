from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Literal

from capital_gains.money import Money

TAX_RATE = Decimal("0.20")  # 20%
EXEMPTION_LIMIT = Money("20000.00")  # R$ 20.000,00


@dataclass(frozen=True)
class InvestmentState:
    quantity: int = 0
    weighted_average_price: Money = Money("0.00")
    accumulated_loss: Money = Money("0.00")


@dataclass(frozen=True)
class OperationResult:
    new_state: InvestmentState
    tax: Money


@dataclass(frozen=True)
class Operation:
    operation: Literal["sell", "buy"]
    unit_cost: Money
    quantity: int


def handle_buy(state: InvestmentState, operation: Operation) -> OperationResult:
    return OperationResult(
        new_state=InvestmentState(
            quantity=state.quantity + operation.quantity,
            weighted_average_price=(
                (state.weighted_average_price * state.quantity)
                + (operation.unit_cost * operation.quantity)
            )
            / (state.quantity + operation.quantity),
            accumulated_loss=state.accumulated_loss,
        ),
        tax=Money("0.00"),
    )


def handle_sell(state: InvestmentState, operation: Operation) -> OperationResult:
    # 1. Calculate Gross Profit
    sell_value = operation.unit_cost * operation.quantity
    cost_of_shares_sold = state.weighted_average_price * operation.quantity
    gross_profit = sell_value - cost_of_shares_sold

    # Gross profit (can be negative, indicating loss)
    gross_profit = sell_value - cost_of_shares_sold

    tax = Money("0.00")
    new_accumulated_loss = state.accumulated_loss  # Maintain previous loss for now

    # 2. Check for Profit and Exemption

    # Check if there is profit (gross_profit.amount > 0)
    if gross_profit.amount > 0:
        net_profit = gross_profit - state.accumulated_loss
        if net_profit.amount <= 0:
            new_accumulated_loss = net_profit * Decimal(
                "-1"
            )  # net_profit is negative or zero
        else:
            new_accumulated_loss = Money("0.00")

            if sell_value <= EXEMPTION_LIMIT:
                # Profit is exempt due to low volume. Tax remains ZERO_MONEY.
                tax = Money("0.00")
            else:
                # Profit is taxable (Volume > R$ 20000.00).
                # Tax is 20% on the Gross Profit (since accumulated_loss is 0 for this test)
                tax_amount = net_profit.amount * TAX_RATE
                tax = Money(tax_amount)
    else:
        loss_from_this_op = gross_profit * Decimal("-1")
        new_accumulated_loss = state.accumulated_loss + loss_from_this_op

    # 3. Update Share State
    new_quantity = state.quantity - operation.quantity

    new_state = InvestmentState(
        quantity=new_quantity,
        weighted_average_price=state.weighted_average_price,  # WAP does not change on sell
        accumulated_loss=new_accumulated_loss,
    )

    return OperationResult(new_state, tax)


def process_operation(state: InvestmentState, operation: Operation) -> OperationResult:
    match operation.operation:
        case "buy":
            return handle_buy(state, operation)
        case "sell":
            return handle_sell(state, operation)


def process_operations_batch(
    operations: Iterable[Operation], initial_state: InvestmentState = InvestmentState()
) -> list[OperationResult]:
    current_state = initial_state
    taxes: list[OperationResult] = []
    for operation in operations:
        result = process_operation(current_state, operation)
        taxes.append(result)
        current_state = result.new_state
    return taxes
