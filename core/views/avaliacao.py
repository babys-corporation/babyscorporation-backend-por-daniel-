from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from core.models import Avaliacao, PerfilPai
from core.serializers import AvaliacaoSerializer


class AvaliacaoViewSet(ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Pega o perfil do pai logado automaticamente
        perfil_pai = PerfilPai.objects.get(usuario=self.request.user)
        serializer.save(pai=perfil_pai)

    def get_queryset(self):
        # Filtra por babá se passar ?baba=<id> na URL
        baba_id = self.request.query_params.get('baba')
        if baba_id:
            return Avaliacao.objects.filter(baba_id=baba_id)
        return Avaliacao.objects.all()