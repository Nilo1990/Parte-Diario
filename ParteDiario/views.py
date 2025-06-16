from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.conf import settings
from .models import Provincia, Municipio, ParteDiario, EnergiaRecuperada, Queja, ServicioRegistro, ContactoAdministrador, ClientesMorosos, OficinaComercial
from django.contrib import messages
from .forms import ContactoAdminForm
from django.db.models import Sum

from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import Provincia, Municipio, ParteDiario, EnergiaRecuperada, Queja, ServicioRegistro
from django.db.models import Sum
from .models import EnergiaRecuperada, Queja, ServicioRegistro, ParteDiario
from datetime import datetime, timedelta

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


def home_redirect(request):
    """Redirige a la raíz del sistema según autenticación"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

@login_required
def dashboard(request):
    # Obtener la fecha de hoy
    hoy = datetime.now().date()
    
    # Estadísticas generales
    provincias_count = Provincia.objects.count()
    municipios_count = Municipio.objects.count()
    partes_hoy_count = ParteDiario.objects.filter(fecha=hoy).count()
    
    # Energía recuperada hoy
    energia_hoy = EnergiaRecuperada.objects.filter(parte__fecha=hoy).aggregate(
        total_plan=Sum('plan_mwh'),
        total_real=Sum('real_mwh')
    )
    energia_recuperada = energia_hoy['total_real'] or 0
    
    # Quejas hoy
    quejas_hoy = Queja.objects.filter(parte__fecha=hoy).aggregate(
        recibidas=Sum('recibidas'),
        resueltas=Sum('resueltas')
    )
    quejas_recibidas = quejas_hoy.get('recibidas', 0) or 0
    quejas_resueltas = quejas_hoy.get('resueltas', 0) or 0
    
    # Porcentaje de quejas resueltas
    try:
        porcentaje_resueltas = (quejas_resueltas / quejas_recibidas * 100) if quejas_recibidas > 0 else 0
    except ZeroDivisionError:
        porcentaje_resueltas = 0
    
    # Servicios ejecutados hoy por tipo
    servicios_hoy = ServicioRegistro.objects.filter(fecha_registro=hoy).values(
        'tipo_servicio'
    ).annotate(
        total=Sum('ejecutados_dia')
    ).order_by('-total')
    
    servicios_count = sum(item['total'] for item in servicios_hoy)
    
    # Distribución de servicios por tipo (para gráfico circular)
    servicios_tipo_data = [
        {'tipo': item['tipo_servicio'], 
         'cantidad': item['total'],
         'label': dict(ServicioRegistro.TIPO_SERVICIO)[item['tipo_servicio']]}
        for item in servicios_hoy
    ]
    
    # Actividad reciente (últimos 5 partes)
    ultimos_partes = ParteDiario.objects.select_related('municipio', 'municipio__provincia').order_by('-fecha')[:5]
    actividad_reciente = [{
        'titulo': f"Parte en {parte.municipio.nombre} ({parte.municipio.provincia.nombre})",
        'fecha': parte.fecha,
        'icono': 'clipboard',
        'usuario': parte.usuario.username
    } for parte in ultimos_partes]
    
    # Gráficos de tendencia (últimos 7 días)
    fechas = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
    
    # Datos para gráfico de energía
    energia_data = []
    for fecha in fechas:
        energia = EnergiaRecuperada.objects.filter(parte__fecha=fecha).aggregate(
            plan=Sum('plan_mwh'),
            real=Sum('real_mwh')
        )
        energia_data.append({
            'fecha': fecha,
            'plan': energia.get('plan', 0) or 0,
            'real': energia.get('real', 0) or 0
        })
    
    # Datos para gráfico de quejas
    quejas_data = []
    for fecha in fechas:
        quejas = Queja.objects.filter(parte__fecha=fecha).aggregate(
            recibidas=Sum('recibidas'),
            resueltas=Sum('resueltas')
        )
        recibidas = quejas.get('recibidas', 0) or 0
        resueltas = quejas.get('resueltas', 0) or 0
        
        try:
            porcentaje = (resueltas / recibidas * 100) if recibidas > 0 else 0
        except ZeroDivisionError:
            porcentaje = 0
            
        quejas_data.append({
            'fecha': fecha,
            'recibidas': recibidas,
            'resueltas': resueltas,
            'porcentaje': porcentaje
        })
    
    # Datos para gráfico de distribución por provincia
    provincias_data = []
    partes_por_provincia = ParteDiario.objects.filter(
        fecha__gte=hoy - timedelta(days=30)
    ).values(
        'municipio__provincia__nombre'
    ).annotate(
        total=Count('id'),
        energia=Sum('energiarecuperada__real_mwh'),
        quejas=Sum('queja__recibidas')
    ).order_by('-total')
    
    for provincia in provincias_data:
        morosidad = ClientesMorosos.objects.filter(
            municipio__provincia__nombre=provincia['nombre'],
            fecha_registro__gte=hoy - timedelta(days=30)
        ).aggregate(
            total_deuda=Sum('deuda_total')
        )
        provincia['deuda'] = morosidad['total_deuda'] or 0
    
    context = {
        'provincias_count': provincias_count,
        'municipios_count': municipios_count,
        'partes_hoy_count': partes_hoy_count,
        'servicios_count': servicios_count,
        'servicios_tipo_data': servicios_tipo_data,
        'energia_recuperada': energia_recuperada,
        'quejas_recibidas': quejas_recibidas,
        'quejas_resueltas': quejas_resueltas,
        'porcentaje_resueltas': porcentaje_resueltas,
        'actividad_reciente': actividad_reciente,
        'energia_data': energia_data,
        'quejas_data': quejas_data,
        'provincias_data': provincias_data,
        'fechas_chart': [fecha.strftime('%d-%m') for fecha in fechas],
        'hoy': hoy.strftime('%d de %B de %Y'),
    }
    
    
     # Datos de clientes morosos
    hoy = datetime.now().date()
    morosos_hoy = ClientesMorosos.objects.filter(fecha_registro__date=hoy)
    morosos_count = morosos_hoy.count()
    deuda_total = morosos_hoy.aggregate(total=Sum('deuda_total'))['total'] or 0
    
    # Top 5 clientes con mayor deuda
    top_morosos = ClientesMorosos.objects.order_by('-deuda_total')[:5]
    
    # Actualizar el contexto
    context.update({
        'morosos_count': morosos_count,
        'deuda_total': deuda_total,
        'top_morosos': top_morosos,
    })
    return render(request, 'dashboard.html', context)

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
    fields = ['provincia','nombre']
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parte = self.object
        
        # 1. Servicios Registrados (pueden ser múltiples)
        context['servicios'] = ServicioRegistro.objects.filter(parte=parte)
        
        # 2. Energía Recuperada (uno por parte)
        try:
            context['energia'] = EnergiaRecuperada.objects.get(parte=parte)
            context['energia'].diferencia = context['energia'].real_mwh - context['energia'].plan_mwh
        except EnergiaRecuperada.DoesNotExist:
            context['energia'] = None
        
        # 3. Quejas (ahora manejamos múltiples registros)
        quejas = Queja.objects.filter(parte=parte)
        context['quejas'] = quejas
        
        # Calculamos totales de quejas
        if quejas.exists():
            context['total_quejas_recibidas'] = quejas.aggregate(Sum('recibidas'))['recibidas__sum']
            context['total_quejas_resueltas'] = quejas.aggregate(Sum('resueltas'))['resueltas__sum']
        else:
            context['total_quejas_recibidas'] = 0
            context['total_quejas_resueltas'] = 0
        
        return context


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

class ContactoAdminView(LoginRequiredMixin, CreateView):
    model = ContactoAdministrador
    form_class = ContactoAdminForm
    template_name = 'contacto/form.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Tu mensaje ha sido enviado al administrador. Recibirás una respuesta pronto."
        )
        return response

class ContactoAdminListView(LoginRequiredMixin, ListView):
    model = ContactoAdministrador
    template_name = 'contacto/list.html'
    context_object_name = 'contactos'
    paginate_by = 10

    def get_queryset(self):
        return ContactoAdministrador.objects.filter(usuario=self.request.user).order_by('-fecha')
    
def Reportes(request):
        return render(request, 'reportes/reportes.html')

def reporte_energia(request):
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Filtrar datos
    partes = ParteDiario.objects.all()
    if fecha_inicio and fecha_fin:
        partes = partes.filter(fecha__range=[fecha_inicio, fecha_fin])
    
    # Obtener datos de energía
    datos_energia = []
    for parte in partes:
        energia = EnergiaRecuperada.objects.filter(parte=parte).first()
        if energia:
            datos_energia.append({
                'fecha': parte.fecha,
                'municipio': parte.municipio,
                'plan': energia.plan_mwh,
                'real': energia.real_mwh,
                'diferencia': float(energia.real_mwh) - float(energia.plan_mwh),
            })
    
    # Estadísticas
    total_plan = sum(item['plan'] for item in datos_energia)
    total_real = sum(item['real'] for item in datos_energia)
    
    context = {
        'datos': datos_energia,
        'total_plan': total_plan,
        'total_real': total_real,
        'diferencia_total': total_real - total_plan,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'reportes/reporte_energia.html', context)

def reporte_quejas(request):
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Filtrar datos
    partes = ParteDiario.objects.all()
    if fecha_inicio and fecha_fin:
        partes = partes.filter(fecha__range=[fecha_inicio, fecha_fin])
    
    # Obtener datos de quejas
    datos_quejas = []
    for parte in partes:
        queja = Queja.objects.filter(parte=parte).first()
        if queja:
            porcentaje = (queja.resueltas / queja.recibidas * 100) if queja.recibidas > 0 else 0
            datos_quejas.append({
                'fecha': parte.fecha,
                'municipio': parte.municipio,
                'recibidas': queja.recibidas,
                'resueltas': queja.resueltas,
                'pendientes': queja.recibidas - queja.resueltas,
                'porcentaje': round(porcentaje, 2),
            })
    
    # Estadísticas
    total_recibidas = sum(item['recibidas'] for item in datos_quejas)
    total_resueltas = sum(item['resueltas'] for item in datos_quejas)
    porcentaje_total = (total_resueltas / total_recibidas * 100) if total_recibidas > 0 else 0
    
    context = {
        'datos': datos_quejas,
        'total_recibidas': total_recibidas,
        'total_resueltas': total_resueltas,
        'porcentaje_total': round(porcentaje_total, 2),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'reportes/reporte_quejas.html', context)

def reporte_servicios(request):
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo_servicio = request.GET.get('tipo_servicio')
    
    # Filtrar datos
    servicios = ServicioRegistro.objects.all()
    if fecha_inicio and fecha_fin:
        servicios = servicios.filter(fecha_registro__range=[fecha_inicio, fecha_fin])
    if tipo_servicio:
        servicios = servicios.filter(tipo_servicio=tipo_servicio)
    
    # Agrupar por tipo de servicio
    tipos_servicio = dict(ServicioRegistro.TIPO_SERVICIO)
    datos_servicios = {}
    
    for servicio in servicios:
        tipo = servicio.get_tipo_servicio_display()
        if tipo not in datos_servicios:
            datos_servicios[tipo] = {
                'pendientes': 0,
                'ejecutados_dia': 0,
                'ejecutados_mes': 0,
                'detalles': []
            }
        
        datos_servicios[tipo]['pendientes'] += servicio.pendientes
        datos_servicios[tipo]['ejecutados_dia'] += servicio.ejecutados_dia
        datos_servicios[tipo]['ejecutados_mes'] += servicio.ejecutados_mes
        datos_servicios[tipo]['detalles'].append({
            'fecha': servicio.fecha_registro,
            'municipio': servicio.parte.municipio,
            'pendientes': servicio.pendientes,
            'ejecutados_dia': servicio.ejecutados_dia,
            'ejecutados_mes': servicio.ejecutados_mes,
        })
    
    context = {
        'datos': datos_servicios,
        'tipos_servicio': tipos_servicio,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tipo_seleccionado': tipo_servicio,
        
    }
    return render(request, 'reportes/reporte_servicios.html', context)

class ClientesMorososListView(LoginRequiredMixin, ListView):
    model = ClientesMorosos
    template_name = 'clientesmorosos/list.html'
    context_object_name = 'clientes'
    paginate_by = 10
    ordering = ['-fecha_registro']

class ClientesMorososCreateView(LoginRequiredMixin, CreateView):
    model = ClientesMorosos
    template_name = 'clientesmorosos/form.html'
    fields = ['parte', 'codigo_cliente', 'nombre_cliente', 'direccion', 'municipio', 
              'deuda_total', 'meses_morosidad', 'fecha_ultimo_pago', 
              'estado_gestion', 'acciones_realizadas', 'fecha_proximo_contacto', 'notas']
    success_url = reverse_lazy('clientesmorosos-list')

    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        return super().form_valid(form)

class ClientesMorososUpdateView(LoginRequiredMixin, UpdateView):
    model = ClientesMorosos
    template_name = 'clientesmorosos/form.html'
    fields = ['parte', 'codigo_cliente', 'nombre_cliente', 'direccion', 'municipio', 
              'deuda_total', 'meses_morosidad', 'fecha_ultimo_pago', 
              'estado_gestion', 'acciones_realizadas', 'fecha_proximo_contacto', 'notas']
    success_url = reverse_lazy('clientesmorosos-list')

class ClientesMorososDeleteView(LoginRequiredMixin, DeleteView):
    model = ClientesMorosos
    template_name = 'clientesmorosos/confirm_delete.html'
    success_url = reverse_lazy('clientesmorosos-list')

class ClientesMorososDetailView(LoginRequiredMixin, DetailView):
    model = ClientesMorosos
    template_name = 'clientesmorosos/detail.html'
    context_object_name = 'cliente'
    
class OficinaComercialListView(LoginRequiredMixin, ListView):
    model = OficinaComercial
    template_name = 'oficinacomercial/list.html'
    context_object_name = 'oficinas'
    paginate_by = 10
    ordering = ['provincia__nombre', 'nombre']

    def get_queryset(self):
        queryset = super().get_queryset()
        provincia_id = self.request.GET.get('provincia')
        municipio_id = self.request.GET.get('municipio')
        
        if provincia_id:
            queryset = queryset.filter(provincia_id=provincia_id)
        if municipio_id:
            queryset = queryset.filter(municipio_id=municipio_id)
            
        return queryset.select_related('provincia', 'municipio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['provincias'] = Provincia.objects.all()
        context['municipios'] = Municipio.objects.all()
        return context

class OficinaComercialCreateView(LoginRequiredMixin, CreateView):
    model = OficinaComercial
    template_name = 'oficinacomercial/form.html'
    fields = ['provincia', 'municipio', 'nombre']
    success_url = reverse_lazy('oficinacomercial-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Mostrar todos los municipios inicialmente
        form.fields['municipio'].queryset = Municipio.objects.all()
        
        # Si hay una provincia en el GET request, filtrar municipios
        if 'provincia' in self.request.GET:
            try:
                provincia_id = int(self.request.GET.get('provincia'))
                form.fields['municipio'].queryset = Municipio.objects.filter(
                    provincia_id=provincia_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                pass
                
        return form

    def form_valid(self, form):
        # Validación adicional para asegurar que el municipio pertenece a la provincia
        municipio = form.cleaned_data.get('municipio')
        provincia = form.cleaned_data.get('provincia')
        
        if municipio and provincia and municipio.provincia != provincia:
            form.add_error('municipio', 'El municipio seleccionado no pertenece a la provincia elegida')
            return self.form_invalid(form)
            
        return super().form_valid(form)

class OficinaComercialUpdateView(LoginRequiredMixin, UpdateView):
    model = OficinaComercial
    template_name = 'oficinacomercial/form.html'
    fields = ['provincia', 'municipio', 'nombre']
    success_url = reverse_lazy('oficinacomercial-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if form.instance.provincia:
            form.fields['municipio'].queryset = Municipio.objects.filter(provincia=form.instance.provincia)
        else:
            form.fields['municipio'].queryset = Municipio.objects.none()
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Oficina comercial actualizada exitosamente')
        return super().form_valid(form)

class OficinaComercialDeleteView(LoginRequiredMixin, DeleteView):
    model = OficinaComercial
    template_name = 'oficinacomercial/confirm_delete.html'
    success_url = reverse_lazy('oficinacomercial-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Oficina comercial eliminada exitosamente')
        return super().delete(request, *args, **kwargs)

class OficinaComercialDetailView(LoginRequiredMixin, DetailView):
    model = OficinaComercial
    template_name = 'oficinacomercial/detail.html'
    context_object_name = 'oficina'
    
def municipios_por_provincia(request, provincia_id):
    municipios = Municipio.objects.filter(
        provincia_id=provincia_id
    ).order_by('nombre').values('id', 'nombre')
    
    return JsonResponse(
        list(municipios), 
        safe=False, 
        encoder=DjangoJSONEncoder
    )
