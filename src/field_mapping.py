"""
field_mapping.py

Maps validated ERP records to the eCommerce API payload shape.
"""

from validators import InventoryRecord, OrderRecord

STATUS_MAP = {
    "NEW": "pending", "PROCESSING": "processing", "SHIPPED": "shipped",
    "DELIVERED": "completed", "CANCELLED": "cancelled", "RETURNED": "refunded",
}


def map_order(o: OrderRecord) -> dict:
    return {
        "external_id": o.order_id,
        "customer": {"external_id": f"ERP-{o.customer_id}"},
        "line_items": [{"sku": o.sku, "quantity": o.quantity,
                        "price": {"amount": f"{o.unit_price:.2f}", "currency": o.currency}}],
        "order_status": STATUS_MAP[o.status_code],
        "created_at": o.order_date.isoformat(),
    }


def map_inventory(i: InventoryRecord) -> dict:
    return {
        "sku": i.sku,
        "location_id": i.warehouse_id,
        "inventory": {"quantity": i.available},
        "updated_at": i.last_updated.isoformat(),
    }
