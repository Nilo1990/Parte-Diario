from django.contrib.auth import views as auth_views
from django.urls import path
from .views import (MunicipioListView, MunicipioCreateView, 
                MunicipioUpdateView, MunicipioDeleteView,
                dashboard, home_redirect, custom_logout, ProvinciaListView, ProvinciaCreateView, 
                ProvinciaUpdateView, ProvinciaDeleteView, ParteDiarioListView, ParteDiarioCreateView,
                ParteDiarioUpdateView, ParteDiarioDeleteView, ParteDiarioDetailView,
                EnergiaRecuperadaListView, EnergiaRecuperadaCreateView, 
                EnergiaRecuperadaUpdateView, EnergiaRecuperadaDeleteView,
                EnergiaRecuperadaDetailView, QuejaListView, QuejaCreateView, 
                QuejaUpdateView, QuejaDeleteView,
                QuejaDetailView, ServicioRegistroListView, ServicioRegistroCreateView, 
                ServicioRegistroUpdateView, ServicioRegistroDeleteView,
                ServicioRegistroDetailView, ContactoAdminView, ContactoAdminListView, Reportes, ClientesMorososDetailView,ClientesMorososDeleteView, ClientesMorososUpdateView, ClientesMorososListView, ClientesMorososCreateView, ) 

from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', home_redirect, name='home-redirect'),

    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('img/favicon.ico')
    )),

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

    path('partediario/', ParteDiarioListView.as_view(), name='partediario-list'),
    path('partediario/nuevo/', ParteDiarioCreateView.as_view(), name='partediario-create'),
    path('partediario/editar/<int:pk>/', ParteDiarioUpdateView.as_view(), name='partediario-update'),
    path('partediario/eliminar/<int:pk>/', ParteDiarioDeleteView.as_view(), name='partediario-delete'),
    path('parte/<int:pk>/', ParteDiarioDetailView.as_view(), name='partediario-detail'),
    
    path('energia/', EnergiaRecuperadaListView.as_view(), name='energia-list'),
    path('energia/nuevo/', EnergiaRecuperadaCreateView.as_view(), name='energia-create'),
    path('energia/<int:pk>/', EnergiaRecuperadaDetailView.as_view(), name='energia-detail'),
    path('energia/<int:pk>/editar/', EnergiaRecuperadaUpdateView.as_view(), name='energia-update'),
    path('energia/<int:pk>/eliminar/', EnergiaRecuperadaDeleteView.as_view(), name='energia-delete'),

    path('quejas/', QuejaListView.as_view(), name='queja-list'),
    path('quejas/nuevo/', QuejaCreateView.as_view(), name='queja-create'),
    path('quejas/<int:pk>/', QuejaDetailView.as_view(), name='queja-detail'),
    path('quejas/<int:pk>/editar/', QuejaUpdateView.as_view(), name='queja-update'),
    path('quejas/<int:pk>/eliminar/', QuejaDeleteView.as_view(), name='queja-delete'),
    
    path('servicios/', ServicioRegistroListView.as_view(), name='servicio-list'),
    path('servicios/nuevo/', ServicioRegistroCreateView.as_view(), name='servicio-create'),
    path('servicios/<int:pk>/', ServicioRegistroDetailView.as_view(), name='servicio-detail'),
    path('servicios/<int:pk>/editar/', ServicioRegistroUpdateView.as_view(), name='servicio-update'),
    path('servicios/<int:pk>/eliminar/', ServicioRegistroDeleteView.as_view(), name='servicio-delete'),

    path('contacto/', ContactoAdminView.as_view(), name='contacto-admin'),
    path('contacto/historial/', ContactoAdminListView.as_view(), name='contacto-list'),

    path('reportes/', Reportes, name='reportes-list'),
    path('reportes/energia/', views.reporte_energia, name='reporte-energia'),
    path('reportes/quejas/', views.reporte_quejas, name='reporte-quejas'),
    path('reportes/servicios/', views.reporte_servicios, name='reporte-servicios'),
    
    path('clientes-morosos/', ClientesMorososListView.as_view(), name='clientesmorosos-list'),
    path('clientes-morosos/nuevo/', ClientesMorososCreateView.as_view(), name='clientesmorosos-create'),
    path('clientes-morosos/editar/<int:pk>/', ClientesMorososUpdateView.as_view(), name='clientesmorosos-update'),
    path('clientes-morosos/eliminar/<int:pk>/', ClientesMorososDeleteView.as_view(), name='clientesmorosos-delete'),
    path('clientes-morosos/<int:pk>/', ClientesMorososDetailView.as_view(), name='clientesmorosos-detail'),
                    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

