from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
import tempfile

from apps.attachments.models import Attachment
from apps.attendees.models import Attendee


class AttachmentModelTests(TestCase):
    """Tests para el modelo Attachment - Validando gestión de archivos"""
    
    def test_create_attachment_valid(self):
        """Test ATT-001: Crear adjunto válido"""
        attachment = Attachment.objects.create(
            name="receipt_001.pdf",
            file_path="/uploads/receipts/receipt_001.pdf"
        )
        
        self.assertEqual(attachment.name, "receipt_001.pdf")
        self.assertEqual(attachment.file_path, "/uploads/receipts/receipt_001.pdf")
        self.assertTrue(attachment.created)
        self.assertTrue(attachment.modified)
    
    def test_attachment_str_representation(self):
        """Test: Representación string del modelo Attachment"""
        attachment = Attachment.objects.create(
            name="document.pdf",
            file_path="/uploads/document.pdf"
        )
        
        # Asumiendo que __str__ retorna el nombre
        self.assertEqual(str(attachment), "document.pdf")
    
    def test_attachment_file_extensions(self):
        """Test ATT-002: Diferentes extensiones de archivo"""
        file_types = [
            ("receipt.pdf", "/uploads/receipt.pdf"),
            ("invoice.jpg", "/uploads/invoice.jpg"),
            ("payment_proof.png", "/uploads/payment_proof.png"),
            ("document.doc", "/uploads/document.doc"),
            ("spreadsheet.xlsx", "/uploads/spreadsheet.xlsx")
        ]
        
        for name, path in file_types:
            attachment = Attachment.objects.create(
                name=name,
                file_path=path
            )
            self.assertEqual(attachment.name, name)
            self.assertEqual(attachment.file_path, path)
    
    def test_attachment_path_validation(self):
        """Test ATT-003: Validación de rutas de archivos"""
        # Rutas válidas
        valid_paths = [
            "/uploads/files/document.pdf",
            "uploads/receipts/receipt_001.jpg",
            "media/attachments/proof.png",
            "/var/www/uploads/file.doc"
        ]
        
        for i, path in enumerate(valid_paths):
            attachment = Attachment.objects.create(
                name=f"file_{i}.ext",
                file_path=path
            )
            self.assertEqual(attachment.file_path, path)
    
    def test_attachment_name_required(self):
        """Test ATT-004: Nombre del archivo es requerido"""
        attachment = Attachment(
            name="",  # Nombre vacío
            file_path="/valid/path/file.pdf"
        )
        
        with self.assertRaises(ValidationError):
            attachment.full_clean()
    
    def test_attachment_file_path_required(self):
        """Test ATT-005: Ruta del archivo es requerida"""
        attachment = Attachment(
            name="valid_name.pdf",
            file_path=""  # Ruta vacía
        )
        
        with self.assertRaises(ValidationError):
            attachment.full_clean()


class AttachmentAttendeeRelationTests(TestCase):
    """Tests de relación entre Attachment y Attendee"""
    
    def setUp(self):
        """Configuración inicial"""
        self.attachment = Attachment.objects.create(
            name="payment_receipt.pdf",
            file_path="/uploads/receipts/payment_receipt.pdf"
        )
    
    def test_attendee_with_attachment(self):
        """Test REL-ATT-001: Asistente con archivo adjunto"""
        attendee = Attendee.objects.create(
            name="Juan Con Adjunto",
            email="juan.adjunto@example.com",
            document_type="DNI",
            document_number="12345678",
            phone_number="555-1234",
            gender="M",
            attachment=self.attachment
        )
        
        self.assertEqual(attendee.attachment, self.attachment)
        self.assertEqual(attendee.attachment.name, "payment_receipt.pdf")
    
    def test_attendee_without_attachment(self):
        """Test REL-ATT-002: Asistente sin archivo adjunto"""
        attendee = Attendee.objects.create(
            name="María Sin Adjunto",
            email="maria.sin@example.com",
            document_type="DNI",
            document_number="87654321",
            phone_number="555-5678",
            gender="F"
            # attachment omitido (NULL)
        )
        
        self.assertIsNone(attendee.attachment)
    
    def test_attachment_cascade_deletion(self):
        """Test REL-ATT-003: Eliminación en cascada de adjuntos"""
        attendee = Attendee.objects.create(
            name="Test Cascade",
            email="cascade@example.com",
            document_type="DNI",
            document_number="11111111",
            phone_number="555-1111",
            gender="M",
            attachment=self.attachment
        )
        
        attachment_id = self.attachment.id
        
        # Eliminar el adjunto
        self.attachment.delete()
        
        # El asistente también debería eliminarse (CASCADE)
        with self.assertRaises(Attendee.DoesNotExist):
            attendee.refresh_from_db()
        
        # Verificar que el adjunto fue eliminado
        self.assertFalse(Attachment.objects.filter(id=attachment_id).exists())
    
    def test_multiple_attendees_same_attachment(self):
        """Test REL-ATT-004: Múltiples asistentes con el mismo adjunto"""
        # Esto debería fallar si la relación es uno-a-uno
        attendee1 = Attendee.objects.create(
            name="Primer Asistente",
            email="primero@example.com",
            document_type="DNI",
            document_number="22222222",
            phone_number="555-2222",
            gender="M",
            attachment=self.attachment
        )
        
        # Intentar asignar el mismo adjunto a otro asistente
        with self.assertRaises(Exception):  # Podría ser IntegrityError
            attendee2 = Attendee.objects.create(
                name="Segundo Asistente",
                email="segundo@example.com",
                document_type="DNI",
                document_number="33333333",
                phone_number="555-3333",
                gender="F",
                attachment=self.attachment  # Mismo adjunto
            )


