"""
run_validation.py

Runs the validation checkpoints on ERP extract files and writes:
  - rejected rows with reasons (for business review)
  - mapped payloads ready for the eCommerce API
  - a reconciliation summary

Usage:
    python src/run_validation.py --orders examples/erp_orders.csv --inventory examples/erp_inventory.csv --out examples/output
"""

import argparse
import csv
import json
from pathlib import Path

from field_mapping import map_inventory, map_order
from validators import InventoryRecord, OrderRecord, find_duplicates, reconcile, validate_batch


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{k: (v if v != "" else None) for k, v in row.items()} for row in csv.DictReader(f)]


def write_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def process(rows, model, key_fields, mapper, name, out: Path):
    dupes = find_duplicates(tuple(r[k] for k in key_fields) for r in rows)
    unique, dup_rows = [], []
    for r in rows:
        if tuple(r[k] for k in key_fields) in dupes:
            dup_rows.append({**r, "validation_error": "duplicate key in batch"})
        else:
            unique.append(r)
    valid, rejected = validate_batch(unique, model)
    rejected = dup_rows + rejected
    payloads = [mapper(v) for v in valid]
    write_csv(rejected, out / f"{name}_rejected.csv")
    (out / f"{name}_payloads.json").write_text(json.dumps(payloads, indent=2))
    # In production target_count comes from the API response; here it is the mapped count.
    summary = {"dataset": name, "rows_in": len(rows), "valid": len(valid), "rejected": len(rejected),
               **reconcile(len(valid), len(payloads))}
    return summary, rejected


def main():
    p = argparse.ArgumentParser(description="ERP to eCommerce validation checkpoints")
    p.add_argument("--orders", required=True)
    p.add_argument("--inventory", required=True)
    p.add_argument("--out", default="examples/output")
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    results = [
        process(read_csv(args.orders), OrderRecord, ("order_id", "sku"), map_order, "orders", out),
        process(read_csv(args.inventory), InventoryRecord, ("sku", "warehouse_id"), map_inventory, "inventory", out),
    ]
    summaries = [s for s, _ in results]
    write_csv(summaries, out / "reconciliation_summary.csv")

    for s, rejected in results:
        print(f"\n{s['dataset'].upper()}: {s['rows_in']} in, {s['valid']} valid, {s['rejected']} rejected")
        for r in rejected:
            key = r.get("order_id") or f"{r.get('sku')}@{r.get('warehouse_id')}"
            print(f"  {key}: {r['validation_error']}")


if __name__ == "__main__":
    main()
