"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from gestion import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/nuevo/', views.cliente_nuevo, name='cliente_nuevo'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),
    path('ordenes/', views.ordenes, name='ordenes'),
    path('ordenes/nueva/', views.orden_nueva, name='orden_nueva'),
    path('ordenes/<int:pk>/', views.orden_detalle, name='orden_detalle'),
    path('ordenes/<int:pk>/editar/', views.orden_editar, name='orden_editar'),
    path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
]
