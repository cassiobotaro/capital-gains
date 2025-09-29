from decimal import Decimal

import pytest

from capital_gains.money import DEFAULT_CURRENCY, Money, Scalar


class TestMoney:
    def test_should_contain_amount_and_currency(self) -> None:
        money = Money(Decimal("10.00"))
        assert money.amount == Decimal("10.00")
        assert money.currency == DEFAULT_CURRENCY

    def test_should_round_amount_to_two_decimal_places(self) -> None:
        money = Money(Decimal("10.123"), "BRL")
        assert money.amount == Decimal("10.12")

        money = Money(Decimal("10.126"), "BRL")
        assert money.amount == Decimal("10.13")

    def test_same_currency_should_be_summable(self) -> None:
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.50"), "BRL")
        assert money1 + money2 == Money(Decimal("15.50"), "BRL")

    def test_different_currency_should_not_be_summable(self) -> None:
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.50"), "USD")
        with pytest.raises(ValueError):
            _ = money1 + money2

    def test_same_currency_should_be_subtractable(self) -> None:
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "BRL")
        assert money1 - money2 == Money(Decimal("5.00"), "BRL")

    def test_different_currency_should_not_be_subtractable(self) -> None:
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
    def test_should_be_able_to_multiply_money_by_scalar(
        self, scalar: Scalar, expected: Decimal
    ) -> None:
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
    def test_should_be_able_to_divide_money_by_scalar(
        self, scalar: Scalar, expected: Decimal
    ) -> None:
        assert Money(Decimal("10.00"), "BRL") / scalar == Money(expected, "BRL")

    def test_same_currency_should_be_comparable(self) -> None:
        money1 = Money(Decimal("10.00"), "BRL")
        money2 = Money(Decimal("5.00"), "BRL")
        money3 = Money(Decimal("10.00"), "BRL")

        assert money1 > money2
        assert money1 >= money2
        assert money2 < money1
        assert money2 <= money1
        assert money1 == money3
        assert not (money1 != money3)

    def test_different_currency_should_not_be_comparable(self) -> None:
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

    def test_different_type_should_not_be_comparable(self) -> None:
        money1 = Money(Decimal("10.00"), "BRL")
        an_object = 42
        with pytest.raises(TypeError):
            _ = money1 > an_object
        with pytest.raises(TypeError):
            _ = money1 < an_object
        with pytest.raises(TypeError):
            _ = money1 >= an_object
        with pytest.raises(TypeError):
            _ = money1 <= an_object

    def test_zero_returns_correct_amount(self) -> None:
        # act
        zero_money = Money.zero()

        # assert
        assert zero_money.amount == Decimal("0.00")

    def test_zero_retains_default_currency(self) -> None:
        # act
        zero_money = Money.zero()

        # assert
        assert zero_money.currency == DEFAULT_CURRENCY

    def test_money_zero_accepts_custom_currency(self) -> None:
        # arrange
        custom_currency = "USD"

        # act
        zero_usd = Money.zero(currency=custom_currency)

        # assert
        assert zero_usd.amount == Decimal("0.00")
        assert zero_usd.currency == custom_currency
