import dataclasses
from decimal import Decimal

import pytest

from capital_gains.money import DEFAULT_CURRENCY, Money


class TestMoney:
    def test_should_contain_amount_and_currency(self):
        money = Money(Decimal("10.00"))
        assert money.amount == Decimal("10.00")
        assert money.currency == DEFAULT_CURRENCY

    def test_should_be_immutable(self):
        money = Money(Decimal("10.00"))
        with pytest.raises(dataclasses.FrozenInstanceError):
            money.amount = Decimal("20.00")

    def test_should_round_amount_to_two_decimal_places(self):
        money = Money(Decimal("10.123"), "BRL")
        assert money.amount == Decimal("10.12")

        money = Money(Decimal("10.126"), "BRL")
        assert money.amount == Decimal("10.13")

    def test_same_currency_should_be_summable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.50"), "BRL")
        assert money1 + money2 == Money(Decimal("15.50"), "BRL")

    def test_different_currency_should_not_be_summable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.50"), "USD")
        with pytest.raises(ValueError):
            _ = money1 + money2

    def test_same_currency_should_be_subtractable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "BRL")
        assert money1 - money2 == Money(Decimal("5.00"), "BRL")

    def test_different_currency_should_not_be_subtractable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "USD")
        with pytest.raises(ValueError):
            _ = money1 - money2

    @pytest.mark.parametrize(
        "scalar, expected",
        [
            (2, Decimal("20.00")),
            (0.5, Decimal("5.00")),
            (Decimal("1.5"), Decimal("15.00")),
        ],
    )
    def test_should_be_able_to_multiply_money_by_scalar(self, scalar, expected):
        assert Money(Decimal("10.00"), "BRL") * scalar == Money(expected, "BRL")
        assert scalar * Money(Decimal("10.00"), "BRL") == Money(expected, "BRL")

    @pytest.mark.parametrize(
        "scalar, expected",
        [
            (2, Decimal("5.00")),
            (1.5, Decimal("6.67")),
            (Decimal("1.5"), Decimal("6.67")),
        ],
    )
    def test_should_be_able_to_divide_money_by_scalar(self, scalar, expected):
        assert Money(Decimal("10.00"), "BRL") / scalar == Money(expected, "BRL")

    def test_same_currency_should_be_comparable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "BRL")
        money3 = Money(Decimal("10.00"), "BRL")

        assert money1 > money2
        assert money1 >= money2
        assert money2 < money1
        assert money2 <= money1
        assert money1 == money3
        assert not (money1 != money3)

    def test_different_currency_should_not_be_comparable(self):
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "USD")
        with pytest.raises(ValueError):
            _ = money1 > money2
        with pytest.raises(ValueError):
            _ = money1 < money2
        with pytest.raises(ValueError):
            _ = money1 >= money2
        with pytest.raises(ValueError):
            _ = money1 <= money2
