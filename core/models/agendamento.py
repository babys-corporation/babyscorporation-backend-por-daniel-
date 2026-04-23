from django.db import models

from core.models.baba import Baba

from .pai import Pai

class Agendamento(models.Model):

    Idbaba = models.ForeignKey(

       Baba,
        on_delete=models.PROTECT,
        related_name='agendamento',
        db_column='idbaba'

    )
    idpai = models.ForeignKey(

       Pai,
        on_delete=models.PROTECT,
        related_name='agendamento',
        db_column='idpai'

     )

    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    precoagendamento = models.DecimalField(max_digits=10, decimal_places=2)
    qtdcriancas = models.IntegerField()