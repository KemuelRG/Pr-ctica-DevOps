import pytest
from datetime import date, timedelta

from core.expense import Expense
from core.domain_error import (
    EmptyTitleError,
    InvalidAmountError,
    InvalidExpenseDateError,
)


def test_create_valid_expense():
    expense = Expense(
        id=1,
        title="Comida",
        amount=10.5,
        description="Almuerzo",
        expense_date=date.today(),
    )

    assert expense.title == "Comida"
    assert expense.amount == 10.5


def test_empty_title_raises_error():
    with pytest.raises(EmptyTitleError):
        Expense(id=1, title="", amount=10, description="", expense_date=date.today())


def test_negative_amount_raises_error():
    """
    Prueba que crear un objeto Expense con un valor negativo en el campo 'amount' (por ejemplo, -5)
    genera la excepción específica InvalidAmountError definida en domain_error.py.
    """
    with pytest.raises(InvalidAmountError):
        Expense(
            id=2,
            title="Transporte",
            amount=-5.0,
            description="Bus",
            expense_date=date.today(),
        )


def test_future_date_raises_error():
    """
    Prueba que al intentar crear un objeto Expense con un campo 'expense_date' posterior a la fecha actual
    (por ejemplo, usando date.today() + timedelta(days=1)), se lanza la excepción InvalidExpenseDateError
    definida en domain_error.py.
    """
    future_date = date.today() + timedelta(days=1)

    with pytest.raises(InvalidExpenseDateError):
        Expense(
            id=3,
            title="Suscripción",
            amount=15.0,
            description="Streaming",
            expense_date=future_date,
        )
