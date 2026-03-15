from datetime import date

from core.expense_service import ExpenseService
from core.in_memory_expense_repository import InMemoryExpenseRepository
from core.no_tocar.sqlite_expense_repository import SQLiteExpenseRepository


def create_service():
    repo = SQLiteExpenseRepository()
    repo.empty()
    return ExpenseService(repo)


def test_create_and_list_expenses():
    service = create_service()

    service.create_expense(
        title="Comida", amount=10, description="", expense_date=date.today()
    )

    expenses = service.list_expenses()

    assert len(expenses) == 1
    assert expenses[0].title == "Comida"


def test_remove_expense():
    service = create_service()

    service.create_expense("A", 5, "", date.today())
    service.create_expense("B", 7, "", date.today())

    service.remove_expense(1)

    expenses = service.list_expenses()
    assert len(expenses) == 1
    assert expenses[0].title == "B"


def test_update_expense():
    service = create_service()

    service.create_expense("Café", 2, "", date.today())

    service.update_expense(expense_id=1, title="Café grande", amount=3)

    expense = service.list_expenses()[0]
    assert expense.title == "Café grande"
    assert expense.amount == 3


def test_update_non_existing_expense_does_nothing():
    service = create_service()

    service.update_expense(expense_id=999, title="Nada")

    assert service.list_expenses() == []


def test_total_amount():
    service = create_service()

    service.create_expense("A", 10, "", date.today())
    service.create_expense("B", 5, "", date.today())

    assert service.total_amount() == 15


def test_total_by_month():
    service = create_service()

    service.create_expense("Enero 1", 10, "", date(2025, 1, 10))
    service.create_expense("Enero 2", 5, "", date(2025, 1, 20))
    service.create_expense("Febrero", 7, "", date(2025, 2, 1))

    totals = service.total_by_month()

    assert totals["2025-01"] == 15
    assert totals["2025-02"] == 7


def test_create_multiple_expenses_and_list():
    """
    Verifica que el servicio permite crear múltiples gastos y que estos se almacenan y recuperan correctamente mediante el método list_expenses.
    """
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)

    # Se agregan dos gastos distintos
    service.create_expense(title="Pan", amount=3.0, description="Mercado")
    service.create_expense(title="Leche", amount=4.0, description="Supermercado")

    # Se obtiene el listado
    expenses = service.list_expenses()

    # Comprobaciones
    assert len(expenses) == 2, "Debe haber exactamente dos gastos en el sistema"

    titles = [expense.title for expense in expenses]
    assert "Pan" in titles, "El título 'Pan' debe estar en la lista"
    assert "Leche" in titles, "El título 'Leche' debe estar en la lista"


def test_remove_expense_reduces_total():
    """
    Evalúa el comportamiento del sistema al eliminar un gasto existente.
    """
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)

    # Se generan dos gastos
    e1 = service.create_expense(title="Libro", amount=20.0, description="Lectura")
    service.create_expense(title="Revista", amount=5.0, description="Kiosco")

    # Se elimina el primero
    service.remove_expense(e1.id)

    # Se recupera la lista actualizada
    expenses = service.list_expenses()

    # Comprobaciones
    assert len(expenses) == 1, "Solo debe quedar un gasto en el sistema"
    assert expenses[0].title == "Revista", "El gasto restante debe ser 'Revista'"


def test_update_expense_partial_fields():
    """
    Comprueba que al actualizar parcialmente un gasto solo cambian los campos especificados y el resto permanece igual.
    """
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)

    # Se crea el gasto base
    expense = service.create_expense(title="Camiseta", amount=15.0, description="Ropa")

    # Se actualiza solo el monto
    service.update_expense(expense_id=expense.id, amount=18.0)

    # Se recupera el gasto actualizado
    updated_expense = repo.get_by_id(expense.id)

    # Comprobaciones
    assert updated_expense is not None
    assert updated_expense.title == "Camiseta", "El título no debió cambiar"
    assert updated_expense.amount == 18.0, "El monto debió actualizarse a 18.0"
    assert updated_expense.description == "Ropa", "La descripción no debió cambiar"


def test_total_amount_after_removal():
    """
    Verifica que el cálculo del total gastado se actualiza correctamente después de eliminar un gasto.
    """
    repo = InMemoryExpenseRepository()
    service = ExpenseService(repo)

    # Se crean dos gastos
    e1 = service.create_expense(title="Cursos", amount=30.0)
    service.create_expense(title="Internet", amount=25.0)

    # Se comprueba la suma inicial
    assert service.total_amount() == 55.0, "La suma inicial debe ser 55.0"

    # Se elimina el gasto de "Cursos" (suponiendo que es el primer elemento)
    service.remove_expense(e1.id)

    # Se recalcula y comprueba el total
    assert service.total_amount() == 25.0, "La suma tras eliminar debe ser 25.0"
