"""
Regras de confirmação de pagamento Pix.

Fluxo:
- O pai marca o Pix como pago (pagamento_marcado_em).
- A babá deve confirmar o recebimento (pagamento_confirmado_em).
- Se não confirmar:
    * 1 dia  -> 1ª advertência
    * 2 dias -> 2ª advertência
    * 3 dias -> 3ª advertência
    * 4+ dias-> conta banida (não aparece na busca)

A aplicação das punições é idempotente (nivel_advertencia_aplicada).
"""

from __future__ import annotations

from django.utils import timezone

from core.models import Agendamento

DIAS_POR_ADVERTENCIA = {
    1: 1,
    2: 2,
    3: 3,
}
DIA_BANIMENTO = 4


def _dias_atrasado(agendamento, agora):
    if not agendamento.pagamento_marcado_em:
        return 0

    criado_delta = agora - agendamento.pagamento_marcado_em
    return max(0, criado_delta.days)


def verificar_pagamentos_atrasados():
    """Aplica advertências/banimento para todos os agendamentos atrasados."""
    agora = timezone.now()

    pendentes = Agendamento.objects.filter(
        status=Agendamento.Status.ACEITO,
        status_pagamento=Agendamento.StatusPagamento.AGUARDANDO,
        pagamento_marcado_em__isnull=False,
        pagamento_confirmado_em__isnull=True,
    )

    resultados = []

    for agendamento in pendentes:
        dias = _dias_atrasado(agendamento, agora)
        if dias >= DIA_BANIMENTO:
            _banir(agendamento)
            resultados.append((agendamento, "BANIDO"))
            continue

        if dias in DIAS_POR_ADVERTENCIA:
            alvo = DIAS_POR_ADVERTENCIA[dias]
            if agendamento.nivel_advertencia_aplicada < alvo:
                agendamento.nivel_advertencia_aplicada = alvo
                agendamento.save(update_fields=["nivel_advertencia_aplicada"])

                perfil = agendamento.baba
                perfil.advertencias = alvo
                perfil.save(update_fields=["advertencias"])
                resultados.append((agendamento, f"ADVERTENCIA_{alvo}"))

    return resultados


def _banir(agendamento):
    perfil = agendamento.baba
    if not perfil.banido:
        perfil.banido = True
        perfil.banido_em = timezone.now()
        perfil.save(update_fields=["banido", "banido_em"])

    agendamento.nivel_advertencia_aplicada = 3
    agendamento.save(update_fields=["nivel_advertencia_aplicada"])