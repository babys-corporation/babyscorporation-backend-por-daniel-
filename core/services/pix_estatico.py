"""
Geração de código Pix (estático) diretamente a partir da chave Pix.

Não depende de gateway nem de contrato: o "copia e cola" é montado
conforme o padrão do Banco Central e, ao pagar, o dinheiro cai direto
na conta da chave informada.
"""

from __future__ import annotations

import struct

CAMPO_GUI = "BR.GOV.BCB.PIX"
CAMPO_CATEGORIA = "0000"  # Merchant Category Code (genérico)
CAMPO_MOEDA = "986"  # BRL
CAMPO_PAIS = "BR"

_CRC_TABLE = []


def _init_crc_table():
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
        _CRC_TABLE.append(crc)


def _crc16(payload: str) -> str:
    if not _CRC_TABLE:
        _init_crc_table()

    crc = 0xFFFF
    for byte in payload.encode("utf-8"):
        crc = ((crc << 8) ^ _CRC_TABLE[((crc >> 8) ^ byte) & 0xFF]) & 0xFFFF
    return format(crc, "04X")


def _emv(campo_id: str, valor: str) -> str:
    tamanho = len(valor.encode("utf-8"))
    return f"{campo_id}{tamanho:02d}{valor}"


def gerar_pix_estatico(
    chave: str,
    valor: float,
    nome_recebedor: str = "BabyCorporation",
    cidade: str = "BRASIL",
    txid: str = "***",
) -> str:
    """Monta o EMV (copia e cola) do Pix estático para a chave informada."""
    chave = chave.strip()
    valor = float(valor)

    if valor < 0.01 or valor > 999999999.99:
        raise ValueError("Valor fora do intervalo permitido pelo Pix.")

    nome = (nome_recebedor or "BabyCorporation").strip()[:25]
    cidade = (cidade or "BRASIL").strip()[:15]
    valor_str = f"{valor:.2f}"

    # Campo 26: informações da chave (GUI + chave)
    mao = (
        _emv("00", CAMPO_GUI)
        + _emv("01", chave)
    )

    # Campo 54: valor
    campo_valor = _emv("54", valor_str)

    # Campo 62: dados adicionais (txid)
    txid = (txid or "***")[:25]
    campo_txid = _emv("05", txid)
    campo_62 = _emv("62", campo_txid)

    payload = (
        _emv("00", "01")
        + _emv("26", mao)
        + _emv("52", CAMPO_CATEGORIA)
        + _emv("53", CAMPO_MOEDA)
        + campo_valor
        + _emv("58", CAMPO_PAIS)
        + _emv("59", nome)
        + _emv("60", cidade)
        + campo_62
    )

    crc = _crc16(payload + "6304")
    return payload + "6304" + crc