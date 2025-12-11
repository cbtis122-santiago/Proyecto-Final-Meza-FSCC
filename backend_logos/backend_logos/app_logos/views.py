
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import Libro, Categoria, Autor, PerfilUsuario, Carrito, Orden, DetalleOrden
from .forms import RegistroForm
import uuid
from django.utils import timezone
import re

# ========== DECORADOR DE ADMINISTRADOR ==========
def es_administrador(user):
    return user.is_authenticated and user.is_staff

admin_required = user_passes_test(es_administrador, login_url='inicio')

# ========== VISTAS PRINCIPALES DE LA TIENDA ==========
def inicio(request):
    libros_destacados = Libro.objects.filter(destacado=True, activo=True)[:8]
    categorias = Categoria.objects.filter(activa=True)
    context = {
        'libros_destacados': libros_destacados,
        'categorias': categorias,
    }
    return render(request, 'app_logos/pages/inicio.html', context)

def tienda(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    libros = Libro.objects.filter(activo=True)
    if query:
        libros = libros.filter(
            Q(titulo__icontains=query) |
            Q(autor__nombre__icontains=query) |
            Q(autor__apellido__icontains=query) |
            Q(descripcion__icontains=query)
        )
    if categoria_id:
        libros = libros.filter(categoria_id=categoria_id)
    categorias = Categoria.objects.filter(activa=True)
    context = {
        'libros': libros,
        'categorias': categorias,
        'query': query,
    }
    return render(request, 'app_logos/pages/tienda.html', context)

def sobre_nosotros(request):
    return render(request, 'app_logos/pages/sobre_nosotros.html')

def contacto(request):
    if request.method == 'POST':
        messages.success(request, '¡Mensaje enviado! Te contactaremos pronto.')
        return redirect('contacto')
    return render(request, 'app_logos/pages/contacto.html')

# ========== GESTIÓN DE USUARIOS Y AUTENTICACIÓN ==========

def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Autenticar al usuario inmediatamente después del registro
            messages.success(request, f'¡Bienvenido, {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('inicio') # Redirigir a la página principal
    else:
        form = RegistroForm()
    
    return render(request, 'app_logos/usuarios/registro.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url or 'inicio')
    else:
        form = AuthenticationForm()
    return render(request, 'app_logos/usuarios/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('inicio')

@login_required
def perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        perfil.telefono = request.POST.get('telefono', '')
        perfil.direccion_envio = request.POST.get('direccion_envio', '')
        perfil.ciudad = request.POST.get('ciudad', '')
        perfil.codigo_postal = request.POST.get('codigo_postal', '')
        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('perfil')
    return render(request, 'app_logos/usuarios/perfil.html', {'perfil': perfil})

# ========== GESTIÓN DEL CARRITO DE COMPRAS ==========

def agregar_al_carrito(request, libro_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Por favor, inicia sesión para agregar productos a tu carrito.')
        return redirect(f'/login/?next={request.path}')

    libro = get_object_or_404(Libro, id=libro_id, activo=True)
    item_carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        libro=libro,
        defaults={'cantidad': 1}
    )
    if not created:
        item_carrito.cantidad += 1
        item_carrito.save()
    messages.success(request, f'\"{libro.titulo}\" fue agregado a tu carrito.')
    return redirect('carrito')

@login_required
def carrito(request):
    items_carrito = Carrito.objects.filter(usuario=request.user)
    subtotal = sum(item.subtotal for item in items_carrito)
    costo_envio = 50 if 0 < subtotal < 500 else 0
    total = subtotal + costo_envio
    faltante_para_envio_gratis = 500 - subtotal if 0 < subtotal < 500 else 0
    context = {
        'items_carrito': items_carrito,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
        'faltante_para_envio_gratis': faltante_para_envio_gratis,
    }
    return render(request, 'app_logos/carrito/carrito.html', context)

@login_required
def actualizar_carrito(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        if nueva_cantidad > 0:
            item.cantidad = nueva_cantidad
            item.save()
            messages.success(request, 'Cantidad actualizada.')
        else:
            item.delete()
            messages.info(request, 'Libro eliminado del carrito.')
    return redirect('carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    item.delete()
    messages.info(request, 'Libro eliminado del carrito.')
    return redirect('carrito')

# ========== PROCESO DE CHECKOUT Y PEDIDOS ==========

@login_required
def checkout(request):
    if request.method != 'POST':
        return redirect('carrito')

    items_carrito = Carrito.objects.filter(usuario=request.user)
    if not items_carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('tienda')

    # Recopilar datos del formulario
    direccion = request.POST.get('direccion_envio', '').strip()
    ciudad = request.POST.get('ciudad', '').strip()
    codigo_postal = request.POST.get('codigo_postal', '').strip()
    banco_tarjeta = request.POST.get('banco_tarjeta', '').strip()
    nombre_tarjeta = request.POST.get('nombre_tarjeta', '').strip()
    numero_tarjeta = request.POST.get('numero_tarjeta', '').strip()
    fecha_exp = request.POST.get('fecha_exp', '').strip()
    cvv = request.POST.get('cvv', '').strip()

    # Validación
    errors = []
    if len(direccion) < 5: errors.append('Introduce una dirección válida.')
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', ciudad): errors.append('La ciudad solo debe contener letras.')
    if not re.match(r'^\d{1,6}$', codigo_postal): errors.append('El código postal debe contener entre 1 y 6 dígitos.')
    if not banco_tarjeta: errors.append('Debes seleccionar un banco.')
    if len(nombre_tarjeta) < 3: errors.append('El nombre en la tarjeta parece muy corto.')
    if not re.match(r'^\d{16}$', numero_tarjeta.replace(' ', '')): errors.append('El número de tarjeta debe tener 16 dígitos.')
    if not re.match(r'^(0[1-9]|1[0-2])\/(\d{2})$', fecha_exp): errors.append('La fecha de expiración debe tener el formato MM/AA.')
    if not re.match(r'^\d{3,4}$', cvv): errors.append('El CVV debe tener 3 o 4 dígitos.')

    if errors:
        for error in errors:
            messages.error(request, error)
        # Aquí recargamos el contexto necesario para volver a renderizar el carrito
        items_carrito = Carrito.objects.filter(usuario=request.user)
        subtotal = sum(item.subtotal for item in items_carrito)
        costo_envio = 50 if 0 < subtotal < 500 else 0
        total = subtotal + costo_envio
        context = {
            'items_carrito': items_carrito,
            'subtotal': subtotal,
            'costo_envio': costo_envio,
            'total': total,
        }
        return render(request, 'app_logos/carrito/carrito.html', context)
    
    # Guardar datos en el perfil y crear la orden
    direccion_completa = f"{direccion}, {ciudad}, C.P. {codigo_postal}"

    perfil = request.user.perfil
    perfil.direccion_envio = direccion
    perfil.ciudad = ciudad
    perfil.codigo_postal = codigo_postal
    perfil.save()

    subtotal = sum(item.subtotal for item in items_carrito)
    costo_envio = 50 if 0 < subtotal < 500 else 0
    total = subtotal + costo_envio

    orden = Orden.objects.create(
        cliente=request.user, 
        subtotal=subtotal, 
        costo_envio=costo_envio,
        total=total, 
        direccion_envio=direccion_completa, 
        estado='pagado',
        metodo_pago='tarjeta',
        banco_tarjeta=banco_tarjeta
    )

    for item in items_carrito:
        DetalleOrden.objects.create(
            orden=orden, libro=item.libro, cantidad=item.cantidad,
            precio_unidad=item.libro.precio, subtotal=item.subtotal
        )
    
    items_carrito.delete()
    
    return redirect('confirmacion_compra', pedido_id=orden.id)

@login_required
def mis_pedidos(request):
    pedidos = request.user.ordenes.all().order_by('-fecha_orden')
    return render(request, 'app_logos/pedidos/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Orden, id=pedido_id, cliente=request.user)
    return render(request, 'app_logos/pedidos/detalle_pedido.html', {'pedido': pedido})

@login_required
def confirmacion_compra(request, pedido_id):
    pedido = get_object_or_404(Orden, id=pedido_id, cliente=request.user)
    context = {'pedido': pedido, 'titulo': '¡Compra Exitosa!'}
    return render(request, 'app_logos/pedidos/confirmacion_compra.html', context)

# ========== CRUD DE PRODUCTOS (SOLO ADMINS) ==========

@admin_required
def admin_productos(request):
    productos = Libro.objects.all().order_by('-fecha_creacion')
    return render(request, 'app_logos/productos/listar_productos.html', {'productos': productos})

@admin_required
def agregar_producto(request):
    pass

@admin_required
def editar_producto(request, pk):
    pass

@admin_required
def eliminar_producto(request, pk):
    pass

# ========== PANELES DE ADMINISTRACIÓN ADICIONALES (SOLO ADMINS) ==========

@admin_required
def admin_pedidos(request):
    pedidos = Orden.objects.all().order_by('-fecha_orden')
    return render(request, 'app_logos/pedidos/admin_pedidos.html', {
        'pedidos': pedidos,
        'titulo': 'Administrar Pedidos'
    })

@admin_required
def admin_usuarios(request):
    perfiles = PerfilUsuario.objects.all().select_related('usuario')
    return render(request, 'app_logos/usuarios/admin_usuarios.html', {
        'perfiles': perfiles,
        'titulo': 'Administrar Usuarios'
    })

@admin_required
def cambiar_estado_pedido(request, pedido_id):
    orden = get_object_or_404(Orden, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Orden.ESTADO_CHOICES):
            orden.estado = nuevo_estado
            orden.save()
            messages.success(request, f'Estado del pedido #{orden.id} actualizado a {orden.get_estado_display()}.')
    
    return redirect('admin_pedidos')
