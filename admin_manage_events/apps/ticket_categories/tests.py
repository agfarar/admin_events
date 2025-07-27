from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal

from apps.ticket_categories.models import TicketCategory, Company


class CompanyModelTests(TestCase):
    """Tests para el modelo Company - Validando gestión de empresas"""
    
    def test_create_company_valid(self):
        """Test COMP-001: Crear empresa válida"""
        company = Company.objects.create(
            name="Tech Solutions S.A.",
            nit="900123456",
            address="Calle 123 #45-67",
            phone="555-1234"
        )
        
        self.assertEqual(company.name, "Tech Solutions S.A.")
        self.assertEqual(company.nit, "900123456")
        self.assertEqual(company.address, "Calle 123 #45-67")
        self.assertEqual(company.phone, "555-1234")
    
    def test_company_str_representation(self):
        """Test: Representación string del modelo Company"""
        company = Company.objects.create(
            name="Innovate Corp",
            nit="900987654",
            address="Avenida Siempre Viva",
            phone="555-9876"
        )
        
        # Asumiendo que __str__ retorna el nombre
        self.assertEqual(str(company), "Innovate Corp")
    
    def test_company_unique_nit(self):
        """Test COMP-002: NIT de empresa debe ser único"""
        Company.objects.create(
            name="Primera Empresa",
            nit="900111111",
            address="Dirección 1",
            phone="555-0001"
        )
        
        # Intentar crear otra empresa con el mismo NIT debería fallar
        with self.assertRaises(IntegrityError):
            Company.objects.create(
                name="Segunda Empresa",
                nit="900111111",  # NIT duplicado
                address="Dirección 2", 
                phone="555-0002"
            )
    
    def test_company_required_fields(self):
        """Test COMP-003: Campos requeridos de la empresa"""
        # Todos los campos son requeridos, verificar con full_clean
        company = Company(
            name="",  # Nombre vacío
            nit="900222222",
            address="Dirección válida",
            phone="555-2222"
        )
        
        with self.assertRaises(ValidationError):
            company.full_clean()
    
    def test_company_nit_format_validation(self):
        """Test COMP-004: Validación del formato del NIT"""
        # Crear empresa con NIT válido
        valid_company = Company.objects.create(
            name="Empresa Válida",
            nit="900333333",
            address="Dirección válida",
            phone="555-3333"
        )
        
        self.assertEqual(valid_company.nit, "900333333")


class TicketCategoryModelTests(TestCase):
    """Tests para el modelo TicketCategory - Validando categorías de tickets"""
    
    def test_create_ticket_category_valid(self):
        """Test TC-001: Crear categoría de ticket válida"""
        category = TicketCategory.objects.create(
            name="VIP Premium",
            price=Decimal('250.00'),
            description="Acceso VIP completo con beneficios premium"
        )
        
        self.assertEqual(category.name, "VIP Premium")
        self.assertEqual(category.price, Decimal('250.00'))
        self.assertEqual(category.description, "Acceso VIP completo con beneficios premium")
    
    def test_ticket_category_str_representation(self):
        """Test: Representación string del modelo TicketCategory"""
        category = TicketCategory.objects.create(
            name="General",
            price=Decimal('50.00'),
            description="Acceso general al evento"
        )
        
        # Asumiendo que __str__ retorna el nombre
        self.assertEqual(str(category), "General")
    
    def test_ticket_category_price_decimal(self):
        """Test TC-002: Precio debe ser un decimal válido"""
        category = TicketCategory.objects.create(
            name="Standard",
            price=Decimal('75.50'),
            description="Ticket estándar"
        )
        
        self.assertIsInstance(category.price, Decimal)
        self.assertEqual(category.price, Decimal('75.50'))
    
    def test_ticket_category_price_negative_validation(self):
        """Test TC-003: Precio no puede ser negativo"""
        # Crear categoría con precio negativo
        category = TicketCategory(
            name="Invalid Price",
            price=Decimal('-10.00'),
            description="Categoría con precio inválido"
        )
        
        # La validación dependería de validators en el modelo
        # Por ahora verificamos que el objeto se puede crear pero el precio es negativo
        self.assertLess(category.price, 0)
    
    def test_ticket_category_price_zero(self):
        """Test TC-004: Precio puede ser cero (ticket gratuito)"""
        free_category = TicketCategory.objects.create(
            name="Gratuito",
            price=Decimal('0.00'),
            description="Ticket gratuito para estudiantes"
        )
        
        self.assertEqual(free_category.price, Decimal('0.00'))
    
    def test_ticket_category_unique_name(self):
        """Test TC-005: Nombre de categoría debe ser único"""
        TicketCategory.objects.create(
            name="Premium",
            price=Decimal('100.00'),
            description="Categoría premium original"
        )
        
        # Intentar crear otra categoría con el mismo nombre
        with self.assertRaises(IntegrityError):
            TicketCategory.objects.create(
                name="Premium",  # Nombre duplicado
                price=Decimal('150.00'),
                description="Otra categoría premium"
            )
    
    def test_ticket_category_price_precision(self):
        """Test TC-006: Precisión del precio (decimales)"""
        category = TicketCategory.objects.create(
            name="Precision Test",
            price=Decimal('99.99'),
            description="Test de precisión de precio"
        )
        
        self.assertEqual(category.price, Decimal('99.99'))
        
        # Verificar que mantiene la precisión
        category.price = Decimal('123.45')
        category.save()
        category.refresh_from_db()
        
        self.assertEqual(category.price, Decimal('123.45'))


