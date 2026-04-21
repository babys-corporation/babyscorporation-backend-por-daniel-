from rest_framework.serializers import ModelSerializer

from core.models import Baba


class BabaSerializer(ModelSerializer):
    class Meta:
        model = Baba
        fields = '__all__'