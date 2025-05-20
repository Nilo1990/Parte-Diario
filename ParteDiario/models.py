from django.db import models
from django.contrib.auth.models import User

class Provincia(models.Model):
    nombre = models.CharField(max_length=50, unique=True, null=True)
    
    def __str__(self):
        return f"{self.nombre}"

class Municipio(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"{self.provincia} - {self.nombre}"

class Servicio(models.Model):
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
    
    nombre = models.CharField(max_length=50, choices=TIPO_SERVICIO, unique=True)
    
    def __str__(self):
        return f"{self.get_nombre_display()}"

class ParteDiario(models.Model):
    fecha = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Parte {self.id} - {self.municipio} ({self.fecha})"

class RegistroServicio(models.Model):
    parte = models.ForeignKey(ParteDiario, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    pendientes = models.PositiveIntegerField(default=0)
    ejecutados_dia = models.PositiveIntegerField(default=0)
    ejecutados_mes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.servicio} - Pend: {self.pendientes} | Ejec: {self.ejecutados_dia}/{self.ejecutados_mes}"

class PendientesPorEdad(models.Model):
    registro = models.ForeignKey(RegistroServicio, on_delete=models.CASCADE)
    rango_edad = models.CharField(max_length=20, choices=[
        ('>10', 'Más de 10 días'),
        ('11-30', 'De 11 a 30 días'),
        ('31-90', 'De 31 a 90 días'),
        ('91-180', 'De 91 a 180 días'),
        ('>180', 'Más de 180 días'),
        ('>1año', 'Más de 1 año'),
    ])
    cantidad = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.registro} - {self.get_rango_edad_display()}: {self.cantidad}"

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

class LogCambios(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modelo_afectado = models.CharField(max_length=50)
    accion = models.CharField(max_length=10, choices=[
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
    ])
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField()
    
    def __str__(self):
        return f"{self.fecha} - {self.usuario} {self.get_accion_display()} {self.modelo_afectado}"