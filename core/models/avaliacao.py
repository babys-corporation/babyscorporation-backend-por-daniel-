from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core.models.user import PerfilBaba, PerfilPai


class Avaliacao(models.Model):
    baba = models.ForeignKey(
        PerfilBaba,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
    )
    pai = models.ForeignKey(
        PerfilPai,
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas',
    )
    estrelas = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),  # não permite nota menor que 1
            MaxValueValidator(5),  # não permite nota maior que 5
        ]
    )
    mensagem = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together garante que um pai só pode avaliar a mesma babá UMA vez
        # se tentar avaliar de novo, o banco rejeita automaticamente
        unique_together = ('baba', 'pai')

        # ordering define a ordem padrão das avaliações ao buscar no banco
        # o '-' antes de 'criado_em' significa DECRESCENTE (mais recente primeiro)
        # sem o '-' seria crescente (mais antiga primeiro)
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.pai} avaliou {self.baba} com {self.estrelas} estrelas"