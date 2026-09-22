"""
Serviço de integração Pix (recebimento via QR Code dinâmico / copia e cola).

Camada pluggável: cada gateway implementa criar_cobranca() e a aplicação
escolhe o provedor via settings.PIX_GATEWAY ("celcoin" ou "mock").

O gateway "mock" é usado em desenvolvimento/homologação e gera um código
Pix fictício, permitindo testar todo o fluxo sem credenciais reais.
"""

from __future__ import annotations

import time
import uuid

import requests

from django.conf import settings


class PixGatewayError(Exception):
    pass


class MockPixGateway:
    """Gera um código Pix fictício para testes (sem chamar provedor)."""

    nome = "mock"

    def criar_cobranca(self, *, chave, valor, descricao, nome_pagador=None):
        valor = f"{float(valor):.2f}".replace(".", ",")
        txid = f"mock{int(time.time() * 1000)}"
        brcode = (
            f"00020101021226170014br.gov.bcb.pix0122{txid}"
            f"5204000053039865405{valor}"  # placeholder
            f"5802BR5909MockPix6009SaoPaulo6304A1B2"
        )
        return {
            "txid": txid,
            "brcode": brcode,
            "emv": brcode,
        }


class CelcoinPixGateway:
    """Integração com a API Pix da Celcoin (sandbox e produção)."""

    nome = "celcoin"

    def _base_url(self):
        return getattr(settings, "PIX_CELCOIN_BASE_URL", "https://sandbox.openfinance.celcoin.dev")

    def _token(self):
        url = f"{self._base_url()}/v5/token"
        body = {
            "client_id": settings.PIX_CELCOIN_CLIENT_ID,
            "grant_type": "client_credentials",
            "client_secret": settings.PIX_CELCOIN_CLIENT_SECRET,
        }
        resposta = requests.post(
            url,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=(5, 20),
        )
        if resposta.status_code != 200:
            raise PixGatewayError(
                f"Celcoin token falhou ({resposta.status_code}): {resposta.text[:300]}"
            )
        dados = resposta.json()
        token = dados.get("access_token")
        if not token:
            raise PixGatewayError("Celcoin não retornou access_token")
        return token

    def criar_cobranca(self, *, chave, valor, descricao, nome_pagador=None):
        token = self._token()
        client_request_id = str(uuid.uuid4())
        valor = f"{float(valor):.2f}"

        payload = {
            "key": chave,
            "amount": valor,
            "merchant": {
                "merchantCategoryCode": "5651",
                "postalCode": "00000000",
                "city": "Sao Paulo",
                "name": "BabyCorporation",
            },
            "expiration": 86400,
            "clientRequestId": client_request_id,
            "payerQuestion": descricao[:140],
        }
        if nome_pagador:
            payload["payerName"] = nome_pagador[:30]

        url = f"{self._base_url()}/pix/v1/brcode/dynamic"
        resposta = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json-patch+json",
            },
            json=payload,
            timeout=(5, 20),
        )

        corpo = resposta.json()
        if resposta.status_code not in (200, 201) or not corpo.get("body"):
            raise PixGatewayError(
                f"Celcoin cobrança falhou ({resposta.status_code}): {str(corpo)[:400]}"
            )

        dados = corpo["body"]

        brcode = (
            dados.get("emv")
            or (dados.get("dynamicBRCodeData") or {}).get("emvqrcps")
            or ""
        )
        if not brcode:
            raise PixGatewayError("Celcoin não retornou o código Pix copia e cola")

        return {
            "txid": str(dados.get("transactionId") or dados.get("transactionIdentification") or client_request_id),
            "brcode": brcode,
            "emv": brcode,
        }


def get_pix_gateway():
    nome = getattr(settings, "PIX_GATEWAY", "mock")

    if nome == "celcoin":
        return CelcoinPixGateway()

    return MockPixGateway()