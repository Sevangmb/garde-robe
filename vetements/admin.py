from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Q, Count
from django.utils.html import format_html
from .models import Categorie, Couleur, Taille, Vetement, Tenue, Valise, ItemValise, Message, Amitie, AnnonceVente, ParametresSite, RapportModeration, ActionModeration, FavoriAnnonce, TransactionVente, EvaluationVendeur


# Personnalisation du site admin pour restreindre l'accès
class RestrictedAdminSite(admin.AdminSite):
    """Site admin accessible uniquement aux superutilisateurs"""
    
    site_header = "Administration Garde-Robe"
    site_title = "Admin Garde-Robe"
    index_title = "Panneau d'administration"

    def has_permission(self, request):
        """Seuls les superutilisateurs peuvent accéder à l'admin"""
        return request.user.is_active and request.user.is_superuser

    def index(self, request, extra_context=None):
        """Personnaliser la page d'accueil de l'admin avec des statistiques"""
        extra_context = extra_context or {}
        
        # Statistiques globales
        extra_context['total_users'] = User.objects.count()
        extra_context['total_vetements'] = Vetement.objects.count()
        extra_context['total_tenues'] = Tenue.objects.count()
        extra_context['total_valises'] = Valise.objects.count()
        extra_context['total_messages'] = Message.objects.count()
        extra_context['total_annonces'] = AnnonceVente.objects.count()
        
        # Utilisateurs actifs (ayant des vêtements)
        extra_context['users_with_clothes'] = User.objects.annotate(
            nb_vetements=Count('vetements')
        ).filter(nb_vetements__gt=0).count()
        
        # Messages non lus
        extra_context['unread_messages'] = Message.objects.filter(lu=False).count()
        
        # Annonces actives
        extra_context['active_announcements'] = AnnonceVente.objects.filter(statut='en_vente').count()
        
        return super().index(request, extra_context)


# Créer une instance du site admin restreint
restricted_admin_site = RestrictedAdminSite(name='restricted_admin')


# GESTION DES UTILISATEURS ET GROUPES

@admin.register(User, site=restricted_admin_site)
class CustomUserAdmin(UserAdmin):
    """Administration personnalisée des utilisateurs"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login', 'nb_vetements', 'nb_tenues']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Statistiques', {
            'fields': ('get_user_stats',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = UserAdmin.readonly_fields + ('get_user_stats',)
    
    def get_queryset(self, request):
        """Ajouter les annotations pour les statistiques"""
        return super().get_queryset(request).annotate(
            nb_vetements=Count('vetements', distinct=True),
            nb_tenues=Count('tenues', distinct=True)
        )
    
    def nb_vetements(self, obj):
        """Nombre de vêtements de l'utilisateur"""
        return obj.nb_vetements if hasattr(obj, 'nb_vetements') else obj.vetements.count()
    nb_vetements.short_description = 'Vêtements'
    nb_vetements.admin_order_field = 'nb_vetements'
    
    def nb_tenues(self, obj):
        """Nombre de tenues de l'utilisateur"""
        return obj.nb_tenues if hasattr(obj, 'nb_tenues') else obj.tenues.count()
    nb_tenues.short_description = 'Tenues'
    nb_tenues.admin_order_field = 'nb_tenues'
    
    def get_user_stats(self, obj):
        """Afficher les statistiques détaillées de l'utilisateur"""
        if not obj.pk:
            return "-"
        
        nb_vetements = obj.vetements.count()
        nb_tenues = obj.tenues.count()
        nb_valises = obj.valises.count()
        nb_messages_envoyes = obj.messages_envoyes.count()
        nb_messages_recus = obj.messages_recus.count()
        nb_annonces = obj.annonces_vente.count()
        
        return format_html(
            "<strong>Garde-robe:</strong> {} vêtements, {} tenues, {} valises<br>"
            "<strong>Messages:</strong> {} envoyés, {} reçus<br>"
            "<strong>Annonces:</strong> {} créées",
            nb_vetements, nb_tenues, nb_valises,
            nb_messages_envoyes, nb_messages_recus,
            nb_annonces
        )
    get_user_stats.short_description = 'Statistiques utilisateur'
    
    actions = ['activer_utilisateurs', 'desactiver_utilisateurs', 'promouvoir_staff']
    
    def activer_utilisateurs(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} utilisateur(s) activé(s).")
    activer_utilisateurs.short_description = "Activer les utilisateurs sélectionnés"
    
    def desactiver_utilisateurs(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} utilisateur(s) désactivé(s).")
    desactiver_utilisateurs.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def promouvoir_staff(self, request, queryset):
        queryset.update(is_staff=True)
        self.message_user(request, f"{queryset.count()} utilisateur(s) promu(s) au statut staff.")
    promouvoir_staff.short_description = "Promouvoir au statut staff"


