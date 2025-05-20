from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (MunicipioListView, MunicipioCreateView, 
                   MunicipioUpdateView, MunicipioDeleteView,
                   dashboard, home_redirect, custom_logout, ProvinciaListView, ProvinciaCreateView, 
                    ProvinciaUpdateView, ProvinciaDeleteView) 

urlpatterns = [
    path('', home_redirect, name='home-redirect'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', custom_logout, name='logout'), 
    
    path('dashboard/', dashboard, name='dashboard'),

    path('municipios/', MunicipioListView.as_view(), name='municipio-list'),
    path('municipios/nuevo/', MunicipioCreateView.as_view(), name='municipio-create'),
    path('municipios/editar/<int:pk>/', MunicipioUpdateView.as_view(), name='municipio-update'),
    path('municipios/eliminar/<int:pk>/', MunicipioDeleteView.as_view(), name='municipio-delete'),

    path('provincias/', ProvinciaListView.as_view(), name='provincia-list'),
    path('provincias/nuevo/', ProvinciaCreateView.as_view(), name='provincia-create'),
    path('provincias/editar/<int:pk>/', ProvinciaUpdateView.as_view(), name='provincia-update'),
    path('provincias/eliminar/<int:pk>/', ProvinciaDeleteView.as_view(), name='provincia-delete'),
    
]