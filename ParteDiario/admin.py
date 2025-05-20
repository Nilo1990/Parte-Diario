from django.contrib import admin
from .models import Municipio, Servicio, ParteDiario, RegistroServicio, PendientesPorEdad, EnergiaRecuperada, Queja, LogCambios, Provincia

admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(Servicio)
admin.site.register(ParteDiario)
admin.site.register(RegistroServicio)
admin.site.register(PendientesPorEdad)
admin.site.register(EnergiaRecuperada)
admin.site.register(Queja)
admin.site.register(LogCambios)