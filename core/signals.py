from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import Usuario, PerfilBaba, PerfilPai, PerfilBabaCompleta


# ---------------------------------------------------------------------
# Criação automática de perfil (Baba ou Pai) quando um Usuario é criado
# ---------------------------------------------------------------------

@receiver(post_save, sender=Usuario)
def criar_perfil_automatico(sender, instance, created, **kwargs):
    """
    Garante que todo Usuario criado (por onde for: admin, API, shell,
    import em massa, etc.) já nasça com o perfil correto associado.
    """
    if not created:
        return

    if instance.tipo == Usuario.TipoUsuario.BABA:
        PerfilBaba.objects.get_or_create(usuario=instance)
    elif instance.tipo == Usuario.TipoUsuario.PAI:
        PerfilPai.objects.get_or_create(usuario=instance)


# ---------------------------------------------------------------------
# Sincronização da tabela utilitária PerfilBabaCompleta
# ---------------------------------------------------------------------

def perfil_baba_esta_completo(perfil_baba: PerfilBaba) -> bool:
    usuario = perfil_baba.usuario

    campos_usuario_obrigatorios = [
        usuario.foto_id,
        usuario.cpf,
        usuario.telefone,
        usuario.cep,
        usuario.cidade,
        usuario.bairro,
    ]

    campos_perfil_obrigatorios = [
        perfil_baba.descricao,
        perfil_baba.valor_hora,
        perfil_baba.habilidades,
        perfil_baba.dtnasc,
        perfil_baba.formacao,
    ]

    return all(
        valor is not None and str(valor).strip() != ""
        for valor in (
            campos_usuario_obrigatorios + campos_perfil_obrigatorios
        )
    )


def sincronizar_completude(perfil_baba: PerfilBaba):
    # Nunca tenta trabalhar com um PerfilBaba ainda não salvo
    if not perfil_baba.pk:
        return

    completo = perfil_baba_esta_completo(perfil_baba)

    if completo:
        PerfilBabaCompleta.objects.get_or_create(
            perfil_baba=perfil_baba
        )
    else:
        PerfilBabaCompleta.objects.filter(
            perfil_baba_id=perfil_baba.pk
        ).delete()


@receiver(post_save, sender=PerfilBaba)
def perfil_baba_salvo(sender, instance, **kwargs):
    sincronizar_completude(instance)


@receiver(post_save, sender=Usuario)
def usuario_salvo(sender, instance, **kwargs):
    if instance.tipo != Usuario.TipoUsuario.BABA:
        return

    # Usa o ID diretamente para evitar acessar uma relação
    # ainda não criada durante o processo do Admin.
    perfil_baba_id = (
        PerfilBaba.objects
        .filter(usuario_id=instance.pk)
        .values_list("pk", flat=True)
        .first()
    )

    if perfil_baba_id:
        perfil_baba = PerfilBaba.objects.get(pk=perfil_baba_id)
        sincronizar_completude(perfil_baba)


@receiver(post_delete, sender=PerfilBaba)
def perfil_baba_deletado(sender, instance, **kwargs):
    # O CASCADE normalmente já remove o registro relacionado,
    # mas esta operação também é segura.
    if instance.pk:
        PerfilBabaCompleta.objects.filter(
            perfil_baba_id=instance.pk
        ).delete()