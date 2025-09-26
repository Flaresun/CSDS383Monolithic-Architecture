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
    supplier_id: str
    supplier_name: str
    supplier_contact: str
    product_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "supplier_contact": self.supplier_contact,
            "product_ids": list(self.product_ids),
        }

# Internal helpers 
def _supplier_exists(cur: sqlite3.Cursor, supplier_id: str) -> bool:
    return cur.execute(
        "SELECT 1 FROM suppliers WHERE id = ? LIMIT 1", (supplier_id,)
    ).fetchone() is not None

def _product_exists(cur: sqlite3.Cursor, product_id: str) -> bool:
    return cur.execute(
        "SELECT 1 FROM products WHERE id = ? LIMIT 1", (product_id,)
    ).fetchone() is not None

def _fetch_supplier(cur: sqlite3.Cursor, supplier_id: str) -> Supplier:
    row = cur.execute(
        "SELECT id, name, contact_email FROM suppliers WHERE id = ?",
        (supplier_id,),
    ).fetchone()
    if not row:
        raise KeyError(f"Supplier {supplier_id} not found")

    sid, name, email = row
    prod_ids = [
        r[0]
        for r in cur.execute(
            "SELECT product_id FROM product_suppliers WHERE supplier_id = ?",
            (supplier_id,),
        ).fetchall()
    ]
    return Supplier(
        supplier_id=sid,
        supplier_name=name,
        supplier_contact=email,
        product_ids=prod_ids,
    )

def _delete_supplier_if_unused(conn: sqlite3.Connection, supplier_id: str) -> None:
    """Optional 'no orphan suppliers' cleanup after unlink."""
    cur = conn.cursor()
    linked = cur.execute(
        "SELECT 1 FROM product_suppliers WHERE supplier_id = ? LIMIT 1",
        (supplier_id,),
    ).fetchone()
    if linked is None:
        cur.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
