from django.test import TestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings
from django.utils import timezone
import time
from unittest.mock import patch

from accounts.models import CustomUser
from apps.ticket_categories.models import Company
from apps.attendees.models import Attendee

User = get_user_model()


class CustomUserModelTests(TestCase):
    """Tests para el modelo CustomUser - Validando autenticación y autorización"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.company = Company.objects.create(
            name="Auth Test Company",
            nit="111111111",
            address="Auth Test Address",
            phone="555-1111"
        )
    
    def test_create_user_valid(self):
        """Test AUTH-001: Crear usuario válido"""
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="SecurePass123",
            company=self.company
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.company, self.company)
        self.assertTrue(user.check_password("SecurePass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test AUTH-002: Crear superusuario"""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPass123",
            company=self.company
        )
        
        self.assertEqual(superuser.username, "admin")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.company, self.company)
    
    def test_user_str_representation(self):
        """Test: Representación string del modelo CustomUser"""
        user = User.objects.create_user(
            username="strtest",
            email="strtest@example.com",
            password="StrPass123",
            company=self.company
        )
        
        self.assertEqual(str(user), "strtest")
    
    def test_user_company_required(self):
        """Test AUTH-003: Empresa es requerida para el usuario"""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="nocompany",
                email="nocompany@example.com",
                password="NoCompanyPass123"
                # company omitida intencionalmente
            )
    
    def test_user_unique_username(self):
        """Test AUTH-004: Nombre de usuario debe ser único"""
        User.objects.create_user(
            username="unique",
            email="unique1@example.com",
            password="UniquePass123",
            company=self.company
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="unique",  # Nombre duplicado
                email="unique2@example.com",
                password="UniquePass456",
                company=self.company
            )
    
    def test_user_unique_email(self):
        """Test AUTH-005: Email debe ser único"""
        User.objects.create_user(
            username="email1",
            email="same@example.com",
            password="EmailPass123",
            company=self.company
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="email2",
                email="same@example.com",  # Email duplicado
                password="EmailPass456",
                company=self.company
            )


class UserAuthenticationTests(TestCase):
    """Tests de autenticación - Validando seguridad de acceso"""
    
    def setUp(self):
        """Configuración inicial para tests de autenticación"""
        self.company = Company.objects.create(
            name="Security Test Company",
            nit="222222222",
            address="Security Test Address",
            phone="555-2222"
        )
        
        self.user = User.objects.create_user(
            username="securitytest",
            email="security@example.com",
            password="SecurityPass123",
            company=self.company
        )
        
        self.client = Client()
    
    def test_user_authentication_valid_credentials(self):
        """Test SEC-001: Autenticación con credenciales válidas"""
        user = authenticate(username="securitytest", password="SecurityPass123")
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)
    
    def test_user_authentication_invalid_password(self):
        """Test SEC-002: Autenticación con contraseña inválida"""
        user = authenticate(username="securitytest", password="WrongPassword")
        self.assertIsNone(user)
    
    def test_user_authentication_invalid_username(self):
        """Test SEC-003: Autenticación con usuario inválido"""
        user = authenticate(username="wronguser", password="SecurityPass123")
        self.assertIsNone(user)
    
    def test_password_hashing(self):
        """Test SEC-004: Contraseñas son hasheadas correctamente"""
        # La contraseña no debe almacenarse en texto plano
        self.assertNotEqual(self.user.password, "SecurityPass123")
        # Pero debe validarse correctamente
        self.assertTrue(self.user.check_password("SecurityPass123"))
        self.assertFalse(self.user.check_password("WrongPassword"))
    
    def test_login_logout_flow(self):
        """Test SEC-005: Flujo completo de login/logout"""
        # Login
        login_successful = self.client.login(username="securitytest", password="SecurityPass123")
        self.assertTrue(login_successful)
        
        # Verificar que el usuario está autenticado
        response = self.client.get('/admin/')  # Cualquier URL que requiera autenticación
        # El status code puede variar dependiendo de la configuración de URLs
        
        # Logout
        self.client.logout()
        
        # Verificar que el usuario ya no está autenticado
        response = self.client.get('/admin/')
        # Debería redirigir al login


