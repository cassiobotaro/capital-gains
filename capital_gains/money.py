from collections.abc import Sequence
from dataclasses import InitVar, dataclass, field
from decimal import Decimal
from functools import total_ordering
from typing import Literal

TWOPLACES = Decimal("0.01")
DEFAULT_CURRENCY = "BRL"

type Scalar = int | Decimal
type DecimalConvertible = Decimal | float | str | tuple[int, Sequence[int], int]


@dataclass(frozen=True)
@total_ordering
class Money:
    raw_amount: InitVar[DecimalConvertible]
    amount: Decimal = field(init=False)
    currency: str = DEFAULT_CURRENCY

    def __post_init__(self, raw_amount: DecimalConvertible) -> None:
        quantized_amount = Decimal(raw_amount).quantize(TWOPLACES)
        object.__setattr__(self, "amount", quantized_amount)

    def _assert_same_currency_as(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError(
                f"Different currencies: {self.currency} and {other.currency}"
            )

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency_as(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._assert_same_currency_as(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, scalar: Scalar) -> Money:
        return Money(self.amount * Decimal(scalar), self.currency)

    __rmul__ = __mul__

    def __truediv__(self, scalar: Scalar) -> Money:
        return Money(self.amount / Decimal(scalar), self.currency)

    def __lt__(self, other: object) -> bool | Literal["NotImplemented"]:
        if not isinstance(other, Money):
            return NotImplemented

        self._assert_same_currency_as(other)
        return self.amount < other.amount

    @classmethod
    def zero(cls, currency: str = DEFAULT_CURRENCY) -> Money:
        return cls("0.00", currency)
