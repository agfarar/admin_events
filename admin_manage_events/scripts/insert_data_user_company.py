import os
import sys
import django
from datetime import datetime
import pytz

# Añadir el directorio raíz del proyecto al PYTHONPATH.
# Esto permite que Python pueda encontrar los módulos del proyecto Django.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Establecer la configuración de Django para el proyecto.
# 'admin_manage_events.settings' es el módulo de configuración del proyecto.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_manage_events.settings')

# Configurar Django para que esté listo para usar los modelos y otras configuraciones.
django.setup()

# Importar el modelo de usuario personalizado.
from django.contrib.auth import get_user_model

# Importar los modelos de Company y Event desde la aplicación 'events'.
from apps.events.models import Company, Event

# Crear una nueva instancia de la compañía.
# 'name' es el nombre de la compañía que se está creando.
company = Company.objects.create(name='My Company')
company_two = Company.objects.create(name='Test Company')

# Obtener el modelo de usuario.
User = get_user_model()

# Crear un superusuario asociado con la compañía creada.
# Se especifican el nombre de usuario, el correo electrónico, la contraseña y la compañía.
superuser = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='password123',
    company=company
)

# Crear un nuevo evento asociado con la compañía.
# Se especifican el título, la descripción, la ubicación, la hora de inicio, la hora de finalización y si es un evento pagado.
# Convertir los tiempos a objetos "aware" con zona horaria.
timezone = pytz.timezone('UTC')  # Cambia 'UTC' a tu zona horaria preferida si es necesario.
start_time_naive = datetime.strptime('2024-06-26 10:00:00', '%Y-%m-%d %H:%M:%S')
end_time_naive = datetime.strptime('2024-06-26 12:00:00', '%Y-%m-%d %H:%M:%S')
start_time = timezone.localize(start_time_naive)
end_time = timezone.localize(end_time_naive)

event = Event.objects.create(
    company=company,
    title='My Event',
    description='This is a test event.',
    location='Event Location',
    start_time=start_time,
    end_time=end_time,
    is_paid_event=True
)

# Imprimir un mensaje de confirmación indicando que la compañía, el superusuario y el evento se crearon correctamente.
print('Company, superuser, and event created successfully.')


# Crear un usuario normal con permisos estándar (sin superusuario)
test_user = User.objects.create_user(
    username='test',
    email='test@example.com',
    password='password123',
    company=company_two,  # Asigna la compañía si es necesario
    is_staff=True  # Marca como personal con permisos administrativos

)

# Agregar todos los permisos, excepto el de superusuario
test_user.is_superuser = False
test_user.save()

print('Usuario "test" creado con permisos estándar.')
