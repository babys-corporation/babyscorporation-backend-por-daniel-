from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.exceptions import ObjectDoesNotExist
from django_cpf_cnpj.validators import is_valid_cpf
from phonenumber_field.phonenumber import PhoneNumber
import re

from uploader.models import Image
from uploader.serializers.image import ImageSerializer

from core.models import (
    Usuario,
    PerfilPai,
    PerfilBaba,
    Crianca,
)


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=True,
    )

    email = serializers.EmailField(
        required=True,
    )

    access = serializers.SerializerMethodField(
        read_only=True,
    )

    refresh = serializers.SerializerMethodField(
        read_only=True,
    )

    foto_attachment_key = SlugRelatedField(
        source="foto",
        queryset=Image.objects.all(),
        slug_field="attachment_key",
        required=False,
        allow_null=True,
        write_only=True,
    )

    primeiro_nome = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=30,
    )

    ultimo_nome = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=30,
    )

    cpf = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    telefone = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    cep = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=9,
    )

    cidade = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    bairro = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    experiencia_anos = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    descricao = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    valor_hora = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=0,
    )

    habilidades = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    dtnasc = serializers.DateField(
        required=False,
        allow_null=True,
    )

    formacao = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Usuario

        fields = [
            "id",
            "email",
            "password",
            "tipo",
            "foto_attachment_key",
            "primeiro_nome",
            "ultimo_nome",
            "cpf",
            "telefone",
            "cep",
            "cidade",
            "bairro",
            "experiencia_anos",
            "descricao",
            "valor_hora",
            "habilidades",
            "dtnasc",
            "formacao",
            "access",
            "refresh",
        ]

        read_only_fields = [
            "id",
            "access",
            "refresh",
        ]

        extra_kwargs = {
            "tipo": {
                "required": False,
                "allow_null": True,
            },
        }

    def validate_cpf(self, value):
        if not value:
            return None

        digitos = re.sub(r"\D", "", value)

        if not is_valid_cpf(digitos):
            raise serializers.ValidationError("CPF inválido.")

        return digitos

    def validate_telefone(self, value):
        if not value:
            return None

        try:
            return PhoneNumber.from_string(value, region="BR")
        except Exception:
            raise serializers.ValidationError(
                "Telefone inválido. Use o formato (DD) 9XXXX-XXXX."
            )

    def _limpar(self, value):
        return value if value not in (None, "") else None

    def create(self, validated_data):
        campos_perfil = {
            campo: self._limpar(validated_data.pop(campo, None))
            for campo in (
                "experiencia_anos",
                "descricao",
                "valor_hora",
                "habilidades",
                "dtnasc",
                "formacao",
            )
        }

        usuario = Usuario.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            tipo=validated_data.get("tipo"),
            foto=self._limpar(validated_data.get("foto")),
            primeiro_nome=self._limpar(validated_data.get("primeiro_nome")),
            ultimo_nome=self._limpar(validated_data.get("ultimo_nome")),
            cpf=self._limpar(validated_data.get("cpf")),
            telefone=self._limpar(validated_data.get("telefone")),
            cep=self._limpar(validated_data.get("cep")),
            cidade=self._limpar(validated_data.get("cidade")),
            bairro=self._limpar(validated_data.get("bairro")),
        )

        campos_perfil = {
            k: v for k, v in campos_perfil.items() if v is not None
        }

        if campos_perfil and usuario.tipo == Usuario.TipoUsuario.BABA:
            try:
                perfil = PerfilBaba.objects.get(usuario=usuario)
            except ObjectDoesNotExist:
                perfil = None

            if perfil is not None:
                for campo, valor in campos_perfil.items():
                    setattr(perfil, campo, valor)
                perfil.save()

        return usuario

    def get_access(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def get_refresh(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh)


class UserSerializer(ModelSerializer):
    foto = ImageSerializer(read_only=True)

    foto_attachment_key = SlugRelatedField(
        source="foto",
        queryset=Image.objects.all(),
        slug_field="attachment_key",
        required=False,
        allow_null=True,
        write_only=True,
    )

    telefone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = Usuario
        exclude = ["password"]

    def validate_cpf(self, value):
        if not value:
            return None

        digitos = re.sub(r"\D", "", value)

        if not is_valid_cpf(digitos):
            raise serializers.ValidationError("CPF inválido.")

        return digitos

    def validate_telefone(self, value):
        if not value:
            return None

        try:
            return PhoneNumber.from_string(value, region="BR")
        except Exception:
            raise serializers.ValidationError(
                "Telefone inválido. Use o formato (DD) 9XXXX-XXXX."
            )


class PerfilPaiSerializer(ModelSerializer):
    class Meta:
        model = PerfilPai
        fields = "__all__"


class PerfilBabaSerializer(ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = PerfilBaba
        fields = "__all__"


class CriancaSerializer(ModelSerializer):
    class Meta:
        model = Crianca
        fields = "__all__"