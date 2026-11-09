from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Agendamento, PerfilBaba, Usuario
from core.models.user import DIAS_SEMANA
from core.services.pix_estatico import gerar_pix_estatico

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_403_FORBIDDEN = 403
CRC_LENGTH = 4


class FluxoAgendamentoPixTestCase(TestCase):
    def setUp(self):
        self.baba_user = Usuario.objects.create_user(
            email='baba.temp@example.com',
            password='x',
            tipo=Usuario.TipoUsuario.BABA,
            primeiro_nome='Baba',
            cidade='Chapeco',
        )
        self.pai_user = Usuario.objects.create_user(
            email='pai.temp@example.com',
            password='x',
            tipo=Usuario.TipoUsuario.PAI,
        )

        self.perfil_baba = PerfilBaba.objects.get(usuario=self.baba_user)
        self.perfil_baba.valor_hora = '100.00'
        self.perfil_baba.chave_pix = 'baba.temp@example.com'
        self.perfil_baba.save()

        self.baba_client = APIClient()
        self.baba_client.force_authenticate(self.baba_user)

        self.pai_client = APIClient()
        self.pai_client.force_authenticate(self.pai_user)

        self.amanha = date.today() + timedelta(days=1)

    def criar_agendamento(self, inicio='08:00', fim='12:00'):
        return self.pai_client.post(
            '/api/agendamentos/',
            {
                'baba': self.perfil_baba.id,
                'data': self.amanha.isoformat(),
                'hora_inicio': inicio,
                'hora_fim': fim,
                'qtd_criancas': 2,
            },
            format='json',
        )

    def test_fluxo_completo_pix(self):
        criado = self.criar_agendamento()
        assert criado.status_code == HTTP_201_CREATED, criado.data
        agendamento_id = criado.data['id']
        assert criado.data['status'] == 'PENDENTE'
        assert criado.data['preco'] == '400.00'

        # O Pix com o valor já sai na solicitação
        assert criado.data['status_pagamento'] == 'AGUARDANDO'
        assert criado.data['pix_txid'] == f'BCORP{agendamento_id}'
        assert '5406400.00' in criado.data['pix_brcode']

        # Consulta do pagamento e QR Code antes da babá aceitar
        pagamento = self.pai_client.get(f'/api/agendamentos/{agendamento_id}/pagamento/')
        assert pagamento.status_code == HTTP_200_OK, pagamento.data
        assert pagamento.data['pix_brcode'] == criado.data['pix_brcode']

        qrcode = self.pai_client.get(f'/api/agendamentos/{agendamento_id}/pagamento_qrcode/')
        assert qrcode.status_code == HTTP_200_OK
        assert qrcode['Content-Type'] == 'image/png'

        # Pai avisa que pagou (agendamento ainda pendente)
        avisado = self.pai_client.post(f'/api/agendamentos/{agendamento_id}/marcar_pago/')
        assert avisado.status_code == HTTP_200_OK, avisado.data
        assert avisado.data['pagamento_marcado_em'] is not None

        # O pai não pode aceitar
        negado = self.pai_client.post(f'/api/agendamentos/{agendamento_id}/aceitar/')
        assert negado.status_code == HTTP_403_FORBIDDEN

        # A babá recebe o Pix e aceita: aceitar confirma o pagamento
        aceito = self.baba_client.post(f'/api/agendamentos/{agendamento_id}/aceitar/')
        assert aceito.status_code == HTTP_200_OK, aceito.data
        assert aceito.data['status'] == 'ACEITO'
        assert aceito.data['status_pagamento'] == 'PAGO'
        assert aceito.data['pagamento_confirmado_em'] is not None

    def test_baba_sem_chave_pix_nao_pode_ser_agendada(self):
        self.perfil_baba.chave_pix = ''
        self.perfil_baba.save()

        criado = self.criar_agendamento()
        assert criado.status_code == HTTP_400_BAD_REQUEST
        assert 'baba' in criado.data

    def test_agendamento_antigo_sem_pix_gera_pix_ao_aceitar(self):
        criado = self.criar_agendamento()
        agendamento = Agendamento.objects.get(pk=criado.data['id'])
        agendamento.status_pagamento = 'NAO_EXIGIDO'
        agendamento.pix_brcode = None
        agendamento.pix_txid = None
        agendamento.save()

        aceito = self.baba_client.post(f'/api/agendamentos/{agendamento.id}/aceitar/')
        assert aceito.status_code == HTTP_200_OK, aceito.data
        assert aceito.data['status_pagamento'] == 'AGUARDANDO'
        assert aceito.data['pix_brcode']

    def test_conflito_de_horario(self):
        primeiro = self.criar_agendamento('08:00', '12:00')
        assert primeiro.status_code == HTTP_201_CREATED

        conflito = self.criar_agendamento('11:00', '13:00')
        assert conflito.status_code == HTTP_400_BAD_REQUEST

        sem_conflito = self.criar_agendamento('12:00', '14:00')
        assert sem_conflito.status_code == HTTP_201_CREATED, sem_conflito.data

    def test_webhook_por_txid_e_sem_fallback(self):
        criado = self.criar_agendamento()
        agendamento_id = criado.data['id']

        # Txid desconhecido não deve confirmar nada
        self.pai_client.post(
            '/api/pix/webhook/celcoin/',
            {
                'entity': 'pix-payment-in',
                'status': 'CONFIRMED',
                'body': {'transactionIdentification': 'DESCONHECIDO', 'amount': 400},
            },
            format='json',
        )
        agendamento = Agendamento.objects.get(pk=agendamento_id)
        assert agendamento.status_pagamento == 'AGUARDANDO'

        # Txid correto confirma o agendamento
        txid = f'BCORP{agendamento_id}'
        self.pai_client.post(
            '/api/pix/webhook/celcoin/',
            {
                'entity': 'pix-payment-in',
                'status': 'CONFIRMED',
                'body': {'transactionIdentification': txid, 'amount': 400},
            },
            format='json',
        )
        agendamento.refresh_from_db()
        assert agendamento.status_pagamento == 'PAGO'
        assert agendamento.pagamento_confirmado_em is not None

    def test_recusar(self):
        criado = self.criar_agendamento()
        agendamento_id = criado.data['id']

        recusado = self.baba_client.post(f'/api/agendamentos/{agendamento_id}/recusar/')
        assert recusado.status_code == HTTP_200_OK, recusado.data
        assert recusado.data['status'] == 'RECUSADO'

    def test_pix_estatico_gera_emv_valido(self):
        brcode = gerar_pix_estatico(
            chave='baba.temp@example.com',
            valor=400,
            nome_recebedor='Baba',
            cidade='Chapeco',
            txid='BCORP1',
        )
        assert brcode.startswith('000201')
        assert 'BR.GOV.BCB.PIX' in brcode
        assert 'BCORP1' in brcode
        assert len(brcode[-CRC_LENGTH:]) == CRC_LENGTH

    def test_pix_estatico_sem_valor_usa_so_a_chave(self):
        brcode = gerar_pix_estatico(
            chave='baba.temp@example.com',
            valor=None,
            nome_recebedor='Baba',
            cidade='Chapeco',
            txid='BCORP1',
        )
        assert 'baba.temp@example.com' in brcode
        assert '5303986' + '54' not in brcode
        assert '53039865802BR' in brcode


