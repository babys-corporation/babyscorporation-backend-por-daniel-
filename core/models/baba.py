from django.db import models

class Baba(models.Model):
    idbaba = models.AutoField(primary_key=True)
    habilidades = models.CharField(max_length=700)
    dtnasc = models.DateField()
    idade = models.IntegerField()
    Formacao = models.CharField(max_length=700)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    sobre = models.CharField(max_length=700)


