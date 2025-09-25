from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import SignupForm, LoginForm, PharmacyForm, MedicineForm, InventoryForm, InventoryFormNoMedicine,InventoryEditForm
from .models import User,Medicine,Inventory,Pharmacy
from django.http import JsonResponse
from django.core.exceptions import ValidationError

def search_medicine(request):
    keyword = request.GET.get("keyword")
    medicines = Medicine.objects.all()
    if keyword:
        medicines = Medicine.objects.search(keyword)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        results = [
            {
                "id": m.id,
                "name": m.name,
                "generic_name": m.generic_name,
                "form": m.form,
                "strength": m.strength,
            }
            for m in medicines
        ]
        return JsonResponse({"results": results})
    return render(request, "search_medicine.html", {
        "medicines": medicines,
        "keyword": keyword,
    })

def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    inventories = Inventory.objects.filter(medicine=medicine).select_related("pharmacy")

    return render(request, "medicine_detail.html", {
        "medicine": medicine,
        "inventories": inventories,
    })
    
def auth_page(request):
    login_form = LoginForm()
    signup_form = SignupForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "login":
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                cd = login_form.cleaned_data
                user = User.objects.authenticate(cd["email"], cd["password"])
                if user:
                    request.session["user_id"] = user.id
                    messages.success(request, f"Welcome back {user.first_name}!")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid email or password")

        elif form_type == "register":
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                cd = signup_form.cleaned_data
                User.objects.create_user(
                    first_name=cd["first_name"],
                    last_name=cd["last_name"],
                    email=cd["email"],
                    password=cd["password"],
                )
                messages.success(request, "Account created successfully! Please login.")
                return redirect("auth_page")
            else:
                messages.error(request, "Please correct the errors below.")

    return render(request, "auth_page.html", {
        "login_form": login_form,
        "signup_form": signup_form
    })

def logout_view(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect("auth_page")

def dashboard(request):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    pharmacies = Pharmacy.objects.filter(user_id=request.session["user_id"])

    return render(request, "dashboard.html", {
        "pharmacies": pharmacies
    })


def add_pharmacy(request):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    if request.method == "POST":
        form = PharmacyForm(request.POST)
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.user_id = request.session["user_id"]
            pharmacy.save()
            messages.success(request, "Pharmacy added successfully.")
            return redirect("dashboard")
    else:
        form = PharmacyForm()
    return render(request, "pharmacy_form.html", {"form": form})

def edit_pharmacy(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    pharmacy = get_object_or_404(Pharmacy, pk=pk, user_id=request.session["user_id"])

    if request.method == "POST":
        form = PharmacyForm(request.POST, instance=pharmacy)
        if form.is_valid():
            form.save()
            messages.success(request, "Pharmacy edited successfully.")
            return redirect("dashboard")
    else:
        form = PharmacyForm(instance=pharmacy)
    return render(request, "pharmacy_form.html", {"form": form, "edit": True})

def delete_pharmacy(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")
    pharmacy = get_object_or_404(Pharmacy, pk=pk, user_id=request.session["user_id"])
    if request.method == "POST":
        pharmacy.delete()
        messages.info(request, "Pharmacy edited successfully.")
        return redirect("dashboard")

    return redirect("dashboard")

def pharmacy_inventory(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    pharmacy = get_object_or_404(Pharmacy, pk=pk, user_id=request.session["user_id"])
    inventory_items = Inventory.objects.filter(pharmacy=pharmacy)
    
    inventory_form = InventoryForm()
    medicine_form = MedicineForm()
    inventory_no_medicine_form = InventoryFormNoMedicine()
    
    context = {
        "pharmacy": pharmacy,
        "inventory_items": inventory_items,
        "inventory_form": inventory_form,
        "medicine_form": medicine_form,
        "inventory_no_medicine_form": inventory_no_medicine_form,
    }
    return render(request, "pharmacy_inventory.html", context)

def add_inventory(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    pharmacy = get_object_or_404(Pharmacy, pk=pk, user_id=request.session["user_id"])

    if request.method != "POST":
        return redirect("pharmacy_inventory", pk=pharmacy.id)

    form_type = request.POST.get("form_type")

    inventory_items = Inventory.objects.filter(pharmacy=pharmacy)

    if form_type == "existing":
        inv_form = InventoryForm(request.POST)
        if inv_form.is_valid():
            inv = inv_form.save(commit=False)
            inv.pharmacy = pharmacy
            try:
                inv.full_clean()
                inv.save()
                messages.success(request, "Inventory item added.")
                return redirect("pharmacy_inventory", pk=pharmacy.id)
            except ValidationError as e:
                inv_form.add_error(None, e)

        return render(request, "pharmacy_inventory.html", {
            "pharmacy": pharmacy,
            "inventory_items": inventory_items,
            "inventory_form": inv_form,
            "medicine_form": MedicineForm(),
            "inventory_no_medicine_form": InventoryFormNoMedicine(),
            "open_modal": "addInventoryModal",
        })

    elif form_type == "new":
        med_form = MedicineForm(request.POST)
        inv_nm_form = InventoryFormNoMedicine(request.POST)
        if med_form.is_valid() and inv_nm_form.is_valid():
            med = med_form.save(commit=False)
            med.created_by_id = request.session["user_id"]
            try:
                med.full_clean()
                med.save()

                inv = Inventory(
                    pharmacy=pharmacy,
                    medicine=med,
                    quantity=inv_nm_form.cleaned_data["quantity"],
                    price=inv_nm_form.cleaned_data["price"],
                    status=inv_nm_form.cleaned_data["status"],
                )
                inv.full_clean()
                inv.save()
                messages.success(request, "New medicine and inventory item added.")
                return redirect("pharmacy_inventory", pk=pharmacy.id)
            except ValidationError as e:
                inv_nm_form.add_error(None, e)

        return render(request, "pharmacy_inventory.html", {
            "pharmacy": pharmacy,
            "inventory_items": inventory_items,
            "inventory_form": InventoryForm(),
            "medicine_form": med_form,
            "inventory_no_medicine_form": inv_nm_form,
            "open_modal": "addMedicineModal",
        })

    return redirect("pharmacy_inventory", pk=pharmacy.id)
def edit_inventory(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    inventory = get_object_or_404(Inventory, pk=pk, pharmacy__user_id=request.session["user_id"])
    pharmacy_id = inventory.pharmacy_id
    
    if request.method == "POST":
        form = InventoryEditForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory updated.")
            return redirect("pharmacy_inventory", pk=inventory.pharmacy.id)

    return redirect("pharmacy_inventory", pk=pharmacy_id)


def delete_inventory(request, pk):
    if "user_id" not in request.session:
        messages.error(request, "You should login first.")
        return redirect("auth_page")

    inventory = get_object_or_404(Inventory, pk=pk, pharmacy__user_id=request.session["user_id"])
    pharmacy_id = inventory.pharmacy_id
    
    if request.method == "POST":
        inventory.delete()
        messages.info(request, "Inventory deleted.")
        return redirect("pharmacy_inventory", pk=pharmacy_id)

    return redirect("pharmacy_inventory", pk=pharmacy_id)
