from django import forms
from .models import Product, Category
from django.core.validators import MinValueValidator


class ProductSearchForm(forms.Form):
    query = forms.CharField(
        label='Search Products',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'}))
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min price',
            'class': 'form-control',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Max price',
            'class': 'form-control',
            'step': '0.01'
        })
    )
    in_stock = forms.BooleanField(
        required=False,
        label='In stock only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ProductForm(forms.ModelForm):
    price = forms.DecimalField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image', 'stock', 'available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'available': 'Is available for purchase'
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'slug': 'URL-friendly version of the name (auto-generated if blank)'
        }