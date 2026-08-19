from rest_framework import serializers
from core.models import Agendamento

class AgendamentoSerializer(serializers.ModelSerializer):
    nome_familia = serializers.CharField(
        source="pai.usuario.email",
        read_only=True
    )

    cidade = serializers.CharField(
        source="pai.usuario.cidade",
        read_only=True
    )

    class Meta:
        model = Agendamento
        fields = [
            "id",
            "baba",
            "pai",
            "nome_familia",
            "cidade",
            "data",
            "hora_inicio",
            "hora_fim",
            "preco",
            "qtd_criancas"
        ]