class DisponibilidadeBabaTestCase(TestCase):
    def setUp(self):
        self.baba_user = Usuario.objects.create_user(
            email='baba.disp@example.com',
            password='x',
            tipo=Usuario.TipoUsuario.BABA,
        )
        self.pai_user = Usuario.objects.create_user(
            email='pai.disp@example.com',
            password='x',
            tipo=Usuario.TipoUsuario.PAI,
        )
        self.perfil_baba = PerfilBaba.objects.get(usuario=self.baba_user)
        self.perfil_baba.valor_hora = '20.00'
        self.perfil_baba.chave_pix = 'baba.disp@example.com'
        self.perfil_baba.save()

        self.baba_client = APIClient()
        self.baba_client.force_authenticate(self.baba_user)
        self.pai_client = APIClient()
        self.pai_client.force_authenticate(self.pai_user)

        hoje = date.today()
        # Próxima segunda e próxima terça (sempre no futuro)
        self.segunda = hoje + timedelta(days=(7 - hoje.weekday()) or 7)
        self.terca = self.segunda + timedelta(days=1)

    def agendar(self, dia):
        return self.pai_client.post(
            '/api/agendamentos/',
            {'baba': self.perfil_baba.id, 'data': dia.isoformat(), 'hora_inicio': '08:00', 'hora_fim': '10:00'},
            format='json',
        )

    def test_padrao_todos_os_dias_disponiveis(self):
        assert all(self.perfil_baba.disponibilidade.values())
        assert len(self.perfil_baba.disponibilidade) == len(DIAS_SEMANA)

    def test_dia_indisponivel_bloqueia_so_novos_pedidos(self):
        marcado = self.agendar(self.segunda)
        assert marcado.status_code == HTTP_201_CREATED, marcado.data

        resposta = self.baba_client.patch(
            '/api/perfil-baba/me/', {'disponibilidade': {'Segunda': False}}, format='json'
        )
        assert resposta.status_code == HTTP_200_OK, resposta.data
        assert resposta.data['disponibilidade']['Segunda'] is False
        assert resposta.data['disponibilidade']['Terça'] is True

        # Novo pedido numa segunda: recusado
        novo = self.pai_client.post(
            '/api/agendamentos/',
            {
                'baba': self.perfil_baba.id,
                'data': self.segunda.isoformat(),
                'hora_inicio': '12:00',
                'hora_fim': '14:00',
            },
            format='json',
        )
        assert novo.status_code == HTTP_400_BAD_REQUEST
        assert 'data' in novo.data

        # Terça continua liberada
        assert self.agendar(self.terca).status_code == HTTP_201_CREATED

        # O agendamento já marcado na segunda continua igual e pode ser aceito
        aceito = self.baba_client.post(f"/api/agendamentos/{marcado.data['id']}/aceitar/")
        assert aceito.status_code == HTTP_200_OK, aceito.data
        assert Agendamento.objects.filter(pk=marcado.data['id']).exists()

    def test_disponibilidade_invalida(self):
        resposta = self.baba_client.patch(
            '/api/perfil-baba/me/', {'disponibilidade': {'Feriado': True}}, format='json'
        )
        assert resposta.status_code == HTTP_400_BAD_REQUEST

        resposta = self.baba_client.patch(
            '/api/perfil-baba/me/', {'disponibilidade': {'Segunda': 'sim'}}, format='json'
        )
        assert resposta.status_code == HTTP_400_BAD_REQUEST
