import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from field_mapping import map_order  # noqa: E402
from validators import InventoryRecord, OrderRecord, find_duplicates, reconcile, validate_batch  # noqa: E402

ORDER = {"order_id": "SO-1", "customer_id": "C-1", "sku": "A", "quantity": 2, "unit_price": "10.00",
         "order_date": "2026-02-03T09:15:00", "status_code": "new", "currency": "usd"}


class TestOrders(unittest.TestCase):
    def test_valid_order_normalized(self):
        o = OrderRecord(**ORDER)
        self.assertEqual((o.status_code, o.currency), ("NEW", "USD"))

    def test_rejections(self):
        bad = [{**ORDER, "quantity": 0}, {**ORDER, "unit_price": "-1"}, {**ORDER, "status_code": "X"},
               {**ORDER, "currency": "JPY"}, {**ORDER, "customer_id": ""}]
        valid, rejected = validate_batch(bad, OrderRecord)
        self.assertEqual((len(valid), len(rejected)), (0, 5))
        self.assertTrue(all("validation_error" in r for r in rejected))

    def test_mapping(self):
        payload = map_order(OrderRecord(**ORDER))
        self.assertEqual(payload["order_status"], "pending")
        self.assertEqual(payload["customer"]["external_id"], "ERP-C-1")


class TestInventory(unittest.TestCase):
    def test_reserved_exceeds_on_hand(self):
        row = {"sku": "A", "warehouse_id": "W", "quantity_on_hand": 5, "quantity_reserved": 6,
               "last_updated": "2026-02-05T06:00:00"}
        _, rejected = validate_batch([row], InventoryRecord)
        self.assertIn("exceeds", rejected[0]["validation_error"])


class TestChecks(unittest.TestCase):
    def test_duplicates(self):
        self.assertEqual(find_duplicates([("a",), ("b",), ("a",)]), {("a",)})

    def test_reconcile(self):
        self.assertTrue(reconcile(100, 100)["passed"])
        self.assertFalse(reconcile(100, 97)["passed"])
        self.assertTrue(reconcile(100, 97, tolerance=0.05)["passed"])


if __name__ == "__main__":
    unittest.main()
