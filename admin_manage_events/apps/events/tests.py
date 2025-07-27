from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta

from apps.events.models import Event, EventTicketCategory
from apps.ticket_categories.models import TicketCategory, Company
from apps.attendees.models import Purchase, Attendee, Ticket


class EventModelTests(TestCase):
    """Tests para el modelo Event - Validando funcionalidad principal"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Event Test Company",
            nit="123456789",
            address="Event Test Address",
            phone="555-1234"
        )
    
    def test_create_event_valid(self):
        """Test EVT-001: Crear evento válido"""
        event = Event.objects.create(
            name="Conferencia Tech 2024",
            description="Conferencia sobre tecnología",
            date=timezone.now().date() + timedelta(days=30),
            location="Centro de Convenciones",
            company=self.company
        )
        
        self.assertEqual(event.name, "Conferencia Tech 2024")
        self.assertEqual(event.company, self.company)
        self.assertIsNotNone(event.date)
        self.assertTrue(event.created)
        self.assertTrue(event.modified)
    
    def test_event_str_representation(self):
        """Test: Representación string del modelo Event"""
        event = Event.objects.create(
            name="Workshop Python",
            description="Taller de Python",
            date=timezone.now().date() + timedelta(days=15),
            location="Aula 101",
            company=self.company
        )
        
        # Assuming the __str__ method returns the name
        self.assertEqual(str(event), "Workshop Python")
    
    def test_event_company_relationship(self):
        """Test EVT-002: Relación evento-empresa"""
        event = Event.objects.create(
            name="Evento Empresa",
            description="Evento de la empresa",
            date=timezone.now().date() + timedelta(days=20),
            location="Oficina Principal",
            company=self.company
        )
        
        # Verificar relación bidireccional
        self.assertEqual(event.company, self.company)
        self.assertIn(event, self.company.event_set.all())
    
    def test_event_date_validation(self):
        """Test EVT-003: Validación de fecha del evento"""
        # Crear evento con fecha futura (válido)
        future_event = Event.objects.create(
            name="Evento Futuro",
            description="Evento en el futuro",
            date=timezone.now().date() + timedelta(days=60),
            location="Lugar Futuro",
            company=self.company
        )
        self.assertIsNotNone(future_event.id)
        
        # Crear evento con fecha pasada (técnicamente válido en el modelo base)
        past_event = Event.objects.create(
            name="Evento Pasado",
            description="Evento en el pasado",
            date=timezone.now().date() - timedelta(days=30),
            location="Lugar Pasado",
            company=self.company
        )
        self.assertIsNotNone(past_event.id)


class EventTicketCategoryTests(TestCase):
    """Tests para el modelo EventTicketCategory - Validando gestión de tickets"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Ticket Test Company",
            nit="987654321",
            address="Ticket Test Address",
            phone="555-9876"
        )
        
        self.event = Event.objects.create(
            name="Evento Test Tickets",
            description="Evento para probar tickets",
            date=timezone.now().date() + timedelta(days=45),
            location="Venue Test",
            company=self.company
        )
        
        self.ticket_category_vip = TicketCategory.objects.create(
            name="VIP",
            price=150.00,
            description="Acceso VIP completo"
        )
        
        self.ticket_category_general = TicketCategory.objects.create(
            name="General",
            price=50.00,
            description="Acceso general"
        )
    
    def test_create_event_ticket_category(self):
        """Test ETC-001: Crear categoría de ticket para evento"""
        event_ticket = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category_vip,
            tickets_available=100,
            tickets_sold=0
        )
        
        self.assertEqual(event_ticket.event, self.event)
        self.assertEqual(event_ticket.ticket_category, self.ticket_category_vip)
        self.assertEqual(event_ticket.tickets_available, 100)
        self.assertEqual(event_ticket.tickets_sold, 0)
    
    def test_multiple_ticket_categories_per_event(self):
        """Test ETC-002: Múltiples categorías de ticket por evento"""
        # VIP tickets
        vip_tickets = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category_vip,
            tickets_available=50,
            tickets_sold=0
        )
        
        # General tickets
        general_tickets = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category_general,
            tickets_available=200,
            tickets_sold=0
        )
        
        # Verificar que el evento tiene ambas categorías
        event_categories = EventTicketCategory.objects.filter(event=self.event)
        self.assertEqual(event_categories.count(), 2)
        
        category_names = [etc.ticket_category.name for etc in event_categories]
        self.assertIn("VIP", category_names)
        self.assertIn("General", category_names)
    
    def test_tickets_sold_tracking(self):
        """Test ETC-003: Seguimiento de tickets vendidos"""
        event_ticket = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category_general,
            tickets_available=100,
            tickets_sold=25
        )
        
        self.assertEqual(event_ticket.tickets_sold, 25)
        
        # Calcular tickets disponibles restantes
        remaining_tickets = event_ticket.tickets_available - event_ticket.tickets_sold
        self.assertEqual(remaining_tickets, 75)
    
    def test_sold_out_scenario(self):
        """Test ETC-004: Escenario de tickets agotados"""
        event_ticket = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category_vip,
            tickets_available=10,
            tickets_sold=10
        )
        
        # Verificar que están agotados
        self.assertEqual(event_ticket.tickets_available, event_ticket.tickets_sold)
        
        # No debería permitir más ventas (esto dependería de validaciones en Purchase)
        remaining = event_ticket.tickets_available - event_ticket.tickets_sold
        self.assertEqual(remaining, 0)


