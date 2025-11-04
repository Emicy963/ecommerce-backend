from django.urls import path
from . import views


urlpatterns = [
    # Wishlist
    path("", views.get_user_wishlist, name="get_user_wishlist"),
    path("add/", views.add_to_wishlist, name="add_to_wishlist"),
    path("<int:pk>/", views.delete_wishlist_item, name="delete_wishlist_item"),
]
