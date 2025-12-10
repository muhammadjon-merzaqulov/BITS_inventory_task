from django.db import models
from decimal import Decimal


class Product(models.Model):
    """Product model with name, SKU, category, price, and dimensions."""
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('clothing', 'Clothing'),
        ('food', 'Food & Beverages'),
        ('office', 'Office Supplies'),
        ('other', 'Other'),
    ]
    
    VALUATION_CHOICES = [
        ('fifo', 'FIFO (First-In, First-Out)'),
        ('lifo', 'LIFO (Last-In, First-Out)'),
        ('avco', 'Average Cost'),
    ]
    
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Selling Price')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text='Average Cost Price')
    valuation_method = models.CharField(max_length=4, choices=VALUATION_CHOICES, default='fifo')
    
    length = models.DecimalField(max_digits=10, decimal_places=2, help_text='Length in cm')
    width = models.DecimalField(max_digits=10, decimal_places=2, help_text='Width in cm')
    height = models.DecimalField(max_digits=10, decimal_places=2, help_text='Height in cm')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def volume(self):
        """Calculate volume in cubic meters (m³)."""
        # Convert cm to m: cm / 100
        l_m = self.length / Decimal('100.00')
        w_m = self.width / Decimal('100.00')
        h_m = self.height / Decimal('100.00')
        return l_m * w_m * h_m


class StockBatch(models.Model):
    """Track incoming stock batches for FIFO/LIFO."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    quantity = models.IntegerField(help_text='Initial quantity received')
    remaining_quantity = models.IntegerField(help_text='Current quantity remaining in this batch')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    received_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['received_date', 'created_at']
    
    def __str__(self):
        return f"{self.product.sku} - {self.received_date} (Qty: {self.remaining_quantity})"


class Stock(models.Model):
    """Stock model tracking product quantities in different warehouses."""
    WAREHOUSE_CHOICES = [
        ('main', 'Main Warehouse'),
        ('north', 'North Branch'),
        ('south', 'South Branch'),
        ('east', 'East Branch'),
        ('west', 'West Branch'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.CharField(max_length=50, choices=WAREHOUSE_CHOICES)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'warehouse']
        ordering = ['warehouse', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse}: {self.quantity}"
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum threshold (10 units)."""
        return self.quantity < 10


class StockTransfer(models.Model):
    """Stock transfer model with complete workflow tracking."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('reconciled', 'Reconciled'),
    ]
    
    WAREHOUSE_CHOICES = Stock.WAREHOUSE_CHOICES
    
    from_warehouse = models.CharField(max_length=50, choices=WAREHOUSE_CHOICES)
    to_warehouse = models.CharField(max_length=50, choices=WAREHOUSE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    driver = models.CharField(max_length=255, blank=True, null=True)
    mismatch_reason = models.TextField(blank=True, null=True, help_text='Reason for any quantity mismatch')
    actual_quantity_received = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='transfers_created')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer #{self.id}: {self.product.name} ({self.from_warehouse} → {self.to_warehouse}) - {self.status}"
    
    @property
    def has_mismatch(self):
        """Check if there's a quantity mismatch."""
        if self.actual_quantity_received is not None:
            return self.actual_quantity_received != self.quantity
        return False


class StockAdjustment(models.Model):
    """Model for tracking stock adjustments (Damage, Theft, Correction)."""
    REASON_CHOICES = [
        ('damage', 'Damaged Stock'),
        ('theft', 'Theft/Loss'),
        ('correction', 'Inventory Correction'),
        ('return', 'Customer Return'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.CharField(max_length=50, choices=Stock.WAREHOUSE_CHOICES)
    quantity = models.IntegerField(help_text='Negative for removal, Positive for addition')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    note = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.product.name} - {self.get_reason_display()} ({self.quantity})"