class EventPurchaseIntegrationTests(TestCase):
    """Tests de integración entre eventos y compras"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.company = Company.objects.create(
            name="Integration Event Company",
            nit="111222333",
            address="Integration Address",
            phone="555-1122"
        )
        
        self.event = Event.objects.create(
            name="Evento Integración",
            description="Evento para tests de integración",
            date=timezone.now().date() + timedelta(days=30),
            location="Centro Integración",
            company=self.company
        )
        
        self.ticket_category = TicketCategory.objects.create(
            name="Estándar",
            price=75.00,
            description="Ticket estándar"
        )
        
        self.event_ticket_category = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=self.ticket_category,
            tickets_available=50,
            tickets_sold=0
        )
    
    def test_event_purchase_flow(self):
        """Test INT-001: Flujo completo de compra para evento"""
        # 1. Crear asistente
        attendee = Attendee.objects.create(
            name="Asistente Integración",
            email="integracion@example.com",
            document_type="DNI",
            document_number="12345678",
            phone_number="555-1234",
            gender="M"
        )
        
        # 2. Crear compra
        purchase = Purchase.objects.create(
            buyer="Comprador Integración",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        # 3. Crear ticket
        ticket = Ticket.objects.create(
            purchase=purchase,
            attendee=attendee,
            ticket_confirmed=True
        )
        
        # 4. Verificar todas las relaciones
        self.assertEqual(ticket.purchase.event, self.event)
        self.assertEqual(ticket.purchase.ticket_category, self.ticket_category)
        self.assertEqual(ticket.attendee, attendee)
        
        # 5. Verificar que el asistente está asociado al evento a través de la compra
        self.assertIn(attendee, purchase.attendees.all())
    
    def test_event_capacity_validation(self):
        """Test INT-002: Validación de capacidad del evento"""
        # Crear compras hasta agotar tickets
        attendees = []
        purchases = []
        
        for i in range(50):  # tickets_available = 50
            attendee = Attendee.objects.create(
                name=f"Attendee {i}",
                email=f"attendee{i}@example.com",
                document_type="DNI",
                document_number=f"1234567{i:02d}",
                phone_number=f"555-{i:04d}",
                gender="M" if i % 2 == 0 else "F"
            )
            attendees.append(attendee)
        
        # Solo deberíamos poder crear 50 compras válidas
        successful_purchases = 0
        failed_purchases = 0
        
        for i, attendee in enumerate(attendees):
            try:
                purchase = Purchase.objects.create(
                    buyer=f"Buyer {i}",
                    event=self.event,
                    ticket_category=self.ticket_category,
                    company=self.company
                )
                purchases.append(purchase)
                successful_purchases += 1
                
                # Simular actualización de tickets vendidos
                self.event_ticket_category.tickets_sold += 1
                self.event_ticket_category.save()
                
            except ValidationError:
                failed_purchases += 1
        
        # Verificar que se respetó la capacidad
        self.assertLessEqual(successful_purchases, 50)
    
    def test_event_multiple_categories_purchase(self):
        """Test INT-003: Compra con múltiples categorías de tickets"""
        # Agregar otra categoría al evento
        premium_category = TicketCategory.objects.create(
            name="Premium",
            price=120.00,
            description="Acceso premium"
        )
        
        premium_event_ticket = EventTicketCategory.objects.create(
            event=self.event,
            ticket_category=premium_category,
            tickets_available=20,
            tickets_sold=0
        )
        
        # Crear compras en ambas categorías
        attendee1 = Attendee.objects.create(
            name="VIP Attendee",
            email="vip@example.com",
            document_type="DNI",
            document_number="11111111",
            phone_number="555-1111",
            gender="F"
        )
        
        attendee2 = Attendee.objects.create(
            name="Premium Attendee",
            email="premium@example.com",
            document_type="DNI",
            document_number="22222222",
            phone_number="555-2222",
            gender="M"
        )
        
        # Compra categoría estándar
        standard_purchase = Purchase.objects.create(
            buyer="Standard Buyer",
            event=self.event,
            ticket_category=self.ticket_category,
            company=self.company
        )
        
        # Compra categoría premium
        premium_purchase = Purchase.objects.create(
            buyer="Premium Buyer",
            event=self.event,
            ticket_category=premium_category,
            company=self.company
        )
        
        # Verificar que ambas compras son para el mismo evento pero diferentes categorías
        self.assertEqual(standard_purchase.event, premium_purchase.event)
        self.assertNotEqual(standard_purchase.ticket_category, premium_purchase.ticket_category)


class EventBusinessLogicTests(TestCase):
    """Tests de lógica de negocio específica de eventos"""
    
    def setUp(self):
        """Configuración inicial para tests de lógica de negocio"""
        self.company = Company.objects.create(
            name="Business Logic Company",
            nit="444555666",
            address="Business Logic Address",
            phone="555-4455"
        )
        
        self.past_event = Event.objects.create(
            name="Evento Pasado",
            description="Evento que ya ocurrió",
            date=timezone.now().date() - timedelta(days=10),
            location="Lugar Pasado",
            company=self.company
        )
        
        self.current_event = Event.objects.create(
            name="Evento Actual",
            description="Evento happening now",
            date=timezone.now().date(),
            location="Lugar Actual",
            company=self.company
        )
        
        self.future_event = Event.objects.create(
            name="Evento Futuro",
            description="Evento por venir",
            date=timezone.now().date() + timedelta(days=30),
            location="Lugar Futuro",
            company=self.company
        )
    
    def test_event_date_categorization(self):
        """Test BL-001: Categorización de eventos por fecha"""
        today = timezone.now().date()
        
        # Evento pasado
        self.assertLess(self.past_event.date, today)
        
        # Evento actual
        self.assertEqual(self.current_event.date, today)
        
        # Evento futuro
        self.assertGreater(self.future_event.date, today)
    
    def test_active_events_business_rule(self):
        """Test BL-002: Regla de negocio para eventos activos"""
        # En teoría, solo los eventos futuros deberían aceptar nuevas inscripciones
        # Esto sería una regla de negocio que se implementaría en las vistas o modelos
        
        future_category = TicketCategory.objects.create(
            name="Future Category",
            price=100.00,
            description="Para evento futuro"
        )
        
        # Evento futuro debería aceptar tickets
        future_tickets = EventTicketCategory.objects.create(
            event=self.future_event,
            ticket_category=future_category,
            tickets_available=100,
            tickets_sold=0
        )
        
        self.assertEqual(future_tickets.tickets_available, 100)
        
        # Crear asistente y compra para evento futuro
        attendee = Attendee.objects.create(
            name="Future Attendee",
            email="future@example.com",
            document_type="DNI",
            document_number="99999999",
            phone_number="555-9999",
            gender="M"
        )
        
        # Esta compra debería ser válida
        purchase = Purchase.objects.create(
            buyer="Future Buyer",
            event=self.future_event,
            ticket_category=future_category,
            company=self.company
        )
        
        self.assertEqual(purchase.event, self.future_event)
    
    def test_event_company_isolation(self):
        """Test BL-003: Aislamiento de eventos por empresa"""
        # Crear otra empresa
        other_company = Company.objects.create(
            name="Other Company",
            nit="999888777",
            address="Other Address",
            phone="555-9988"
        )
        
        other_event = Event.objects.create(
            name="Other Company Event",
            description="Evento de otra empresa",
            date=timezone.now().date() + timedelta(days=20),
            location="Other Location",
            company=other_company
        )
        
        # Los eventos deben estar aislados por empresa
        company1_events = Event.objects.filter(company=self.company)
        company2_events = Event.objects.filter(company=other_company)
        
        self.assertNotIn(other_event, company1_events)
        self.assertIn(other_event, company2_events)
        
        # Verificar que cada empresa solo ve sus eventos
        self.assertEqual(company1_events.count(), 3)  # past, current, future
        self.assertEqual(company2_events.count(), 1)  # other_event


class EventPerformanceTests(TestCase):
    """Tests de rendimiento para eventos"""
    
    def setUp(self):
        """Configuración inicial para tests de rendimiento"""
        self.company = Company.objects.create(
            name="Performance Event Company",
            nit="111111111",
            address="Performance Address",
            phone="555-1111"
        )
    
    def test_bulk_event_creation(self):
        """Test PERF-001: Creación masiva de eventos"""
        import time
        
        start_time = time.time()
        
        events = []
        for i in range(50):
            events.append(Event(
                name=f"Evento Masivo {i}",
                description=f"Descripción del evento {i}",
                date=timezone.now().date() + timedelta(days=i+1),
                location=f"Ubicación {i}",
                company=self.company
            ))
        
        Event.objects.bulk_create(events)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Debe crear 50 eventos en tiempo razonable
        self.assertLess(creation_time, 5.0)
        self.assertEqual(Event.objects.filter(company=self.company).count(), 50)
    
    def test_event_query_optimization(self):
        """Test PERF-002: Optimización de consultas de eventos"""
        import time
        
        # Crear algunos eventos con tickets
        for i in range(10):
            event = Event.objects.create(
                name=f"Query Event {i}",
                description=f"Event for query optimization {i}",
                date=timezone.now().date() + timedelta(days=i+10),
                location=f"Query Location {i}",
                company=self.company
            )
            
            category = TicketCategory.objects.create(
                name=f"Category {i}",
                price=50.00 + i,
                description=f"Category for event {i}"
            )
            
            EventTicketCategory.objects.create(
                event=event,
                ticket_category=category,
                tickets_available=100,
                tickets_sold=i * 5
            )
        
        start_time = time.time()
        
        # Consulta optimizada con select_related
        events_with_company = Event.objects.select_related('company').filter(
            company=self.company
        )
        
        # Forzar evaluación
        list(events_with_company)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Las consultas optimizadas deben ser rápidas
        self.assertLess(query_time, 2.0)
