from django.db import models
from .user import User


class Pai(models.Model):
    idpai = models.AutoField(primary_key=True)
    QuantidadeFilhos = models.IntegerField()
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pais',
        db_column='iduser'
    )