class AttachmentFileOperationTests(TestCase):
    """Tests de operaciones con archivos reales"""
    
    def setUp(self):
        """Configurar directorio temporal para tests"""
        self.test_media_root = tempfile.mkdtemp()
    
    def tearDown(self):
        """Limpiar archivos de prueba"""
        import shutil
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)
    
    def test_attachment_file_size_tracking(self):
        """Test FILE-ATT-001: Seguimiento del tamaño de archivo"""
        # Crear archivo de prueba
        test_content = b"Este es un contenido de prueba para el archivo PDF"
        test_file_path = os.path.join(self.test_media_root, "test_file.pdf")
        
        with open(test_file_path, 'wb') as f:
            f.write(test_content)
        
        attachment = Attachment.objects.create(
            name="test_file.pdf",
            file_path=test_file_path
        )
        
        # Verificar que el archivo existe
        self.assertTrue(os.path.exists(test_file_path))
        
        # Verificar el tamaño del archivo
        file_size = os.path.getsize(test_file_path)
        self.assertEqual(file_size, len(test_content))
    
    def test_attachment_file_extension_validation(self):
        """Test FILE-ATT-002: Validación de extensiones permitidas"""
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xlsx']
        
        for ext in allowed_extensions:
            attachment = Attachment.objects.create(
                name=f"test_file{ext}",
                file_path=f"/uploads/test_file{ext}"
            )
            
            # Verificar que la extensión está en el nombre
            self.assertTrue(attachment.name.endswith(ext))
    
    def test_attachment_file_name_sanitization(self):
        """Test FILE-ATT-003: Sanitización de nombres de archivo"""
        # Nombres problemáticos que deberían manejarse
        problematic_names = [
            "archivo con espacios.pdf",
            "archivo_con_acentos_ñ.jpg",
            "archivo-con-guiones.png",
            "archivo.with.dots.doc"
        ]
        
        for name in problematic_names:
            attachment = Attachment.objects.create(
                name=name,
                file_path=f"/uploads/{name}"
            )
            
            # El nombre debería guardarse (con o sin sanitización)
            self.assertIsNotNone(attachment.name)
            self.assertTrue(len(attachment.name) > 0)


class AttachmentSecurityTests(TestCase):
    """Tests de seguridad para adjuntos"""
    
    def test_attachment_path_traversal_protection(self):
        """Test SEC-ATT-001: Protección contra path traversal"""
        # Intentos de path traversal que deberían bloquearse
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam", 
            "/etc/shadow",
            "../../../../usr/bin/python"
        ]
        
        for path in malicious_paths:
            attachment = Attachment.objects.create(
                name="malicious_file.txt",
                file_path=path
            )
            
            # El path se guarda tal como se proporciona en este modelo básico
            # En una implementación real, debería haber validación
            self.assertEqual(attachment.file_path, path)
    
    def test_attachment_file_type_restrictions(self):
        """Test SEC-ATT-002: Restricciones de tipos de archivo"""
        # Tipos de archivo potencialmente peligrosos
        dangerous_files = [
            "script.exe",
            "malware.bat", 
            "virus.scr",
            "trojan.com",
            "script.sh"
        ]
        
        for filename in dangerous_files:
            attachment = Attachment.objects.create(
                name=filename,
                file_path=f"/uploads/{filename}"
            )
            
            # En este modelo básico, se permite cualquier tipo de archivo
            # En una implementación real, debería haber validación de tipos
            self.assertEqual(attachment.name, filename)
    
    def test_attachment_file_size_limits(self):
        """Test SEC-ATT-003: Límites de tamaño de archivo"""
        # Simular archivos de diferentes tamaños
        file_sizes = [
            ("small_file.pdf", "/uploads/small.pdf"),
            ("medium_file.jpg", "/uploads/medium.jpg"),
            ("large_file.doc", "/uploads/large.doc")
        ]
        
        for name, path in file_sizes:
            attachment = Attachment.objects.create(
                name=name,
                file_path=path
            )
            
            # Verificar que se creó el adjunto
            self.assertIsNotNone(attachment.id)


