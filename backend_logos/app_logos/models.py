
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# Modelo para Autores, corresponde a la tabla 'Autores'
class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True)
    biografia = models.TextField(blank=True, help_text="Biografía del autor")
    nacionalidad = models.CharField(max_length=50, blank=True)
    foto_url = models.URLField(blank=True, null=True, help_text="URL de la foto del autor")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name_plural = "Autores"

# Modelo para Categorías de libros, corresponde a la tabla 'Categorias'
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="Versión amigable del nombre para URLs")
    categoria_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias', help_text="Categoría padre para anidar categorías")
    imagen_url = models.URLField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

# Modelo para los Libros, corresponde a la tabla 'Libros' (antes 'Producto')
class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='libros')
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    imagen = models.ImageField(upload_to='libros/', default='libros/default.png', help_text="Imagen de portada del libro")
    activo = models.BooleanField(default=True, help_text="Indica si el libro está disponible en la tienda")
    destacado = models.BooleanField(default=False, help_text="Marcar para que aparezca en la página de inicio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# Modelo de Perfil de Usuario, complementa el modelo User de Django para representar 'Clientes'
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    direccion_envio = models.TextField(blank=True, help_text="Dirección completa para envíos")
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    es_administrador = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

# Hook para crear/actualizar el perfil de usuario automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(usuario=instance)

# Modelo para el Carrito de Compras
class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'libro')

    @property
    def subtotal(self):
        return self.libro.precio * self.cantidad

# Modelo para las Órdenes, corresponde a la tabla 'Ordenes' (antes 'Pedido')
class Orden(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
    ]

    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordenes')
    fecha_orden = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='tarjeta')
    banco_tarjeta = models.CharField(max_length=50, blank=True, help_text="Banco emisor de la tarjeta")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Orden #{self.id} de {self.cliente.username}"

# Modelo para los Detalles de la Orden, corresponde a la tabla 'Detallesorden' (antes 'ItemPedido')
class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unidad = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.libro.titulo}"
