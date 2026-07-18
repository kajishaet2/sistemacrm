import json
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import ClienteForm, OrdenTrabajoForm, PagoForm
from .models import Cliente, Conversacion, OrdenTrabajo, Pago


def cerrar_sesion(request):
    auth_logout(request)
    request.session.flush()
    response = redirect('login')
    response.delete_cookie('sessionid')
    return response


@login_required
def dashboard(request):
    clientes = Cliente.objects.count()
    ordenes = OrdenTrabajo.objects.count()
    pendientes = OrdenTrabajo.objects.filter(estado='Pendiente').count()
    entregadas = OrdenTrabajo.objects.filter(estado='Entregado').count()
    ordenes_recientes = OrdenTrabajo.objects.select_related('cliente').order_by('-fecha_ingreso')[:5]
    clientes_recientes = Cliente.objects.order_by('-fecha_registro')[:5]
    return render(request, 'dashboard.html', {
        'clientes': clientes,
        'ordenes': ordenes,
        'pendientes': pendientes,
        'entregadas': entregadas,
        'ordenes_recientes': ordenes_recientes,
        'clientes_recientes': clientes_recientes,
    })


@login_required
def clientes(request):
    texto = request.GET.get('q', '')
    queryset = Cliente.objects.all()
    if texto:
        queryset = queryset.filter(Q(nombre__icontains=texto) | Q(telefono__icontains=texto) | Q(email__icontains=texto))
    return render(request, 'clientes/list.html', {'clientes': queryset, 'texto': texto})


@login_required
def cliente_nuevo(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.creado_por = request.user
            cliente.save()
            messages.success(request, 'Cliente registrado correctamente.')
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'accion': 'Crear cliente'})


@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'accion': 'Editar cliente'})


@login_required
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    messages.success(request, 'Cliente eliminado.')
    return redirect('clientes')


@login_required
def ordenes(request):
    texto = request.GET.get('q', '')
    queryset = OrdenTrabajo.objects.select_related('cliente', 'asignado_a')
    if texto:
        queryset = queryset.filter(Q(descripcion__icontains=texto) | Q(cliente__nombre__icontains=texto))
    return render(request, 'ordenes/list.html', {'ordenes': queryset, 'texto': texto})


@login_required
def orden_nueva(request):
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save()
            messages.success(request, 'Orden creada correctamente.')
            return redirect('orden_detalle', pk=orden.id)
    else:
        form = OrdenTrabajoForm()
    return render(request, 'ordenes/form.html', {'form': form, 'accion': 'Crear orden'})


@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    pago = getattr(orden, 'pago', None)
    pago_form = PagoForm(instance=pago) if pago else PagoForm()
    conversaciones = orden.conversaciones.all()[:10]

    if request.method == 'POST' and 'monto_total' in request.POST:
        pago_form = PagoForm(request.POST, instance=pago)
        if pago_form.is_valid():
            pago_obj = pago_form.save(commit=False)
            pago_obj.orden = orden
            pago_obj.save()
            messages.success(request, 'Pago registrado correctamente.')
            return redirect('orden_detalle', pk=orden.id)

    return render(request, 'ordenes/detail.html', {
        'orden': orden,
        'pago_form': pago_form,
        'conversaciones': conversaciones,
    })


@login_required
def orden_editar(request, pk):
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orden actualizada.')
            return redirect('orden_detalle', pk=orden.id)
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, 'ordenes/form.html', {'form': form, 'accion': 'Editar orden'})


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == settings.WHATSAPP_VERIFY_TOKEN:
            return JsonResponse(challenge, safe=False)
        return JsonResponse({'status': 'invalid'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'status': 'ok'})

    if request.content_type == 'application/json':
        data = json.loads(request.body.decode('utf-8'))
    else:
        data = request.POST.dict()

    if 'entry' not in data and 'from' in data and 'text' in data:
        data = {'entry': [{'changes': [{'value': {'messages': [{'from': data.get('from'), 'text': {'body': data.get('text')}}]}}]}]}

    entries = data.get('entry') or []
    for entry in entries:
        changes = entry.get('changes') or []
        for change in changes:
            value = change.get('value') or {}
            messages = value.get('messages') or []
            for message in messages:
                phone = message.get('from') or ''
                text = ''
                if message.get('text'):
                    text = message['text'].get('body', '')
                if phone and text:
                    cliente, _ = Cliente.objects.get_or_create(
                        telefono=phone,
                        defaults={'nombre': f'Cliente {phone}', 'observaciones': 'Creado desde WhatsApp'}
                    )
                    Conversacion.objects.create(cliente=cliente, remitente='cliente', mensaje=text, canal='whatsapp')

    return JsonResponse({'status': 'received'})


def enviar_mensaje_whatsapp(destino, mensaje):
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        return {'ok': False, 'error': 'Faltan credenciales de WhatsApp'}

    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': destino,
        'type': 'text',
        'text': {'body': mensaje},
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return {'ok': True, 'response': response.json()}
    except requests.RequestException as exc:
        return {'ok': False, 'error': str(exc)}
