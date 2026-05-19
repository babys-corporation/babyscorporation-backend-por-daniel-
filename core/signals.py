from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Usuario, PerfilPai, PerfilBaba


@receiver(post_save, sender=Usuario)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        if instance.tipo == Usuario.TipoUsuario.PAI:
            PerfilPai.objects.create(usuario=instance)
        elif instance.tipo == Usuario.TipoUsuario.BABA:
            PerfilBaba.objects.create(usuario=instance)