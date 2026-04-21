from django.db import models

class Agendamento(models.Model):
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    precoagendamento = models.DecimalField(max_digits=10, decimal_places=2)
    qtdcriancas = models.IntegerField()