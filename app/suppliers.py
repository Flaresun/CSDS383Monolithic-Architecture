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
    cur = conn.cursor()
    linked = cur.execute(
        "SELECT 1 FROM product_suppliers WHERE supplier_id = ? LIMIT 1",
        (supplier_id,),
    ).fetchone()
    if linked is None:
        cur.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))

# Public API (CRUD) 
def create_supplier(
    conn: sqlite3.Connection,
    supplier_name: str,
    supplier_contact: str,
    supplier_id: Optional[str] = None,
) -> str:
    if not supplier_name or len(supplier_name) > 2000:
        raise ValueError("supplier_name is required and must be ≤ 2000 chars")
    _require_email(supplier_contact)
    sid = supplier_id or str(uuid.uuid4())
    _require_uuid(sid, "supplier_id")
    with conn:
        conn.execute(
            "INSERT INTO suppliers(id, name, contact_email) VALUES (?, ?, ?)",
            (sid, supplier_name, supplier_contact),
        )
    return sid

def read_supplier(conn: sqlite3.Connection, supplier_id: str) -> Supplier:
    _require_uuid(supplier_id, "supplier_id")
    return _fetch_supplier(conn.cursor(), supplier_id)

def list_suppliers(conn: sqlite3.Connection) -> Iterable[Supplier]:
    cur = conn.cursor()
    ids = cur.execute("SELECT id FROM suppliers ORDER BY name").fetchall()
    for (sid,) in ids:
        yield _fetch_supplier(cur, sid)

def update_supplier(
    conn: sqlite3.Connection,
    supplier_id: str,
    supplier_name: Optional[str] = None,
    supplier_contact: Optional[str] = None,
) -> None:
    _require_uuid(supplier_id, "supplier_id")
    sets: List[str] = []
    args: List[str] = []
    if supplier_name is not None:
        if not supplier_name or len(supplier_name) > 2000:
            raise ValueError("supplier_name must be 1..2000 chars")
        sets.append("name = ?")
        args.append(supplier_name)
    if supplier_contact is not None:
        _require_email(supplier_contact)
        sets.append("contact_email = ?")
        args.append(supplier_contact)
    if not sets:
        return
    args.append(supplier_id)
    with conn:
        cur = conn.execute(f"UPDATE suppliers SET {', '.join(sets)} WHERE id = ?", args)
        if cur.rowcount == 0:
            raise KeyError(f"Supplier {supplier_id} not found")

def delete_supplier(conn: sqlite3.Connection, supplier_id: str) -> None:
    _require_uuid(supplier_id, "supplier_id")
    with conn:
        cur = conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        if cur.rowcount == 0:
            raise KeyError(f"Supplier {supplier_id} not found")
            
# Link management (bidirectional) 
def add_product_to_supplier(
    conn: sqlite3.Connection, supplier_id: str, product_id: str
) -> None:
    _require_uuid(supplier_id, "supplier_id")
    _require_uuid(product_id, "product_id")
    with conn:
        cur = conn.cursor()
        if not _supplier_exists(cur, supplier_id):
            raise KeyError(f"Supplier {supplier_id} not found")
        if not _product_exists(cur, product_id):
            raise KeyError(f"Product {product_id} not found")
        cur.execute(
            "INSERT OR IGNORE INTO product_suppliers(product_id, supplier_id) VALUES (?, ?)",
            (product_id, supplier_id),
        )

def remove_product_from_supplier(
    conn: sqlite3.Connection, supplier_id: str, product_id: str, *,
    delete_supplier_if_unused: bool = True
) -> None:
    _require_uuid(supplier_id, "supplier_id")
    _require_uuid(product_id, "product_id")
    with conn:
        conn.execute(
            "DELETE FROM product_suppliers WHERE product_id = ? AND supplier_id = ?",
            (product_id, supplier_id),
        )
        if delete_supplier_if_unused:
            _delete_supplier_if_unused(conn, supplier_id)
