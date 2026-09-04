# AGENTS.md — Odoo 11 Customized Modules Repository

## Project Overview

This repository contains **50+ custom Odoo 11 modules** developed for various clients and business needs. Each module is a self-contained Odoo addon following standard Odoo 11 module structure.

**Odoo Version**: 11.0  
**Python Version**: 3.6+ (Odoo 11 requirement)  
**Primary Language**: Python, XML, JavaScript  

---

## Repository Structure

```
odoo11_customized/
├── .gitignore
├── .project
├── .pydevproject
├── AGENTS.md                 # This file
├── account_payment_balance/          # Module: account payment balance
├── androidapp_companion/             # Module: Android app companion
├── anugerah_jaya_express/            # Module: Anugerah Jaya Express
├── arayu_clinic/                     # Module: Arayu Clinic
├── asia_florist/                     # Module: Asia Florist
├── attendances_based_payroll/        # Module: Attendance-based payroll
├── auth_ldap_tls/                    # Module: LDAP TLS authentication
├── bintang_satelit/                  # Module: Bintang Satelit
├── bizibi_cafe/                      # Module: Bizibi Cafe
├── check_payment/                    # Module: Check payment
├── contact_transporter/              # Module: Contact transporter
├── contract_benefit/                 # Module: Contract benefit
├── deliver_auto_invoice/             # Module: Auto invoice on delivery
├── delivery_invoice_same_sequence/   # Module: Same sequence for delivery/invoice
├── delivery_status/                  # Module: Delivery status
├── discount_total_sale/              # Module: Discount total sale
├── employee_qr_code/                 # Module: Employee QR code
├── equity_change/                    # Module: Equity change
├── hide_confidential_info/           # Module: Hide confidential info
├── hr_disciplinary_tracking/         # Module: HR disciplinary tracking
├── hr_employee_updation/             # Module: HR employee updation
├── hr_insurance/                     # Module: HR insurance
├── hr_payroll_payment/               # Module: HR payroll payment
├── hr_zk_attendance_pyzk/            # Module: ZK attendance (pyzk)
├── indonesia_template/               # Module: Indonesia template
├── indonesia_template_purchasing/    # Module: Indonesia purchasing template
├── limit_partner_credit/             # Module: Limit partner credit
├── megajaya/                         # Module: Megajaya (invoice reports)
├── ni_bundle_pack_product/           # Module: Bundle pack product
├── oh_employee_creation_from_user/   # Module: Employee creation from user
├── ohrms_loan/                       # Module: OHrms loan
├── ohrms_loan_accounting/            # Module: OHrms loan accounting
├── other_income/                     # Module: Other income
├── partner_iterative_archive/        # Module: Partner iterative archive
├── petstore/                         # Module: Petstore
├── product_description/              # Module: Product description
├── purchase_request/                 # Module: Purchase request
├── rejeki_jaya/                      # Module: Rejeki Jaya
├── reset_sequence_monthly/           # Module: Reset sequence monthly
├── rma_rythe/                        # Module: RMA (Rythe)
├── sale_advance_payment/             # Module: Sale advance payment
├── sale_priority/                    # Module: Sale priority
├── sale_purchase_previous_price/     # Module: Previous price sale/purchase
├── sale_requested_date/              # Module: Sale requested date
├── sms_frame/                        # Module: SMS frame
├── stock_inventory_subcateg/         # Module: Stock inventory subcategory
├── stock_inventory_valuation_location/ # Module: Stock valuation by location
├── stock_picking_validation/         # Module: Stock picking validation
├── template_scaffold/                # Module: Template scaffold
├── toserba23/                        # Module: Toserba23
└── toserba23_branch/                 # Module: Toserba23 branch
```

---

## Module Structure (Standard)

Each module follows standard Odoo 11 structure:

```
module_name/
├── __init__.py           # Python package init
├── __manifest__.py       # Module metadata (name, depends, data, etc.)
├── models/               # Python models (*.py)
├── views/                # XML views (*.xml) - optional
├── reports/              # QWeb reports (*.xml) - optional
├── security/             # Security rules (ir.model.access.csv) - optional
├── wizards/              # Transient models - optional
├── controllers/          # HTTP controllers - optional
├── data/                 # Data files (XML/CSV) - optional
├── demo/                 # Demo data - optional
└── static/               # Static assets (JS, CSS, images) - optional
```

---

## Development Guidelines

