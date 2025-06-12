Modelo de base de datos:
### 1. Usuarios (`users`)

Esta tabla almacenará la información de los usuarios que pueden crear y gestionar eventos.

- `user_id` (PK): Identificador único del usuario.
- `username`: Nombre de usuario.
- `email`: Correo electrónico.
- `company`: Nombre de la empresa.
- `password`: Contraseña (asegurada con hash).
- `created_at`: Fecha y hora de creación del usuario.
- `updated_at`: Fecha y hora de la última actualización del perfil del usuario.


### 2. Eventos (`events`)

Esta tabla contendrá los datos de los eventos creados por los usuarios.

- `event_id` (PK): Identificador único del evento.
- `company` (FK): Identificador de la empresa que organiza el evento.
- `title`: Título del evento.
- `description`: Descripción del evento.
- `location`: Ubicación del evento.
- `start_time`: Fecha y hora de inicio del evento.
- `end_time`: Fecha y hora de finalización del evento.
- `is_paid_event`: Booleano que indica si el evento es de pago.
- `created_at`: Fecha y hora de creación del evento.
- `updated_at`: Fecha y hora de la última actualización del evento.

### 3. Categorías de Boletos (`ticket_categories`)

Esta tabla contendrá las diferentes categorías de boletos disponibles para los eventos.

- `ticket_category_id` (PK): Identificador único de la categoría de boletos.
- `event_id` (FK): Identificador del evento.
- `name`: Nombre de la categoría (ej. "General", "VIP").
- `price`: Precio de la categoría de boletos.

### 4. Archivos Adjuntos (`attachments`)

Esta tabla almacenará los archivos adjuntos relacionados con los eventos, como pantallazos de confirmación de pago.

- `attachment_id` (PK): Identificador único del archivo adjunto.
- `event_id` (FK): Identificador del evento relacionado.
- `file_path`: Ruta o URL del archivo adjunto.
- `uploaded_at`: Fecha y hora de subida del archivo.


### 5. Asistentes (`attendees`)

Esta tabla manejará la información de los asistentes a los eventos, la cual es ingresada por el creador del evento.

- `attendee_id` (PK): Identificador único del asistente.
- `event_id` (FK): Identificador del evento.
- `ticket_category_id` (FK): Identificador de la categoría de boletos comprada.
- `name`: Nombre del asistente.
- `email`: Correo electrónico del asistente.
- `ticket_confirmed`: Booleano que indica si el pago del evento ha sido confirmado.
- `created_at`: Fecha y hora de creación del registro del asistente.
- `attachment_id` (PK): Identificador único del archivo adjunto.


### 6. Gastos (`expenses`)

Esta tabla manejará la gestión del presupuesto y los gastos relacionados con cada evento, incluyendo facturas.

- `expense_id` (PK): Identificador único del gasto.
- `event_id` (FK): Identificador del evento.
- `description`: Descripción del gasto.
- `amount`: Monto del gasto.
- `invoice_path`: Ruta o URL de la factura (si existe).
- `created_at`: Fecha y hora de creación del gasto.

### 7. Ingresos (`revenues`)

Esta tabla manejará los ingresos relacionados con cada evento, incluyendo las ventas de boletos y otras ganancias internas.

- `revenue_id` (PK): Identificador único del ingreso.
- `event_id` (FK): Identificador del evento.
- `description`: Descripción del ingreso (ej. "Venta de boletos", "Venta de comida").
- `amount`: Monto del ingreso.
- `created_at`: Fecha y hora de creación del ingreso.

### Relaciones entre tablas

- **Usuarios y Eventos**: Relación uno a muchos (un usuario puede crear múltiples eventos).
- **Eventos y Categorías de Boletos**: Relación uno a muchos (un evento puede tener múltiples categorías de boletos).
- **Eventos y Asistentes**: Relación uno a muchos (un evento puede tener múltiples asistentes).
- **Categorías de Boletos y Asistentes**: Relación uno a muchos (una categoría de boletos puede tener múltiples asistentes).
- **Eventos y Archivos Adjuntos**: Relación uno a muchos (un evento puede tener múltiples archivos adjuntos).
- **Eventos y Categorías**: Relación muchos a muchos (un evento puede pertenecer a múltiples categorías y una categoría puede tener múltiples eventos).
- **Eventos y Gastos**: Relación uno a muchos (un evento puede tener múltiples gastos presupuestarios).
- **Eventos y Ingresos**: Relación uno a muchos (un evento puede tener múltiples ingresos).