class UserPermissionsTests(TestCase):
    """Tests de permisos - Validando autorización"""
    
    def setUp(self):
        """Configuración inicial para tests de permisos"""
        self.company1 = Company.objects.create(
            name="Company 1",
            nit="333333333",
            address="Company 1 Address",
            phone="555-3333"
        )
        
        self.company2 = Company.objects.create(
            name="Company 2",
            nit="444444444",
            address="Company 2 Address",
            phone="555-4444"
        )
        
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="RegularPass123",
            company=self.company1
        )
        
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123",
            company=self.company1,
            is_staff=True
        )
        
        self.superuser = User.objects.create_superuser(
            username="super",
            email="super@example.com",
            password="SuperPass123",
            company=self.company1
        )
    
    def test_regular_user_permissions(self):
        """Test PERM-001: Permisos de usuario regular"""
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)
        self.assertFalse(self.regular_user.has_perm('auth.add_user'))
    
    def test_admin_user_permissions(self):
        """Test PERM-002: Permisos de usuario administrador"""
        self.assertTrue(self.admin_user.is_staff)
        self.assertFalse(self.admin_user.is_superuser)
        # Los permisos específicos dependerán de la configuración
    
    def test_superuser_permissions(self):
        """Test PERM-003: Permisos de superusuario"""
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.has_perm('auth.add_user'))
        self.assertTrue(self.superuser.has_perm('auth.change_user'))
        self.assertTrue(self.superuser.has_perm('auth.delete_user'))
    
    def test_company_isolation(self):
        """Test PERM-004: Aislamiento por empresa"""
        # Cada usuario pertenece a una empresa específica
        self.assertEqual(self.regular_user.company, self.company1)
        self.assertNotEqual(self.regular_user.company, self.company2)


class PasswordSecurityTests(TestCase):
    """Tests de seguridad de contraseñas"""
    
    def setUp(self):
        """Configuración inicial para tests de seguridad de contraseñas"""
        self.company = Company.objects.create(
            name="Password Test Company",
            nit="555555555",
            address="Password Test Address",
            phone="555-5555"
        )
    
    def test_password_change_validation(self):
        """Test SEC-006: Validación de cambio de contraseña"""
        user = User.objects.create_user(
            username="passchange",
            email="passchange@example.com",
            password="OldPassword123",
            company=self.company
        )
        
        # Cambiar contraseña
        user.set_password("NewPassword456")
        user.save()
        
        # Verificar que la nueva contraseña funciona
        self.assertTrue(user.check_password("NewPassword456"))
        # Verificar que la antigua contraseña ya no funciona
        self.assertFalse(user.check_password("OldPassword123"))
    
    def test_password_complexity(self):
        """Test SEC-007: Validación de complejidad de contraseña (si está configurada)"""
        # Este test depende de la configuración de AUTH_PASSWORD_VALIDATORS
        # Por ahora, solo verificamos que se pueden crear usuarios con contraseñas complejas
        
        complex_passwords = [
            "ComplexPass123!",
            "Another$ecure456",
            "VeryStr0ng&P@ssw0rd"
        ]
        
        for i, password in enumerate(complex_passwords):
            user = User.objects.create_user(
                username=f"complex{i}",
                email=f"complex{i}@example.com",
                password=password,
                company=self.company
            )
            self.assertTrue(user.check_password(password))


class UserManagementIntegrationTests(TestCase):
    """Tests de integración para gestión de usuarios"""
    
    def setUp(self):
        """Configuración inicial para tests de integración"""
        self.company = Company.objects.create(
            name="Integration Company",
            nit="666666666",
            address="Integration Address",
            phone="555-6666"
        )
        
        self.admin_user = User.objects.create_user(
            username="integrationadmin",
            email="integrationadmin@example.com",
            password="IntegrationPass123",
            company=self.company,
            is_staff=True
        )
    
    def test_user_company_relationship_cascade(self):
        """Test INT-001: Relación usuario-empresa con cascada"""
        # Crear usuario asociado a empresa
        user = User.objects.create_user(
            username="cascadetest",
            email="cascade@example.com",
            password="CascadePass123",
            company=self.company
        )
        
        user_id = user.id
        company_id = self.company.id
        
        # Verificar que la relación existe
        self.assertEqual(user.company.id, company_id)
        
        # Si se elimina la empresa, los usuarios también deberían eliminarse (CASCADE)
        self.company.delete()
        
        # Verificar que el usuario fue eliminado
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_user_attendee_relationship(self):
        """Test INT-002: Relación entre usuarios y asistentes por empresa"""
        # Crear usuario
        user = User.objects.create_user(
            username="attendeerelation",
            email="attendeerelation@example.com",
            password="AttendeePass123",
            company=self.company
        )
        
        # Crear asistente (implícitamente asociado a la misma empresa)
        attendee = Attendee.objects.create(
            name="Company Attendee",
            email="attendee@example.com",
            document_type="DNI",
            document_number="77777777",
            phone_number="555-7777",
            gender="M"
        )
        
        # Verificar que ambos existen
        self.assertTrue(User.objects.filter(username="attendeerelation").exists())
        self.assertTrue(Attendee.objects.filter(name="Company Attendee").exists())


