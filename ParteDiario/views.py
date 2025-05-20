from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Provincia, Municipio, Servicio
from django.contrib.auth import logout
from django.conf import settings

def home_redirect(request):
    """Redirige a la raíz del sistema según autenticación"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

class ProvinciaListView(LoginRequiredMixin, ListView):
    model = Provincia
    template_name = 'provincias/list.html'
    context_object_name = 'provincias'
    paginate_by = 10
    ordering = ['nombre']

class ProvinciaCreateView(LoginRequiredMixin, CreateView):
    model = Provincia
    template_name = 'provincias/form.html'
    fields = ['nombre']
    success_url = reverse_lazy('provincia-list')

class ProvinciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Provincia
    template_name = 'provincias/form.html'
    fields = ['nombre']
    success_url = reverse_lazy('provincia-list')

class ProvinciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Provincia
    template_name = 'provincias/confirm_delete.html'
    success_url = reverse_lazy('provincia-list')

class MunicipioListView(LoginRequiredMixin, ListView):
    model = Municipio
    template_name = 'municipios/list.html'
    context_object_name = 'municipios'
    paginate_by = 10

class MunicipioCreateView(LoginRequiredMixin, CreateView):
    model = Municipio
    template_name = 'municipios/form.html'
    fields = ['nombre']
    success_url = reverse_lazy('municipio-list')

class MunicipioUpdateView(LoginRequiredMixin, UpdateView):
    model = Municipio
    template_name = 'municipios/form.html'
    fields = ['nombre']
    success_url = reverse_lazy('municipio-list')

class MunicipioDeleteView(LoginRequiredMixin, DeleteView):
    model = Municipio
    template_name = 'municipios/confirm_delete.html'
    success_url = reverse_lazy('municipio-list')

def custom_logout(request):
    """Vista personalizada para cerrar sesión que siempre redirige al login"""
    logout(request)
    # Redirige a LOGIN_URL configurado en settings o directamente a 'login'
    return redirect(getattr(settings, 'LOGIN_URL', 'login'))

