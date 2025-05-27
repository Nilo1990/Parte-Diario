from django import forms
from .models import ContactoAdministrador
from django.core.validators import FileExtensionValidator

class ContactoAdminForm(forms.ModelForm):
    class Meta:
        model = ContactoAdministrador
        fields = ['tipo_consulta', 'asunto', 'mensaje', 'adjunto']
        widgets = {
            'tipo_consulta': forms.Select(attrs={
                'class': 'form-select',
                'style': 'margin-bottom: 15px;'
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resumen breve de tu consulta'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu consulta con el mayor detalle posible...'
            }),
            'adjunto': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.png,.xls,.xlsx'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['adjunto'].validators = [
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'xls', 'xlsx'])
        ]
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.usuario = self.user
        if commit:
            instance.save()
        return instance