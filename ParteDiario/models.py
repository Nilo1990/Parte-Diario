from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Provincia(models.Model):
    nombre = models.CharField(max_length=50, unique=True, null=True)
    
    def __str__(self):
        return f"{self.nombre}"

class Municipio(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"{self.provincia} - {self.nombre}"

class ParteDiario(models.Model):
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Parte {self.id} - {self.municipio} ({self.fecha})"

class EnergiaRecuperada(models.Model):
    parte = models.ForeignKey(ParteDiario, on_delete=models.CASCADE)
    plan_mwh = models.DecimalField(max_digits=10, decimal_places=2)
    real_mwh = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Energía: Plan {self.plan_mwh} MWh | Real {self.real_mwh} MWh"

class Queja(models.Model):
    parte = models.ForeignKey(ParteDiario, on_delete=models.CASCADE)
    recibidas = models.PositiveIntegerField(default=0)
    resueltas = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Quejas: {self.recibidas} recibidas | {self.resueltas} resueltas"

class ServicioRegistro(models.Model):
    TIPO_SERVICIO = [
        ('NUEVO', 'Nuevo Servicio'),
        ('VOLTAJE', 'Cambio de Voltaje'),
        ('LUGAR', 'Cambio de Lugar'),
        ('ENERGIA', 'Energía Recuperada'),
        ('QUEJAS', 'Gestión de Quejas'),
        ('FRAUDES', 'Fraudes Detectados'),
        ('CORTES', 'Cortes Ejecutados'),
        ('MOROSIDAD', 'Gestión de Morosidad'),
        ('MEDIDORES', 'Medidores Defectuosos'),
        ('TENDEDERAS', 'Corte a Tendederas'),
    ]
    
    parte = models.ForeignKey('ParteDiario', on_delete=models.CASCADE, related_name='servicios')
    tipo_servicio = models.CharField(
        max_length=20,
        choices=TIPO_SERVICIO,
        verbose_name="Tipo de Servicio"
    )
    pendientes = models.PositiveIntegerField(
        default=0,
        verbose_name="Pendientes",
        help_text="Casos pendientes al inicio del día"
    )
    ejecutados_dia = models.PositiveIntegerField(
        default=0,
        verbose_name="Ejecutados hoy",
        help_text="Casos resueltos en el día"
    )
    ejecutados_mes = models.PositiveIntegerField(
        default=0,
        verbose_name="Ejecutados mes",
        help_text="Acumulado mensual"
    )
    fecha_registro = models.DateField(
        default=timezone.now,  # Cambiado a default en lugar de auto_now_add
        verbose_name="Fecha de registro"
    )

    class Meta:
        verbose_name = "Registro de Servicio"
        verbose_name_plural = "Registros de Servicios"
        unique_together = ('parte', 'tipo_servicio')
        ordering = ['-fecha_registro', 'tipo_servicio']

    def __str__(self):
        return (f"{self.get_tipo_servicio_display()} | "
                f"P: {self.pendientes} | "
                f"Día: {self.ejecutados_dia} | "
                f"Mes: {self.ejecutados_mes}")

    def save(self, *args, **kwargs):
        """Actualiza automáticamente el acumulado mensual"""
        # Asegurarse de que la fecha está establecida
        if not self.fecha_registro:
            self.fecha_registro = timezone.now().date()
            
        # Solo para nuevos registros
        if not self.pk:
            # Buscar registros del mismo mes y servicio
            ultimo_registro = ServicioRegistro.objects.filter(
                tipo_servicio=self.tipo_servicio,
                fecha_registro__year=self.fecha_registro.year,
                fecha_registro__month=self.fecha_registro.month
            ).order_by('-fecha_registro').first()
            
            if ultimo_registro:
                self.ejecutados_mes = ultimo_registro.ejecutados_mes + self.ejecutados_dia
            else:
                self.ejecutados_mes = self.ejecutados_dia
                
        super().save(*args, **kwargs)

class ContactoAdministrador(models.Model):
    TIPO_CONSULTA = [
        ('ERROR', 'Reportar un error'),
        ('SUGERENCIA', 'Hacer una sugerencia'),
        ('CONSULTA', 'Realizar una consulta'),
        ('OTRO', 'Otro asunto'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contactos')
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_consulta = models.CharField(
        max_length=20,
        choices=TIPO_CONSULTA,
        default='CONSULTA',
        verbose_name="Tipo de consulta"
    )
    asunto = models.CharField(max_length=100, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje detallado")
    adjunto = models.FileField(
        upload_to='static/adjuntos/',
        null=True,
        blank=True,
        verbose_name="Adjuntar archivo (opcional)"
    )
    respondido = models.BooleanField(default=False, verbose_name="¿Respondido?")
    notas_admin = models.TextField(blank=True, null=True, verbose_name="Notas del administrador")

    class Meta:
        verbose_name = "Contacto con Administrador"
        verbose_name_plural = "Contactos con Administradores"
        ordering = ['-fecha', 'respondido']

    def __str__(self):
        return f"Contacto de {self.usuario.username} - {self.get_tipo_consulta_display()} ({self.fecha.date()})"
    
    
class ClientesMorosos(models.Model):
    ESTADO_GESTION_CHOICES = [  # Nombre más descriptivo
        ('PENDIENTE', 'Pendiente de gestión'),
        ('CONTACTADO', 'Cliente contactado'),
        ('ACUERDO', 'Acuerdo de pago establecido'),
        ('PAGADO', 'Deuda saldada'),
        ('CORTADO', 'Servicio cortado'),
        ('RECONECTADO', 'Servicio reconectado'),
    ]
    
    parte = models.ForeignKey(
        'ParteDiario', 
        on_delete=models.CASCADE, 
        related_name='clientes_morosos',
        verbose_name="Parte diario asociado"
    )
    codigo_cliente = models.CharField(
        max_length=20,
        verbose_name="Código de cliente",
        help_text="Número de identificación del cliente en el sistema"
    )
    nombre_cliente = models.CharField(
        max_length=100,
        verbose_name="Nombre completo"
    )
    direccion = models.CharField(
        max_length=200,
        verbose_name="Dirección del servicio"
    )
    municipio = models.ForeignKey(
        'Municipio',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Municipio del cliente"
    )
    deuda_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto total adeudado (CUP)"
    )
    meses_morosidad = models.PositiveIntegerField(
        verbose_name="Meses de morosidad"
    )
    fecha_ultimo_pago = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha del último pago realizado"
    )
    estado_gestion = models.CharField(
        max_length=20,
        choices=ESTADO_GESTION_CHOICES,  # Usando el nombre correcto
        default='PENDIENTE',
        verbose_name="Estado de gestión"
    )
    acciones_realizadas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Acciones realizadas",
        help_text="Detalle de las gestiones realizadas con el cliente"
    )
    fecha_proximo_contacto = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha próxima gestión"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas adicionales"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    usuario_registro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clientes_registrados',
        verbose_name="Usuario que registró"
    )

    class Meta:
        verbose_name = "Cliente Moroso"
        verbose_name_plural = "Clientes Morosos"
        ordering = ['-fecha_registro', 'municipio']
        unique_together = ('parte', 'codigo_cliente')

    def __str__(self):
        return f"{self.codigo_cliente} - {self.nombre_cliente} ({self.get_estado_gestion_display()})"
    
    
