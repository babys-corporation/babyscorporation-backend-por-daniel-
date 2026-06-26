from rest_framework.serializers import ModelSerializer
from core.models import Avaliacao


class AvaliacaoSerializer(ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = ['id', 'baba', 'pai', 'estrelas', 'mensagem', 'criado_em']
        read_only_fields = ['id', 'criado_em']