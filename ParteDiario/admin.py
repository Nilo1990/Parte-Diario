from django.contrib import admin
from .models import Municipio, ParteDiario, EnergiaRecuperada, Queja, Provincia, ServicioRegistro, ContactoAdministrador,ClientesMorosos, OficinaComercial, RegistroRecaudacion, ResumenAnualRecaudacion, HistorialMorosidad

admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(ParteDiario)
admin.site.register(EnergiaRecuperada)
admin.site.register(Queja)
admin.site.register(ServicioRegistro)
admin.site.register(ContactoAdministrador)
admin.site.register(ClientesMorosos)
admin.site.register(OficinaComercial)
admin.site.register(RegistroRecaudacion)
admin.site.register(ResumenAnualRecaudacion)
admin.site.register(HistorialMorosidad)



