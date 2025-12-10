from django.db import models
from decimal import Decimal
from inventory.models import Product


class Customer(models.Model):
    """Customer model for managing client information."""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Invoice(models.Model):
    """Invoice model with customer, date, discount, and total amount."""
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='invoices_created')
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"
    
    def calculate_total(self):
        """Calculate total amount from sale items minus discount."""
        subtotal = sum(item.subtotal for item in self.items.all())
        return subtotal - self.discount
    
    def update_payment_status(self):
        """Update status based on amount paid."""
        if self.amount_paid >= self.total_amount:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        self.save(update_fields=['status', 'amount_paid'])
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate total if items exist."""
        super().save(*args, **kwargs)
        # Recalculate total after items are saved
        if self.items.exists():
            self.total_amount = self.calculate_total()
            # Also check payment status in case total changed
            if self.amount_paid >= self.total_amount:
                self.status = 'paid'
            elif self.amount_paid > 0:
                self.status = 'partial'
            else:
                self.status = 'unpaid'
            super().save(update_fields=['total_amount', 'status'])


class SaleItem(models.Model):
    """Sale item model representing individual products in an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this line item."""
        return Decimal(str(self.quantity)) * self.price


class Payment(models.Model):
    """Payment model for tracking invoice payments."""
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('transfer', 'Bank Transfer'),
        ('check', 'Check'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    reference = models.CharField(max_length=100, blank=True, help_text='Transaction ID or Check Number')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"{self.invoice.invoice_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount paid
        total_paid = self.invoice.payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0.00')
        self.invoice.amount_paid = total_paid
        self.invoice.update_payment_status()
