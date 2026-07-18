from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Cliente, ConfiguracionEmpresa, Conversacion, OrdenTrabajo


class ConfiguracionEmpresaTests(TestCase):
    def test_get_config_crea_y_recupera_la_configuracion(self):
        ConfiguracionEmpresa.objects.all().delete()

        config = ConfiguracionEmpresa.get_config()

        self.assertTrue(ConfiguracionEmpresa.objects.filter(pk=config.pk).exists())
        self.assertIsNotNone(config.nombre_empresa)

    def test_admin_redirige_al_formulario_de_edicion(self):
        user = get_user_model().objects.create_superuser('admin_test', 'admin@example.com', 'password123')
        self.client.force_login(user)
        ConfiguracionEmpresa.get_config()

        response = self.client.get('/admin/gestion/configuracionempresa/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/change/', response.url)


class WhatsAppWebhookTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.cliente = Cliente.objects.create(nombre='Cliente Prueba', telefono='999999999')
        self.orden = OrdenTrabajo.objects.create(cliente=self.cliente, descripcion='Pedido de prueba')

    def test_webhook_crea_conversacion(self):
        response = self.client.post(
            reverse('whatsapp_webhook'),
            {
                'from': '51999999999',
                'text': 'Hola, necesito una nueva orden',
                'order_id': self.orden.id,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Conversacion.objects.filter(mensaje='Hola, necesito una nueva orden').exists())
