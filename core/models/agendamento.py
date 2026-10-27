from django.db import models
from core.models.user import PerfilBaba, PerfilPai


class Agendamento(models.Model):

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        ACEITO = "ACEITO", "Aceito"
        RECUSADO = "RECUSADO", "Recusado"

    class StatusPagamento(models.TextChoices):
        AGUARDANDO = "AGUARDANDO", "Aguardando pagamento"
        PAGO = "PAGO", "Pago"
        NAO_EXIGIDO = "NAO_EXIGIDO", "Pagamento não exigido"

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

    status_pagamento = models.CharField(
        max_length=20,
        choices=StatusPagamento.choices,
        default=StatusPagamento.NAO_EXIGIDO,
    )

    pix_brcode = models.TextField(
        null=True,
        blank=True,
        verbose_name="Código Pix copia e cola",
    )

    pix_txid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Identificador da cobrança Pix",
    )

    pagamento_marcado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Quando o pai marcou o Pix como pago",
    )

    pagamento_confirmado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Quando a babá confirmou o recebimento",
    )

    nivel_advertencia_aplicada = models.PositiveIntegerField(
        default=0,
        help_text="Quantas advertências já foram aplicadas (0 a 3).",
    )

    criado_em = models.DateTimeField(auto_now_add=True)