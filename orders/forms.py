from django import forms
from django.core.validators import RegexValidator
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'address', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add any custom email validation here
        return email.lower()  # Normalize to lowercase

    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validation here
        return cleaned_data

    # Enhanced field definitions with custom widgets and validation
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        }),
        max_length=100,
        required=True
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        required=True
    )

    address = forms.CharField(
        label="Delivery Address",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Full address including postal code'
        }),
        required=True
    )

    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (123) 456-7890'
        }),
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        required=True
    )

