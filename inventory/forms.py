from django import forms
from .models import Product, Stock, StockTransfer, StockBatch, StockAdjustment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'price', 'cost_price', 'valuation_method', 'length', 'width', 'height']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'valuation_method': forms.Select(attrs={'class': 'form-select'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'warehouse', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['from_warehouse', 'to_warehouse', 'product', 'quantity', 'driver']
        widgets = {
            'from_warehouse': forms.Select(attrs={'class': 'form-select'}),
            'to_warehouse': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'driver': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from_warehouse = cleaned_data.get('from_warehouse')
        to_warehouse = cleaned_data.get('to_warehouse')
        
        if from_warehouse and to_warehouse and from_warehouse == to_warehouse:
            raise forms.ValidationError("Source and destination warehouses cannot be the same.")
        return cleaned_data

class StockTransferUpdateForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['status', 'actual_quantity_received', 'mismatch_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'actual_quantity_received': forms.NumberInput(attrs={'class': 'form-control'}),
            'mismatch_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockEntryForm(forms.ModelForm):
    """Form for purchasing/adding new stock batches."""
    warehouse = forms.ChoiceField(choices=Stock.WAREHOUSE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = StockBatch
        fields = ['product', 'quantity', 'unit_cost', 'received_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'received_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class StockAdjustmentForm(forms.ModelForm):
    """Form for adjusting stock (damage, theft, etc)."""
    class Meta:
        model = StockAdjustment
        fields = ['product', 'warehouse', 'quantity', 'reason', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Negative for removal, Positive for addition'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
