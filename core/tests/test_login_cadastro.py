from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Usuario

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400


class LoginCadastroTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Usuario.objects.create_user(email='Maria@example.com', password='senha-forte-123')

    def login(self, email):
        return self.client.post('/api/token/', {'email': email, 'password': 'senha-forte-123'}, format='json')

    def test_login_ignora_maiusculas(self):
        for email in ('Maria@example.com', 'maria@example.com', 'MARIA@EXAMPLE.COM'):
            resposta = self.login(email)
            assert resposta.status_code == HTTP_200_OK, (email, resposta.data)

    def test_login_senha_errada_continua_falhando(self):
        resposta = self.client.post(
            '/api/token/', {'email': 'maria@example.com', 'password': 'errada'}, format='json'
        )
        assert resposta.status_code != HTTP_200_OK

    def test_cadastro_salva_email_minusculo(self):
        resposta = self.client.post(
            '/api/registro/',
            {'email': ' Joana@Example.com ', 'password': 'senha-forte-123', 'tipo': 'PAI'},
            format='json',
        )
        assert resposta.status_code == HTTP_201_CREATED, resposta.data
        assert Usuario.objects.filter(email='joana@example.com').exists()

    def test_cadastro_recusa_email_repetido_com_maiusculas(self):
        resposta = self.client.post(
            '/api/registro/',
            {'email': 'MARIA@example.com', 'password': 'senha-forte-123', 'tipo': 'PAI'},
            format='json',
        )
        assert resposta.status_code == HTTP_400_BAD_REQUEST
        assert 'email' in resposta.data

    def test_cadastro_funciona_com_token_velho_no_navegador(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer token-invalido')
        resposta = self.client.post(
            '/api/registro/',
            {'email': 'nova@example.com', 'password': 'senha-forte-123', 'tipo': 'BABA'},
            format='json',
        )
        assert resposta.status_code == HTTP_201_CREATED, resposta.data
