from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import Usuario, PerfilBaba, PerfilBabaCompleta


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

    todos_campos = campos_usuario_obrigatorios + campos_perfil_obrigatorios

    return all(
        valor is not None and str(valor).strip() != ""
        for valor in todos_campos
    )


def sincronizar_completude(perfil_baba: PerfilBaba):
    completo = perfil_baba_esta_completo(perfil_baba)

    if completo:
        PerfilBabaCompleta.objects.get_or_create(perfil_baba=perfil_baba)
    else:
        PerfilBabaCompleta.objects.filter(perfil_baba=perfil_baba).delete()


@receiver(post_save, sender=PerfilBaba)
def perfil_baba_salvo(sender, instance, **kwargs):
    sincronizar_completude(instance)


@receiver(post_save, sender=Usuario)
def usuario_salvo(sender, instance, **kwargs):
    # Usuario não é BABA ou ainda não tem perfil_baba criado
    if instance.tipo != Usuario.TipoUsuario.BABA:
        return

    if not hasattr(instance, "perfil_baba"):
        return

    sincronizar_completude(instance.perfil_baba)


@receiver(post_delete, sender=PerfilBaba)
def perfil_baba_deletado(sender, instance, **kwargs):
    PerfilBabaCompleta.objects.filter(perfil_baba=instance).delete()