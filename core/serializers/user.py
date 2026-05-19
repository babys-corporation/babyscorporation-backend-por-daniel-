from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.models import Usuario, PerfilPai, PerfilBaba


class UserSerializer(ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'tipo', 'foto', 'telefone', 'is_active', 'is_staff']
        read_only_fields = ['id', 'is_active', 'is_staff']


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'tipo']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class PerfilPaiSerializer(ModelSerializer):
    class Meta:
        model = PerfilPai
        fields = ['id', 'numero_filhos', 'endereco']


class PerfilBabaSerializer(ModelSerializer):
    class Meta:
        model = PerfilBaba
        fields = ['id', 'experiencia_anos', 'descricao', 'disponivel', 'valor_hora']