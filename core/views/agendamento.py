from rest_framework.viewsets import ModelViewSet

from core.models import Agendamento
from core.serializers import AgendamentoSerializer


class AgendamentoViewSet(ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer