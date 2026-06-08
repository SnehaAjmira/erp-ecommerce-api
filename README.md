# ERP-to-eCommerce API Integration

> Bidirectional ERP and eCommerce platform integration achieving 95% data accuracy across order and inventory datasets — built at Apex Supply Company.
>
> ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python) ![REST API](https://img.shields.io/badge/REST-API-orange) ![SQL](https://img.shields.io/badge/SQL-Server-red) ![Status](https://img.shields.io/badge/status-complete-green)
>
> ---
>
> ## 📌 Project Overview
>
> This integration synchronizes order and inventory data between a legacy ERP system and a modern eCommerce platform. It replaced a manual, error-prone data entry process that caused order fulfillment delays and inventory discrepancies. The solution uses REST APIs with robust error handling, data validation checkpoints, and UAT documentation.
>
> **Key outcomes:**
> - 95% accuracy across order and inventory datasets
> - - Eliminated ~20 hours/week of manual data entry
>   - - Enabled real-time inventory visibility on the eCommerce platform
>     - - Delivered end-user training documentation for business and technical stakeholders
>      
>       - ---
>
> ## 🏗️ Integration Architecture
>
> ```
> ERP System (Source of Truth)
>     │
>     ├── Order Events (new, updated, cancelled)
>     ├── Inventory Updates (stock levels, adjustments)
>     │
>     ▼
> Integration Middleware (Python)
>     ├── Data Validation Checkpoints
>     ├── Error Handling & Retry Logic
>     ├── Field Mapping & Transformation
>     │
>     ▼
> eCommerce Platform API (Target)
>     ├── Product/Inventory API
>     └── Order Management API
> ```
>
> ---
>
> ## 📁 Project Structure
>
> ```
> erp-ecommerce-api/
> ├── src/
> │   ├── erp_client.py           # ERP system API client
> │   ├── ecommerce_client.py     # eCommerce platform API client
> │   ├── sync_engine.py          # Core synchronization logic
> │   ├── validators.py           # Data validation checkpoints
> │   └── error_handler.py        # Retry logic and error logging
> ├── tests/
> │   ├── test_sync_engine.py
> │   └── test_validators.py
> ├── docs/
> │   ├── data_mapping.md         # ERP to eCommerce field mappings
> │   ├── uat_test_cases.md       # UAT test plan and results
> │   └── training_guide.md       # End-user training documentation
> ├── config/
> │   └── settings.yaml           # Integration configuration
> ├── requirements.txt
> └── README.md
> ```
>
> ---
>
> ## 🔧 Tech Stack
>
> | Layer | Technology |
> |---|---|
> | Language | Python 3.10 |
> | HTTP Client | requests / httpx |
> | Data Validation | pydantic |
> | Error Handling | Custom retry w/ exponential backoff |
> | Testing | pytest |
> | Documentation | Markdown |
>
> ---
>
> ## 📋 Data Mapping (Sample)
>
> | ERP Field | eCommerce Field | Transformation |
> |---|---|---|
> | `ITEM_CODE` | `sku` | Direct mapping |
> | `QTY_ON_HAND` | `inventory.quantity` | Integer cast |
> | `UNIT_PRICE` | `price.amount` | 2 decimal places |
> | `ORDER_DATE` | `created_at` | ISO 8601 format |
> | `CUSTOMER_ID` | `customer.external_id` | Prefix + ID |
> | `STATUS_CODE` | `order_status` | Status lookup table |
>
> ---
>
> ## ✅ Data Validation Checkpoints
>
> 1. **Schema Validation** — Pydantic models enforce field types and required fields
> 2. 2. **Business Rules** — Price > 0, quantity >= 0, valid status codes only
>    3. 3. **Duplicate Detection** — Check for existing records before insert/update
>       4. 4. **Referential Integrity** — Validate customer and product IDs exist in target
>          5. 5. **Post-sync Reconciliation** — Row count and checksum comparison after each batch
>            
>             6. ---
>            
>             7. ## 🚀 Getting Started
>            
>             8. ```bash
> git clone https://github.com/SnehaAjmira/erp-ecommerce-api.git
> cd erp-ecommerce-api
> pip install -r requirements.txt
>
> # Configure credentials
> cp config/settings.yaml.example config/settings.yaml
> # Edit settings.yaml with ERP and eCommerce API credentials
>
> # Run full sync
> python src/sync_engine.py --mode full
>
> # Run incremental sync (last 24h)
> python src/sync_engine.py --mode incremental --hours 24
> ```
>
> ---
>
> *Built by [Sneha Ajmira](https://linkedin.com/in/contactsnehaajmira) | Business Systems Analyst @ Apex Supply Company*
