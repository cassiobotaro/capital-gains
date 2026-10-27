from dataclasses import replace
from decimal import Decimal

import pytest

from capital_gains.money import DEFAULT_CURRENCY, Money, Scalar


def test_should_contain_amount_and_currency() -> None:
    money = Money(Decimal("10.00"))
    assert money.amount == Decimal("10.00")
    assert money.currency == DEFAULT_CURRENCY


def test_should_accept_amount_as_keyword() -> None:
    money = Money(amount=Decimal("10.00"), currency="BRL")
    assert money == Money(Decimal("10.00"), "BRL")


def test_should_support_dataclass_replace() -> None:
    money = Money(Decimal("10.00"), "BRL")

    assert replace(money, currency="USD") == Money(Decimal("10.00"), "USD")
    assert replace(money, amount=Decimal("5.555")) == Money(Decimal("5.56"), "BRL")


def test_should_round_amount_to_two_decimal_places() -> None:
    money = Money(Decimal("10.123"), "BRL")
    assert money.amount == Decimal("10.12")

    money = Money(Decimal("10.126"), "BRL")
    assert money.amount == Decimal("10.13")


def test_same_currency_should_be_summable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.50"), "BRL")
    assert money1 + money2 == Money(Decimal("15.50"), "BRL")


def test_different_currency_should_not_be_summable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.50"), "USD")
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 + money2


def test_same_currency_should_be_subtractable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.00"), "BRL")
    assert money1 - money2 == Money(Decimal("5.00"), "BRL")


def test_different_currency_should_not_be_subtractable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.00"), "USD")
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 - money2


def test_should_be_negatable() -> None:
    money = Money(Decimal("10.00"), "BRL")
    assert -money == Money(Decimal("-10.00"), "BRL")
    negated = -money
    assert -negated == money
    assert -Money.zero() == Money.zero()


def test_different_type_should_not_be_summable_or_subtractable() -> None:
    money = Money(Decimal("10.00"), "BRL")
    an_object = 42
    with pytest.raises(TypeError):
        _ = money + an_object  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        _ = an_object + money  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        _ = money - an_object  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        _ = an_object - money  # ty: ignore[unsupported-operator]


@pytest.mark.parametrize(
    ("scalar", "expected"),
    [
        (2, Decimal("20.00")),
        (Decimal("0.5"), Decimal("5.00")),
        (Decimal("1.5"), Decimal("15.00")),
    ],
)
def test_should_be_able_to_multiply_money_by_scalar(
    scalar: Scalar, expected: Decimal
) -> None:
    assert Money(Decimal("10.00"), "BRL") * scalar == Money(expected, "BRL")
    assert scalar * Money(Decimal("10.00"), "BRL") == Money(expected, "BRL")


@pytest.mark.parametrize(
    ("scalar", "expected"),
    [
        (2, Decimal("5.00")),
        (Decimal("0.5"), Decimal("20.00")),
        (Decimal("1.5"), Decimal("6.67")),
    ],
)
def test_should_be_able_to_divide_money_by_scalar(
    scalar: Scalar, expected: Decimal
) -> None:
    assert Money(Decimal("10.00"), "BRL") / scalar == Money(expected, "BRL")


def test_should_reject_float_scalars() -> None:
    money = Money(Decimal("10.00"), "BRL")

    with pytest.raises(TypeError):
        _ = money * 0.5  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        _ = 0.5 * money  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError):
        _ = money / 0.5  # ty: ignore[unsupported-operator]


def test_same_currency_should_be_comparable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.00"), "BRL")
    money3 = Money(Decimal("10.00"), "BRL")

    assert money1 > money2
    assert money1 >= money2
    assert money2 < money1
    assert money2 <= money1
    assert money1 == money3
    assert money1 != money2


def test_different_currency_should_not_be_comparable() -> None:
    money1 = Money(Decimal("10.00"), "BRL")
    money2 = Money(Decimal("5.00"), "USD")
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 > money2
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 < money2
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 >= money2
    with pytest.raises(TypeError, match="Different currencies"):
        _ = money1 <= money2


def test_different_type_should_not_be_comparable() -> None:
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


def test_zero_returns_correct_amount() -> None:
    zero_money = Money.zero()

    assert zero_money.amount == Decimal("0.00")


def test_zero_retains_default_currency() -> None:
    zero_money = Money.zero()

    assert zero_money.currency == DEFAULT_CURRENCY


def test_money_zero_accepts_custom_currency() -> None:
    custom_currency = "USD"

    zero_usd = Money.zero(currency=custom_currency)

    assert zero_usd.amount == Decimal("0.00")
    assert zero_usd.currency == custom_currency
