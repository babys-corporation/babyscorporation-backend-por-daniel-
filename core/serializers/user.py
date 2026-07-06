import requests
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SlugRelatedField
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Usuario, PerfilPai, PerfilBaba, Crianca
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
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'tipo', 'foto', 'foto_attachment_key', 'telefone', 'is_active', 'is_staff', 'cpf', 'cep', 'cidade', 'bairro']
        read_only_fields = ['id', 'is_active', 'is_staff', 'cidade', 'bairro']

    def validate_cep(self, value):
        cep = value.replace('-', '').strip()
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
        dados = r.json()
        if 'erro' in dados:
            raise serializers.ValidationError("CEP inválido.")
        return cep

    def update(self, instance, validated_data):
        cep = validated_data.get('cep')
        if cep:
            r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
            dados = r.json()
            if 'erro' not in dados:
                validated_data['cidade'] = dados['localidade']
                validated_data['bairro'] = dados['bairro']
        return super().update(instance, validated_data)


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

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'tipo', 'foto_attachment_key', 'access', 'refresh']

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

    def get_access(self, obj):
        return str(RefreshToken.for_user(obj).access_token)

    def get_refresh(self, obj):
        return str(RefreshToken.for_user(obj))


class CriancaSerializer(ModelSerializer):
    class Meta:
        model = Crianca
        fields = ['id', 'nome', 'genero', 'idade', 'alergias', 'condicoes']


class PerfilPaiSerializer(ModelSerializer):
    criancas = CriancaSerializer(many=True, read_only=True)

    class Meta:
        model = PerfilPai
        fields = ['id', 'numero_filhos', 'criancas']


class PerfilBabaSerializer(ModelSerializer):
    class Meta:
        model = PerfilBaba
        fields = ['id', 'usuario', 'experiencia_anos', 'descricao', 'disponivel', 'valor_hora', 'habilidades', 'dtnasc', 'formacao']
        depth = 2