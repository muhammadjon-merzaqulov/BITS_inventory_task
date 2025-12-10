from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, F
from django.db import transaction
from .models import Product, Stock, StockTransfer, StockBatch, StockAdjustment
from .forms import ProductForm, StockForm, StockTransferForm, StockTransferUpdateForm, StockEntryForm, StockAdjustmentForm

@login_required
def product_list(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'title': 'Product Management'
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
@permission_required('inventory.add_product', raise_exception=True)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product'
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
@permission_required('inventory.change_product', raise_exception=True)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Edit Product'
    }
    return render(request, 'inventory/product_form.html', context)

@login_required
@permission_required('inventory.delete_product', raise_exception=True)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')
    
    context = {'product': product}
    return render(request, 'inventory/product_confirm_delete.html', context)

@login_required
def stock_list(request):
    stocks = Stock.objects.select_related('product').all()
    # Group by warehouse
    warehouse_stocks = {}
    for stock in stocks:
        if stock.warehouse not in warehouse_stocks:
            warehouse_stocks[stock.warehouse] = []
        warehouse_stocks[stock.warehouse].append(stock)
        
    context = {
        'warehouse_stocks': warehouse_stocks,
        'title': 'Stock Levels'
    }
    return render(request, 'inventory/stock_list.html', context)

@login_required
def transfer_list(request):
    transfers = StockTransfer.objects.select_related('product', 'created_by').all()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        transfers = transfers.filter(status=status)
        
    context = {
        'transfers': transfers,
        'current_status': status,
        'title': 'Stock Transfers'
    }
    return render(request, 'inventory/transfer_list.html', context)

@login_required
def transfer_create(request):
    if request.method == 'POST':
        form = StockTransferForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.created_by = request.user
            
            # Check if sufficient stock exists
            try:
                source_stock = Stock.objects.get(
                    product=transfer.product,
                    warehouse=transfer.from_warehouse
                )
                if source_stock.quantity < transfer.quantity:
                    messages.error(request, f'Insufficient stock in {transfer.get_from_warehouse_display()}. Available: {source_stock.quantity}')
                    return render(request, 'inventory/transfer_form.html', {'form': form, 'title': 'Create Transfer'})
            except Stock.DoesNotExist:
                messages.error(request, f'No stock record found for {transfer.product} in {transfer.get_from_warehouse_display()}')
                return render(request, 'inventory/transfer_form.html', {'form': form, 'title': 'Create Transfer'})
            
            transfer.save()
            messages.success(request, 'Transfer request created successfully.')
            return redirect('transfer_list')
    else:
        form = StockTransferForm()
    
    context = {
        'form': form,
        'title': 'Create Transfer'
    }
    return render(request, 'inventory/transfer_form.html', context)

@login_required
def transfer_update(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    
    if request.method == 'POST':
        form = StockTransferUpdateForm(request.POST, instance=transfer)
        if form.is_valid():
            with transaction.atomic():
                old_status = StockTransfer.objects.get(pk=pk).status
                transfer = form.save()
                
                # Handle status changes
                if transfer.status == 'reconciled' and old_status != 'reconciled':
                    # Deduct from source
                    source_stock, _ = Stock.objects.get_or_create(
                        product=transfer.product,
                        warehouse=transfer.from_warehouse
                    )
                    source_stock.quantity -= transfer.quantity
                    source_stock.save()
                    
                    # Add to destination (use actual received if available, else requested)
                    qty_to_add = transfer.actual_quantity_received if transfer.actual_quantity_received is not None else transfer.quantity
                    dest_stock, _ = Stock.objects.get_or_create(
                        product=transfer.product,
                        warehouse=transfer.to_warehouse
                    )
                    dest_stock.quantity += qty_to_add
                    dest_stock.save()
                    
                    messages.success(request, 'Transfer reconciled and stock levels updated.')
                else:
                    messages.success(request, 'Transfer updated successfully.')
                    
            return redirect('transfer_list')
    else:
        form = StockTransferUpdateForm(instance=transfer)
    
    context = {
        'form': form,
        'transfer': transfer,
        'title': 'Update Transfer'
    }
    return render(request, 'inventory/transfer_form.html', context)

@login_required
def stock_entry_create(request):
    """View to handle new stock purchases (Stock In)."""
    if request.method == 'POST':
        form = StockEntryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                batch = form.save(commit=False)
                batch.remaining_quantity = batch.quantity
                batch.save()
                
                # Update Stock model
                warehouse = form.cleaned_data['warehouse']
                stock, _ = Stock.objects.get_or_create(
                    product=batch.product,
                    warehouse=warehouse
                )
                stock.quantity += batch.quantity
                stock.save()
                
                # Update Product Average Cost
                # Simple moving average calculation
                product = batch.product
                current_total_value = (product.cost_price * (stock.quantity - batch.quantity)) if stock.quantity > batch.quantity else 0
                new_batch_value = batch.unit_cost * batch.quantity
                total_qty = stock.quantity # This is approximation across all warehouses if we want global average
                
                # Better: Calculate global weighted average
                all_batches = StockBatch.objects.filter(product=product, remaining_quantity__gt=0)
                total_value = sum(b.remaining_quantity * b.unit_cost for b in all_batches)
                total_units = sum(b.remaining_quantity for b in all_batches)
                
                if total_units > 0:
                    product.cost_price = total_value / total_units
                    product.save()
                
                messages.success(request, f'Stock added successfully. New Average Cost: ${product.cost_price:.2f}')
                return redirect('stock_list')
    else:
        form = StockEntryForm()
        
    context = {
        'form': form,
        'title': 'Purchase Stock (Stock In)'
    }
    return render(request, 'inventory/stock_entry_form.html', context)

@login_required
def stock_adjustment_create(request):
    """View to handle stock adjustments (Damage, Theft, etc)."""
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                adj = form.save(commit=False)
                adj.created_by = request.user
                adj.save()
                
                # Update Stock model
                stock, _ = Stock.objects.get_or_create(
                    product=adj.product,
                    warehouse=adj.warehouse
                )
                stock.quantity += adj.quantity # Quantity can be negative
                stock.save()
                
                messages.success(request, 'Stock adjustment recorded successfully.')
                return redirect('stock_list')
    else:
        form = StockAdjustmentForm()
        
    context = {
        'form': form,
        'title': 'Stock Adjustment'
    }
    return render(request, 'inventory/stock_adjustment_form.html', context)
