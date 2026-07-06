from django.db import models
from core.models.user import PerfilBaba, PerfilPai


class Agendamento(models.Model):

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        ACEITO = "ACEITO", "Aceito"
        RECUSADO = "RECUSADO", "Recusado"

    baba = models.ForeignKey(
        PerfilBaba,
        on_delete=models.PROTECT,
        related_name="agendamentos",
    )

    pai = models.ForeignKey(
        PerfilPai,
        on_delete=models.PROTECT,
        related_name="agendamentos",
    )

    data = models.DateField()

    hora_inicio = models.TimeField()

    hora_fim = models.TimeField()

    preco = models.DecimalField(max_digits=10, decimal_places=2)

    qtd_criancas = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    criado_em = models.DateTimeField(auto_now_add=True)