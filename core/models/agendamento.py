from django.db import models
from core.models.user import PerfilBaba, PerfilPai


class Agendamento(models.Model):
    baba = models.ForeignKey(
        PerfilBaba,
        on_delete=models.PROTECT,
        related_name='agendamentos',
    )
    pai = models.ForeignKey(
        PerfilPai,
        on_delete=models.PROTECT,
        related_name='agendamentos',
    )
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    qtd_criancas = models.IntegerField(verbose_name="Quantidade de Crianças")

    def __str__(self):
        return f"Agendamento {self.pai} com {self.baba} em {self.data}"