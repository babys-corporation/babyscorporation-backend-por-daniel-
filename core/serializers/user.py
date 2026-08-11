from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
)
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from uploader.models import Image

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

    class Meta:
        model = Usuario

        fields = [
            "id",
            "email",
            "password",
            "tipo",
            "foto_attachment_key",
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

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]

        tipo = validated_data.get("tipo")
        foto = validated_data.get("foto")

        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            tipo=tipo,
            foto=foto,
        )

        if tipo == Usuario.TipoUsuario.PAI:
            PerfilPai.objects.create(
                usuario=usuario,
            )

        elif tipo == Usuario.TipoUsuario.BABA:
            PerfilBaba.objects.create(
                usuario=usuario,
            )

        return usuario

    def get_access(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def get_refresh(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh)


class UserSerializer(ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"


class PerfilPaiSerializer(ModelSerializer):
    class Meta:
        model = PerfilPai
        fields = "__all__"


class PerfilBabaSerializer(ModelSerializer):
    class Meta:
        model = PerfilBaba
        fields = "__all__"


class CriancaSerializer(ModelSerializer):
    class Meta:
        model = Crianca
        fields = "__all__"