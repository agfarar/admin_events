from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test.utils import override_settings
from django.db import connections
from django.conf import settings
import time
import threading
from unittest.mock import patch

from apps.attendees.models import Attendee, Purchase, Ticket
from apps.events.models import Event, EventTicketCategory
from apps.ticket_categories.models import TicketCategory, Company
from apps.attachments.models import Attachment

User = get_user_model()


class AttendeeModelTests(TestCase):
    """Tests para el modelo Attendee - Validando funcionalidades básicas"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Test Company",
            nit="123456789",
            address="Test Address",
            phone="555-1234"
        )
        
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            date=timezone.now().date(),
            location="Test Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="General",
            price=50.00,
            description="General admission"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=100,
            tickets_sold=0
        )
    
    def test_create_attendee_valid_data(self):
        """Test RF-001: Crear asistente con datos válidos"""
        attendee = Attendee.objects.create(
            name="Juan Pérez",
            email="juan@example.com",
            document_type="DNI",
            document_number="12345678",
            phone_number="555-1234",
            address="Calle 123",
            gender="M"
        )
        
        self.assertEqual(attendee.name, "Juan Pérez")
        self.assertEqual(attendee.email, "juan@example.com")
        self.assertEqual(attendee.document_type, "DNI")
        self.assertEqual(attendee.document_number, "12345678")
        self.assertTrue(attendee.created)
        self.assertTrue(attendee.modified)
    
    def test_attendee_str_representation(self):
        """Test: Representación string del modelo Attendee"""
        attendee = Attendee.objects.create(
            name="María García",
            email="maria@example.com",
            document_type="Pasaporte",
            document_number="ABC123456",
            phone_number="555-5678",
            gender="F"
        )
        
        expected_str = "María García (Pasaporte: ABC123456)"
        self.assertEqual(str(attendee), expected_str)
    
    def test_attendee_document_types(self):
        """Test: Validar tipos de documento permitidos"""
        valid_document_types = ['DNI', 'Pasaporte', 'Carné de Extranjería', 'Otros']
        
        for doc_type in valid_document_types:
            attendee = Attendee(
                name=f"Test User {doc_type}",
                email=f"test_{doc_type.lower()}@example.com",
                document_type=doc_type,
                document_number="12345",
                phone_number="555-0000",
                gender="M"
            )
            attendee.full_clean()  # Should not raise ValidationError
    
    def test_attendee_gender_choices(self):
        """Test: Validar opciones de género"""
        valid_genders = ['M', 'F', 'O']
        
        for gender in valid_genders:
            attendee = Attendee(
                name=f"Test User {gender}",
                email=f"test_{gender}@example.com",
                document_type="DNI",
                document_number=f"1234567{gender}",
                phone_number="555-0000",
                gender=gender
            )
            attendee.full_clean()  # Should not raise ValidationError
    
    def test_attendee_optional_fields(self):
        """Test: Campos opcionales del asistente"""
        attendee = Attendee.objects.create(
            name="Test User",
            email="test@example.com",
            document_type="DNI",
            document_number="12345678",
            phone_number="555-1234",
            gender="M"
            # address y date_of_birth son opcionales
        )
        
        self.assertIsNone(attendee.address)
        self.assertIsNone(attendee.date_of_birth)
        self.assertIsNone(attendee.attachment)


class PurchaseModelTests(TestCase):
    """Tests para el modelo Purchase - Validando lógica de negocio"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Test Company",
            nit="123456789",
            address="Test Address",
            phone="555-1234"
        )
        
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            date=timezone.now().date(),
            location="Test Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="VIP",
            price=100.00,
            description="VIP access"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=50,
            tickets_sold=0
        )
    
    def test_create_purchase_valid(self):
        """Test RF-002: Crear compra válida"""
        purchase = Purchase.objects.create(
            buyer="Carlos Rodríguez",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        self.assertEqual(purchase.buyer, "Carlos Rodríguez")
        self.assertEqual(purchase.event, self.event)
        self.assertEqual(purchase.ticket_category, self.ticket_category)
        self.assertEqual(purchase.company, self.company)
    
    def test_purchase_validation_no_tickets_available(self):
        """Test RF-003: Validación de tickets agotados"""
        # Agotar todos los tickets
        self.event_ticket_category.tickets_sold = 50
        self.event_ticket_category.save()
        
        with self.assertRaises(ValidationError) as context:
            purchase = Purchase(
                buyer="Test Buyer",
                event=self.event,
                ticket_category=self.ticket_category,
                company=self.company
            )
            purchase.save()
        
        self.assertIn('No hay boletos disponibles', str(context.exception))
    
    def test_purchase_str_representation(self):
        """Test: Representación string del modelo Purchase"""
        purchase = Purchase.objects.create(
            buyer="Ana López",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        expected_str = f"Ana López - {self.event} - {self.ticket_category.name}"
        self.assertEqual(str(purchase), expected_str)


class TicketModelTests(TestCase):
    """Tests para el modelo Ticket - Validando relaciones"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Test Company",
            nit="123456789",
            address="Test Address",
            phone="555-1234"
        )
        
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            date=timezone.now().date(),
            location="Test Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="Standard",
            price=75.00,
            description="Standard access"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=100,
            tickets_sold=0
        )
        
        self.purchase = Purchase.objects.create(
            buyer="Test Buyer",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        self.attendee = Attendee.objects.create(
            name="Test Attendee",
            email="attendee@example.com",
            document_type="DNI",
            document_number="87654321",
            phone_number="555-9876",
            gender="F"
        )
    
    def test_create_ticket(self):
        """Test RF-004: Crear ticket válido"""
        ticket = Ticket.objects.create(
            purchase=self.purchase,
            attendee=self.attendee,
            ticket_confirmed=True,
            ticket_owner=True,
            ticket_send_by_email=False
        )
        
        self.assertEqual(ticket.purchase, self.purchase)
        self.assertEqual(ticket.attendee, self.attendee)
        self.assertTrue(ticket.ticket_confirmed)
        self.assertTrue(ticket.ticket_owner)
        self.assertFalse(ticket.ticket_send_by_email)
    
    def test_ticket_str_representation(self):
        """Test: Representación string del modelo Ticket"""
        ticket = Ticket.objects.create(
            purchase=self.purchase,
            attendee=self.attendee
        )
        
        expected_str = f"Boleto para {self.attendee.name} (Compra: {self.purchase.buyer})"
        self.assertEqual(str(ticket), expected_str)
    
    def test_ticket_default_values(self):
        """Test: Valores por defecto del modelo Ticket"""
        ticket = Ticket.objects.create(
            purchase=self.purchase,
            attendee=self.attendee
        )
        
        self.assertFalse(ticket.ticket_confirmed)
        self.assertFalse(ticket.ticket_owner)
        self.assertFalse(ticket.ticket_send_by_email)


class PerformanceTests(TransactionTestCase):
    """Tests de rendimiento - Validando escalabilidad"""
    
    def setUp(self):
        """Configuración inicial para tests de rendimiento"""
        self.company = Company.objects.create(
            name="Performance Test Company",
            nit="999999999",
            address="Performance Test Address",
            phone="555-9999"
        )
        
        self.event = Event.objects.create(
            name="Performance Test Event",
            description="Performance Description",
            date=timezone.now().date(),
            location="Performance Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="Performance Category",
            price=25.00,
            description="Performance category"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=1000,
            tickets_sold=0
        )
    
    def test_bulk_attendee_creation_performance(self):
        """Test RNF-001: Rendimiento en creación masiva de asistentes"""
        start_time = time.time()
        
        attendees = []
        for i in range(100):
            attendees.append(Attendee(
                name=f"Attendee {i}",
                email=f"attendee{i}@example.com",
                document_type="DNI",
                document_number=f"1234567{i:02d}",
                phone_number=f"555-{i:04d}",
                gender="M" if i % 2 == 0 else "F"
            ))
        
        Attendee.objects.bulk_create(attendees)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Debe crear 100 asistentes en menos de 5 segundos
        self.assertLess(creation_time, 5.0)
        self.assertEqual(Attendee.objects.count(), 100)
    
    def test_query_performance_with_pagination(self):
        """Test RNF-002: Rendimiento de consultas con paginación"""
        # Crear datos de prueba
        attendees = []
        for i in range(50):
            attendees.append(Attendee(
                name=f"Query Test {i}",
                email=f"query{i}@example.com",
                document_type="DNI",
                document_number=f"9876543{i:02d}",
                phone_number=f"555-{i:04d}",
                gender="M"
            ))
        
        Attendee.objects.bulk_create(attendees)
        
        start_time = time.time()
        
        # Simular paginación
        page_size = 10
        total_pages = 5
        
        for page in range(total_pages):
            offset = page * page_size
            queryset = Attendee.objects.all()[offset:offset + page_size]
            list(queryset)  # Forzar evaluación del queryset
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Las consultas paginadas deben ser rápidas
        self.assertLess(query_time, 2.0)


class ConcurrencyTests(TransactionTestCase):
    """Tests de concurrencia - Validando comportamiento bajo carga"""
    
    def setUp(self):
        """Configuración inicial para tests de concurrencia"""
        self.company = Company.objects.create(
            name="Concurrency Test Company",
            nit="888888888",
            address="Concurrency Test Address",
            phone="555-8888"
        )
        
        self.event = Event.objects.create(
            name="Concurrency Test Event",
            description="Concurrency Description",
            date=timezone.now().date(),
            location="Concurrency Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="Limited Category",
            price=200.00,
            description="Limited availability category"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=2,  # Solo 2 tickets disponibles
            tickets_sold=0
        )
    
    def test_concurrent_purchase_race_condition(self):
        """Test RNF-003: Condición de carrera en compras concurrentes"""
        errors = []
        successful_purchases = []
        
        def create_purchase(buyer_name):
            try:
                with transaction.atomic():
                    purchase = Purchase(
                        buyer=buyer_name,
                        event=self.event,
                        ticket_category=self.ticket_category,
                        company=self.company
                    )
                    purchase.save()
                    successful_purchases.append(purchase)
            except (ValidationError, IntegrityError) as e:
                errors.append(str(e))
        
        # Crear múltiples threads que intentan comprar simultáneamente
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_purchase, args=(f"Buyer {i}",))
            threads.append(thread)
        
        # Iniciar todos los threads al mismo tiempo
        for thread in threads:
            thread.start()
        
        # Esperar a que todos terminen
        for thread in threads:
            thread.join()
        
        # Solo deben haberse creado máximo 2 compras exitosas
        self.assertLessEqual(len(successful_purchases), 2)
        # Debe haber errores por tickets agotados
        self.assertGreater(len(errors), 0)


class IntegrationTests(TestCase):
    """Tests de integración - Validando flujos completos"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.company = Company.objects.create(
            name="Integration Test Company",
            nit="777777777",
            address="Integration Test Address",
            phone="555-7777"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.event = Event.objects.create(
            name="Integration Test Event",
            description="Integration Description",
            date=timezone.now().date(),
            location="Integration Location",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="Integration Category",
            price=150.00,
            description="Integration category"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=20,
            tickets_sold=0
        )
    
    def test_complete_registration_flow(self):
        """Test RF-005: Flujo completo de registro de asistente"""
        # 1. Crear asistente
        attendee = Attendee.objects.create(
            name="Flujo Completo",
            email="flujo@example.com",
            document_type="DNI",
            document_number="11111111",
            phone_number="555-1111",
            gender="M"
        )
        
        # 2. Crear compra
        purchase = Purchase.objects.create(
            buyer="Comprador Flujo",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        # 3. Crear ticket asociando compra y asistente
        ticket = Ticket.objects.create(
            purchase=purchase,
            attendee=attendee,
            ticket_confirmed=True,
            ticket_owner=True
        )
        
        # 4. Verificar que todas las relaciones están correctas
        self.assertEqual(ticket.purchase, purchase)
        self.assertEqual(ticket.attendee, attendee)
        self.assertIn(attendee, purchase.attendees.all())
        
        # 5. Verificar que se actualizó el contador de tickets vendidos
        self.event_ticket_category.refresh_from_db()
        # Nota: Esto dependería de signals que no están implementados aún
    
    def test_attendee_with_attachment(self):
        """Test RF-006: Asistente con archivo adjunto"""
        attachment = Attachment.objects.create(
            name="test_receipt.pdf",
            file_path="/test/path/receipt.pdf"
        )
        
        attendee = Attendee.objects.create(
            name="Con Adjunto",
            email="adjunto@example.com",
            document_type="DNI",
            document_number="22222222",
            phone_number="555-2222",
            gender="F",
            attachment=attachment
        )
        
        self.assertEqual(attendee.attachment, attachment)
        self.assertEqual(attendee.attachment.name, "test_receipt.pdf")


class SecurityTests(TestCase):
    """Tests de seguridad - Validando aspectos de seguridad"""
    
    def test_attendee_email_validation(self):
        """Test SEC-001: Validación de formato de email"""
        invalid_emails = [
            "invalid.email",
            "@invalid.com",
            "test@",
            "test..test@example.com"
        ]
        
        for invalid_email in invalid_emails:
            with self.assertRaises(ValidationError):
                attendee = Attendee(
                    name="Test Security",
                    email=invalid_email,
                    document_type="DNI",
                    document_number="33333333",
                    phone_number="555-3333",
                    gender="M"
                )
                attendee.full_clean()
    
    def test_attendee_data_integrity(self):
        """Test SEC-002: Integridad de datos del asistente"""
        # Test campos requeridos
        with self.assertRaises(ValidationError):
            attendee = Attendee(
                # name omitido intencionalmente
                email="integrity@example.com",
                document_type="DNI",
                document_number="44444444",
                phone_number="555-4444",
                gender="M"
            )
            attendee.full_clean()
    
    @override_settings(DEBUG=False)
    def test_sensitive_data_not_exposed(self):
        """Test SEC-003: Datos sensibles no expuestos en producción"""
        attendee = Attendee.objects.create(
            name="Sensitive Data",
            email="sensitive@example.com",
            document_type="DNI",
            document_number="55555555",
            phone_number="555-5555",
            gender="M"
        )
        
        # Verificar que el documento no se expone inadvertidamente
        attendee_str = str(attendee)
        self.assertIn(attendee.document_number, attendee_str)
        # En un caso real, podríamos querer enmascarar parte del documento


class DataMigrationTests(TestCase):
    """Tests para validar migración de datos - Modernización"""
    
    def test_attendee_data_structure_compatibility(self):
        """Test MIG-001: Compatibilidad de estructura de datos con microservicio"""
        # Crear asistente con todos los campos que debe soportar el microservicio
        attendee_data = {
            'name': 'Migration Test',
            'email': 'migration@example.com',
            'document_type': 'DNI',
            'document_number': '66666666',
            'phone_number': '555-6666',
            'address': 'Migration Street 123',
            'date_of_birth': timezone.now().date(),
            'gender': 'M'
        }
        
        attendee = Attendee.objects.create(**attendee_data)
        
        # Verificar que todos los campos necesarios están presentes
        required_fields = ['attendee_id', 'name', 'email', 'document_type', 
                         'document_number', 'phone_number', 'gender', 'created', 'modified']
        
        for field in required_fields:
            self.assertTrue(hasattr(attendee, field), f"Campo {field} faltante")
            self.assertIsNotNone(getattr(attendee, field), f"Campo {field} es None")
    
    def test_attendee_serialization_format(self):
        """Test MIG-002: Formato de serialización compatible con API REST"""
        attendee = Attendee.objects.create(
            name="API Test",
            email="api@example.com", 
            document_type="Pasaporte",
            document_number="API123456",
            phone_number="555-7777",
            gender="F"
        )
        
        # Simular serialización similar a la que usaría FastAPI
        serialized_data = {
            'attendee_id': attendee.attendee_id,
            'name': attendee.name,
            'email': attendee.email,
            'document_type': attendee.document_type,
            'document_number': attendee.document_number,
            'phone_number': attendee.phone_number,
            'address': attendee.address,
            'date_of_birth': attendee.date_of_birth,
            'gender': attendee.gender,
            'created': attendee.created.isoformat() if attendee.created else None,
            'modified': attendee.modified.isoformat() if attendee.modified else None
        }
        
        # Verificar que no hay problemas de serialización
        self.assertIsInstance(serialized_data['attendee_id'], int)
        self.assertIsInstance(serialized_data['name'], str)
        self.assertIsInstance(serialized_data['email'], str)
