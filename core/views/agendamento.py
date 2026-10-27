from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

import io

import qrcode
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from core.models import Agendamento, PerfilPai
from core.serializers import AgendamentoSerializer
from core.services.pix_estatico import gerar_pix_estatico
from core.services.regras_pix import verificar_pagamentos_atrasados


class AgendamentoViewSet(ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.tipo == "BABA":
            return Agendamento.objects.filter(baba__usuario=user)

        if user.tipo == "PAI":
            return Agendamento.objects.filter(pai__usuario=user)

        return Agendamento.objects.none()

    def perform_create(self, serializer):
        try:
            perfil_pai = PerfilPai.objects.get(usuario=self.request.user)
        except PerfilPai.DoesNotExist:
            raise PermissionDenied(
                {"detail": "Usuário precisa ter um perfil de pai para agendar."}
            )

        serializer.save(
            pai=perfil_pai,
            qtd_criancas=serializer.validated_data.get("qtd_criancas", 1),
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        verificar_pagamentos_atrasados()

        if request.user.tipo == "BABA":
            queryset = Agendamento.objects.filter(
                baba__usuario=request.user
            )

        else:
            queryset = Agendamento.objects.filter(
                pai__usuario=request.user
            )

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def _agendamento_da_baba(self, request, agendamento):
        if request.user.tipo != "BABA" or agendamento.baba.usuario != request.user:
            raise PermissionDenied(
                {"detail": "Somente a babá deste agendamento pode responder."}
            )

    @action(detail=True, methods=['post'])
    def aceitar(self, request, pk=None):
        agendamento = self.get_object()
        self._agendamento_da_baba(request, agendamento)

        if agendamento.status != Agendamento.Status.PENDENTE:
            return Response(
                {"detail": "Somente agendamentos pendentes podem ser aceitos."},
                status=400,
            )

        agendamento.status = Agendamento.Status.ACEITO

        chave_pix = agendamento.baba.chave_pix
        if chave_pix:
            nome = agendamento.baba.usuario.primeiro_nome or "Baba"
            brcode = gerar_pix_estatico(
                chave=chave_pix,
                valor=float(agendamento.preco),
                nome_recebedor=nome,
                cidade=agendamento.baba.usuario.cidade or "BRASIL",
                txid=f"BCORP{agendamento.id}",
            )
            agendamento.status_pagamento = Agendamento.StatusPagamento.AGUARDANDO
            agendamento.pix_brcode = brcode
            agendamento.pix_txid = f"BCORP{agendamento.id}"
        else:
            agendamento.status_pagamento = Agendamento.StatusPagamento.NAO_EXIGIDO

        agendamento.save()

        return Response(self.get_serializer(agendamento).data)

    @action(detail=True, methods=['get'])
    def pagamento(self, request, pk=None):
        agendamento = self.get_object()

        if request.user.tipo == "BABA":
            if agendamento.baba.usuario != request.user:
                raise PermissionDenied({"detail": "Nao e a sua babá."})
        elif request.user.tipo == "PAI":
            if agendamento.pai.usuario != request.user:
                raise PermissionDenied({"detail": "Nao e o seu agendamento."})
        else:
            raise PermissionDenied({"detail": "Usuário inválido."})

        if agendamento.status != Agendamento.Status.ACEITO:
            return Response(
                {"detail": "Somente agendamentos aceitos possuem cobrança."},
                status=400,
            )

        if agendamento.status_pagamento == Agendamento.StatusPagamento.NAO_EXIGIDO:
            return Response(
                {
                    "detail": "A babá ainda não cadastrou uma chave Pix para receber.",
                    "status_pagamento": agendamento.status_pagamento,
                }
            )

        return Response(
            {
                "id": agendamento.id,
                "preco": agendamento.preco,
                "status_pagamento": agendamento.status_pagamento,
                "pix_brcode": agendamento.pix_brcode,
                "pix_txid": agendamento.pix_txid,
            }
        )

    @action(detail=True, methods=['get'])
    def pagamento_qrcode(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.status != Agendamento.Status.ACEITO:
            return Response(
                {"detail": "Somente agendamentos aceitos possuem cobrança."},
                status=400,
            )

        if (
            agendamento.status_pagamento == Agendamento.StatusPagamento.NAO_EXIGIDO
            or not agendamento.pix_brcode
        ):
            return Response(
                {"detail": "A babá ainda não cadastrou uma chave Pix."},
                status=400,
            )

        return HttpResponse(
            _gerar_qrcode_png(agendamento.pix_brcode),
            content_type="image/png",
        )

    @action(detail=True, methods=['post'])
    def marcar_pago(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.pai.usuario != request.user:
            raise PermissionDenied({"detail": "Somente o pai deste agendamento."})

        if agendamento.status != Agendamento.Status.ACEITO:
            return Response(
                {"detail": "Somente agendamentos aceitos possuem cobrança."},
                status=400,
            )

        if agendamento.status_pagamento != Agendamento.StatusPagamento.AGUARDANDO:
            return Response(
                {"detail": "Este agendamento não está aguardando pagamento."},
                status=400,
            )

        agendamento.pagamento_marcado_em = timezone.now()
        agendamento.save(update_fields=["pagamento_marcado_em"])

        return Response(self.get_serializer(agendamento).data)

    @action(detail=True, methods=['post'])
    def marcar_pago(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.pai.usuario != request.user:
            raise PermissionDenied({"detail": "Somente o pai deste agendamento."})

        if agendamento.status != Agendamento.Status.ACEITO:
            return Response(
                {"detail": "Somente agendamentos aceitos possuem cobrança."},
                status=400,
            )

        if agendamento.status_pagamento != Agendamento.StatusPagamento.AGUARDANDO:
            return Response(
                {"detail": "Este agendamento não está aguardando pagamento."},
                status=400,
            )

        agendamento.pagamento_marcado_em = timezone.now()
        agendamento.save(update_fields=["pagamento_marcado_em"])

        return Response(self.get_serializer(agendamento).data)

    @action(detail=True, methods=['post', 'patch'])
    def confirmar_pagamento(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.baba.usuario != request.user:
            raise PermissionDenied({"detail": "Somente a babá deste agendamento."})

        if agendamento.status != Agendamento.Status.ACEITO:
            return Response(
                {"detail": "Somente agendamentos aceitos."},
                status=400,
            )

        if agendamento.status_pagamento != Agendamento.StatusPagamento.AGUARDANDO:
            return Response(
                {"detail": "Este agendamento não está aguardando pagamento."},
                status=400,
            )

        if not agendamento.pagamento_marcado_em:
            return Response(
                {"detail": "O pai ainda não marcou o Pix como pago."},
                status=400,
            )

        agendamento.status_pagamento = Agendamento.StatusPagamento.PAGO
        agendamento.pagamento_confirmado_em = timezone.now()
        agendamento.save(update_fields=["status_pagamento", "pagamento_confirmado_em"])

        return Response(self.get_serializer(agendamento).data)

    @action(detail=True, methods=['post'])
    def recusar(self, request, pk=None):
        agendamento = self.get_object()
        self._agendamento_da_baba(request, agendamento)

        if agendamento.status != Agendamento.Status.PENDENTE:
            return Response(
                {"detail": "Somente agendamentos pendentes podem ser recusados."},
                status=400,
            )

        agendamento.status = Agendamento.Status.RECUSADO
        agendamento.save()

        return Response(self.get_serializer(agendamento).data)


class CelcoinPixWebhookView(APIView):
    """Recebe notificações de pagamento da Celcoin (pix-payment-in)."""

    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data or {}
        token_recebido = (
            request.headers.get("Authorization", "")
            .replace("Bearer", "")
            .strip()
        )
        token_cfg = getattr(settings, "PIX_WEBHOOK_TOKEN", "")

        if token_cfg and token_cfg != token_recebido:
            return Response({"detail": "Token inválido."}, status=403)

        entity = payload.get("entity")
        status = payload.get("status")
        body = payload.get("body", {}) or {}

        if entity == "pix-payment-in" and status == "CONFIRMED":
            txid = (
                body.get("transactionIdentification")
                or body.get("clientCode")
                or ""
            )
            valor = float(body.get("amount", 0))

            agendamento = None

            if txid:
                agendamento = (
                    Agendamento.objects.filter(
                        pix_txid=txid,
                        status=Agendamento.Status.ACEITO,
                        status_pagamento=Agendamento.StatusPagamento.AGUARDANDO,
                    )
                    .first()
                )

            if agendamento is None:
                agendamento = (
                    Agendamento.objects.filter(
                        status=Agendamento.Status.ACEITO,
                        status_pagamento=Agendamento.StatusPagamento.AGUARDANDO,
                    )
                    .order_by("-criado_em")
                    .first()
                )

            if agendamento is not None:
                agendamento.status_pagamento = Agendamento.StatusPagamento.PAGO
                agendamento.save(update_fields=["status_pagamento"])

        return Response({"ok": True})


def _gerar_qrcode_png(conteudo: str) -> bytes:
    img = qrcode.make(conteudo)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()