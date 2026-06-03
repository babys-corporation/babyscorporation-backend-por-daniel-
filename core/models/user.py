from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django_cpf_cnpj.fields import CPFField
from phonenumber_field.modelfields import PhoneNumberField
from uploader.models import Image


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        PAI = "PAI", "Pai/Mãe"
        BABA = "BABA", "Babá"

    tipo = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PAI,
    )
    foto = models.ForeignKey(
        Image,
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    cpf = CPFField(null=True, blank=True, unique=True)
    telefone = PhoneNumberField(null=True, blank=True, region='BR')

    def clean(self):
        if self.tipo == self.TipoUsuario.BABA and not self.foto:
            raise ValidationError({'foto': 'Foto é obrigatória para babás.'})

    def __str__(self):
        nome = self.get_full_name()
        return f"{nome if nome else self.username} ({self.tipo})"


class PerfilPai(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_pai",
    )
    numero_filhos = models.PositiveIntegerField(default=0)
    endereco = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Perfil Pai - {self.usuario}"


class PerfilBaba(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_baba",
    )
    experiencia_anos = models.PositiveIntegerField(default=0)
    descricao = models.TextField(null=True, blank=True)
    disponivel = models.BooleanField(default=True)
    valor_hora = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    habilidades = models.CharField(max_length=700, null=True, blank=True)
    dtnasc = models.DateField(verbose_name="Data de Nascimento", null=True, blank=True)
    formacao = models.CharField(max_length=700, null=True, blank=True)

    def __str__(self):
        return f"Perfil Babá - {self.usuario}"