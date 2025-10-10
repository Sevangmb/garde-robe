from .models import Message

def unread_messages_count(request):
    """
    Context processor pour ajouter le nombre de messages non lus
    dans tous les templates
    """
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            destinataire=request.user,
            lu=False,
            archive_destinataire=False
        ).count()
        return {'unread_messages_count': unread_count}
    return {'unread_messages_count': 0}
