from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Cliente, ConfiguracionEmpresa, Conversacion, OrdenTrabajo, Pago


@admin.register(ConfiguracionEmpresa)
class ConfiguracionEmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'slogan')

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ConfiguracionEmpresa.get_config()
        return HttpResponseRedirect(reverse('admin:gestion_configuracionempresa_change', args=[obj.pk]))

    def add_view(self, request, form_url='', extra_context=None):
        obj = ConfiguracionEmpresa.get_config()
        return HttpResponseRedirect(reverse('admin:gestion_configuracionempresa_change', args=[obj.pk]))


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'es_recurrente', 'fecha_registro')
    search_fields = ('nombre', 'telefono', 'email')


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estado', 'fecha_entrega', 'asignado_a')
    list_filter = ('estado',)
    search_fields = ('cliente__nombre', 'descripcion')


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('orden', 'monto_total', 'monto_adelanto', 'metodo_pago')


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'orden', 'remitente', 'canal', 'fecha_envio')
    search_fields = ('mensaje',)
