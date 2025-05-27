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
        upload_to='contacto/adjuntos/',
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