from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django_cpf_cnpj.fields import CPFField
from phonenumber_field.modelfields import PhoneNumberField
from uploader.models import Image


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório.")

        email = self.normalize_email(email)

        usuario = self.model(
            email=email,
            **extra_fields,
        )

        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusuário precisa ter is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_superuser=True.")

        return self.create_user(
            email=email,
            password=password,
            **extra_fields,
        )


class Usuario(AbstractUser):
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class TipoUsuario(models.TextChoices):
        PAI = "PAI", "Pai/Mãe"
        BABA = "BABA", "Babá"

    objects = UsuarioManager()

    tipo = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PAI,
    )

    foto = models.ForeignKey(
        Image,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    email = models.EmailField(unique=True)

    primeiro_nome = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    ultimo_nome = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )

    cpf = CPFField(
        null=True,
        blank=True,
        unique=True,
    )

    telefone = PhoneNumberField(
        null=True,
        blank=True,
        region="BR",
    )

    cep = models.CharField(
        max_length=9,
        null=True,
        blank=True,
    )

    cidade = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    bairro = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    def clean(self):
        if self.tipo == self.TipoUsuario.BABA and not self.foto:
            raise ValidationError({
                "foto": "Foto é obrigatória para babás."
            })

    def __str__(self):
        nome = self.get_full_name()

        if nome:
            return f"{nome} ({self.tipo})"

        return f"{self.email} ({self.tipo})"


class PerfilPai(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_pai",
    )

    numero_filhos = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Perfil Pai - {self.usuario}"


class PerfilBaba(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_baba",
    )

    experiencia_anos = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
    )

    descricao = models.TextField(
        null=True,
        blank=True,
    )

    disponivel = models.BooleanField(
        default=True,
    )

    valor_hora = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    habilidades = models.CharField(
        max_length=700,
        null=True,
        blank=True,
    )

    dtnasc = models.DateField(
        verbose_name="Data de Nascimento",
        null=True,
        blank=True,
    )

    formacao = models.CharField(
        max_length=700,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Perfil Babá - {self.usuario}"


class Crianca(models.Model):
    class Genero(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMININO = "F", "Feminino"
        OUTRO = "O", "Outro"

    perfil_pai = models.ForeignKey(
        PerfilPai,
        on_delete=models.CASCADE,
        related_name="criancas",
    )

    nome = models.CharField(
        max_length=255,
    )

    genero = models.CharField(
        max_length=1,
        choices=Genero.choices,
    )

    idade = models.PositiveIntegerField()

    alergias = models.TextField(
        null=True,
        blank=True,
    )

    condicoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Condições físicas/mentais",
    )

    def __str__(self):
        return f"{self.nome} - filho de {self.perfil_pai.usuario}"


class PerfilBabaCompleta(models.Model):
    """
    Tabela utilitária: guarda apenas os perfis de babá
    que estão com todas as informações necessárias preenchidas.

    É mantida sincronizada automaticamente via signals
    (veja core/signals.py) — não deve ser editada manualmente.
    """

    perfil_baba = models.OneToOneField(
        PerfilBaba,
        on_delete=models.CASCADE,
        related_name="completude",
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Completa - {self.perfil_baba.usuario}"