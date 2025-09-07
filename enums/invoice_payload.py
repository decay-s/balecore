from enum import Enum

class InvoicePayload(str, Enum):
    FLEXIBLE = "flexible"
    FIXED = "fixed"