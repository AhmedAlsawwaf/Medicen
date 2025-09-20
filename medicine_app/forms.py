from django import forms
from django.core.exceptions import ValidationError
from .models import User, Pharmacy, Medicine, Inventory, PASSWORD_RE

class SignupForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(),
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
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    remember_me = forms.BooleanField(required=False)

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ["name", "city", "address", "phone", "is_active", "cr_number"]

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

    def clean_description(self):
        desc = self.cleaned_data.get("description")
        if desc and len(desc) > 500:
            raise ValidationError("Description cannot exceed 500 characters.")
        return desc

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ["medicine", "pharmacy", "quantity", "price", "status"]

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
