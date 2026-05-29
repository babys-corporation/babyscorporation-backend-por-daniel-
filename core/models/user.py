from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        PAI = "PAI", "Pai/Mãe"
        BABA = "BABA", "Babá"

    tipo = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PAI,
    )
    foto = models.ImageField(upload_to="usuarios/fotos/", null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        nome = self.get_full_name()
        return f"{nome if nome else self.username} ({self.tipo})"

class PerfilPai(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_pai",
    )
    cpf = models.CharField(max_length=11, unique=True)
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
    dtnasc = models.DateField(verbose_name=("Data de Nascimento"),null=True, blank=True)
    formacao = models.CharField(max_length=700, null=True, blank=True)
    sobre = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Perfil Babá - {self.usuario}"