from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.views.user import CriancaViewSet
from uploader.router import router as uploader_router
from core.views import UserRegistrationView, UserViewSet, PerfilPaiViewSet, PerfilBabaViewSet, AgendamentoViewSet
from core.views.avaliacao import AvaliacaoViewSet

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuarios')
router.register(r'perfil-pai', PerfilPaiViewSet, basename='perfil-pai')
router.register(r'perfil-baba', PerfilBabaViewSet, basename='perfil-baba')
router.register(r'avaliacoes', AvaliacaoViewSet, basename='avaliacoes')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamentos')
router.register(r'criancas', CriancaViewSet, basename='criancas')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/registro/', UserRegistrationView.as_view(), name='user_registration'),
    path('api/media/', include(uploader_router.urls)),
    path('api/', include(router.urls)),
    
]

urlpatterns += static(settings.MEDIA_ENDPOINT, document_root=settings.MEDIA_ROOT)