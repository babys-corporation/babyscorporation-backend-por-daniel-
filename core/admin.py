import requests
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core.models import Usuario, PerfilPai, PerfilBaba, Agendamento, Crianca


class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'cpf': forms.TextInput(attrs={
                'placeholder': '000.000.000-00',
                'maxlength': '14',
            }),
        }


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    form = UsuarioAdminForm
    ordering = ['id']
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_staff']
    list_filter = ['tipo', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email', 'cpf', 'tipo', 'foto', 'telefone')}),
        (_('Localização'), {'fields': ('cep', 'cidade', 'bairro')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ['last_login', 'date_joined', 'cidade', 'bairro']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'cpf', 'tipo', 'foto', 'telefone', 'cep', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    def save_model(self, request, obj, form, change):
        cep = obj.cep
        if cep:
            cep_limpo = cep.replace('-', '').strip()
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            dados = r.json()
            if 'erro' not in dados:
                obj.cidade = dados['localidade']
                obj.bairro = dados['bairro']
        super().save_model(request, obj, form, change)
        if not change:
            if obj.tipo == Usuario.TipoUsuario.PAI:
                PerfilPai.objects.get_or_create(usuario=obj)
            elif obj.tipo == Usuario.TipoUsuario.BABA:
                PerfilBaba.objects.get_or_create(usuario=obj)


@admin.register(PerfilPai)
class PerfilPaiAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_filhos']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'usuario':
            kwargs['queryset'] = Usuario.objects.filter(tipo=Usuario.TipoUsuario.PAI)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PerfilBaba)
class PerfilBabaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'experiencia_anos', 'disponivel', 'valor_hora']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'usuario':
            kwargs['queryset'] = Usuario.objects.filter(tipo=Usuario.TipoUsuario.BABA)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'genero', 'idade', 'perfil_pai']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'perfil_pai':
            kwargs['queryset'] = PerfilPai.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['pai', 'baba', 'data', 'hora_inicio', 'hora_fim']