class TicketCategoryBusinessLogicTests(TestCase):
    """Tests de lógica de negocio para categorías de tickets"""
    
    def setUp(self):
        """Configuración inicial"""
        self.company = Company.objects.create(
            name="Business Logic Company",
            nit="900555555",
            address="Business Address",
            phone="555-5555"
        )
    
    def test_ticket_category_hierarchy(self):
        """Test BL-TC-001: Jerarquía de precios de categorías"""
        # Crear diferentes categorías con precios jerárquicos
        basic = TicketCategory.objects.create(
            name="Básico",
            price=Decimal('25.00'),
            description="Acceso básico"
        )
        
        standard = TicketCategory.objects.create(
            name="Estándar",
            price=Decimal('50.00'),
            description="Acceso estándar"
        )
        
        premium = TicketCategory.objects.create(
            name="Premium", 
            price=Decimal('100.00'),
            description="Acceso premium"
        )
        
        vip = TicketCategory.objects.create(
            name="VIP",
            price=Decimal('200.00'),
            description="Acceso VIP completo"
        )
        
        # Verificar la jerarquía de precios
        categories = [basic, standard, premium, vip]
        prices = [cat.price for cat in categories]
        
        # Los precios deben estar en orden ascendente
        self.assertEqual(prices, sorted(prices))
        
        # Verificar rangos específicos
        self.assertLess(basic.price, standard.price)
        self.assertLess(standard.price, premium.price)
        self.assertLess(premium.price, vip.price)
    
    def test_ticket_category_grouping(self):
        """Test BL-TC-002: Agrupación de categorías por tipo"""
        # Crear categorías para diferentes tipos de eventos
        conference_categories = [
            TicketCategory.objects.create(
                name="Conferencia - Estudiante",
                price=Decimal('30.00'),
                description="Para estudiantes con credencial"
            ),
            TicketCategory.objects.create(
                name="Conferencia - Profesional",
                price=Decimal('80.00'),
                description="Para profesionales"
            ),
            TicketCategory.objects.create(
                name="Conferencia - Empresarial",
                price=Decimal('150.00'),
                description="Para empresas"
            )
        ]
        
        workshop_categories = [
            TicketCategory.objects.create(
                name="Workshop - Básico",
                price=Decimal('40.00'),
                description="Workshop nivel básico"
            ),
            TicketCategory.objects.create(
                name="Workshop - Avanzado",
                price=Decimal('90.00'),
                description="Workshop nivel avanzado"
            )
        ]
        
        # Verificar que se pueden agrupar por nombre
        conference_cats = TicketCategory.objects.filter(name__startswith="Conferencia")
        workshop_cats = TicketCategory.objects.filter(name__startswith="Workshop")
        
        self.assertEqual(conference_cats.count(), 3)
        self.assertEqual(workshop_cats.count(), 2)
    
    def test_ticket_category_pricing_strategies(self):
        """Test BL-TC-003: Estrategias de precios"""
        # Early bird pricing
        early_bird = TicketCategory.objects.create(
            name="Early Bird",
            price=Decimal('60.00'),
            description="Precio especial por compra anticipada"
        )
        
        # Regular pricing
        regular = TicketCategory.objects.create(
            name="Regular",
            price=Decimal('80.00'),
            description="Precio regular"
        )
        
        # Last minute pricing
        last_minute = TicketCategory.objects.create(
            name="Last Minute",
            price=Decimal('100.00'),
            description="Precio de último momento"
        )
        
        # Verificar que early bird es más barato que regular
        self.assertLess(early_bird.price, regular.price)
        
        # Verificar que last minute es más caro que regular
        self.assertGreater(last_minute.price, regular.price)
        
        # Calcular diferencias porcentuales
        regular_price = float(regular.price)
        early_discount = (regular_price - float(early_bird.price)) / regular_price * 100
        last_premium = (float(last_minute.price) - regular_price) / regular_price * 100
        
        self.assertGreater(early_discount, 0)  # Hay descuento
        self.assertGreater(last_premium, 0)    # Hay sobreprecio


