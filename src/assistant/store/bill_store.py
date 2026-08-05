from src.assistant.models.bill import Bill

class BillStore:
    def __init__(self):
        # Dictionary keyed by bill.id
        self.bills = {}

    def add_bill(self, bill: Bill):
        """Store a new Bill object."""
        self.bills[bill.id] = bill

    def get_bill(self, bill_id: str) -> Bill | None:
        """Retrieve a Bill by its UUID."""
        return self.bills.get(bill_id)

    def list_bills(self) -> list[Bill]:
        """Return all stored bills."""
        return list(self.bills.values())

    def update_bill(self, bill_id: str, **updates):
        """Update fields on an existing Bill."""
        bill = self.bills.get(bill_id)
        if not bill:
            return None

        for field, value in updates.items():
            if hasattr(bill, field):
                setattr(bill, field, value)

        return bill

    def delete_bill(self, bill_id: str) -> bool:
        """Remove a bill from the store."""
        if bill_id in self.bills:
            del self.bills[bill_id]
            return True
        return False

# Shared instance used by all tools
bill_store = BillStore()
