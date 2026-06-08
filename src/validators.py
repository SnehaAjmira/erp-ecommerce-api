"""
validators.py
-------------
Data validation checkpoints for ERP-to-eCommerce integration.
  Ensures 95%+ data accuracy before syncing records to eCommerce platform.
  """

  from pydantic import BaseModel, validator, Field
    from typing import Optional
      from datetime import datetime
        from decimal import Decimal


          class OrderRecord(BaseModel):
                """Pydantic model for ERP order records."""
            order_id: str = Field(..., min_length=1, max_length=50)
            customer_id: str = Field(..., min_length=1)
            sku: str = Field(..., min_length=1)
            quantity: int = Field(..., ge=0)
            unit_price: Decimal = Field(..., gt=0)
                order_date: datetime
                status_code: str
            currency: str = Field(default="USD", max_length=3)

            @validator("status_code")
            def validate_status(cls, v):
            valid_statuses = {"NEW", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"}
            if v.upper() not in valid_statuses:
              raise ValueError(f"Invalid status code '{v}'. Must be one of: {valid_statuses}")
              return v.upper()

              @validator("currency")
              def validate_currency(cls, v):
              valid_currencies = {"USD", "EUR", "GBP", "CAD"}
              if v.upper() not in valid_currencies:
                raise ValueError(f"Unsupported currency: {v}")
                return v.upper()


                class InventoryRecord(BaseModel):
                      """Pydantic model for ERP inventory records."""
                  sku: str = Field(..., min_length=1)
                      warehouse_id: str
                  quantity_on_hand: int = Field(..., ge=0)
                  quantity_reserved: int = Field(..., ge=0)
                  reorder_point: Optional[int] = Field(default=None, ge=0)
                      last_updated: datetime

                  @validator("quantity_reserved")
                  def reserved_not_exceed_on_hand(cls, v, values):
                  if "quantity_on_hand" in values and v > values["quantity_on_hand"]:
                    raise ValueError("Reserved quantity cannot exceed on-hand quantity")
                            return v


                    def validate_order_batch(records: list[dict]) -> tuple[list[OrderRecord], list[dict]]:
                        """
                        Validates a batch of order records.

                        Returns:
                    Tuple of (valid_records, error_records) where error_records
                            contain the original dict plus a 'validation_error' key.
                        """
                    valid, errors = [], []
                        for record in records:
                                  try:
                          valid.append(OrderRecord(**record))
                                  except Exception as e:
                          errors.append({**record, "validation_error": str(e)})
                              return valid, errors


                          def validate_inventory_batch(records: list[dict]) -> tuple[list[InventoryRecord], list[dict]]:
                              """Validates a batch of inventory records."""
                          valid, errors = [], []
                              for record in records:
                                        try:
                                valid.append(InventoryRecord(**record))
                                        except Exception as e:
                                errors.append({**record, "validation_error": str(e)})
                                    return valid, errors


                                def check_duplicate(record_id: str, existing_ids: set) -> bool:
                                    """Returns True if a record already exists in the target system."""
                                    return record_id in existing_ids


                                def reconcile_batch(source_count: int, target_count: int, tolerance: float = 0.05) -> bool:
                                    """
                                    Post-sync reconciliation check.
                                Returns True if sync is within acceptable tolerance (default 5%).
                                      """
                                      if source_count == 0:
                                                return target_count == 0
                                            accuracy = target_count / source_count
                                        return accuracy >= (1 - tolerance)