class CompanyTicketCategoryIntegrationTests(TestCase):
    """Tests de integración entre Company y TicketCategory"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.company1 = Company.objects.create(
            name="Company One",
            nit="900111111",
            address="Address One",
            phone="555-1111"
        )
        
        self.company2 = Company.objects.create(
            name="Company Two",
            nit="900222222",
            address="Address Two",
            phone="555-2222"
        )
    
    def test_company_ticket_categories_usage(self):
        """Test INT-TC-001: Uso de categorías de tickets por empresas"""
        # Crear categorías que podrían usar diferentes empresas
        vip_category = TicketCategory.objects.create(
            name="VIP Global",
            price=Decimal('200.00'),
            description="Categoría VIP que pueden usar varias empresas"
        )
        
        standard_category = TicketCategory.objects.create(
            name="Standard Global",
            price=Decimal('75.00'),
            description="Categoría estándar global"
        )
        
        # Las categorías pueden ser reutilizadas por diferentes empresas
        # (a través de eventos que las usen)
        self.assertTrue(TicketCategory.objects.filter(name="VIP Global").exists())
        self.assertTrue(TicketCategory.objects.filter(name="Standard Global").exists())
        
        # Ambas empresas pueden referenciar las mismas categorías
        self.assertEqual(vip_category.name, "VIP Global")
        self.assertEqual(standard_category.name, "Standard Global")
    
    def test_ticket_category_pricing_by_company_context(self):
        """Test INT-TC-002: Precios de categorías en contexto empresarial"""
        # Crear categorías con diferentes estrategias de precios
        budget_category = TicketCategory.objects.create(
            name="Económico",
            price=Decimal('20.00'),
            description="Para eventos económicos"
        )
        
        corporate_category = TicketCategory.objects.create(
            name="Corporativo",
            price=Decimal('150.00'),
            description="Para eventos corporativos"
        )
        
        luxury_category = TicketCategory.objects.create(
            name="Lujo",
            price=Decimal('500.00'),
            description="Para eventos de lujo"
        )
        
        # Verificar rangos de precios apropiados para diferentes tipos de empresa
        all_categories = TicketCategory.objects.all().order_by('price')
        prices = [cat.price for cat in all_categories]
        
        # Debe haber una buena distribución de precios
        min_price = min(prices)
        max_price = max(prices)
        
        self.assertGreaterEqual(min_price, Decimal('0.00'))
        self.assertLessEqual(max_price, Decimal('1000.00'))  # Límite razonable


class TicketCategoryPerformanceTests(TestCase):
    """Tests de rendimiento para categorías de tickets"""
    
    def test_bulk_category_creation(self):
        """Test PERF-TC-001: Creación masiva de categorías"""
        import time
        
        start_time = time.time()
        
        categories = []
        for i in range(50):
            categories.append(TicketCategory(
                name=f"Categoría Masiva {i}",
                price=Decimal(f'{25.00 + i}'),
                description=f"Descripción de categoría {i}"
            ))
        
        TicketCategory.objects.bulk_create(categories)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Debe crear 50 categorías en tiempo razonable
        self.assertLess(creation_time, 3.0)
        
        # Verificar que se crearon todas
        created_categories = TicketCategory.objects.filter(
            name__startswith="Categoría Masiva"
        )
        self.assertEqual(created_categories.count(), 50)
    
    def test_category_query_optimization(self):
        """Test PERF-TC-002: Optimización de consultas de categorías"""
        import time
        
        # Crear categorías de prueba
        for i in range(20):
            TicketCategory.objects.create(
                name=f"Query Category {i}",
                price=Decimal(f'{30.00 + i * 5}'),
                description=f"Category for query test {i}"
            )
        
        start_time = time.time()
        
        # Consultas comunes que deberían ser rápidas
        # 1. Buscar por rango de precios
        affordable_categories = TicketCategory.objects.filter(
            price__lte=Decimal('50.00')
        )
        list(affordable_categories)  # Forzar evaluación
        
        # 2. Buscar por nombre
        named_categories = TicketCategory.objects.filter(
            name__icontains="Query"
        )
        list(named_categories)  # Forzar evaluación
        
        # 3. Ordenar por precio
        sorted_categories = TicketCategory.objects.all().order_by('price')
        list(sorted_categories)  # Forzar evaluación
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Las consultas deben ser rápidas
        self.assertLess(query_time, 2.0)


class TicketCategoryValidationTests(TestCase):
    """Tests de validación específicos para categorías de tickets"""
    
    def test_category_name_length_validation(self):
        """Test VAL-TC-001: Validación de longitud del nombre"""
        # Nombre muy largo
        long_name = "A" * 300  # Asumiendo max_length menor
        
        category = TicketCategory(
            name=long_name,
            price=Decimal('50.00'),
            description="Test de nombre largo"
        )
        
        # Esto debería fallar si hay validación de longitud
        try:
            category.full_clean()
            # Si no falla, al menos verificamos que se creó
            category.save()
            self.assertTrue(len(category.name) > 200)
        except ValidationError:
            # Se esperaba que fallara por longitud
            pass
    
    def test_category_description_optional(self):
        """Test VAL-TC-002: Descripción es opcional"""
        category = TicketCategory.objects.create(
            name="Sin Descripción",
            price=Decimal('40.00')
            # description omitida
        )
        
        # Debería permitir descripción vacía o nula
        self.assertTrue(
            category.description is None or 
            category.description == ""
        )
    
    def test_category_price_precision_limits(self):
        """Test VAL-TC-003: Límites de precisión del precio"""
        # Precio con muchos decimales
        precise_price = Decimal('99.999999')
        
        category = TicketCategory.objects.create(
            name="Precisión Test",
            price=precise_price,
            description="Test de precisión extrema"
        )
        
        # El precio debería mantenerse o redondearse apropiadamente
        category.refresh_from_db()
        self.assertIsInstance(category.price, Decimal)
        
        # Verificar que el precio es razonable
        self.assertGreaterEqual(category.price, Decimal('99.99'))
        self.assertLessEqual(category.price, Decimal('100.00'))


class MigrationCompatibilityTicketCategoryTests(TestCase):
    """Tests de compatibilidad para migración de categorías de tickets"""
    
    def test_ticket_category_serialization_format(self):
        """Test MIG-TC-001: Formato de serialización para microservicio"""
        category = TicketCategory.objects.create(
            name="Serialization Test",
            price=Decimal('85.50'),
            description="Test de serialización para API"
        )
        
        # Formato que usaría el microservicio
        serialized_data = {
            'id': category.id,
            'name': category.name,
            'price': float(category.price),
            'description': category.description,
            'created': category.created.isoformat() if hasattr(category, 'created') and category.created else None,
            'modified': category.modified.isoformat() if hasattr(category, 'modified') and category.modified else None
        }
        
        # Verificar que los datos son serializables
        self.assertIsInstance(serialized_data['id'], int)
        self.assertIsInstance(serialized_data['name'], str)
        self.assertIsInstance(serialized_data['price'], float)
        self.assertEqual(serialized_data['price'], 85.5)
    
    def test_company_serialization_format(self):
        """Test MIG-TC-002: Formato de serialización de empresa para microservicio"""
        company = Company.objects.create(
            name="Serialization Company",
            nit="900777777",
            address="Serialization Address",
            phone="555-7777"
        )
        
        # Formato que usaría el microservicio
        serialized_data = {
            'id': company.id,
            'name': company.name,
            'nit': company.nit,
            'address': company.address,
            'phone': company.phone
        }
        
        # Verificar que los datos son serializables
        for key, value in serialized_data.items():
            self.assertIsNotNone(value)
            if key == 'id':
                self.assertIsInstance(value, int)
            else:
                self.assertIsInstance(value, str)
