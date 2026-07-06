from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Agendamento
from core.serializers import AgendamentoSerializer


class AgendamentoViewSet(ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]

    queryset = Agendamento.objects.all()

    @action(detail=False, methods=['get'])
    def me(self, request):

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