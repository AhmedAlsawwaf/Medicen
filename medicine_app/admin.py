from django.contrib import admin
from .models import User, Pharmacy, Medicine, Inventory
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("created_at",)

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "phone", "user", "is_active")
    search_fields = ("name", "city", "cr_number")
    list_filter = ("is_active", "city")
    
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "generic_name", "form", "strength", "created_by")
    search_fields = ("name", "generic_name", "form", "strength")

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("id", "pharmacy", "medicine", "quantity", "price", "status")
    search_fields = ("pharmacy__name", "medicine__name")
    list_filter = ("status",)
