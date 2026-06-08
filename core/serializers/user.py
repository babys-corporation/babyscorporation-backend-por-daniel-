from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Usuario, PerfilPai, PerfilBaba
from uploader.models import Image
from uploader.serializers import ImageSerializer


class UserSerializer(ModelSerializer):
    foto_attachment_key = SlugRelatedField(
        source='foto',
        queryset=Image.objects.all(),
        slug_field='attachment_key',
        required=False,
        write_only=True,
    )
    foto = ImageSerializer(required=False, read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'tipo', 'foto', 'foto_attachment_key', 'telefone', 'is_active', 'is_staff']
        read_only_fields = ['id', 'is_active', 'is_staff']


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)
    foto_attachment_key = SlugRelatedField(
        source='foto',
        queryset=Image.objects.all(),
        slug_field='attachment_key',
        required=False,
        write_only=True,
    )

    class Meta:                          # ← dentro da classe
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'password', 'tipo', 'foto_attachment_key',
            'access', 'refresh'
        ]

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

    def get_access(self, obj):
        return str(RefreshToken.for_user(obj).access_token)

    def get_refresh(self, obj):
        return str(RefreshToken.for_user(obj))


class PerfilPaiSerializer(ModelSerializer):
    class Meta:
        model = PerfilPai
        fields = ['id', 'usuario', 'numero_filhos', 'endereco']
        read_only_fields = ['usuario']
        depth = 1


class PerfilBabaSerializer(ModelSerializer):
    class Meta:
        model = PerfilBaba
        fields = ['id', 'usuario', 'experiencia_anos', 'descricao', 'disponivel', 'valor_hora', 'habilidades', 'dtnasc', 'formacao', 'sobre']
        depth = 2