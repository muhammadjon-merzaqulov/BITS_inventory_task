from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class StaffProfile(models.Model):
    """Staff profile model with role and performance metrics."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('ceo', 'CEO'),
        ('sales', 'Sales Staff'),
        ('warehouse', 'Warehouse Manager'),
        ('accountant', 'Accountant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    customer_satisfaction = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), 
                                                 help_text='Customer satisfaction percentage')
    hire_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"


class KPI(models.Model):
    """KPI model tracking staff performance metrics."""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='kpis')
    month = models.DateField(help_text='First day of the month')
    sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    target_sales = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['staff', 'month']
        ordering = ['-month', 'staff']
        verbose_name = 'KPI'
        verbose_name_plural = 'KPIs'
    
    def __str__(self):
        return f"{self.staff.user.username} - {self.month.strftime('%B %Y')}"
    
    @property
    def achievement_percentage(self):
        """Calculate achievement percentage."""
        if self.target_sales > 0:
            return (self.sales_amount / self.target_sales) * Decimal('100.00')
        return Decimal('0.00')
    
    @property
    def is_target_met(self):
        """Check if sales target is met."""
        return self.sales_amount >= self.target_sales


class Bonus(models.Model):
    """Bonus model for tracking staff bonuses."""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='bonuses')
    month = models.DateField(help_text='Month for which bonus is awarded')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True, help_text='Reason for bonus')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-month', 'staff']
        verbose_name_plural = 'Bonuses'
    
    def __str__(self):
        return f"{self.staff.user.username} - ${self.amount} ({self.month.strftime('%B %Y')})"
