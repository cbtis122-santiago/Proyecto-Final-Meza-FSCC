
from django.urls import path
from . import views

urlpatterns = [
    # Páginas estáticas
    path('', views.inicio, name='inicio'),
    path('tienda/', views.tienda, name='tienda'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    
    # Usuarios y Perfil
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),

    # Carrito y Proceso de Compra
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:libro_id>/', views.agregar_al_carrito, name='agregar_al_carrito'), 
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),

    # Órdenes de Usuario
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('confirmacion-compra/<int:pedido_id>/', views.confirmacion_compra, name='confirmacion_compra'),
    
    # --- RUTAS DE ADMINISTRACIÓN DE PRODUCTOS ---
    path('admin/productos/', views.admin_productos, name='admin_productos'),
    path('admin/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('admin/productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # --- RUTAS DE ADMINISTRACIÓN DE PEDIDOS Y USUARIOS ---
    path('admin/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/pedidos/cambiar-estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

]
