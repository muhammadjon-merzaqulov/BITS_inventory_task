from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from datetime import date
from .models import StaffProfile, KPI, Bonus


@login_required
def kpi_dashboard(request):
    """KPI dashboard showing staff performance metrics."""
    # Get current month
    today = date.today()
    current_month = today.replace(day=1)
    
    # Get all staff profiles
    staff_profiles = StaffProfile.objects.select_related('user').all()
    
    # Get KPIs for current month
    current_kpis = KPI.objects.filter(month=current_month).select_related('staff__user')
    
    # Get recent bonuses
    recent_bonuses = Bonus.objects.select_related('staff__user').order_by('-month')[:10]
    
    # Calculate aggregate statistics
    kpi_stats = current_kpis.aggregate(
        avg_achievement=Avg('sales_amount'),
        total_sales=Sum('sales_amount'),
        total_target=Sum('target_sales')
    )
    
    # Filter KPIs by user if not admin/CEO
    try:
        profile = request.user.profile
        if profile.role not in ['admin', 'ceo']:
            current_kpis = current_kpis.filter(staff=profile)
            recent_bonuses = recent_bonuses.filter(staff=profile)
    except StaffProfile.DoesNotExist:
        pass
    
    context = {
        'staff_profiles': staff_profiles,
        'current_kpis': current_kpis,
        'recent_bonuses': recent_bonuses,
        'kpi_stats': kpi_stats,
        'current_month': current_month,
    }
    
    return render(request, 'staff/kpi_dashboard.html', context)


@login_required
def staff_profile(request, pk):
    """View individual staff profile with KPI history."""
    staff = StaffProfile.objects.select_related('user').get(pk=pk)
    kpis = KPI.objects.filter(staff=staff).order_by('-month')
    bonuses = Bonus.objects.filter(staff=staff).order_by('-month')
    
    # Calculate total bonuses
    total_bonuses = bonuses.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'staff': staff,
        'kpis': kpis,
        'bonuses': bonuses,
        'total_bonuses': total_bonuses,
    }
    
    return render(request, 'staff/staff_profile.html', context)