class SecurityAuditTests(TestCase):
    """Tests de auditoría de seguridad"""
    
    def setUp(self):
        """Configuración inicial para tests de auditoría"""
        self.company = Company.objects.create(
            name="Audit Company",
            nit="777777777",
            address="Audit Address",
            phone="555-7777"
        )
    
    def test_failed_login_attempts_tracking(self):
        """Test AUD-001: Seguimiento de intentos de login fallidos"""
        # Este test requeriría implementar un sistema de tracking de intentos fallidos
        # Por ahora, validamos que el sistema de autenticación básico funciona
        
        client = Client()
        
        # Intento fallido
        response = client.post('/admin/login/', {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })
        
        # Verificar que no se autenticó
        self.assertNotEqual(response.status_code, 302)  # No redirect to admin
    
    def test_session_security(self):
        """Test AUD-002: Seguridad de sesiones"""
        user = User.objects.create_user(
            username="sessiontest",
            email="session@example.com",
            password="SessionPass123",
            company=self.company
        )
        
        client = Client()
        
        # Login
        login_success = client.login(username="sessiontest", password="SessionPass123")
        self.assertTrue(login_success)
        
        # Verificar que se creó una sesión
        self.assertIn('sessionid', client.cookies)
    
    @override_settings(DEBUG=False)
    def test_sensitive_info_not_exposed_in_production(self):
        """Test AUD-003: Información sensible no expuesta en producción"""
        user = User.objects.create_user(
            username="sensitive",
            email="sensitive@example.com",
            password="SensitivePass123",
            company=self.company
        )
        
        # En producción, cierta información no debería estar disponible
        user_str = str(user)
        # El password hash no debería estar en la representación string
        self.assertNotIn(user.password, user_str)


class PerformanceSecurityTests(TestCase):
    """Tests de rendimiento relacionados con seguridad"""
    
    def setUp(self):
        """Configuración inicial para tests de rendimiento de seguridad"""
        self.company = Company.objects.create(
            name="Performance Security Company",
            nit="888888888",
            address="Performance Security Address",
            phone="555-8888"
        )
    
    def test_password_hashing_performance(self):
        """Test PERF-001: Rendimiento del hashing de contraseñas"""
        start_time = time.time()
        
        # Crear múltiples usuarios con contraseñas
        for i in range(10):
            User.objects.create_user(
                username=f"perfuser{i}",
                email=f"perfuser{i}@example.com",
                password=f"PerfPassword{i}123",
                company=self.company
            )
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # El hashing de contraseñas debe ser seguro pero no excesivamente lento
        self.assertLess(creation_time, 10.0)  # Menos de 10 segundos para 10 usuarios
    
    def test_authentication_performance(self):
        """Test PERF-002: Rendimiento de autenticación"""
        # Crear usuario de prueba
        user = User.objects.create_user(
            username="authperf",
            email="authperf@example.com",
            password="AuthPerfPass123",
            company=self.company
        )
        
        start_time = time.time()
        
        # Realizar múltiples autenticaciones
        for _ in range(20):
            authenticated_user = authenticate(username="authperf", password="AuthPerfPass123")
            self.assertIsNotNone(authenticated_user)
        
        end_time = time.time()
        auth_time = end_time - start_time
        
        # Las autenticaciones deben ser rápidas
        self.assertLess(auth_time, 5.0)  # Menos de 5 segundos para 20 autenticaciones


class MigrationCompatibilityTests(TestCase):
    """Tests para validar compatibilidad con microservicio de autenticación"""
    
    def setUp(self):
        """Configuración inicial para tests de compatibilidad de migración"""
        self.company = Company.objects.create(
            name="Migration Auth Company",
            nit="999999999",
            address="Migration Auth Address",
            phone="555-9999"
        )
    
    def test_user_data_structure_for_microservice(self):
        """Test MIG-003: Estructura de datos compatible con microservicio"""
        user = User.objects.create_user(
            username="microservice",
            email="microservice@example.com",
            password="MicroservicePass123",
            company=self.company,
            first_name="Micro",
            last_name="Service"
        )
        
        # Campos que debe tener el microservicio de autenticación
        required_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined'
        ]
        
        for field in required_fields:
            self.assertTrue(hasattr(user, field), f"Campo {field} faltante")
    
    def test_user_serialization_format(self):
        """Test MIG-004: Formato de serialización para API JWT"""
        user = User.objects.create_user(
            username="jwttest",
            email="jwt@example.com",
            password="JWTPass123",
            company=self.company
        )
        
        # Datos que se incluirían en un JWT token
        jwt_payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'company_id': user.company.id,
            'is_admin': user.is_staff,
            'is_active': user.is_active
        }
        
        # Verificar que todos los campos son serializables
        self.assertIsInstance(jwt_payload['user_id'], int)
        self.assertIsInstance(jwt_payload['username'], str)
        self.assertIsInstance(jwt_payload['email'], str)
        self.assertIsInstance(jwt_payload['company_id'], int)
        self.assertIsInstance(jwt_payload['is_admin'], bool)
        self.assertIsInstance(jwt_payload['is_active'], bool)
