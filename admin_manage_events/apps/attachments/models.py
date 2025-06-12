# apps/attachments/models.py


from django.db import models
from utils.models import TimeStampedModel
from apps.events.models import Company
from django.core.exceptions import ValidationError
import os

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]  # obtiene la extensión del archivo
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if ext.lower() not in valid_extensions:
        raise ValidationError(f'Tipo de archivo no soportado. Solo se permiten archivos: {", ".join(valid_extensions)}.')

def validate_file_size(file):
    max_size_kb = 5120  # 5 MB
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"El tamaño máximo del archivo es {max_size_kb} KB")

class Attachment(TimeStampedModel):
    attachment_id = models.AutoField(primary_key=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE,verbose_name='Evento')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', validators=[validate_file_size,validate_file_extension], verbose_name='Archivo')
    name = models.CharField(max_length=255, verbose_name='Asunto')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')

    class Meta:
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'

    def __str__(self):
        return self.name