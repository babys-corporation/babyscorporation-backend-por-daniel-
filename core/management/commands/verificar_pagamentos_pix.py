from django.core.management.base import BaseCommand

from core.services.regras_pix import verificar_pagamentos_atrasados


class Command(BaseCommand):
    help = (
        "Aplica advertências e banimentos para pagamentos Pix não confirmados "
        "pelas babás."
    )

    def handle(self, *args, **options):
        resultados = verificar_pagamentos_atrasados()

        if not resultados:
            self.stdout.write(self.style.SUCCESS("Nenhum pagamento atrasado."))
            return

        for agendamento, acao in resultados:
            self.stdout.write(
                f"Agendamento #{agendamento.id} -> {acao}"
            )