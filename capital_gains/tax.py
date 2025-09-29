from collections.abc import Iterable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from capital_gains.money import Money

TAX_RATE = Decimal("0.20")  # 20%
EXEMPTION_LIMIT = Money("20000.00")  # R$ 20.000,00


@dataclass(frozen=True)
class InvestmentState:
    quantity: int = 0
    weighted_average_price: Money = field(default_factory=Money.zero)
    accumulated_loss: Money = field(default_factory=Money.zero)


@dataclass(frozen=True)
class OperationResult:
    new_state: InvestmentState
    tax: Money


@dataclass(frozen=True)
class Operation:
    operation: Literal["sell", "buy"]
    unit_cost: Money
    quantity: int

    @classmethod
    def from_dict(cls, data: dict) -> Operation:
        return cls(
            operation=data["operation"],
            unit_cost=Money(str(data["unit-cost"])),
            quantity=data["quantity"],
        )


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
        tax=Money.zero(),
    )


def handle_sell(state: InvestmentState, operation: Operation) -> OperationResult:
    def calculate_new_loss(current_loss: Money, profit: Money) -> Money:
        return max(Money.zero(), current_loss - profit)

    def calculate_taxable_profit(current_loss: Money, profit: Money) -> Money:
        profit_after_deduction = profit - current_loss
        return max(Money.zero(), profit_after_deduction)

    def calculate_tax(taxable_profit: Money, total_operation_value: Money) -> Money:
        if taxable_profit > Money.zero() and total_operation_value > EXEMPTION_LIMIT:
            return taxable_profit * TAX_RATE
        return Money.zero()

    price_diff_per_share = operation.unit_cost - state.weighted_average_price
    gross_profit = price_diff_per_share * operation.quantity
    total_operation_value = operation.unit_cost * operation.quantity

    new_accumulated_loss = calculate_new_loss(state.accumulated_loss, gross_profit)
    taxable_profit = calculate_taxable_profit(state.accumulated_loss, gross_profit)
    tax = calculate_tax(taxable_profit, total_operation_value)

    new_quantity = state.quantity - operation.quantity

    new_state = InvestmentState(
        quantity=new_quantity,
        weighted_average_price=state.weighted_average_price,
        accumulated_loss=new_accumulated_loss,
    )

    return OperationResult(new_state=new_state, tax=tax)


def process_operation(state: InvestmentState, operation: Operation) -> OperationResult:
    match operation.operation:
        case "buy":
            return handle_buy(state, operation)
        case "sell":
            return handle_sell(state, operation)


INITIAL_INVESTMENT = InvestmentState()


def process_operations_batch(
    operations: Iterable[Operation], initial_state: InvestmentState = INITIAL_INVESTMENT
) -> list[OperationResult]:
    current_state = initial_state
    taxes: list[OperationResult] = []
    for operation in operations:
        result = process_operation(current_state, operation)
        taxes.append(result)
        current_state = result.new_state
    return taxes