### Python Code Style
- Follow **PEP 8** with Odoo conventions
- Use **4-space indentation**
- Model names: `module.model_name` (snake_case)
- Field names: `field_name` (snake_case)
- Method names: `method_name` (snake_case)
- Class names: `ModelName` (PascalCase)

### XML Files
- Use proper indentation (4 spaces)
- Follow Odoo 11 view architecture
- Use `inherit_id` for view inheritance
- Group related fields in `<group>`

### Manifest (`__manifest__.py`)
Required keys:
```python
{
    'name': 'Module Display Name',
    'version': '1.0',
    'depends': ['base', 'other_module'],
    'data': ['views/file.xml', 'reports/file.xml'],
    'author': 'Author Name',
    'category': 'Category',
}
```

---

## Common Commands

### Run Odoo Server (Development)
```bash
# From odoo11 source directory (not this repo)
./odoo-bin -c odoo.conf -d database_name --addons-path=/path/to/odoo11_customized,/path/to/odoo11/addons
```

### Install/Upgrade Module
```bash
# Via Odoo CLI
./odoo-bin -c odoo.conf -d database_name -i module_name --addons-path=...

# Or upgrade
./odoo-bin -c odoo.conf -d database_name -u module_name --addons-path=...
```

### Run Tests
```bash
# Odoo 11 test runner
./odoo-bin -c odoo.conf -d database_name --test-enable -i module_name --addons-path=...
```

### Lint Python
```bash
# Using flake8 (if configured)
flake8 module_name/

# Or pylint
pylint module_name/
```

---

## Module Categories

| Category | Modules |
|----------|---------|
| **Accounting/Finance** | `account_payment_balance`, `check_payment`, `contract_benefit`, `deliver_auto_invoice`, `delivery_invoice_same_sequence`, `equity_change`, `limit_partner_credit`, `ohrms_loan`, `ohrms_loan_accounting`, `other_income` |
| **HR/Payroll** | `attendances_based_payroll`, `employee_qr_code`, `hr_disciplinary_tracking`, `hr_employee_updation`, `hr_insurance`, `hr_payroll_payment`, `hr_zk_attendance_pyzk`, `oh_employee_creation_from_user` |
| **Sales/CRM** | `delivery_status`, `discount_total_sale`, `meggajaya`, `sale_advance_payment`, `sale_priority`, `sale_purchase_previous_price`, `sale_requested_date`, `rma_rythe` |
| **Purchase/Inventory** | `ni_bundle_pack_product`, `product_description`, `purchase_request`, `reset_sequence_monthly`, `stock_inventory_subcateg`, `stock_inventory_valuation_location`, `stock_picking_validation` |
| **Localization (Indonesia)** | `indonesia_template`, `indonesia_template_purchasing`, `bintang_satelit`, `rejeki_jaya`, `toserba23`, `toserba23_branch` |
| **Vertical/Client-Specific** | `anugerah_jaya_express`, `arayu_clinic`, `asia_florist`, `bizibi_cafe`, `contact_transporter`, `megajaya`, `petstore` |
| **Technical/Utils** | `auth_ldap_tls`, `hide_confidential_info`, `partner_iterative_archive`, `sms_frame`, `template_scaffold`, `androidapp_companion` |

---

## Key Modules Detail

### `megajaya` (Latest per git history)
- **Purpose**: Custom invoice reports for Megajaya
- **Dependencies**: `base`, `account`
- **Reports**: Master template, Sale Order, Inventory, Invoice documents
- **Location**: `reports/master_template.xml`, `reports/saleorder_document.xml`, `reports/inventory_document.xml`, `reports/invoice_document.xml`

### `purchase_request`
- Large module (14 subdirectories)
- Complete purchase request workflow

### `sms_frame`
- SMS integration framework

### `indonesia_template` / `indonesia_template_purchasing`
- Indonesian localization templates

---

## Testing

### Unit Tests
Place test files in `tests/` directory within each module:
```
module_name/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_wizards.py
```

Run:
```bash
./odoo-bin -c odoo.conf -d test_db --test-enable -i module_name
```

---

## Git Workflow

- **Branch**: `master` (main)
- **Commits**: Conventional commits preferred
- **Recent**: Invoice report for Megajaya added (commit `d7ee3ef`)

---

## Deployment Notes

1. Copy module directories to Odoo `addons_path`
2. Update Apps list in Odoo
3. Install/Upgrade module
4. Configure any module-specific settings

---

## Contact / Maintainer

- **Author**: Ryanto The
- **Repository**: Custom Odoo 11 modules for various clients

---

*Generated for AI agent assistance. Update as modules evolve.*