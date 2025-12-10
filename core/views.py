from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date
from decimal import Decimal
from .forms import CustomLoginForm
from inventory.models import Product, Stock, StockTransfer
from sales.models import Invoice, Customer
from staff.models import StaffProfile


def custom_login(request):
    """Custom login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def custom_logout(request):
    """Custom logout view."""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard view with role-based context."""
    context = {
        'user': request.user,
    }
    
    # Get user profile and role
    try:
        profile = request.user.profile
        role = profile.role
        context['role'] = role
        context['role_display'] = profile.get_role_display()
    except StaffProfile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else None
        context['role'] = role
        context['role_display'] = 'Administrator' if request.user.is_superuser else 'User'
    
    # Common metrics for all roles
    context['total_products'] = Product.objects.count()
    context['total_customers'] = Customer.objects.count()
    
    # Today's sales
    today = date.today()
    today_invoices = Invoice.objects.filter(date=today)
    context['today_sales'] = today_invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    context['today_invoice_count'] = today_invoices.count()
    
    # Pending transfers
    context['pending_transfers'] = StockTransfer.objects.filter(
        status__in=['pending', 'approved', 'in_transit']
    ).count()
    
    # Low stock alerts
    low_stock_items = Stock.objects.filter(quantity__lt=10)
    context['low_stock_count'] = low_stock_items.count()
    context['low_stock_items'] = low_stock_items[:5]  # Show top 5
    
    # Recent activities based on role
    if role in ['admin', 'ceo']:
        context['recent_invoices'] = Invoice.objects.all()[:5]
        context['recent_transfers'] = StockTransfer.objects.all()[:5]
    elif role == 'sales':
        context['recent_invoices'] = Invoice.objects.filter(
            created_by=request.user
        )[:5]
    elif role == 'warehouse':
        context['recent_transfers'] = StockTransfer.objects.all()[:5]
        context['recent_products'] = Product.objects.all()[:5]
    elif role == 'accountant':
        context['recent_invoices'] = Invoice.objects.all()[:5]
        context['monthly_revenue'] = Invoice.objects.filter(
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    return render(request, 'core/dashboard.html', context)
