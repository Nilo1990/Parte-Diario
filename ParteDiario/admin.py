from django.contrib import admin
from .models import Municipio, ParteDiario, EnergiaRecuperada, Queja, LogCambios, Provincia, ServicioRegistro

admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(ParteDiario)
admin.site.register(EnergiaRecuperada)
admin.site.register(Queja)
admin.site.register(LogCambios)
admin.site.register(ServicioRegistro)

