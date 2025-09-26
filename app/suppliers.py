from __future__ import annotations
import re, sqlite3, uuid
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

# ---------------- Validation ----------------
UUID_RX = re.compile(
    r'^[0-9a-fA-F]{8}-'
    r'[0-9a-fA-F]{4}-'
    r'[1-5][0-9a-fA-F]{3}-'
    r'[89abAB][0-9a-fA-F]{3}-'
    r'[0-9a-fA-F]{12}$'
)
EMAIL_RX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def _is_uuid(x: str) -> bool:
    return bool(UUID_RX.fullmatch(x or ""))

def _require_uuid(x: str, label: str = "id") -> None:
    if not _is_uuid(x):
        raise ValueError(f"{label} must be a UUID string")

def _require_email(x: str) -> None:
    if not EMAIL_RX.fullmatch(x or ""):
        raise ValueError("supplier_contact must be a valid email address")

class Supplier:
    def __init__(self, supplier_id, supplier_name, supplier_contact, product_ids=None):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.supplier_contact = supplier_contact
        self.product_ids = product_ids or []

        def add_product(self, product_id):
            self.product_ids.append(product_id)

        def remove_product(self, product_id):
            self.product_ids.remove(product_id)    
