from django.urls import path
from . import views

urlpatterns = [
    # Reviews
    path("api/reviews/add/", views.add_review, name="add_review"),
    path("api/reviews/<int:pk>/", views.update_review, name="update_review"),
    path("api/reviews/<int:pk>/delete/", views.delete_review, name="delete_review"),
    path(
        "api/reviews/product/<int:product_id>/",
        views.get_product_reviews,
        name="product_reviews",
    ),
    path("api/reviews/user/", views.get_user_reviews, name="user_reviews"),
    # Seller reviews
    path("api/seller/reviews/", views.get_store_product_reviews, name="store_reviews"),
]
