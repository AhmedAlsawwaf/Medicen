from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_medicine, name="search_medicine"),
    path("auth/", views.auth_page, name="auth_page"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("pharmacy/add/", views.add_pharmacy, name="add_pharmacy"),
    path("pharmacy/<int:pk>/edit/", views.edit_pharmacy, name="edit_pharmacy"),
    path("pharmacy/<int:pk>/delete/", views.delete_pharmacy, name="delete_pharmacy"),
    
    path("pharmacy/<int:pk>/inventory/", views.pharmacy_inventory, name="pharmacy_inventory"),
    path("pharmacy/<int:pk>/inventory/add/", views.add_inventory, name="add_inventory"),
    path("inventory/<int:pk>/edit/", views.edit_inventory, name="edit_inventory"),
    path("inventory/<int:pk>/delete/", views.delete_inventory, name="delete_inventory"),
    
    path("medicine/<int:pk>/", views.medicine_detail, name="medicine_detail"),

]
