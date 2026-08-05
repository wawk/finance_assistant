from pydantic import BaseModel, computed_field
from datetime import date
from typing import Optional, ClassVar
from enum import Enum

class Category(Enum):
    FOOD = 'food'
    UTILITIES = 'utilities'
    AUTO = 'auto'
    INSURANCE = 'insurance'
    MEDICAL = 'medical'
    PERSCRIPTIONS = 'perscriptions'
    HOME = 'home'
    ENTERTAINMENT = 'enteretainment'
    HOBBIES = 'hobbies'
    SUBSCRIPTIONS = 'subscriptions'
    OTHER = 'other'

class PayType(Enum):
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    SEASONAL = 'seasonal'
    ONETIME = 'onetime'

class Bill(BaseModel):
    identity_provider: ClassVar[callable] = None

    def __init__(self, **data):
        bill_id = None
        alias = None

        if Bill.identity_provider is not None:
            bill_id, alias = Bill.identity_provider()
            data.setdefault("id", bill_id)
            data.setdefault("alias", alias)

        super().__init__(**data)


    id: str | None = None
    alias: str | None = None
    name: str | None = None
    amount: float | None = None
    amount_paid: float | None = None
    due_date: date | None = None
    paid_date: date | None = None
    paid: bool = False
    auto_pay: bool = False
    pay_type: PayType | None = None
    account_id: str | None = None
    category: Category | None = None
    notes: str | None = None

    @computed_field
    @property
    def remaining_balance(self) -> float:
        return self.amount or 0.0  - (self.amount_paid or 0.0)

    model_config = {
        "validate_assignment": True
    }