from django.urls import path
from rest_framework.authtoken import views

from .views import registration_view, logout_view
# from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView  ##JWT_Token


urlpatterns = [
    path('login/', views.obtain_auth_token, name="login"),
    path('register/', registration_view, name="register"),
    path('logout/', logout_view , name="logout"),

    ##JWT_Token
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
]

