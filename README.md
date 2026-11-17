# ERP-to-eCommerce Integration: Data Validation Layer

The validation and mapping layer for an ERP-to-eCommerce order and inventory sync. It checks every record against schema and business rules, quarantines failures with a reason, maps valid records to the target API format, and reconciles counts after each batch.

| | |
|---|---|
| **Domain** | Systems integration, order management, inventory |
| **Tools** | Python 3, pydantic v2 |
| **Techniques** | Schema validation, business rule checks, duplicate detection, field mapping, post-sync reconciliation |
| **Contents** | 3 modules, sample ERP extracts, generated outputs, unit tests |

---

## 1. Data Flow

```
ERP extract (CSV)
    -> 1. Duplicate key check (order_id + sku, sku + warehouse_id)
    -> 2. Schema and business rules (pydantic models)
    -> 3a. Rejected rows + reason  -> *_rejected.csv   (business review)
    -> 3b. Valid rows -> field mapping -> *_payloads.json (eCommerce API)
    -> 4. Reconciliation (source vs target counts) -> reconciliation_summary.csv
```

## 2. Validation Rules

| Dataset | Rule |
|---|---|
| Orders | `order_id`, `customer_id`, `sku` required |
| Orders | `quantity` greater than 0; `unit_price` greater than 0, 2 decimals |
| Orders | `status_code` in NEW, PROCESSING, SHIPPED, DELIVERED, CANCELLED, RETURNED (case-insensitive) |
| Orders | `currency` in USD, EUR, GBP, CAD; `order_date` must be a valid datetime |
| Inventory | `quantity_on_hand` and `quantity_reserved` not negative |
| Inventory | `quantity_reserved` cannot exceed `quantity_on_hand` |
| Both | No duplicate business keys within a batch |

## 3. Field Mapping

| ERP field | eCommerce field | Transformation |
|---|---|---|
| `order_id` | `external_id` | Direct |
| `customer_id` | `customer.external_id` | Prefix `ERP-` |
| `unit_price`, `currency` | `line_items[].price` | 2 decimals, upper-case currency |
| `status_code` | `order_status` | Lookup table (for example DELIVERED to completed) |
| `order_date` | `created_at` | ISO 8601 |
| `quantity_on_hand - quantity_reserved` | `inventory.quantity` | Available-to-sell calculation |

## 4. Example Run

Input: `examples/erp_orders.csv` (12 rows) and `examples/erp_inventory.csv` (6 rows), seeded with common ERP data defects.

| Dataset | Rows in | Valid | Rejected | Reasons |
|---|---:|---:|---:|---|
| Orders | 12 | 4 | 8 | Duplicate key (2), zero quantity, negative price, missing customer, unknown status, unsupported currency, invalid date |
| Inventory | 6 | 4 | 2 | Reserved exceeds on hand, negative on hand |

All outputs are in `examples/output/`.

## 5. How to Run

```bash
pip install -r requirements.txt
python src/run_validation.py --orders examples/erp_orders.csv --inventory examples/erp_inventory.csv --out examples/output
python -m unittest discover -s tests -v
```

## 6. Repository Structure

```
erp-ecommerce-api/
├── src/
│   ├── validators.py        # pydantic models, batch validation, duplicates, reconciliation
│   ├── field_mapping.py     # ERP to eCommerce payload mapping
│   └── run_validation.py    # CLI: validate, map, quarantine, reconcile
├── examples/
│   ├── erp_orders.csv
│   ├── erp_inventory.csv
│   └── output/
├── tests/test_validators.py
└── requirements.txt
```

## 7. Scope

This repository contains the validation and mapping layer only. API clients, scheduling, and retry logic depend on the specific ERP and eCommerce platforms and are not included.

Author: [Sneha Ajmira](https://linkedin.com/in/contactsnehaajmira)