class OficinaComercial(models.Model):
    provincia = models.ForeignKey(Provincia, null=True,on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, null=True, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.provincia})"

class RegistroRecaudacion(models.Model):
    MESES = [
        ('ENERO', 'Enero'),
        ('FEBRERO', 'Febrero'),
        ('MARZO', 'Marzo'),
        ('ABRIL', 'Abril'),
        ('MAYO', 'Mayo'),
        ('JUNIO', 'Junio'),
        ('JULIO', 'Julio'),
        ('AGOSTO', 'Agosto'),
        ('SEPTIEMBRE', 'Septiembre'),
        ('OCTUBRE', 'Octubre'),
        ('NOVIEMBRE', 'Noviembre'),
        ('DICIEMBRE', 'Diciembre'),
    ]
    
    oficina = models.ForeignKey(OficinaComercial, on_delete=models.CASCADE, related_name='recaudaciones')
    año = models.PositiveIntegerField()
    mes = models.CharField(max_length=15, choices=MESES)
    
    # Campos de deuda
    deuda_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_cobrada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Campos para gestión de cortes
    plan_cortes_diario = models.PositiveIntegerField(default=0)
    clientes_cortados_dia = models.PositiveIntegerField(default=0)
    cortes_acumulados_mes = models.PositiveIntegerField(default=0)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Registro de Recaudación"
        verbose_name_plural = "Registros de Recaudación"
        unique_together = ('oficina', 'año', 'mes')
        ordering = ['año', 'mes', 'oficina']
    
    def __str__(self):
        return f"{self.oficina} - {self.mes}/{self.año}"

class ResumenAnualRecaudacion(models.Model):
    oficina = models.ForeignKey(OficinaComercial, on_delete=models.CASCADE, related_name='resumenes_anuales')
    año = models.PositiveIntegerField()
    
    # Totales anuales
    deuda_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cobrado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Desglose por años anteriores (para historial)
    deuda_2021 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_2022 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deuda_2023 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Resumen Anual de Recaudación"
        verbose_name_plural = "Resúmenes Anuales de Recaudación"
        unique_together = ('oficina', 'año')
        ordering = ['-año', 'oficina']
    
    def __str__(self):
        return f"Resumen {self.oficina} - {self.año}"

class HistorialMorosidad(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('GESTIONADO', 'Gestionado'),
        ('ACUERDO_PAGO', 'Acuerdo de pago'),
        ('PAGADO', 'Pagado'),
        ('CORTADO', 'Servicio cortado'),
    ]
    
    oficina = models.ForeignKey(OficinaComercial, on_delete=models.CASCADE, related_name='morosidad')
    cliente_id = models.CharField(max_length=20)
    nombre_cliente = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    
    # Datos de morosidad
    deuda_total = models.DecimalField(max_digits=12, decimal_places=2)
    meses_morosidad = models.PositiveIntegerField()
    fecha_ultimo_pago = models.DateField(null=True, blank=True)
    
    # Gestión
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    acciones_realizadas = models.TextField(blank=True, null=True)
    fecha_proximo_contacto = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True, null=True)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = "Historial de Morosidad"
        verbose_name_plural = "Historiales de Morosidad"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.cliente_id} - {self.nombre_cliente} ({self.get_estado_display()})"