from django import forms
from .models import Product

class ProductSearchForm(forms.Form):
    query = forms.CharField(label='Search', required=False)
