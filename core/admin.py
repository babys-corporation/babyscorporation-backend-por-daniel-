from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core.models import Usuario, PerfilPai, PerfilBaba, Agendamento


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_staff']
    list_filter = ['tipo', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email', 'tipo', 'foto', 'telefone')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ['last_login', 'date_joined']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'tipo', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            if obj.tipo == Usuario.TipoUsuario.PAI:
                PerfilPai.objects.get_or_create(usuario=obj)
            elif obj.tipo == Usuario.TipoUsuario.BABA:
                PerfilBaba.objects.get_or_create(usuario=obj)


@admin.register(PerfilPai)
class PerfilPaiAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_filhos', 'endereco']


@admin.register(PerfilBaba)
class PerfilBabaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'experiencia_anos', 'disponivel', 'valor_hora']


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['pai', 'baba', 'data', 'hora_inicio', 'hora_fim']