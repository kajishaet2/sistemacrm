from django import forms

from .models import Cliente, OrdenTrabajo, Pago


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'redes_sociales', 'es_recurrente', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['cliente', 'descripcion', 'especificaciones', 'estado', 'observaciones', 'fecha_entrega', 'asignado_a']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'especificaciones': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto_total', 'monto_adelanto', 'metodo_pago']
