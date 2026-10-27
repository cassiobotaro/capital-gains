from decimal import Decimal

from capital_gains.money import Money


def brl(amount: str) -> Money:
    return Money(Decimal(amount))
