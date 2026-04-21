from rest_framework.viewsets import ModelViewSet

from core.models import Baba
from core.serializers import BabaSerializer


class BabaViewSet(ModelViewSet):
    queryset = Baba.objects.all()
    serializer_class = BabaSerializer