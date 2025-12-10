from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from inventory.models import Product, Stock, StockTransfer
from sales.models import Customer, Invoice, SaleItem
from staff.models import StaffProfile, KPI, Bonus


class Command(BaseCommand):
    help = 'Populate database with sample data for demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✓ Created superuser: admin / admin123'))
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write('✓ Superuser already exists')
        
        # Create staff users
        users_data = [
            {'username': 'ceo', 'password': 'ceo123', 'role': 'ceo', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'sales1', 'password': 'sales123', 'role': 'sales', 'first_name': 'Sarah', 'last_name': 'Johnson'},
            {'username': 'warehouse1', 'password': 'warehouse123', 'role': 'warehouse', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'accountant', 'password': 'acc123', 'role': 'accountant', 'first_name': 'Emily', 'last_name': 'Davis'},
        ]
        
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=f"{user_data['username']}@company.com"
                )
                StaffProfile.objects.create(
                    user=user,
                    role=user_data['role'],
                    attendance_percentage=Decimal('95.50'),
                    customer_satisfaction=Decimal('88.00'),
                    hire_date=date.today() - timedelta(days=365)
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Created user: {user_data['username']} / {user_data['password']}"))
        
        # Create products
        products_data = [
            {'name': 'Laptop Dell XPS 15', 'sku': 'LAP-001', 'category': 'electronics', 'price': '1299.99', 'l': 35, 'w': 25, 'h': 2},
            {'name': 'Office Chair Premium', 'sku': 'FUR-001', 'category': 'furniture', 'price': '299.99', 'l': 70, 'w': 70, 'h': 120},
            {'name': 'Wireless Mouse', 'sku': 'ELC-001', 'category': 'electronics', 'price': '29.99', 'l': 12, 'w': 8, 'h': 4},
            {'name': 'USB-C Cable 2m', 'sku': 'ELC-002', 'category': 'electronics', 'price': '15.99', 'l': 200, 'w': 1, 'h': 1},
            {'name': 'Desk Lamp LED', 'sku': 'OFF-001', 'category': 'office', 'price': '45.00', 'l': 20, 'w': 15, 'h': 40},
            {'name': 'Notebook A4 Pack', 'sku': 'OFF-002', 'category': 'office', 'price': '12.50', 'l': 30, 'w': 21, 'h': 2},
            {'name': 'Monitor 27 inch', 'sku': 'ELC-003', 'category': 'electronics', 'price': '399.00', 'l': 65, 'w': 20, 'h': 45},
            {'name': 'Standing Desk', 'sku': 'FUR-002', 'category': 'furniture', 'price': '599.00', 'l': 160, 'w': 80, 'h': 75},
        ]
        
        for prod in products_data:
            Product.objects.get_or_create(
                sku=prod['sku'],
                defaults={
                    'name': prod['name'],
                    'category': prod['category'],
                    'price': Decimal(prod['price']),
                    'length': Decimal(str(prod['l'])),
                    'width': Decimal(str(prod['w'])),
                    'height': Decimal(str(prod['h']))
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(products_data)} products'))
        
        # Create stock records
        products = Product.objects.all()
        warehouses = ['main', 'north', 'south', 'east', 'west']
        for product in products:
            for warehouse in warehouses:
                Stock.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={'quantity': 50 if warehouse == 'main' else 20}
                )
        
        self.stdout.write(self.style.SUCCESS('✓ Created stock records'))
        
        # Create some low stock items
        low_stock_items = Stock.objects.filter(warehouse='east')[:3]
        for stock in low_stock_items:
            stock.quantity = 5
            stock.save()
        
        # Create stock transfers
        laptop = Product.objects.filter(sku='LAP-001').first()
        if laptop:
            StockTransfer.objects.get_or_create(
                product=laptop,
                from_warehouse='main',
                to_warehouse='north',
                defaults={
                    'quantity': 10,
                    'status': 'in_transit',
                    'driver': 'John Delivery',
                    'created_by': admin
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Created stock transfers'))
        
        # Create customers
        customers_data = [
            {'name': 'ABC Corporation', 'email': 'contact@abc.com', 'phone': '+1-555-0101', 'address': '123 Business St, NY'},
            {'name': 'XYZ Enterprises', 'email': 'info@xyz.com', 'phone': '+1-555-0102', 'address': '456 Commerce Ave, LA'},
            {'name': 'Tech Solutions Inc', 'email': 'sales@techsol.com', 'phone': '+1-555-0103', 'address': '789 Innovation Dr, SF'},
        ]
        
        for cust in customers_data:
            Customer.objects.get_or_create(
                email=cust['email'],
                defaults={
                    'name': cust['name'],
                    'phone': cust['phone'],
                    'address': cust['address']
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(customers_data)} customers'))
        
        # Create invoices
        customers = Customer.objects.all()
        for i, customer in enumerate(customers, 1):
            invoice, created = Invoice.objects.get_or_create(
                invoice_number=f'INV-2024-{i:04d}',
                defaults={
                    'customer': customer,
                    'date': date.today() - timedelta(days=i),
                    'discount': Decimal('50.00'),
                    'created_by': admin
                }
            )
            
            if created:
                # Add sale items
                products_for_invoice = products[:3]
                for product in products_for_invoice:
                    SaleItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=2,
                        price=product.price
                    )
                
                # Recalculate total
                invoice.total_amount = invoice.calculate_total()
                invoice.save()
        
        self.stdout.write(self.style.SUCCESS('✓ Created invoices with items'))
        
        # Create KPIs for staff
        current_month = date.today().replace(day=1)
        sales_profiles = StaffProfile.objects.filter(role='sales')
        for profile in sales_profiles:
            KPI.objects.get_or_create(
                staff=profile,
                month=current_month,
                defaults={
                    'sales_amount': Decimal('15000.00'),
                    'target_sales': Decimal('20000.00')
                }
            )
            
            # Add bonus
            Bonus.objects.get_or_create(
                staff=profile,
                month=current_month - timedelta(days=30),
                defaults={
                    'amount': Decimal('500.00'),
                    'reason': 'Excellent performance in previous month'
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Created KPIs and bonuses'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Created Successfully! ==='))
        self.stdout.write(self.style.SUCCESS('\nLogin Credentials:'))
        self.stdout.write('- Admin: admin / admin123')
        self.stdout.write('- CEO: ceo / ceo123')
        self.stdout.write('- Sales: sales1 / sales123')
        self.stdout.write('- Warehouse: warehouse1 / warehouse123')
        self.stdout.write('- Accountant: accountant / acc123')
        self.stdout.write(self.style.SUCCESS('\nRun: python manage.py runserver'))