@admin.register(Group, site=restricted_admin_site)
class CustomGroupAdmin(admin.ModelAdmin):
    """Administration des groupes"""
    
    list_display = ['name', 'nb_users', 'permissions_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            nb_users=Count('user')
        )
    
    def nb_users(self, obj):
        return obj.nb_users if hasattr(obj, 'nb_users') else obj.user_set.count()
    nb_users.short_description = 'Utilisateurs'
    nb_users.admin_order_field = 'nb_users'
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions'


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
    autocomplete_fields = []  # Pour permettre l'autocomplete dans d'autres modèles

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


class ItemValiseInline(admin.TabularInline):
    """Inline pour gérer les items d'une valise"""
    model = ItemValise
    extra = 1
    fields = ['vetement', 'categorie_valise', 'poids_estime', 'emballe', 'note', 'ordre']
    autocomplete_fields = ['vetement']


@admin.register(Valise, site=restricted_admin_site)
class ValiseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'destination', 'type_voyage', 'date_depart', 'date_retour', 'duree_affichage', 'statut', 'nombre_items']
    list_filter = ['type_voyage', 'statut', 'date_depart', 'climat']
    search_fields = ['nom', 'destination', 'notes']
    filter_horizontal = ['tenues']
    readonly_fields = ['date_creation', 'date_modification']
    date_hierarchy = 'date_depart'
    inlines = [ItemValiseInline]

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
        ('Poids', {
            'fields': ('poids_max',)
        }),
        ('Contenu de la valise', {
            'fields': ('tenues',),
            'description': 'Les vêtements individuels sont gérés via l\'interface de checklist interactive'
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
        """Limiter les tenues disponibles à celles de l'utilisateur"""
        if db_field.name == "tenues":
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


# PARAMÈTRES ET MODÉRATION

@admin.register(ParametresSite, site=restricted_admin_site)
class ParametresSiteAdmin(admin.ModelAdmin):
    """Administration des paramètres du site"""
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_site', 'description_site', 'email_admin')
        }),
        ('Paramètres fonctionnels', {
            'fields': ('inscription_ouverte', 'validation_inscription', 'messages_actifs', 'annonces_actives', 'amitie_active')
        }),
        ('Limitations', {
            'fields': ('max_vetements_par_user', 'max_tenues_par_user', 'max_valises_par_user', 'taille_max_image')
        }),
        ('Modération', {
            'fields': ('moderation_active', 'moderation_messages', 'moderation_annonces')
        }),
        ('Maintenance', {
            'fields': ('mode_maintenance', 'message_maintenance')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_creation', 'date_modification']
    
    def has_add_permission(self, request):
        # Empêcher la création de nouveaux paramètres s'ils existent déjà
        return not ParametresSite.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression des paramètres
        return False


@admin.register(RapportModeration, site=restricted_admin_site)
class RapportModerationAdmin(admin.ModelAdmin):
    """Administration des rapports de modération"""
    
    list_display = ['get_objet_signale', 'type_contenu', 'rapporteur', 'utilisateur_concerne', 'statut', 'date_rapport', 'moderateur']
    list_filter = ['type_contenu', 'statut', 'date_rapport', 'action_prise']
    search_fields = ['rapporteur__username', 'utilisateur_concerne__username', 'motif', 'commentaire_moderateur']
    readonly_fields = ['date_rapport']
    date_hierarchy = 'date_rapport'
    
    fieldsets = (
        ('Signalement', {
            'fields': ('rapporteur', 'type_contenu', 'objet_id', 'utilisateur_concerne')
        }),
        ('Détails', {
            'fields': ('motif', 'description', 'date_rapport')
        }),
        ('Traitement', {
            'fields': ('statut', 'moderateur', 'action_prise', 'commentaire_moderateur', 'date_traitement')
        }),
    )
    
    def get_objet_signale(self, obj):
        """Afficher une représentation de l'objet signalé"""
        return f"{obj.get_type_contenu_display()} #{obj.objet_id}"
    get_objet_signale.short_description = 'Objet signalé'
    
    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement le modérateur et la date de traitement"""
        if change and obj.statut in ['en_cours', 'resolu', 'rejete'] and not obj.moderateur:
            obj.moderateur = request.user
        if change and obj.statut in ['resolu', 'rejete'] and not obj.date_traitement:
            from django.utils import timezone
            obj.date_traitement = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['prendre_en_charge', 'resoudre_rapports', 'rejeter_rapports']
    
    def prendre_en_charge(self, request, queryset):
        queryset.filter(statut='en_attente').update(statut='en_cours', moderateur=request.user)
        self.message_user(request, f"{queryset.filter(statut='en_cours').count()} rapport(s) pris en charge.")
    prendre_en_charge.short_description = "Prendre en charge"
    
    def resoudre_rapports(self, request, queryset):
        from django.utils import timezone
        for rapport in queryset.filter(statut__in=['en_attente', 'en_cours']):
            rapport.statut = 'resolu'
            rapport.moderateur = request.user
            rapport.date_traitement = timezone.now()
            rapport.save()
        self.message_user(request, f"{queryset.filter(statut='resolu').count()} rapport(s) résolu(s).")
    resoudre_rapports.short_description = "Marquer comme résolu"
    
    def rejeter_rapports(self, request, queryset):
        from django.utils import timezone
        for rapport in queryset.filter(statut__in=['en_attente', 'en_cours']):
            rapport.statut = 'rejete'
            rapport.moderateur = request.user
            rapport.date_traitement = timezone.now()
            rapport.save()
        self.message_user(request, f"{queryset.filter(statut='rejete').count()} rapport(s) rejeté(s).")
    rejeter_rapports.short_description = "Rejeter"


@admin.register(ActionModeration, site=restricted_admin_site)
class ActionModerationAdmin(admin.ModelAdmin):
    """Administration des actions de modération"""
    
    list_display = ['utilisateur', 'type_action', 'moderateur', 'date_action', 'date_fin', 'rapport_lie']
    list_filter = ['type_action', 'date_action', 'moderateur']
    search_fields = ['utilisateur__username', 'moderateur__username', 'motif']
    readonly_fields = ['date_action']
    date_hierarchy = 'date_action'
    
    fieldsets = (
        ('Action', {
            'fields': ('utilisateur', 'moderateur', 'type_action')
        }),
        ('Détails', {
            'fields': ('motif', 'date_action', 'date_fin')
        }),
        ('Contexte', {
            'fields': ('rapport_lie',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Attribuer automatiquement le modérateur"""
        if not change:
            obj.moderateur = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['lever_sanctions']
    
    def lever_sanctions(self, request, queryset):
        from django.utils import timezone
        for action in queryset.filter(type_action__in=['suspension', 'bannissement']):
            # Créer une action de levée de sanction
            ActionModeration.objects.create(
                utilisateur=action.utilisateur,
                moderateur=request.user,
                type_action='levee_sanction',
                motif=f"Levée de sanction : {action.get_type_action_display()}",
                rapport_lie=action.rapport_lie
            )
        self.message_user(request, f"Sanctions levées pour {queryset.count()} action(s).")
    lever_sanctions.short_description = "Lever les sanctions"
