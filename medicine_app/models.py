from django.db import models
from django.core.exceptions import ValidationError
import re
import bcrypt

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s\-'`]{1,}$")
EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")
CITY_RE = re.compile(r"^[A-Za-z\s\-']+$")
PHONE_RE = re.compile(r"^\+?\d{8,15}$")
CR_NUMBER_RE = re.compile(r"^[A-Z0-9\-]{5,30}$")
MEDICINE_NAME_RE = re.compile(r"^[A-Za-z0-9\s\-']+$")
STRENGTH_RE = re.compile(r"^\d+(\.\d+)?\s?(mg|ml|g|mcg|IU)$", re.IGNORECASE)

FORM_CHOICES = [
    ("Tablet", "Tablet"),
    ("Capsule", "Capsule"),
    ("Syrup", "Syrup"),
    ("Injection", "Injection"),
]

class UserManager(models.Manager):
    def create_user(self, first_name, last_name, email, password):
        if not NAME_RE.match(first_name):
            raise ValidationError("Invalid first name.")
        if not NAME_RE.match(last_name):
            raise ValidationError("Invalid last name.")
        if not EMAIL_RE.match(email):
            raise ValidationError("Invalid email format.")
        if not PASSWORD_RE.match(password):
            raise ValidationError("Password must be at least 8 chars, include letters & numbers.")

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            password=hashed_pw,
        )
        user.save(using=self._db)
        return user

    def authenticate(self, email, password):
        try:
            user = self.get(email=email.lower())
            if bcrypt.checkpw(password.encode(), user.password.encode()):
                return user
        except self.model.DoesNotExist:
            return None
        return None


class PharmacyManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)

class MedicineManager(models.Manager):
    def search(self, keyword):
        return self.filter(
            models.Q(name__icontains=keyword) |
            models.Q(generic_name__icontains=keyword)
        )
class User(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Pharmacy(models.Model):
    name = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    address = models.CharField(max_length=120)
    phone = models.CharField(max_length=45)
    is_active = models.BooleanField(default=True)
    cr_number = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pharmacies")
    medicines = models.ManyToManyField("Medicine", through="Inventory", related_name="pharmacies")
    objects = PharmacyManager()

    class Meta:
        unique_together = ("user", "name", "city")
    def clean(self):
        if not CITY_RE.match(self.city):
            raise ValidationError("Invalid city name.")
        if not PHONE_RE.match(self.phone):
            raise ValidationError("Invalid phone number.")
        if not CR_NUMBER_RE.match(self.cr_number):
            raise ValidationError("Invalid CR number.")


class Medicine(models.Model):
    name = models.CharField(max_length=120)
    generic_name = models.CharField(max_length=120, blank=True, null=True)
    form = models.CharField(max_length=45, choices=FORM_CHOICES)
    strength = models.CharField(max_length=45)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="medicines")
    objects = MedicineManager()
    
    class Meta:
        unique_together = ("created_by", "name", "strength", "form")
    
    def clean(self):
        if not MEDICINE_NAME_RE.match(self.name):
            raise ValidationError("Invalid medicine name.")
        if self.generic_name and not MEDICINE_NAME_RE.match(self.generic_name):
            raise ValidationError("Invalid generic name.")
        if not STRENGTH_RE.match(self.strength):
            raise ValidationError("Invalid strength format (e.g., '500mg').")
    def __str__(self):
        return f"{self.name}"

class Inventory(models.Model):
    STATUS_CHOICES = [
        ('IN', 'In Stock'),
        ('OUT', 'Out of Stock'),
    ]
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='IN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE,null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        unique_together = ("medicine", "pharmacy")

    def clean(self):
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        if self.price < 0:
            raise ValidationError("Price must be positive.")
        if self.quantity == 0 and self.status != "OUT":
            raise ValidationError("If quantity = 0, status must be OUT.")
        if self.quantity > 0 and self.status != "IN":
            raise ValidationError("If quantity > 0, status must be IN.")
        if self.medicine and self.pharmacy:
            if Inventory.objects.exclude(pk=self.pk).filter(
                medicine=self.medicine, pharmacy=self.pharmacy
            ).exists():
                raise ValidationError("This medicine already exists in this pharmacy.")
