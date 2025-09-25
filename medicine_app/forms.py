from django import forms
from django.core.exceptions import ValidationError
from .models import User, Pharmacy, Medicine, Inventory, PASSWORD_RE

class SignupForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "password": forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        cpw = cleaned_data.get("confirm_password")

        if pw and not PASSWORD_RE.match(pw):
            raise ValidationError("Password must be at least 8 characters and include letters and numbers.")
        if pw != cpw:
            raise ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ["name", "city", "address", "phone", "is_active", "cr_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Pharmacy Name"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Address"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "cr_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Commercial Registration No."}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 2:
            raise ValidationError("Pharmacy name must be at least 2 characters long.")
        return name

    def clean_address(self):
        address = self.cleaned_data.get("address")
        if len(address) < 5:
            raise ValidationError("Address must be at least 5 characters long.")
        return address

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "generic_name", "form", "strength", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "generic_name": forms.TextInput(attrs={"class": "form-control"}),
            "form": forms.Select(attrs={"class": "form-select"}),
            "strength": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
    def clean_description(self):
        desc = self.cleaned_data.get("description")
        if desc and len(desc) > 500:
            raise ValidationError("Description cannot exceed 500 characters.")
        return desc

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["medicine", "quantity", "price", "status"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is not None and qty < 0:
            raise ValidationError("Quantity cannot be negative.")
        return qty

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise ValidationError("Price must be positive.")
        return price

class InventoryFormNoMedicine(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["quantity", "price", "status"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": 0}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
class InventoryEditForm(InventoryFormNoMedicine):
    pass