from rest_framework.viewsets import ModelViewSet

from core.models import Pai
from core.serializers import PaiSerializer


class PaiViewSet(ModelViewSet):
    queryset = Pai.objects.all()
    serializer_class = PaiSerializer