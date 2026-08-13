import requests

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import (
    Usuario,
    PerfilPai,
    PerfilBaba,
    Agendamento,
    Crianca,
    Avaliacao,
)


class PerfilBabaInline(admin.StackedInline):
    model = PerfilBaba
    can_delete = False
    verbose_name_plural = "Perfil Babá"


class PerfilPaiInline(admin.StackedInline):
    model = PerfilPai
    can_delete = False
    verbose_name_plural = "Perfil Pai"


class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"

        widgets = {
            "cpf": forms.TextInput(
                attrs={
                    "placeholder": "000.000.000-00",
                    "maxlength": "14",
                }
            ),
        }


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    inlines = [PerfilPaiInline, PerfilBabaInline]
    form = UsuarioAdminForm

    ordering = ["id"]

    list_display = [
        "email",
        "primeiro_nome",
        "ultimo_nome",
        "tipo",
        "is_staff",
    ]

    list_filter = [
        "tipo",
        "is_staff",
        "is_active",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),

        (
            _("Informações pessoais"),
            {
                "fields": (
                    "primeiro_nome",
                    "ultimo_nome",
                    "cpf",
                    "tipo",
                    "foto",
                    "telefone",
                )
            },
        ),

        (
            _("Localização"),
            {
                "fields": (
                    "cep",
                    "cidade",
                    "bairro",
                )
            },
        ),

        (
            _("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            _("Datas importantes"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    readonly_fields = [
        "last_login",
        "date_joined",
        "cidade",
        "bairro",
    ]

    def save_model(self, request, obj, form, change):

        cep = obj.cep

        if cep:
            cep_limpo = cep.replace("-", "").strip()
          
            try:
                r = requests.get(
                    f"https://viacep.com.br/ws/{cep_limpo}/json/"
                    timeout=5
                )   

                r.raise_for_status()
                dados = r.json()


                if "erro" not in dados:
                    obj.cidade = dados["localidade"]
                    obj.bairro = dados["bairro"]

            except requests.exceptions.RequestException:
                # ViaCEP fora do ar ou sem conexão: segue o cadastro
                # sem preencher cidade/bairro automaticamente
                pass

        super().save_model(request, obj, form, change)


@admin.register(PerfilPai)
class PerfilPaiAdmin(admin.ModelAdmin):
    list_display = ["usuario", "numero_filhos"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = Usuario.objects.filter(
                tipo=Usuario.TipoUsuario.PAI
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


@admin.register(PerfilBaba)
class PerfilBabaAdmin(admin.ModelAdmin):
    list_display = [
        "usuario",
        "experiencia_anos",
        "disponivel",
        "valor_hora",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "usuario":
            kwargs["queryset"] = Usuario.objects.filter(
                tipo=Usuario.TipoUsuario.BABA
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = [
        "nome",
        "genero",
        "idade",
        "perfil_pai",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "perfil_pai":
            kwargs["queryset"] = PerfilPai.objects.all()

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = [
        "pai",
        "baba",
        "data",
        "hora_inicio",
        "hora_fim",
    ]


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = [
        "pai",
        "baba",
        "estrelas",
        "criado_em",
    ]

    list_filter = ["estrelas"]

    ordering = ["-criado_em"]