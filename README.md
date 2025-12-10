# Smart Inventory & Sales Performance Management System

A complete Django-based inventory and sales management system designed for BIT students to learn real-world business workflows.

## Features

### Core Features
- **Role-Based Access Control** - 5 user roles (Admin, CEO, Sales Staff, Warehouse Manager, Accountant)
- **Responsive Dashboard** - Different views based on user role
- **Modern UI** - Bootstrap 5 with custom styling and animations

### Inventory Module
- Product management with SKU, category, pricing, and dimensions
- Stock tracking across multiple warehouses
- 5-state stock transfer workflow:
  1. Pending
  2. Approved
  3. In Transit
  4. Received
  5. Reconciled
- Low stock alerts
- Quantity mismatch tracking

### Sales Module
- Customer management
- Invoice creation with dynamic line items (formsets)
- Real-time total calculation
- Decimal-based pricing (no float/Decimal conflicts)
- Invoice detail view and PDF-ready layout

### Staff & KPI Module
- Staff profiles with attendance and satisfaction metrics
- Monthly KPI tracking (sales amount vs target)
- Achievement percentage calculation
- Bonus management
- Performance dashboard with progress bars

## Technology Stack

- **Backend**: Django 5.2.9
- **Database**: SQLite3
- **Frontend**: Bootstrap 5, Custom CSS, Vanilla JavaScript
- **Authentication**: Django built-in authentication
- **Forms**: Django Forms with inline formsets

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip

### 2. Virtual Environment (Already Created)
```bash
cd /Users/muhammadjonmerzaqulov/Downloads/bits
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd inventory_system
pip install django
```

### 4. Run Migrations (Already Done)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Sample Data (Already Done)
```bash
python manage.py populate_data
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Then open your browser to: **http://localhost:8000/login/**

## User Accounts

| Username    | Password     | Role              | Access                                    |
|-------------|--------------|-------------------|-------------------------------------------|
| admin       | admin123     | Administrator     | Full access to all modules + Django admin |
| ceo         | ceo123       | CEO               | Dashboard and KPI access                  |
| sales1      | sales123     | Sales Staff       | Customers and Invoices                    |
| warehouse1  | warehouse123 | Warehouse Manager | Products, Stock, Transfers                |
| accountant  | acc123       | Accountant        | Invoices, Payments, Reports               |

## Project Structure

```
inventory_system/
├── manage.py
├── db.sqlite3
├── inventory_system/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # Authentication & Dashboard
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── inventory/                 # Inventory Management
│   ├── models.py             # Product, Stock, StockTransfer
│   ├── views.py              # CRUD operations
│   ├── forms.py
│   └── urls.py
├── sales/                     # Sales Management
│   ├── models.py             # Customer, Invoice, SaleItem
│   ├── views.py              # Invoice with formsets
│   ├── forms.py
│   └── urls.py
├── staff/                     # KPI & Performance
│   ├── models.py             # StaffProfile, KPI, Bonus
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html             # Base template
│   ├── core/                 # Login, Dashboard
│   ├── inventory/            # Product, Stock, Transfer templates
│   ├── sales/                # Customer, Invoice templates
│   └── staff/                # KPI templates
└── static/
    ├── css/
    │   └── style.css         # Custom styling
    └── js/
        └── main.js           # Formset management
```

## Key Models

### Inventory
- **Product**: name, SKU (unique), category, price (Decimal), dimensions (L×W×H)
- **Stock**: product, warehouse, quantity
- **StockTransfer**: from/to warehouse, product, quantity, status, driver, mismatch tracking

### Sales
- **Customer**: name, email, phone, address
- **Invoice**: customer, invoice_number, date, discount (Decimal), total_amount (Decimal)
- **SaleItem**: invoice, product, quantity, price (Decimal), subtotal property

### Staff
- **StaffProfile**: user, role, attendance_percentage, customer_satisfaction
- **KPI**: staff, month, sales_amount, target_sales, achievement_percentage (calculated)
- **Bonus**: staff, month, amount, reason

## Key Features Implemented

### 1. Decimal Field Usage
All monetary values use `DecimalField` to prevent float/Decimal type conflicts:
```python
price = models.DecimalField(max_digits=10, decimal_places=2)
```

### 2. Dynamic Formsets
Invoice form uses inline formsets for managing sale items:
```python
SaleItemFormSet = inlineformset_factory(Invoice, SaleItem, ...)
```

### 3. Role-Based Navigation
Base template shows/hides menu items based on user role:
```html
{% if user.is_superuser or user.profile.role == 'warehouse' %}
    <!-- Inventory menu -->
{% endif %}
```

### 4. Stock Transfer Workflow
5-state workflow with automatic stock updates on reconciliation:
- Status progression tracked
- Quantity mismatch handling
- Driver assignment
- Automatic stock level adjustments

### 5. Real-Time Calculations
JavaScript calculates invoice subtotals and totals in real-time:
- Quantity × Price = Subtotal
- Sum(Subtotals) - Discount = Total

## Usage Scenarios

### As Warehouse Manager
1. Login with `warehouse1` / `warehouse123`
2. View dashboard showing total products and low stock alerts
3. Navigate to Inventory → Products
4. Add/edit/delete products
5. View stock levels by warehouse
6. Create stock transfers between warehouses
7. Update transfer status through the workflow

### As Sales Staff
1. Login with `sales1` / `sales123`
2. View dashboard showing today's sales
3. Navigate to Sales → Customers
4. Add new customers
5. Navigate to Sales → Invoices
6. Create invoice with multiple line items
7. Dynamically add/remove invoice items
8. Apply discount
9. View calculated totals

### As CEO
1. Login with `ceo` / `ceo123`
2. View comprehensive dashboard
3. Navigate to KPI Dashboard
4. Review staff performance metrics
5. View achievement percentages
6. Check recent bonuses

## Development Notes

### Running Tests
```bash
python manage.py test
```

### Creating Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Accessing Django Admin
Navigate to: http://localhost:8000/admin/
Login with admin credentials

### Adding More Sample Data
Edit `core/management/commands/populate_data.py` and run:
```bash
python manage.py populate_data
```

## Customization

### Adding New Roles
1. Update `StaffProfile.ROLE_CHOICES` in `staff/models.py`
2. Update navigation logic in `templates/base.html`
3. Update dashboard context in `core/views.py`

### Adding PDF Export
Install reportlab:
```bash
pip install reportlab
```

Then add PDF generation view in sales/views.py

### Adding Charts
Include Chart.js in base.html and create chart views

## Security Notes

- CSRF protection enabled on all forms
- Login required decorators on all views
- Role-based access control implemented
- Debug mode should be False in production
- SECRET_KEY should be environment variable in production

## Educational Purpose

This project demonstrates:
- Django MVT architecture
- Model relationships (ForeignKey, OneToOne)
- Form validation and inline formsets
- User authentication and permissions
- Template inheritance
- Static file management
- Database migrations
- Management commands
- Decimal field usage for financial data
- JavaScript DOM manipulation
- Responsive web design with Bootstrap

## Future Enhancements

- [ ] PDF/Excel export for invoices and reports
- [ ] Charts and graphs for sales analytics
- [ ] Email notifications for low stock
- [ ] REST API with Django REST Framework
- [ ] Barcode/QR code generation
- [ ] Multi-currency support
- [ ] Inventory forecasting
- [ ] Advanced reporting module

## License

Educational use for BIT students.

## Author

Created as a comprehensive learning project for BIT students to understand real-world business application development with Django.
