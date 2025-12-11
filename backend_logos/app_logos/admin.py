from django.contrib import admin
from .models import Autor, Categoria, Libro, PerfilUsuario, Orden, DetalleOrden, Carrito

# Personalización para el panel de administración

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'nacionalidad')
    search_fields = ('nombre', 'apellido')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'categoria_padre', 'activa')
    prepopulated_fields = {'slug': ('nombre',)}
    list_filter = ('activa', 'categoria_padre')
    search_fields = ('nombre', 'slug') # <-- Added this line

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'precio', 'stock', 'activo', 'destacado')
    list_filter = ('activo', 'destacado', 'categoria', 'autor')
    search_fields = ('titulo', 'autor__nombre', 'autor__apellido')
    autocomplete_fields = ('autor', 'categoria') # Mejora la selección de autor y categoría

class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    raw_id_fields = ['libro']
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_orden', 'total', 'estado')
    list_filter = ('estado', 'fecha_orden')
    search_fields = ('cliente__username', 'id')
    inlines = [DetalleOrdenInline]
    readonly_fields = ('fecha_orden', 'total', 'subtotal', 'costo_envio')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'ciudad', 'es_administrador')
    search_fields = ('usuario__username',)

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'cantidad', 'fecha_agregado')
    list_filter = ('usuario', 'fecha_agregado')
