from src.assistant.models.bill import Bill
from src.assistant.store.bill_store import bill_store

def add_bill_tool(
    name: str,
    amount: float,
    due_date: str,
    category: str,
    pay_type: str,
    notes: str | None = None
):
    """
    Create a new Bill object and store it in the BillStore.
    """

    # Create the Bill object
    bill = Bill(
        name=name,
        amount=amount,
        due_date=due_date,
        category=category,
        pay_type=pay_type,
        notes=notes
    )

    # Store it
    bill_store.add_bill(bill)

    # Return confirmation
    return {
        "message": f"Bill '{bill.name}' added successfully.",
        "id": bill.id,
        "alias": bill.alias
    }
