from django.urls import path
from . import views

urlpatterns = [
    # Reviews
    path("add/", views.add_review, name="add_review"),
    path("<int:pk>/", views.update_review, name="update_review"),
    path("<int:pk>/delete/", views.delete_review, name="delete_review"),
    path(
        "product/<int:product_id>/",
        views.get_product_reviews,
        name="product_reviews",
    ),
    path("user/", views.get_user_reviews, name="user_reviews"),
    # Seller reviews
    path("reviews/", views.get_store_product_reviews, name="store_reviews"),
]
