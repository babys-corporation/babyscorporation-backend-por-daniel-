from rest_framework.serializers import ModelSerializer

from core.models import Pai


class PaiSerializer(ModelSerializer):
    class Meta:
        model = Pai
        fields = '__all__'