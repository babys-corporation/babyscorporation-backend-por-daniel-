from datetime import time

from rest_framework import serializers
from core.models import Agendamento

LIMITE_INICIO = time(8, 0)
LIMITE_FIM = time(21, 0)


class AgendamentoSerializer(serializers.ModelSerializer):
    nome_familia = serializers.SerializerMethodField()

    def get_nome_familia(self, obj):
        usuario = obj.pai.usuario
        nome = " ".join(
            parte for parte in [usuario.primeiro_nome, usuario.ultimo_nome] if parte
        ).strip()
        return nome or usuario.email

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
            "qtd_criancas",
            "status",
            "status_pagamento",
            "pix_brcode",
            "pix_txid",
            "pagamento_marcado_em",
            "pagamento_confirmado_em",
            "nivel_advertencia_aplicada",
            "criado_em",
        ]

        read_only_fields = [
            "pai",
            "status",
            "status_pagamento",
            "pix_brcode",
            "pix_txid",
            "pagamento_marcado_em",
            "pagamento_confirmado_em",
            "nivel_advertencia_aplicada",
            "criado_em",
        ]

        extra_kwargs = {
            "qtd_criancas": {"required": False},
        }

    def validate(self, attrs):
        hora_inicio = attrs.get("hora_inicio")
        hora_fim = attrs.get("hora_fim")

        if hora_inicio is not None and hora_fim is not None:
            if hora_inicio < LIMITE_INICIO:
                raise serializers.ValidationError({
                    "hora_inicio": "O agendamento não pode começar antes das 08:00."
                })

            if hora_fim > LIMITE_FIM:
                raise serializers.ValidationError({
                    "hora_fim": "O agendamento não pode terminar depois das 21:00."
                })

            if hora_fim <= hora_inicio:
                raise serializers.ValidationError({
                    "hora_fim": "O horário de término deve ser depois do horário de início."
                })

        return attrs