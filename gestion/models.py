from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ConfiguracionEmpresa(models.Model):
    nombre_empresa = models.CharField(max_length=150, default='Grafimaster', verbose_name='Nombre de la empresa')
    descripcion_sistema = models.TextField(default='Sistema de gestión moderno para clientes, órdenes y conversaciones.', verbose_name='Descripción del sistema')
    slogan = models.CharField(max_length=200, blank=True, default='Gestión profesional para tu empresa.', verbose_name='Slogan')

    class Meta:
        verbose_name = 'Configuración de empresa'
        verbose_name_plural = 'Configuración de empresa'

    def __str__(self):
        return self.nombre_empresa

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={
            'nombre_empresa': 'Grafimaster',
            'descripcion_sistema': 'Sistema de gestión moderno para clientes, órdenes y conversaciones.',
            'slogan': 'Gestión profesional para tu empresa.',
        })
        return obj


class Cliente(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre/Razón Social')
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    redes_sociales = models.CharField(max_length=100, blank=True, null=True, help_text='Ej: Facebook, Instagram')
    es_recurrente = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes_creados')

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.nombre


class OrdenTrabajo(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente de adelanto'),
        ('Diseno', 'En diseño'),
        ('Correccion', 'En corrección'),
        ('Validado', 'Validado para producción'),
        ('Produccion', 'En producción (Plotter/Impresión)'),
        ('Entregado', 'Entregado al cliente'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordenes')
    descripcion = models.TextField(help_text='Ej: Gigantografía 3x2m, Tarjetas personales')
    especificaciones = models.TextField(blank=True, null=True, help_text='Detalles técnicos: Tipo de lona, ojales, etc.')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    observaciones = models.TextField(blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes_asignadas')

    class Meta:
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f'Orden #{self.id} - {self.cliente.nombre}'


class Pago(models.Model):
    METODOS = [
        ('Efectivo', 'Efectivo'),
        ('Yape', 'Yape'),
        ('Plin', 'Plin'),
        ('Transferencia', 'Transferencia Bancaria'),
    ]

    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name='pago')
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_adelanto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    metodo_pago = models.CharField(max_length=20, choices=METODOS, default='Efectivo')

    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_adelanto

    def clean(self):
        if self.orden.estado == 'Entregado' and self.saldo_pendiente > 0:
            raise ValidationError("No se puede marcar como 'Entregado' si hay un saldo pendiente.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Pago Orden #{self.orden.id} - Saldo: S/ {self.saldo_pendiente}'


class Conversacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='conversaciones', blank=True, null=True)
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='conversaciones', blank=True, null=True)
    remitente = models.CharField(max_length=20, choices=[('cliente', 'Cliente'), ('staff', 'Staff')], default='cliente')
    mensaje = models.TextField()
    canal = models.CharField(max_length=20, default='whatsapp')
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_envio']

    def __str__(self):
        return f'{self.remitente}: {self.mensaje[:40]}'
