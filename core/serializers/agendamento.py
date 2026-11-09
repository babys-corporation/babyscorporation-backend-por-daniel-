from datetime import time

from rest_framework import serializers

from core.models import Agendamento
from core.models.user import DIAS_SEMANA

LIMITE_INICIO = time(8, 0)
LIMITE_FIM = time(21, 0)


class AgendamentoSerializer(serializers.ModelSerializer):
    nome_familia = serializers.SerializerMethodField()

    def get_nome_familia(self, obj):
        usuario = obj.pai.usuario
        nome = ' '.join(parte for parte in [usuario.primeiro_nome, usuario.ultimo_nome] if parte).strip()
        return nome or usuario.email

    cidade = serializers.CharField(source='pai.usuario.cidade', read_only=True)

    nome_baba = serializers.SerializerMethodField()

    def get_nome_baba(self, obj):
        usuario = obj.baba.usuario
        nome = ' '.join(parte for parte in [usuario.primeiro_nome, usuario.ultimo_nome] if parte).strip()
        return nome or usuario.email

    class Meta:
        model = Agendamento
        fields = [
            'id',
            'baba',
            'nome_baba',
            'pai',
            'nome_familia',
            'cidade',
            'data',
            'hora_inicio',
            'hora_fim',
            'preco',
            'qtd_criancas',
            'status',
            'status_pagamento',
            'pix_brcode',
            'pix_txid',
            'pagamento_marcado_em',
            'pagamento_confirmado_em',
            'nivel_advertencia_aplicada',
            'criado_em',
        ]

        read_only_fields = [
            'pai',
            'preco',
            'status',
            'status_pagamento',
            'pix_brcode',
            'pix_txid',
            'pagamento_marcado_em',
            'pagamento_confirmado_em',
            'nivel_advertencia_aplicada',
            'criado_em',
        ]

        extra_kwargs = {
            'qtd_criancas': {'required': False},
        }

    def validate(self, attrs):
        hora_inicio = attrs.get(
            'hora_inicio',
            getattr(self.instance, 'hora_inicio', None),
        )
        hora_fim = attrs.get(
            'hora_fim',
            getattr(self.instance, 'hora_fim', None),
        )

        if hora_inicio is not None and hora_fim is not None:
            if hora_inicio < LIMITE_INICIO:
                raise serializers.ValidationError({'hora_inicio': 'O agendamento não pode começar antes das 08:00.'})

            if hora_fim > LIMITE_FIM:
                raise serializers.ValidationError({'hora_fim': 'O agendamento não pode terminar depois das 21:00.'})

            if hora_fim <= hora_inicio:
                raise serializers.ValidationError({
                    'hora_fim': 'O horário de término deve ser depois do horário de início.'
                })

            baba = attrs.get('baba', getattr(self.instance, 'baba', None))
            data = attrs.get('data', getattr(self.instance, 'data', None))

            # Disponibilidade semanal da babá: vale só para novos pedidos
            # (agendamentos já marcados não são revalidados).
            if self.instance is None and baba is not None and data is not None:
                dia = DIAS_SEMANA[data.weekday()]
                if (baba.disponibilidade or {}).get(dia, True) is False:
                    raise serializers.ValidationError({
                        'data': f'A babá não está disponível às {dia.lower()}s.'
                        if dia not in {'Sábado', 'Domingo'}
                        else f'A babá não está disponível aos {dia.lower()}s.'
                    })

            if baba is not None and data is not None:
                conflitos = Agendamento.objects.filter(
                    baba=baba,
                    data=data,
                    hora_inicio__lt=hora_fim,
                    hora_fim__gt=hora_inicio,
                ).exclude(status=Agendamento.Status.RECUSADO)

                if self.instance is not None:
                    conflitos = conflitos.exclude(pk=self.instance.pk)

                if conflitos.exists():
                    raise serializers.ValidationError({'detail': ('A babá já possui um agendamento nesse horário.')})

        return attrs
