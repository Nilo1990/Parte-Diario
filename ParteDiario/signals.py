from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ParteDiario, Notificacion

@receiver(post_save, sender=ParteDiario)
def crear_notificacion_parte(sender, instance, created, **kwargs):
    if created:
        # Notificar a todos los usuarios staff excepto al creador
        usuarios = User.objects.filter(is_staff=True).exclude(id=instance.usuario.id)
        
        for usuario in usuarios:
            Notificacion.objects.create(
                usuario=usuario,
                mensaje=f"Nuevo parte diario creado en {instance.municipio.nombre}",
                tipo='PARTE',
                url=f"/parte/{instance.id}/",  # URL para ver el detalle del parte
                parte=instance
            )