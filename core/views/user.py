from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.models import Usuario, PerfilPai, PerfilBaba
from core.serializers import UserRegistrationSerializer, UserSerializer, PerfilPaiSerializer, PerfilBabaSerializer


class UserViewSet(ModelViewSet):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UserSerializer

    @extend_schema(summary="Dados do usuário autenticado", responses={200: UserSerializer, 401: None})
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Upload de foto do usuário autenticado", responses={200: UserSerializer, 400: None, 401: None})
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def upload_foto(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
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


class PerfilBabaViewSet(ModelViewSet):
    queryset = PerfilBaba.objects.all().order_by('id')
    serializer_class = PerfilBabaSerializer