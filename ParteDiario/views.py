from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Provincia, Municipio, ParteDiario, EnergiaRecuperada, Queja, ServicioRegistro
from django.contrib.auth import logout
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError

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

class ParteDiarioListView(LoginRequiredMixin, ListView):
    model = ParteDiario
    template_name = 'partediario/list.html'  # Ruta similar a municipios
    context_object_name = 'partes'
    paginate_by = 10
    ordering = ['-fecha']  # Ordenar por fecha descendente

class ParteDiarioCreateView(LoginRequiredMixin, CreateView):
    model = ParteDiario
    template_name = 'partediario/form.html'
    fields = ['municipio']  # Campos editables (usuario y fecha son automáticos)
    success_url = reverse_lazy('partediario-list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user  # Asigna el usuario autenticado
        return super().form_valid(form)

class ParteDiarioUpdateView(LoginRequiredMixin, UpdateView):
    model = ParteDiario
    template_name = 'partediario/form.html'
    fields = ['municipio']
    success_url = reverse_lazy('partediario-list')

class ParteDiarioDeleteView(LoginRequiredMixin, DeleteView):
    model = ParteDiario
    template_name = 'partediario/confirm_delete.html'
    success_url = reverse_lazy('partediario-list')

    
class ParteDiarioDetailView(LoginRequiredMixin, DetailView):
    model = ParteDiario
    template_name = 'partediario/detail.html'
    context_object_name = 'parte'


class EnergiaRecuperadaListView(LoginRequiredMixin, ListView):
    model = EnergiaRecuperada
    template_name = 'energia/list.html'
    context_object_name = 'energias'
    ordering = ['-parte__fecha']
    paginate_by = 10

class EnergiaRecuperadaCreateView(LoginRequiredMixin, CreateView):
    model = EnergiaRecuperada
    template_name = 'energia/form.html'
    fields = ['parte', 'plan_mwh', 'real_mwh']
    success_url = reverse_lazy('energia-list')

    def form_valid(self, form):
        # Validación adicional
        if form.cleaned_data['plan_mwh'] < 0 or form.cleaned_data['real_mwh'] < 0:
            form.add_error(None, "Los valores de energía no pueden ser negativos")
            return self.form_invalid(form)
        return super().form_valid(form)

class EnergiaRecuperadaUpdateView(LoginRequiredMixin, UpdateView):
    model = EnergiaRecuperada
    template_name = 'energia/form.html'
    fields = ['parte', 'plan_mwh', 'real_mwh']
    success_url = reverse_lazy('energia-list')

class EnergiaRecuperadaDeleteView(LoginRequiredMixin, DeleteView):
    model = EnergiaRecuperada
    template_name = 'energia/confirm_delete.html'
    success_url = reverse_lazy('energia-list')

class EnergiaRecuperadaDetailView(LoginRequiredMixin, DetailView):
    model = EnergiaRecuperada
    template_name = 'energia/detail.html'
    context_object_name = 'energia'


class QuejaListView(LoginRequiredMixin, ListView):
    model = Queja
    template_name = 'quejas/list.html'
    context_object_name = 'quejas'
    ordering = ['-parte__fecha']
    paginate_by = 10

class QuejaCreateView(LoginRequiredMixin, CreateView):
    model = Queja
    template_name = 'quejas/form.html'
    fields = ['parte', 'recibidas', 'resueltas']
    success_url = reverse_lazy('queja-list')

    def form_valid(self, form):
        # Validación: resueltas no puede ser mayor que recibidas
        if form.cleaned_data['resueltas'] > form.cleaned_data['recibidas']:
            form.add_error('resueltas', "No pueden resolverse más quejas de las recibidas")
            return self.form_invalid(form)
        return super().form_valid(form)

class QuejaUpdateView(LoginRequiredMixin, UpdateView):
    model = Queja
    template_name = 'quejas/form.html'
    fields = ['parte', 'recibidas', 'resueltas']
    success_url = reverse_lazy('queja-list')

    def form_valid(self, form):
        if form.cleaned_data['resueltas'] > form.cleaned_data['recibidas']:
            form.add_error('resueltas', "No pueden resolverse más quejas de las recibidas")
            return self.form_invalid(form)
        return super().form_valid(form)

class QuejaDeleteView(LoginRequiredMixin, DeleteView):
    model = Queja
    template_name = 'quejas/confirm_delete.html'
    success_url = reverse_lazy('queja-list')

class QuejaDetailView(LoginRequiredMixin, DetailView):
    model = Queja
    template_name = 'quejas/detail.html'
    context_object_name = 'queja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['porcentaje_resueltas'] = (self.object.resueltas / self.object.recibidas) * 100 if self.object.recibidas > 0 else 0
        return context

class ServicioRegistroListView(LoginRequiredMixin, ListView):
    model = ServicioRegistro
    template_name = 'servicios/list.html'
    context_object_name = 'servicios'
    ordering = ['-fecha_registro']
    paginate_by = 10

class ServicioRegistroCreateView(LoginRequiredMixin, CreateView):
    model = ServicioRegistro
    template_name = 'servicios/form.html'
    fields = ['parte', 'tipo_servicio', 'pendientes', 'ejecutados_dia', 'ejecutados_mes', 'fecha_registro']
    success_url = reverse_lazy('servicio-list')

    def form_valid(self, form):
        # Validación personalizada (ejemplo: no permitir pendientes negativos)
        if form.cleaned_data['pendientes'] < 0:
            form.add_error('pendientes', "Los pendientes no pueden ser negativos")
            return self.form_invalid(form)
        return super().form_valid(form)

class ServicioRegistroUpdateView(LoginRequiredMixin, UpdateView):
    model = ServicioRegistro
    template_name = 'servicios/form.html'
    fields = ['parte', 'tipo_servicio', 'pendientes', 'ejecutados_dia', 'ejecutados_mes', 'fecha_registro']
    success_url = reverse_lazy('servicio-list')

class ServicioRegistroDeleteView(LoginRequiredMixin, DeleteView):
    model = ServicioRegistro
    template_name = 'servicios/confirm_delete.html'
    success_url = reverse_lazy('servicio-list')

class ServicioRegistroDetailView(LoginRequiredMixin, DetailView):
    model = ServicioRegistro
    template_name = 'servicios/detail.html'
    context_object_name = 'servicio'