from django.db import models

class Pai(models.Model):
    idpai = models.AutoField(primary_key=True)
    QuantidadeFilhos = models.IntegerField()