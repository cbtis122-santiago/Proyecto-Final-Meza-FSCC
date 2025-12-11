from .models import Carrito

def carrito_context(request):
    """
    Procesador de contexto para que el número de items en el carrito
    esté disponible en todas las plantillas.
    """
    if request.user.is_authenticated:
        # Contar el número total de artículos (sumando cantidades) para el usuario actual
        num_items = sum(item.cantidad for item in Carrito.objects.filter(usuario=request.user))
    else:
        num_items = 0
    
    return {'num_items_carrito': num_items}
