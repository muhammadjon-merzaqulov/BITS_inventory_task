from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from .models import Customer, Invoice, SaleItem, Payment
from .forms import CustomerForm, InvoiceForm, SaleItemFormSet, PaymentForm

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'title': 'Customers'
    }
    return render(request, 'sales/customer_list.html', context)

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Add Customer'
    }
    return render(request, 'sales/customer_form.html', context)

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('customer').all()
    context = {
        'invoices': invoices,
        'title': 'Invoices'
    }
    return render(request, 'sales/invoice_list.html', context)

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = SaleItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.created_by = request.user
                invoice.save()
                
                formset.instance = invoice
                formset.save()
                
                # Trigger total calculation
                invoice.save()
                
                messages.success(request, 'Invoice created successfully.')
                return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = SaleItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice'
    }
    return render(request, 'sales/invoice_form.html', context)

@login_required
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = SaleItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                invoice.save() # Recalculate total
                messages.success(request, 'Invoice updated successfully.')
                return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = SaleItemFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Edit Invoice'
    }
    return render(request, 'sales/invoice_form.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.select_related('product').all()
    payments = invoice.payments.all()
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'title': f'Invoice {invoice.invoice_number}'
    }
    return render(request, 'sales/invoice_detail.html', context)

@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully.')
        return redirect('invoice_list')
    
    context = {'invoice': invoice}
    return render(request, 'sales/invoice_confirm_delete.html', context)

@login_required
def payment_create(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            payment.save()
            messages.success(request, 'Payment recorded successfully.')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        # Pre-fill amount with remaining balance
        remaining = invoice.total_amount - invoice.amount_paid
        form = PaymentForm(initial={'amount': remaining})
    
    context = {
        'form': form,
        'invoice': invoice,
        'title': 'Record Payment'
    }
    return render(request, 'sales/payment_form.html', context)
