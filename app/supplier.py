from __future__ import annotations
import re, sqlite3, uuid, json
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

# Validation 
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

def _load_json_list(s: Optional[str]) -> List[str]:
    if not s:
        return []
    try:
        v = json.loads(s)
        return v if isinstance(v, list) else []
    except json.JSONDecodeError:
        return []

def _dump_json_list(lst: List[str]) -> str:
    return json.dumps(lst, separators=(",", ":"))

@dataclass
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
        "SELECT 1 FROM Suppliers WHERE Supplier_Id = ? LIMIT 1", (supplier_id,)
    ).fetchone() is not None

def _product_exists(cur: sqlite3.Cursor, product_id: str) -> bool:
    return cur.execute(
        "SELECT 1 FROM Products WHERE Product_Id = ? LIMIT 1", (product_id,)
    ).fetchone() is not None

def _fetch_supplier(cur: sqlite3.Cursor, supplier_id: str) -> Supplier:
    row = cur.execute(
        "SELECT Supplier_Id, Supplier_Name, Supplier_Contact, Product_Ids FROM Suppliers WHERE Supplier_Id = ?",
        (supplier_id,),
    ).fetchone()
    if not row:
        raise KeyError(f"Supplier {supplier_id} not found")

    sid, name, email, prod_json = row
    return Supplier(
        supplier_id=sid,
        supplier_name=name,
        supplier_contact=email,
        product_ids=_load_json_list(prod_json),
    )

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
            "INSERT INTO Suppliers (Supplier_Id, Supplier_Name, Supplier_Contact, Product_Ids) VALUES (?, ?, ?, ?)",
            (sid, supplier_name, supplier_contact, "[]"),
        )
    return sid

def read_supplier(conn: sqlite3.Connection, supplier_id: str) -> Supplier:
    _require_uuid(supplier_id, "supplier_id")
    return _fetch_supplier(conn.cursor(), supplier_id)

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
        sets.append("Supplier_Name = ?")
        args.append(supplier_name)
    if supplier_contact is not None:
        _require_email(supplier_contact)
        sets.append("Supplier_Contact = ?")
        args.append(supplier_contact)
    if not sets:
        return
    args.append(supplier_id)
    with conn:
        cur = conn.execute(f"UPDATE Suppliers SET {', '.join(sets)} WHERE Supplier_Id = ?", args)
        if cur.rowcount == 0:
            raise KeyError(f"Supplier {supplier_id} not found")

def delete_supplier(conn: sqlite3.Connection, supplier_id: str) -> None:
    _require_uuid(supplier_id, "supplier_id")
    cur = conn.cursor()
    row = cur.execute(
        "SELECT Product_Ids FROM Suppliers WHERE Supplier_Id = ?", (supplier_id,)
    ).fetchone()
    if not row:
        raise KeyError(f"Supplier {supplier_id} not found")
    product_ids = _load_json_list(row[0])
    with conn:
        for pid in product_ids:
            prow = cur.execute(
                "SELECT Supplier_Ids FROM Products WHERE Product_Id = ?", (pid,)
            ).fetchone()
            if not prow:
                continue
            sup_ids = _load_json_list(prow[0])
            if supplier_id in sup_ids:
                sup_ids.remove(supplier_id)
                conn.execute(
                    "UPDATE Products SET Supplier_Ids = ? WHERE Product_Id = ?",
                    (_dump_json_list(sup_ids), pid),
                )
        cur = conn.execute("DELETE FROM Suppliers WHERE Supplier_Id = ?", (supplier_id,))
        if cur.rowcount == 0:
            raise KeyError(f"Supplier {supplier_id} not found")

# Link management (bidirectional via JSON lists) 
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

        s_row = cur.execute(
            "SELECT Product_Ids FROM Suppliers WHERE Supplier_Id = ?", (supplier_id,)
        ).fetchone()
        p_row = cur.execute(
            "SELECT Supplier_Ids FROM Products WHERE Product_Id = ?", (product_id,)
        ).fetchone()

        s_products = _load_json_list(s_row[0]) if s_row else []
        p_suppliers = _load_json_list(p_row[0]) if p_row else []

        changed = False
        if product_id not in s_products:
            s_products.append(product_id)
            changed = True
        if supplier_id not in p_suppliers:
            p_suppliers.append(supplier_id)
            changed = True

        if not changed:
            return

        conn.execute(
            "UPDATE Suppliers SET Product_Ids = ? WHERE Supplier_Id = ?",
            (_dump_json_list(s_products), supplier_id),
        )
        conn.execute(
            "UPDATE Products SET Supplier_Ids = ? WHERE Product_Id = ?",
            (_dump_json_list(p_suppliers), product_id),
        )

def remove_product_from_supplier(
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

        s_row = cur.execute(
            "SELECT Product_Ids FROM Suppliers WHERE Supplier_Id = ?", (supplier_id,)
        ).fetchone()
        p_row = cur.execute(
            "SELECT Supplier_Ids FROM Products WHERE Product_Id = ?", (product_id,)
        ).fetchone()

        s_products = _load_json_list(s_row[0]) if s_row else []
        p_suppliers = _load_json_list(p_row[0]) if p_row else []

        changed = False
        if product_id in s_products:
            s_products.remove(product_id)
            changed = True
        if supplier_id in p_suppliers:
            p_suppliers.remove(supplier_id)
            changed = True

        if not changed:
            return

        conn.execute(
            "UPDATE Suppliers SET Product_Ids = ? WHERE Supplier_Id = ?",
            (_dump_json_list(s_products), supplier_id),
        )
        conn.execute(
            "UPDATE Products SET Supplier_Ids = ? WHERE Product_Id = ?",
            (_dump_json_list(p_suppliers), product_id),
        )
