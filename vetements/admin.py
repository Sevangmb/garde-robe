from django.contrib import admin
from django.db.models import Q
from .models import Categorie, Couleur, Taille, Vetement, Tenue, Valise, Message, Amitie, AnnonceVente


# Personnalisation du site admin pour restreindre l'accès
class RestrictedAdminSite(admin.AdminSite):
    """Site admin accessible uniquement aux superutilisateurs"""

    def has_permission(self, request):
        """Seuls les superutilisateurs peuvent accéder à l'admin"""
        return request.user.is_active and request.user.is_superuser


# Créer une instance du site admin restreint
restricted_admin_site = RestrictedAdminSite(name='restricted_admin')


# Register your models here.

@admin.register(Categorie, site=restricted_admin_site)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['date_creation']


@admin.register(Couleur, site=restricted_admin_site)
class CouleurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code_hex', 'apercu_couleur']
    search_fields = ['nom', 'code_hex']

    def apercu_couleur(self, obj):
        if obj.code_hex:
            return f'<div style="width: 30px; height: 30px; background-color: {obj.code_hex}; border: 1px solid #ccc;"></div>'
        return '-'
    apercu_couleur.short_description = 'Aperçu'
    apercu_couleur.allow_tags = True


@admin.register(Taille, site=restricted_admin_site)
class TailleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_taille', 'ordre']
    list_filter = ['type_taille']
    search_fields = ['nom']
    ordering = ['ordre', 'nom']