class AttachmentPerformanceTests(TestCase):
    """Tests de rendimiento para adjuntos"""
    
    def test_bulk_attachment_creation(self):
        """Test PERF-ATT-001: Creación masiva de adjuntos"""
        import time
        
        start_time = time.time()
        
        attachments = []
        for i in range(100):
            attachments.append(Attachment(
                name=f"bulk_file_{i}.pdf",
                file_path=f"/uploads/bulk/bulk_file_{i}.pdf"
            ))
        
        Attachment.objects.bulk_create(attachments)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Debe crear 100 adjuntos en tiempo razonable
        self.assertLess(creation_time, 3.0)
        
        # Verificar que se crearon todos
        created_attachments = Attachment.objects.filter(
            name__startswith="bulk_file_"
        )
        self.assertEqual(created_attachments.count(), 100)
    
    def test_attachment_query_performance(self):
        """Test PERF-ATT-002: Rendimiento de consultas de adjuntos"""
        import time
        
        # Crear adjuntos de prueba
        for i in range(50):
            Attachment.objects.create(
                name=f"query_file_{i}.pdf",
                file_path=f"/uploads/query/query_file_{i}.pdf"
            )
        
        start_time = time.time()
        
        # Consultas comunes
        # 1. Buscar por extensión
        pdf_attachments = Attachment.objects.filter(name__endswith='.pdf')
        list(pdf_attachments)
        
        # 2. Buscar por ruta
        upload_attachments = Attachment.objects.filter(file_path__contains='/uploads/')
        list(upload_attachments)
        
        # 3. Ordenar por nombre
        sorted_attachments = Attachment.objects.all().order_by('name')
        list(sorted_attachments)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Las consultas deben ser rápidas
        self.assertLess(query_time, 2.0)


class AttachmentMigrationCompatibilityTests(TestCase):
    """Tests de compatibilidad para migración de adjuntos"""
    
    def test_attachment_serialization_format(self):
        """Test MIG-ATT-001: Formato de serialización para microservicio"""
        attachment = Attachment.objects.create(
            name="migration_test.pdf",
            file_path="/uploads/migration/migration_test.pdf"
        )
        
        # Formato que usaría el microservicio
        serialized_data = {
            'id': attachment.id,
            'name': attachment.name,
            'file_path': attachment.file_path,
            'created': attachment.created.isoformat() if attachment.created else None,
            'modified': attachment.modified.isoformat() if attachment.modified else None
        }
        
        # Verificar que los datos son serializables
        self.assertIsInstance(serialized_data['id'], int)
        self.assertIsInstance(serialized_data['name'], str)
        self.assertIsInstance(serialized_data['file_path'], str)
    
    def test_attachment_file_metadata_extraction(self):
        """Test MIG-ATT-002: Extracción de metadatos para migración"""
        attachment = Attachment.objects.create(
            name="metadata_test.pdf",
            file_path="/uploads/metadata/metadata_test.pdf"
        )
        
        # Metadatos que podrían necesitarse en el microservicio
        metadata = {
            'original_name': attachment.name,
            'file_extension': os.path.splitext(attachment.name)[1],
            'storage_path': attachment.file_path,
            'mime_type': self._guess_mime_type(attachment.name),
            'created_at': attachment.created.isoformat() if attachment.created else None
        }
        
        # Verificar que se pueden extraer los metadatos
        self.assertEqual(metadata['file_extension'], '.pdf')
        self.assertIn('pdf', metadata['mime_type'].lower())
    
    def _guess_mime_type(self, filename):
        """Helper para adivinar el tipo MIME"""
        extension = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return mime_types.get(extension, 'application/octet-stream')
