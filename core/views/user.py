from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Usuario, PerfilPai, PerfilBaba, Crianca, PerfilBabaCompleta
from core.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    PerfilPaiSerializer,
    PerfilBabaSerializer,
    CriancaSerializer,
)


class UserViewSet(ModelViewSet):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UserSerializer

    @extend_schema(
        summary="Dados do usuário autenticado",
        responses={200: UserSerializer, 401: None},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Upload de foto do usuário autenticado",
        responses={200: UserSerializer, 400: None, 401: None},
    )
    @action(
        detail=False,
        methods=['patch'],
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_foto(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationView(CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class PerfilPaiViewSet(ModelViewSet):
    queryset = PerfilPai.objects.all().order_by('id')
    serializer_class = PerfilPaiSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if PerfilPai.objects.filter(usuario=self.request.user).exists():
            raise ValidationError(
                {"detail": "Este usuário já possui um perfil de pai."}
            )

        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        perfil = PerfilPai.objects.get(usuario=request.user)
        serializer = self.get_serializer(perfil)
        return Response(serializer.data)


class PerfilBabaViewSet(ModelViewSet):
    queryset = PerfilBaba.objects.all().order_by('id')
    serializer_class = PerfilBabaSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("list", "retrieve", "completas"):
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        if PerfilBaba.objects.filter(usuario=self.request.user).exists():
            raise ValidationError(
                {"detail": "Perfil de babá já existe para este usuário."}
            )

        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=["get"])
    def me(self, request):
        perfil = PerfilBaba.objects.get(usuario=request.user)
        serializer = self.get_serializer(perfil)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def completas(self, request):
        babas_completas = PerfilBaba.objects.filter(
            completude__isnull=False
        ).order_by("id")
        page = self.paginate_queryset(babas_completas)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(babas_completas, many=True)
        return Response(serializer.data)


class CriancaViewSet(ModelViewSet):
    queryset = Crianca.objects.all().order_by('id')
    serializer_class = CriancaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        perfil_pai = PerfilPai.objects.get(usuario=self.request.user)
        serializer.save(perfil_pai=perfil_pai)