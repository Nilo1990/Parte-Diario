from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        return {
            'num_notificaciones': Notificacion.objects.filter(usuario=request.user, leida=False).count(),
            'notificaciones_no_leidas': Notificacion.objects.filter(usuario=request.user, leida=False).order_by('-fecha_creacion')[:5]
        }
    return {}