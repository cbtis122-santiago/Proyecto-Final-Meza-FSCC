
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from app_logos.models import Autor, Categoria, Libro, PerfilUsuario, Orden, DetalleOrden, Carrito

class Command(BaseCommand):
    help = 'Seeds the database with a rich and diverse set of data, including books, authors, users, and orders.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO('Starting database seeding process...'))

        self.clear_data()
        authors = self.create_authors()
        categories = self.create_categories()
        self.create_books(authors, categories)
        self.create_users_and_profiles()
        self.create_carts_and_orders()

        self.stdout.write(self.style.SUCCESS('\nDatabase seeding complete! Your bookstore is now populated with a diverse range of data.'))

    def clear_data(self):
        self.stdout.write(self.style.WARNING('\nClearing existing data...'))
        DetalleOrden.objects.all().delete()
        Orden.objects.all().delete()
        Carrito.objects.all().delete()
        Libro.objects.all().delete()
        Categoria.objects.all().delete()
        Autor.objects.all().delete()
        PerfilUsuario.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write(self.style.SUCCESS('Data cleared.'))

    def create_authors(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating Authors...'))
        authors_data = [
            ('Gabriel', 'García Márquez', 'Colombiana'), ('Julio', 'Cortázar', 'Argentina'),
            ('Jorge Luis', 'Borges', 'Argentina'), ('Mario', 'Vargas Llosa', 'Peruana'),
            ('Isabel', 'Allende', 'Chilena'), ('Juan', 'Rulfo', 'Mexicana'),
            ('Carlos', 'Fuentes', 'Mexicana'), ('Octavio', 'Paz', 'Mexicana'),
            ('Isaac', 'Asimov', 'Rusa'), ('Arthur C.', 'Clarke', 'Británica'),
            ('Frank', 'Herbert', 'Estadounidense'), ('Philip K.', 'Dick', 'Estadounidense'),
            ('William', 'Gibson', 'Estadounidense'),
            ('J.R.R.', 'Tolkien', 'Británica'), ('George R.R.', 'Martin', 'Estadounidense'),
            ('J.K.', 'Rowling', 'Británica'), ('Patrick', 'Rothfuss', 'Estadounidense'),
            ('Brandon', 'Sanderson', 'Estadounidense'),
            ('Yuval Noah', 'Harari', 'Israelí'), ('Carl', 'Sagan', 'Estadounidense'),
            ('Stephen', 'Hawking', 'Británica'), ('Michel', 'Foucault', 'Francesa'),
            ('Eduardo', 'Galeano', 'Uruguaya'),
            ('Agatha', 'Christie', 'Británica'), ('Arthur Conan', 'Doyle', 'Británica'),
            ('Gillian', 'Flynn', 'Estadounidense'), ('Stieg', 'Larsson', 'Sueca'),
            ('Jo', 'Nesbø', 'Noruega'),
            ('Miguel', 'de Cervantes', 'Española'), ('Fiódor', 'Dostoyevski', 'Rusa'),
            ('León', 'Tolstói', 'Rusa'), ('Jane', 'Austen', 'Británica'),
            ('George', 'Orwell', 'Británica'),
        ]
        authors = {}
        for nombre, apellido, nacionalidad in authors_data:
            autor, created = Autor.objects.get_or_create(
                nombre=nombre, apellido=apellido, defaults={'nacionalidad': nacionalidad, 'biografia': f'Biografía de {nombre} {apellido}'}
            )
            authors[f'{nombre} {apellido}'] = autor
            if created: self.stdout.write(f'  Autor creado: {nombre} {apellido}')
        return authors

    def create_categories(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating Categories...'))
        categories_data = [
            'Realismo Mágico y Latinoamericano', 'Ciencia Ficción Clásica', 'Fantasía Épica',
            'Ensayo y Divulgación', 'Misterio y Thriller', 'Clásicos Universales'
        ]
        categories = {}
        for name in categories_data:
            cat, created = Categoria.objects.get_or_create(nombre=name, defaults={'descripcion': f'Libros de {name}'})
            categories[name] = cat
            if created: self.stdout.write(f'  Categoría creada: {name}')
        return categories

    def create_books(self, authors, categories):
        self.stdout.write(self.style.HTTP_INFO('\nCreating Books (10 per category)...'))
        books_data = [
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Gabriel García Márquez', 'tit': 'Cien años de soledad', 'pr': 350},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Julio Cortázar', 'tit': 'Rayuela', 'pr': 330},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Jorge Luis Borges', 'tit': 'Ficciones', 'pr': 290},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Mario Vargas Llosa', 'tit': 'La ciudad y los perros', 'pr': 300},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Isabel Allende', 'tit': 'La casa de los espíritus', 'pr': 310},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Juan Rulfo', 'tit': 'Pedro Páramo', 'pr': 250},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Carlos Fuentes', 'tit': 'La región más transparente', 'pr': 320},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Octavio Paz', 'tit': 'El laberinto de la soledad', 'pr': 280},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Gabriel García Márquez', 'tit': 'El amor en los tiempos del cólera', 'pr': 340},
            {'cat': 'Realismo Mágico y Latinoamericano', 'aut': 'Eduardo Galeano', 'tit': 'Las venas abiertas de América Latina', 'pr': 360},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Isaac Asimov', 'tit': 'Fundación', 'pr': 420},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Arthur C. Clarke', 'tit': '2001: Una odisea espacial', 'pr': 400},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Frank Herbert', 'tit': 'Dune', 'pr': 480},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Philip K. Dick', 'tit': '¿Sueñan los androides con ovejas eléctricas?', 'pr': 360},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Isaac Asimov', 'tit': 'Yo, Robot', 'pr': 380},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'William Gibson', 'tit': 'Neuromante', 'pr': 390},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'George Orwell', 'tit': '1984', 'pr': 300},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Frank Herbert', 'tit': 'El mesías de Dune', 'pr': 450},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Isaac Asimov', 'tit': 'Los propios dioses', 'pr': 410},
            {'cat': 'Ciencia Ficción Clásica', 'aut': 'Philip K. Dick', 'tit': 'Ubik', 'pr': 370},
            {'cat': 'Fantasía Épica', 'aut': 'J.R.R. Tolkien', 'tit': 'El Señor de los Anillos: La Comunidad del Anillo', 'pr': 550},
            {'cat': 'Fantasía Épica', 'aut': 'George R.R. Martin', 'tit': 'Juego de Tronos', 'pr': 580},
            {'cat': 'Fantasía Épica', 'aut': 'J.K. Rowling', 'tit': 'Harry Potter y la piedra filosofal', 'pr': 400},
            {'cat': 'Fantasía Épica', 'aut': 'Patrick Rothfuss', 'tit': 'El nombre del viento', 'pr': 530},
            {'cat': 'Fantasía Épica', 'aut': 'Brandon Sanderson', 'tit': 'Mistborn: El imperio final', 'pr': 510},
            {'cat': 'Fantasía Épica', 'aut': 'J.R.R. Tolkien', 'tit': 'El Hobbit', 'pr': 450},
            {'cat': 'Fantasía Épica', 'aut': 'George R.R. Martin', 'tit': 'Choque de Reyes', 'pr': 590},
            {'cat': 'Fantasía Épica', 'aut': 'J.K. Rowling', 'tit': 'Harry Potter y la cámara secreta', 'pr': 420},
            {'cat': 'Fantasía Épica', 'aut': 'Patrick Rothfuss', 'tit': 'El temor de un hombre sabio', 'pr': 620},
            {'cat': 'Fantasía Épica', 'aut': 'Brandon Sanderson', 'tit': 'El camino de los reyes', 'pr': 650},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Yuval Noah Harari', 'tit': 'Sapiens: De animales a dioses', 'pr': 450},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Carl Sagan', 'tit': 'Cosmos', 'pr': 430},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Stephen Hawking', 'tit': 'Breve historia del tiempo', 'pr': 380},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Michel Foucault', 'tit': 'Vigilar y castigar', 'pr': 410},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Yuval Noah Harari', 'tit': 'Homo Deus: Breve historia del mañana', 'pr': 460},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Carl Sagan', 'tit': 'Un punto azul pálido', 'pr': 440},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Eduardo Galeano', 'tit': 'Espejos: Una historia casi universal', 'pr': 370},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Stephen Hawking', 'tit': 'El universo en una cáscara de nuez', 'pr': 390},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Michel Foucault', 'tit': 'Las palabras y las cosas', 'pr': 420},
            {'cat': 'Ensayo y Divulgación', 'aut': 'Yuval Noah Harari', 'tit': '21 lecciones para el siglo XXI', 'pr': 470},
            {'cat': 'Misterio y Thriller', 'aut': 'Agatha Christie', 'tit': 'Asesinato en el Orient Express', 'pr': 280},
            {'cat': 'Misterio y Thriller', 'aut': 'Arthur Conan Doyle', 'tit': 'Estudio en escarlata', 'pr': 260},
            {'cat': 'Misterio y Thriller', 'aut': 'Gillian Flynn', 'tit': 'Perdida', 'pr': 350},
            {'cat': 'Misterio y Thriller', 'aut': 'Stieg Larsson', 'tit': 'Los hombres que no amaban a las mujeres', 'pr': 380},
            {'cat': 'Misterio y Thriller', 'aut': 'Jo Nesbø', 'tit': 'El muñeco de nieve', 'pr': 360},
            {'cat': 'Misterio y Thriller', 'aut': 'Agatha Christie', 'tit': 'Diez negritos', 'pr': 290},
            {'cat': 'Misterio y Thriller', 'aut': 'Arthur Conan Doyle', 'tit': 'El sabueso de los Baskerville', 'pr': 270},
            {'cat': 'Misterio y Thriller', 'aut': 'Gillian Flynn', 'tit': 'Heridas abiertas', 'pr': 340},
            {'cat': 'Misterio y Thriller', 'aut': 'Stieg Larsson', 'tit': 'La chica que soñaba con una cerilla y un bidón de gasolina', 'pr': 390},
            {'cat': 'Misterio y Thriller', 'aut': 'Jo Nesbø', 'tit': 'Petirrojo', 'pr': 370},
            {'cat': 'Clásicos Universales', 'aut': 'Miguel de Cervantes', 'tit': 'Don Quijote de la Mancha', 'pr': 500},
            {'cat': 'Clásicos Universales', 'aut': 'Fiódor Dostoyevski', 'tit': 'Crimen y castigo', 'pr': 450},
            {'cat': 'Clásicos Universales', 'aut': 'León Tolstói', 'tit': 'Guerra y paz', 'pr': 600},
            {'cat': 'Clásicos Universales', 'aut': 'Jane Austen', 'tit': 'Orgullo y prejuicio', 'pr': 320},
            {'cat': 'Clásicos Universales', 'aut': 'George Orwell', 'tit': 'Rebelión en la granja', 'pr': 250},
            {'cat': 'Clásicos Universales', 'aut': 'Fiódor Dostoyevski', 'tit': 'Los hermanos Karamázov', 'pr': 550},
            {'cat': 'Clásicos Universales', 'aut': 'León Tolstói', 'tit': 'Anna Karénina', 'pr': 520},
            {'cat': 'Clásicos Universales', 'aut': 'Jane Austen', 'tit': 'Sentido y sensibilidad', 'pr': 310},
            {'cat': 'Clásicos Universales', 'aut': 'Miguel de Cervantes', 'tit': 'Novelas ejemplares', 'pr': 480},
            {'cat': 'Clásicos Universales', 'aut': 'George Orwell', 'tit': 'Homenaje a Cataluña', 'pr': 290},
        ]

        for data in books_data:
            libro = Libro.objects.create(
                titulo=data['tit'],
                autor=authors[data['aut']],
                categoria=categories[data['cat']],
                descripcion=f"Una obra fundamental en el género de {data['cat']}, escrita por {data['aut']}.",
                precio=data['pr'],
                stock=random.randint(5, 40),
                activo=True,
                destacado=random.choice([True, False, False, False])
            )
            self.stdout.write(f'  Libro creado: {libro.titulo}')

    def create_users_and_profiles(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating 10 Users and Profiles...'))
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@logos.com', 'admin123')
            self.stdout.write(self.style.SUCCESS("  Superuser 'admin' created with password 'admin123'."))

        first_names = ['Ana', 'Luis', 'Elena', 'Carlos', 'Sofía', 'David', 'Laura', 'Miguel', 'Isabel', 'Javier']
        last_names = ['García', 'Martínez', 'López', 'Sánchez', 'Pérez', 'Gómez', 'Díaz', 'Hernández', 'Vázquez', 'Moreno']
        for i in range(10):
            username = f'{first_names[i].lower()}{last_names[i][0].lower()}{random.randint(10,99)}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'{username}@test.com', 'password123', first_name=first_names[i], last_name=last_names[i])
                self.stdout.write(f"  User '{username}' created.")

    def create_carts_and_orders(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating 10 Orders and Carts for users...'))
        users = User.objects.filter(is_superuser=False)
        all_books = list(Libro.objects.all())

        if not all_books or not users.exists():
            self.stdout.write(self.style.WARNING('  Not enough books or users to create carts/orders.'))
            return

        for user in random.sample(list(users), min(5, len(users))):
            num_items = random.randint(1, 3)
            for book in random.sample(all_books, num_items):
                if not Carrito.objects.filter(usuario=user, libro=book).exists():
                    Carrito.objects.create(usuario=user, libro=book, cantidad=random.randint(1, 2))
            self.stdout.write(f"  Created cart with {num_items} distinct items for user '{user.username}'.")

        for i in range(10):
            user = random.choice(users)
            
            order_subtotal = Decimal('0.00')
            libros_en_orden = []
            num_items_pedido = random.randint(1, 4)

            for book in random.sample(all_books, num_items_pedido):
                cantidad = random.randint(1, 3)
                precio_unidad = book.precio
                subtotal_item = cantidad * precio_unidad
                order_subtotal += subtotal_item
                libros_en_orden.append({
                    'libro': book, 'cantidad': cantidad, 'precio_unidad': precio_unidad, 'subtotal': subtotal_item
                })

            costo_envio = Decimal('150.00')
            order_total = order_subtotal + costo_envio

            orden = Orden.objects.create(
                cliente=user,
                subtotal=order_subtotal,
                costo_envio=costo_envio,
                total=order_total,
                estado=random.choice(['pendiente', 'pagado', 'enviado', 'entregado']),
                direccion_envio=f'Calle Ficticia {i+1}, Colonia Centro, Ciudad de México'
            )
            orden.fecha_orden = timezone.now() - timezone.timedelta(days=random.randint(1, 90))
            orden.save()

            for item in libros_en_orden:
                DetalleOrden.objects.create(
                    orden=orden, 
                    libro=item['libro'], 
                    cantidad=item['cantidad'], 
                    precio_unidad=item['precio_unidad'],
                    subtotal=item['subtotal']
                )
            
            self.stdout.write(f"  Created order {orden.id} with {num_items_pedido} items for user '{user.username}'.")