@admin.register(Vetement, site=restricted_admin_site)
class VetementAdmin(admin.ModelAdmin):
    change_form_template = 'admin/vetements/vetement_change_form.html'
    add_form_template = 'admin/vetements/vetement_change_form.html'

    list_display = ['nom', 'categorie', 'couleur', 'taille', 'etat', 'nombre_portage', 'favori_icon', 'besoin_entretien_icon']
    list_filter = ['categorie', 'genre', 'saison', 'etat', 'favori', 'a_laver', 'a_repasser', 'prete', 'date_ajout']
    search_fields = ['nom', 'marque', 'description', 'emplacement', 'notes']
    readonly_fields = ['date_ajout', 'date_modification']

    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'description', 'categorie', 'image')
        }),
        ('Caractéristiques', {
            'fields': ('genre', 'saison', 'couleur', 'taille', 'marque', 'matiere')
        }),
        ('Achat', {
            'fields': ('prix_achat', 'date_achat', 'lieu_achat'),
            'classes': ('collapse',)
        }),
        ('Utilisation', {
            'fields': ('etat', 'favori', 'nombre_portage', 'derniere_utilisation')
        }),
        ('Organisation', {
            'fields': ('emplacement', 'a_laver', 'a_repasser', 'prete', 'prete_a')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_ajout', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filtrer les vêtements par utilisateur sauf pour les superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(proprietaire=request.user)

    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement l'utilisateur connecté comme propriétaire"""
        if not change:  # Si c'est une création
            obj.proprietaire = request.user
        super().save_model(request, obj, form, change)

    def favori_icon(self, obj):
        if obj.favori:
            return '⭐'
        return ''
    favori_icon.short_description = '⭐'

    def besoin_entretien_icon(self, obj):
        icons = []
        if obj.a_laver:
            icons.append('🧺')
        if obj.a_repasser:
            icons.append('👔')
        if obj.etat == 'reparer':
            icons.append('🔧')
        if obj.prete:
            icons.append('👤')
        return ' '.join(icons) if icons else ''
    besoin_entretien_icon.short_description = 'État'

    list_per_page = 50

    actions = ['marquer_a_laver', 'marquer_lave', 'incrementer_portage']

    def marquer_a_laver(self, request, queryset):
        queryset.update(a_laver=True)
        self.message_user(request, f"{queryset.count()} vêtement(s) marqué(s) à laver.")
    marquer_a_laver.short_description = "Marquer comme à laver"

    def marquer_lave(self, request, queryset):
        queryset.update(a_laver=False)
        self.message_user(request, f"{queryset.count()} vêtement(s) marqué(s) comme lavé(s).")
    marquer_lave.short_description = "Marquer comme lavé"

    def incrementer_portage(self, request, queryset):
        from django.utils import timezone
        for vetement in queryset:
            vetement.nombre_portage += 1
            vetement.derniere_utilisation = timezone.now().date()
            vetement.save()
        self.message_user(request, f"Portage incrémenté pour {queryset.count()} vêtement(s).")
    incrementer_portage.short_description = "Incrémenter le nombre de portages"


@admin.register(Tenue, site=restricted_admin_site)
class TenuAdmin(admin.ModelAdmin):
    list_display = ['nom', 'occasion', 'saison', 'nombre_fois_portee', 'favori_icon']
    list_filter = ['occasion', 'saison', 'favori', 'date_creation']
    search_fields = ['nom', 'description']
    filter_horizontal = ['vetements']
    readonly_fields = ['date_creation', 'date_modification']

    fieldsets = (
        ('Informations', {
            'fields': ('nom', 'description', 'image')
        }),
        ('Caractéristiques', {
            'fields': ('occasion', 'saison', 'favori')
        }),
        ('Composition', {
            'fields': ('vetements',)
        }),
        ('Utilisation', {
            'fields': ('nombre_fois_portee', 'derniere_fois_portee')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filtrer les tenues par utilisateur sauf pour les superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(proprietaire=request.user)

    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement l'utilisateur connecté comme propriétaire"""
        if not change:
            obj.proprietaire = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Limiter les vêtements disponibles à ceux de l'utilisateur"""
        if db_field.name == "vetements":
            if not request.user.is_superuser:
                kwargs["queryset"] = Vetement.objects.filter(proprietaire=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def favori_icon(self, obj):
        if obj.favori:
            return '⭐'
        return ''
    favori_icon.short_description = '⭐'

    actions = ['incrementer_portage_tenue']

    def incrementer_portage_tenue(self, request, queryset):
        from django.utils import timezone
        for tenue in queryset:
            tenue.nombre_fois_portee += 1
            tenue.derniere_fois_portee = timezone.now().date()
            tenue.save()
        self.message_user(request, f"Portage incrémenté pour {queryset.count()} tenue(s).")
    incrementer_portage_tenue.short_description = "Incrémenter le nombre de portages"


@admin.register(Valise, site=restricted_admin_site)
class ValiseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'destination', 'type_voyage', 'date_depart', 'date_retour', 'duree_affichage', 'statut', 'nombre_items']
    list_filter = ['type_voyage', 'statut', 'date_depart', 'climat']
    search_fields = ['nom', 'destination', 'notes']
    filter_horizontal = ['vetements', 'tenues']
    readonly_fields = ['date_creation', 'date_modification']
    date_hierarchy = 'date_depart'

    fieldsets = (
        ('Informations du voyage', {
            'fields': ('nom', 'destination', 'type_voyage', 'statut')
        }),
        ('Dates', {
            'fields': ('date_depart', 'date_retour')
        }),
        ('Météo et Climat', {
            'fields': ('meteo_prevue', 'climat')
        }),
        ('Contenu de la valise', {
            'fields': ('vetements', 'tenues')
        }),
        ('Organisation', {
            'fields': ('liste_articles_supplementaires', 'checklist_faite')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filtrer les valises par utilisateur sauf pour les superusers"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(proprietaire=request.user)

    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement l'utilisateur connecté comme propriétaire"""
        if not change:
            obj.proprietaire = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Limiter les vêtements et tenues disponibles à ceux de l'utilisateur"""
        if db_field.name == "vetements":
            if not request.user.is_superuser:
                kwargs["queryset"] = Vetement.objects.filter(proprietaire=request.user)
        elif db_field.name == "tenues":
            if not request.user.is_superuser:
                kwargs["queryset"] = Tenue.objects.filter(proprietaire=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def duree_affichage(self, obj):
        return f"{obj.duree_sejour} jour(s)"
    duree_affichage.short_description = 'Durée'

    def nombre_items(self, obj):
        return f"{obj.nombre_vetements} vêtement(s)"
    nombre_items.short_description = 'Contenu'

    actions = ['marquer_prete', 'marquer_en_cours', 'marquer_terminee']

    def marquer_prete(self, request, queryset):
        queryset.update(statut='prete')
        self.message_user(request, f"{queryset.count()} valise(s) marquée(s) comme prête(s).")
    marquer_prete.short_description = "Marquer comme prête"

    def marquer_en_cours(self, request, queryset):
        queryset.update(statut='en_cours')
        self.message_user(request, f"{queryset.count()} valise(s) marquée(s) en cours de voyage.")
    marquer_en_cours.short_description = "Marquer en cours de voyage"

    def marquer_terminee(self, request, queryset):
        queryset.update(statut='terminee')
        self.message_user(request, f"{queryset.count()} valise(s) marquée(s) comme terminée(s).")
    marquer_terminee.short_description = "Marquer comme terminée"


@admin.register(Message, site=restricted_admin_site)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sujet', 'expediteur', 'destinataire', 'date_envoi', 'lu_icon', 'archive_icon']
    list_filter = ['lu', 'date_envoi', 'archive_expediteur', 'archive_destinataire']
    search_fields = ['sujet', 'contenu', 'expediteur__username', 'destinataire__username']
    readonly_fields = ['date_envoi', 'date_lecture']
    date_hierarchy = 'date_envoi'

    fieldsets = (
        ('Participants', {
            'fields': ('expediteur', 'destinataire')
        }),
        ('Message', {
            'fields': ('sujet', 'contenu', 'en_reponse_a')
        }),
        ('Statut', {
            'fields': ('lu', 'archive_expediteur', 'archive_destinataire')
        }),
        ('Dates', {
            'fields': ('date_envoi', 'date_lecture'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Filtrer les messages: superuser voit tout, utilisateur normal voit ses messages"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(expediteur=request.user) | Q(destinataire=request.user))

    def lu_icon(self, obj):
        if obj.lu:
            return '✓ Lu'
        return '○ Non lu'
    lu_icon.short_description = 'Statut'

    def archive_icon(self, obj):
        if obj.archive_expediteur or obj.archive_destinataire:
            return '📦 Archivé'
        return ''
    archive_icon.short_description = 'Archive'

    actions = ['marquer_comme_lu', 'marquer_comme_non_lu', 'archiver']

    def marquer_comme_lu(self, request, queryset):
        from django.utils import timezone
        for message in queryset:
            if not message.lu:
                message.lu = True
                message.date_lecture = timezone.now()
                message.save()
        self.message_user(request, f"{queryset.count()} message(s) marqué(s) comme lu(s).")
    marquer_comme_lu.short_description = "Marquer comme lu"

    def marquer_comme_non_lu(self, request, queryset):
        queryset.update(lu=False, date_lecture=None)
        self.message_user(request, f"{queryset.count()} message(s) marqué(s) comme non lu(s).")
    marquer_comme_non_lu.short_description = "Marquer comme non lu"

    def archiver(self, request, queryset):
        queryset.update(archive_expediteur=True, archive_destinataire=True)
        self.message_user(request, f"{queryset.count()} message(s) archivé(s).")
    archiver.short_description = "Archiver"


@admin.register(Amitie, site=restricted_admin_site)
class AmitieAdmin(admin.ModelAdmin):
    list_display = ['demandeur', 'destinataire', 'statut', 'date_demande', 'date_reponse']
    list_filter = ['statut', 'date_demande']
    search_fields = ['demandeur__username', 'destinataire__username']
    readonly_fields = ['date_demande', 'date_reponse']
    date_hierarchy = 'date_demande'

    fieldsets = (
        ('Participants', {
            'fields': ('demandeur', 'destinataire')
        }),
        ('Statut', {
            'fields': ('statut', 'date_demande', 'date_reponse')
        }),
    )

    def get_queryset(self, request):
        """Filtrer les amitiés: superuser voit tout, utilisateur normal voit ses relations"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(demandeur=request.user) | Q(destinataire=request.user))

    actions = ['accepter_demande', 'refuser_demande']

    def accepter_demande(self, request, queryset):
        from django.utils import timezone
        for amitie in queryset.filter(statut='en_attente'):
            amitie.statut = 'acceptee'
            amitie.date_reponse = timezone.now()
            amitie.save()
        self.message_user(request, f"{queryset.filter(statut='acceptee').count()} demande(s) acceptée(s).")
    accepter_demande.short_description = "Accepter la demande d'amitié"

    def refuser_demande(self, request, queryset):
        from django.utils import timezone
        for amitie in queryset.filter(statut='en_attente'):
            amitie.statut = 'refusee'
            amitie.date_reponse = timezone.now()
            amitie.save()
        self.message_user(request, f"{queryset.filter(statut='refusee').count()} demande(s) refusée(s).")
    refuser_demande.short_description = "Refuser la demande d'amitié"


@admin.register(AnnonceVente, site=restricted_admin_site)
class AnnonceVenteAdmin(admin.ModelAdmin):
    list_display = ['vetement', 'vendeur', 'prix_vente', 'statut', 'negociable', 'livraison_possible', 'date_publication']
    list_filter = ['statut', 'negociable', 'livraison_possible', 'date_publication']
    search_fields = ['vetement__nom', 'vendeur__username', 'description_vente']
    readonly_fields = ['date_publication', 'date_vente']
    date_hierarchy = 'date_publication'

    fieldsets = (
        ('Vêtement', {
            'fields': ('vetement', 'vendeur')
        }),
        ('Prix et conditions', {
            'fields': ('prix_vente', 'negociable', 'livraison_possible', 'description_vente')
        }),
        ('Statut de vente', {
            'fields': ('statut', 'acheteur', 'date_publication', 'date_vente')
        }),
    )

    def get_queryset(self, request):
        """Filtrer les annonces: superuser voit tout, utilisateur normal voit ses annonces ou les annonces disponibles"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # L'utilisateur voit ses propres annonces ou les annonces en vente
        return qs.filter(Q(vendeur=request.user) | Q(statut='en_vente'))

    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement l'utilisateur connecté comme vendeur"""
        if not change:
            obj.vendeur = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limiter les vêtements disponibles à ceux de l'utilisateur pour le champ vetement"""
        if db_field.name == "vetement":
            if not request.user.is_superuser:
                kwargs["queryset"] = Vetement.objects.filter(proprietaire=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    actions = ['marquer_reservee', 'marquer_vendue', 'marquer_retiree']

    def marquer_reservee(self, request, queryset):
        queryset.filter(statut='en_vente').update(statut='reservee')
        self.message_user(request, f"{queryset.filter(statut='reservee').count()} annonce(s) marquée(s) comme réservée(s).")
    marquer_reservee.short_description = "Marquer comme réservée"

    def marquer_vendue(self, request, queryset):
        from django.utils import timezone
        for annonce in queryset.filter(statut__in=['en_vente', 'reservee']):
            annonce.statut = 'vendue'
            annonce.date_vente = timezone.now()
            annonce.save()
        self.message_user(request, f"{queryset.filter(statut='vendue').count()} annonce(s) marquée(s) comme vendue(s).")
    marquer_vendue.short_description = "Marquer comme vendue"

    def marquer_retiree(self, request, queryset):
        queryset.update(statut='retiree')
        self.message_user(request, f"{queryset.filter(statut='retiree').count()} annonce(s) retirée(s) de la vente.")
    marquer_retiree.short_description = "Retirer de la vente"
