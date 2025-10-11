from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    # Authentcation
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.get_user_profile, name="user_profile"),

    # Store management
    path("store/create/", views.create_store, name="create_store"),
    path("store/", views.manage_store, name="manage_store"),

    # Admin functions
    path("admin/pending-sellers/", views.get_pending_sellers, name="pending_sellers"),
    path("admin/approve-seller/<int:user_id>/", views.approve_seller, name="approve_seller"),
]

