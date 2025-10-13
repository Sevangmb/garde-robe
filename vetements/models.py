from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

# Create your models here.

class Categorie(models.Model):
    """Catégorie de vêtement (ex: Pantalon, T-shirt, Robe, etc.)"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Couleur(models.Model):
    """Couleur disponible pour les vêtements"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    code_hex = models.CharField(max_length=7, blank=True, verbose_name="Code couleur (hex)", help_text="Ex: #FF5733")

    class Meta:
        verbose_name = "Couleur"
        verbose_name_plural = "Couleurs"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Taille(models.Model):
    """Tailles disponibles (XS, S, M, L, XL, etc.)"""
    TYPES_TAILLE = [
        ('standard', 'Standard (XS, S, M, L, XL, XXL)'),
        ('numerique', 'Numérique (36, 38, 40, 42, etc.)'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=10, unique=True, verbose_name="Nom")
    type_taille = models.CharField(max_length=20, choices=TYPES_TAILLE, default='standard', verbose_name="Type de taille")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Taille"
        verbose_name_plural = "Tailles"
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class Vetement(models.Model):
    """Vêtement dans la garde-robe"""
    GENRE_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
        ('unisexe', 'Unisexe'),
        ('enfant', 'Enfant'),
    ]

    SAISON_CHOICES = [
        ('printemps', 'Printemps'),
        ('ete', 'Été'),
        ('automne', 'Automne'),
        ('hiver', 'Hiver'),
        ('toute_saison', 'Toute saison'),
    ]

    ETAT_CHOICES = [
        ('neuf', 'Neuf'),
        ('excellent', 'Excellent état'),
        ('bon', 'Bon état'),
        ('usage', 'État d\'usage'),
        ('reparer', 'À réparer'),
    ]

    # Propriétaire
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vetements', verbose_name="Propriétaire", default=1)

    # Informations principales
    nom = models.CharField(max_length=200, verbose_name="Nom", help_text="Ex: T-shirt bleu Nike")
    description = models.TextField(blank=True, verbose_name="Description")

    # Classification
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name='vetements', verbose_name="Catégorie")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, verbose_name="Genre")
    saison = models.CharField(max_length=20, choices=SAISON_CHOICES, default='toute_saison', verbose_name="Saison")

    # Caractéristiques
    couleur = models.ForeignKey(Couleur, on_delete=models.SET_NULL, null=True, related_name='vetements', verbose_name="Couleur principale")
    taille = models.ForeignKey(Taille, on_delete=models.SET_NULL, null=True, related_name='vetements', verbose_name="Taille")
    marque = models.CharField(max_length=100, blank=True, verbose_name="Marque")
    matiere = models.CharField(max_length=200, blank=True, verbose_name="Matière", help_text="Ex: Coton 100%, Polyester 60%, etc.")

    # Informations d'achat
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name="Prix d'achat (€)", help_text="Optionnel")
    date_achat = models.DateField(null=True, blank=True, verbose_name="Date d'achat")
    lieu_achat = models.CharField(max_length=200, blank=True, verbose_name="Lieu d'achat", help_text="Ex: Zara, en ligne, marché...")

    # État et utilisation
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='bon', verbose_name="État")
    favori = models.BooleanField(default=False, verbose_name="Favori", help_text="Vêtement que vous portez souvent")
    nombre_portage = models.IntegerField(default=0, verbose_name="Nombre de fois porté")
    derniere_utilisation = models.DateField(null=True, blank=True, verbose_name="Dernière fois porté")

    # Organisation
    emplacement = models.CharField(max_length=100, blank=True, verbose_name="Emplacement", help_text="Ex: Armoire chambre, Penderie entrée")
    a_laver = models.BooleanField(default=False, verbose_name="À laver")
    a_repasser = models.BooleanField(default=False, verbose_name="À repasser")
    prete = models.BooleanField(default=False, verbose_name="Prêté", help_text="Cochez si vous avez prêté ce vêtement")
    prete_a = models.CharField(max_length=100, blank=True, verbose_name="Prêté à")

    # Image
    image = models.ImageField(upload_to='vetements/', blank=True, null=True, verbose_name="Photo")

    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes", help_text="Notes personnelles, taille réelle, conseils d'entretien...")

    # Dates
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout à la garde-robe")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Vêtement"
        verbose_name_plural = "Vêtements"
        ordering = ['-date_ajout']

    def __str__(self):
        return self.nom

    @property
    def cout_par_portage(self):
        """Calcule le coût par portage"""
        if self.prix_achat and self.nombre_portage > 0:
            return self.prix_achat / self.nombre_portage
        return None

    @property
    def peu_porte(self):
        """Vérifie si le vêtement est peu porté (moins de 3 fois)"""
        return self.nombre_portage < 3

    @property
    def besoin_entretien(self):
        """Vérifie si le vêtement nécessite un entretien"""
        return self.a_laver or self.a_repasser or self.etat == 'reparer'


class Tenue(models.Model):
    """Tenue composée de plusieurs vêtements"""
    # Propriétaire
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenues', verbose_name="Propriétaire", default=1)

    nom = models.CharField(max_length=200, verbose_name="Nom de la tenue", help_text="Ex: Bureau casual, Soirée été")
    description = models.TextField(blank=True, verbose_name="Description")
    vetements = models.ManyToManyField(Vetement, related_name='tenues', verbose_name="Vêtements")

    OCCASION_CHOICES = [
        ('travail', 'Travail'),
        ('sport', 'Sport'),
        ('soiree', 'Soirée'),
        ('decontracte', 'Décontracté'),
        ('ceremonie', 'Cérémonie'),
        ('autre', 'Autre'),
    ]

    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, default='decontracte', verbose_name="Occasion")
    saison = models.CharField(max_length=20, choices=Vetement.SAISON_CHOICES, default='toute_saison', verbose_name="Saison")
    favori = models.BooleanField(default=False, verbose_name="Tenue favorite")
    nombre_fois_portee = models.IntegerField(default=0, verbose_name="Nombre de fois portée")
    derniere_fois_portee = models.DateField(null=True, blank=True, verbose_name="Dernière fois portée")

    image = models.ImageField(upload_to='tenues/', blank=True, null=True, verbose_name="Photo de la tenue")

    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Tenue"
        verbose_name_plural = "Tenues"
        ordering = ['-date_creation']

    def __str__(self):
        return self.nom


class Valise(models.Model):
    """Valise/bagage pour les voyages"""
    TYPE_VOYAGE_CHOICES = [
        ('weekend', 'Weekend (1-3 jours)'),
        ('semaine', 'Semaine (4-7 jours)'),
        ('long', 'Long séjour (8+ jours)'),
        ('professionnel', 'Voyage professionnel'),
        ('vacances', 'Vacances'),
    ]

    STATUT_CHOICES = [
        ('preparation', 'En préparation'),
        ('prete', 'Prête'),
        ('en_cours', 'En cours de voyage'),
        ('terminee', 'Terminée'),
    ]

    # Propriétaire
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='valises', verbose_name="Propriétaire", default=1)

    # Informations du voyage
    nom = models.CharField(max_length=200, verbose_name="Nom du voyage", help_text="Ex: Barcelone Juillet 2025, Weekend Normandie")
    destination = models.CharField(max_length=200, verbose_name="Destination")
    type_voyage = models.CharField(max_length=20, choices=TYPE_VOYAGE_CHOICES, verbose_name="Type de voyage")

    # Dates
    date_depart = models.DateField(verbose_name="Date de départ")
    date_retour = models.DateField(verbose_name="Date de retour")

    # Météo et climat
    meteo_prevue = models.CharField(max_length=200, blank=True, verbose_name="Météo prévue", help_text="Ex: Ensoleillé 25°C, Pluvieux 15°C")
    climat = models.CharField(max_length=50, blank=True, verbose_name="Climat", help_text="Ex: Chaud, Froid, Tempéré")

    # Contenu de la valise
    vetements = models.ManyToManyField(Vetement, related_name='valises_old', blank=True, verbose_name="Vêtements emportés (ancien système)")
    tenues = models.ManyToManyField(Tenue, related_name='valises', blank=True, verbose_name="Tenues prévues")

    # Statut et organisation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='preparation', verbose_name="Statut")
    liste_articles_supplementaires = models.TextField(blank=True, verbose_name="Autres articles", help_text="Articles non-vêtements: trousse de toilette, médicaments, chargeurs, etc.")

    # Nouveau: Poids estimé de la valise (en kg)
    poids_estime = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Poids estimé (kg)", help_text="Calculé automatiquement")
    poids_max = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(0)], verbose_name="Poids maximum autorisé (kg)")

    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes", help_text="Activités prévues, contraintes, rappels...")
    checklist_faite = models.BooleanField(default=False, verbose_name="Checklist complétée")

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Valise"
        verbose_name_plural = "Valises"
        ordering = ['-date_depart']

    def __str__(self):
        return f"{self.nom} - {self.destination}"

    @property
    def duree_sejour(self):
        """Calcule la durée du séjour en jours"""
        if self.date_depart and self.date_retour:
            return (self.date_retour - self.date_depart).days + 1
        return 0

    @property
    def nombre_vetements(self):
        """Compte le nombre de vêtements dans la valise (nouveau système)"""
        return self.items.count()

    @property
    def nombre_emballe(self):
        """Compte le nombre d'items déjà emballés"""
        return self.items.filter(emballe=True).count()

    @property
    def pourcentage_completion(self):
        """Calcule le pourcentage de completion de la valise"""
        total = self.items.count()
        if total == 0:
            return 0
        return int((self.nombre_emballe / total) * 100)

    @property
    def poids_total_kg(self):
        """Calcule le poids total des items en kg"""
        total_grammes = sum([item.poids_estime for item in self.items.all()])
        return round(total_grammes / 1000, 2)

    @property
    def est_passee(self):
        """Vérifie si le voyage est passé"""
        from datetime import date
        return self.date_retour < date.today() if self.date_retour else False

    @property
    def est_en_cours(self):
        """Vérifie si le voyage est en cours"""
        from datetime import date
        today = date.today()
        return self.date_depart <= today <= self.date_retour if self.date_depart and self.date_retour else False

    @property
    def est_a_venir(self):
        """Vérifie si le voyage est à venir"""
        from datetime import date
        return self.date_depart > date.today() if self.date_depart else False


class ItemValise(models.Model):
    """Table intermédiaire pour tracker l'état d'emballage de chaque vêtement dans une valise"""
    CATEGORIES_VALISE = [
        ('vetements', 'Vêtements'),
        ('chaussures', 'Chaussures'),
        ('sous_vetements', 'Sous-vêtements'),
        ('accessoires', 'Accessoires'),
        ('toilette', 'Toilette'),
        ('electronique', 'Électronique'),
        ('documents', 'Documents'),
        ('sante', 'Santé'),
        ('autre', 'Autre'),
    ]

    valise = models.ForeignKey(Valise, on_delete=models.CASCADE, related_name='items', verbose_name="Valise")
    vetement = models.ForeignKey(Vetement, on_delete=models.CASCADE, verbose_name="Vêtement")

    # État d'emballage
    emballe = models.BooleanField(default=False, verbose_name="Emballé")

    # Catégorisation pour une meilleure organisation
    categorie_valise = models.CharField(max_length=20, choices=CATEGORIES_VALISE, default='vetements', verbose_name="Catégorie dans la valise")

    # Poids estimé de l'item (en grammes)
    poids_estime = models.IntegerField(default=200, validators=[MinValueValidator(0)], verbose_name="Poids estimé (g)", help_text="Poids moyen de l'article")

    # Ordre d'affichage
    ordre = models.IntegerField(default=0, verbose_name="Ordre")

    # Notes spécifiques à cet item dans cette valise
    note = models.CharField(max_length=200, blank=True, verbose_name="Note", help_text="Ex: À laver avant de partir, Fragile, etc.")

    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Ajouté le")

    class Meta:
        verbose_name = "Item de valise"
        verbose_name_plural = "Items de valise"
        unique_together = ['valise', 'vetement']
        ordering = ['categorie_valise', 'ordre', 'date_ajout']

    def __str__(self):
        return f"{self.vetement.nom} dans {self.valise.nom} ({'✓' if self.emballe else '○'})"


class Message(models.Model):
    """Messages entre utilisateurs"""
    # Expéditeur et destinataire
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes', verbose_name="Expéditeur")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus', verbose_name="Destinataire")

    # Contenu du message
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    contenu = models.TextField(verbose_name="Message")

    # Statut
    lu = models.BooleanField(default=False, verbose_name="Lu")
    archive_expediteur = models.BooleanField(default=False, verbose_name="Archivé par l'expéditeur")
    archive_destinataire = models.BooleanField(default=False, verbose_name="Archivé par le destinataire")

    # Dates
    date_envoi = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    date_lecture = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")

    # Réponse à un message
    en_reponse_a = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reponses', verbose_name="En réponse à")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.sujet} - De {self.expediteur.username} à {self.destinataire.username}"

    def marquer_comme_lu(self):
        """Marque le message comme lu"""
        if not self.lu:
            from django.utils import timezone
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()


class Amitie(models.Model):
    """Relation d'amitié entre utilisateurs"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    demandeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_amitie_envoyees', verbose_name="Demandeur")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_amitie_recues', verbose_name="Destinataire")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    date_reponse = models.DateTimeField(null=True, blank=True, verbose_name="Date de réponse")

    class Meta:
        verbose_name = "Amitié"
        verbose_name_plural = "Amitiés"
        unique_together = ['demandeur', 'destinataire']
        ordering = ['-date_demande']

    def __str__(self):
        return f"{self.demandeur.username} → {self.destinataire.username} ({self.get_statut_display()})"


class AnnonceVente(models.Model):
    """Annonce de vente d'un vêtement"""
    STATUT_CHOICES = [
        ('en_vente', 'En vente'),
        ('reservee', 'Réservée'),
        ('vendue', 'Vendue'),
        ('retiree', 'Retirée'),
    ]

    vetement = models.OneToOneField(Vetement, on_delete=models.CASCADE, related_name='annonce_vente', verbose_name="Vêtement")
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annonces_vente', verbose_name="Vendeur")

    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix de vente (€)")
    description_vente = models.TextField(blank=True, verbose_name="Description pour la vente", help_text="Informations supplémentaires pour l'acheteur")

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_vente', verbose_name="Statut")
    acheteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='achats', verbose_name="Acheteur")

    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")
    date_vente = models.DateTimeField(null=True, blank=True, verbose_name="Date de vente")

    negociable = models.BooleanField(default=True, verbose_name="Prix négociable")
    livraison_possible = models.BooleanField(default=False, verbose_name="Livraison possible")

    class Meta:
        verbose_name = "Annonce de vente"
        verbose_name_plural = "Annonces de vente"
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.vetement.nom} - {self.prix_vente}€ ({self.get_statut_display()})"

    @property
    def est_disponible(self):
        """Vérifie si l'annonce est disponible à l'achat"""
        return self.statut == 'en_vente'


class FavoriAnnonce(models.Model):
    """Système de favoris pour les annonces"""
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annonces_favorites', verbose_name="Utilisateur")
    annonce = models.ForeignKey(AnnonceVente, on_delete=models.CASCADE, related_name='favoris', verbose_name="Annonce")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout aux favoris")
    notification_changement_prix = models.BooleanField(default=True, verbose_name="Notifier en cas de changement de prix")

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ['utilisateur', 'annonce']
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.utilisateur.username} → {self.annonce.vetement.nom}"


class TransactionVente(models.Model):
    """Historique des transactions de vente"""
    STATUT_CHOICES = [
        ('en_cours', 'En cours de négociation'),
        ('acceptee', 'Acceptée - En attente de finalisation'),
        ('finalisee', 'Finalisée'),
        ('annulee', 'Annulée'),
    ]

    annonce = models.ForeignKey(AnnonceVente, on_delete=models.CASCADE, related_name='transactions', verbose_name="Annonce")
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventes', verbose_name="Vendeur")
    acheteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achats_transactions', verbose_name="Acheteur")

    # Détails de la transaction
    prix_final = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix final (€)")
    prix_initial = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Prix initial (€)")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours', verbose_name="Statut")

    # Livraison
    avec_livraison = models.BooleanField(default=False, verbose_name="Avec livraison")
    adresse_livraison = models.TextField(blank=True, verbose_name="Adresse de livraison")

    # Notes et commentaires
    notes_vendeur = models.TextField(blank=True, verbose_name="Notes du vendeur")
    notes_acheteur = models.TextField(blank=True, verbose_name="Notes de l'acheteur")

    # Dates
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_acceptation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'acceptation")
    date_finalisation = models.DateTimeField(null=True, blank=True, verbose_name="Date de finalisation")
    date_annulation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'annulation")

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Transaction: {self.annonce.vetement.nom} - {self.vendeur.username} → {self.acheteur.username} ({self.get_statut_display()})"

    @property
    def reduction_pourcent(self):
        """Calcule le pourcentage de réduction négocié"""
        if self.prix_initial and self.prix_final:
            return ((self.prix_initial - self.prix_final) / self.prix_initial) * 100
        return 0


class EvaluationVendeur(models.Model):
    """Système d'évaluation des vendeurs"""
    NOTES = [
        (1, '⭐ - Très insatisfait'),
        (2, '⭐⭐ - Insatisfait'),
        (3, '⭐⭐⭐ - Correct'),
        (4, '⭐⭐⭐⭐ - Satisfait'),
        (5, '⭐⭐⭐⭐⭐ - Très satisfait'),
    ]

    transaction = models.OneToOneField(TransactionVente, on_delete=models.CASCADE, related_name='evaluation', verbose_name="Transaction")
    evaluateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations_donnees', verbose_name="Évaluateur")
    vendeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations_recues', verbose_name="Vendeur évalué")

    # Notes (de 1 à 5)
    note_globale = models.IntegerField(choices=NOTES, verbose_name="Note globale")
    note_communication = models.IntegerField(choices=NOTES, verbose_name="Communication")
    note_description = models.IntegerField(choices=NOTES, verbose_name="Conformité à la description")
    note_rapidite = models.IntegerField(choices=NOTES, verbose_name="Rapidité")

    # Commentaire
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    recommande = models.BooleanField(default=True, verbose_name="Je recommande ce vendeur")

    # Métadonnées
    date_evaluation = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'évaluation")

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-date_evaluation']

    def __str__(self):
        return f"Évaluation de {self.vendeur.username} par {self.evaluateur.username} - {self.note_globale}/5"

    @property
    def note_moyenne(self):
        """Calcule la moyenne des notes"""
        return (self.note_globale + self.note_communication + self.note_description + self.note_rapidite) / 4


class ParametresSite(models.Model):
    """Paramètres globaux du site"""
    
    # Informations générales
    nom_site = models.CharField(max_length=200, default="Ma Garde-Robe", verbose_name="Nom du site")
    description_site = models.TextField(blank=True, verbose_name="Description du site")
    email_admin = models.EmailField(blank=True, verbose_name="Email administrateur")
    
    # Paramètres fonctionnels
    inscription_ouverte = models.BooleanField(default=True, verbose_name="Inscription ouverte")
    validation_inscription = models.BooleanField(default=False, verbose_name="Validation manuelle des inscriptions")
    messages_actifs = models.BooleanField(default=True, verbose_name="Système de messages activé")
    annonces_actives = models.BooleanField(default=True, verbose_name="Système d'annonces activé")
    amitie_active = models.BooleanField(default=True, verbose_name="Système d'amitié activé")
    
    # Limitations
    max_vetements_par_user = models.IntegerField(default=1000, validators=[MinValueValidator(1)], verbose_name="Max vêtements par utilisateur")
    max_tenues_par_user = models.IntegerField(default=200, validators=[MinValueValidator(1)], verbose_name="Max tenues par utilisateur")
    max_valises_par_user = models.IntegerField(default=50, validators=[MinValueValidator(1)], verbose_name="Max valises par utilisateur")
    taille_max_image = models.IntegerField(default=5, validators=[MinValueValidator(1)], verbose_name="Taille max image (MB)")
    
    # Modération
    moderation_active = models.BooleanField(default=False, verbose_name="Modération activée")
    moderation_messages = models.BooleanField(default=False, verbose_name="Modérer les messages")
    moderation_annonces = models.BooleanField(default=False, verbose_name="Modérer les annonces")
    
    # Maintenance
    mode_maintenance = models.BooleanField(default=False, verbose_name="Mode maintenance")
    message_maintenance = models.TextField(blank=True, verbose_name="Message de maintenance")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
    
    def __str__(self):
        return f"Paramètres - {self.nom_site}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        if ParametresSite.objects.exists() and not self.pk:
            # Mettre à jour l'instance existante
            existing = ParametresSite.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls):
        """Obtenir l'instance unique des paramètres"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class RapportModeration(models.Model):
    """Rapports de modération pour contenus signalés"""
    
    TYPES_CONTENU = [
        ('message', 'Message'),
        ('annonce', 'Annonce de vente'),
        ('vetement', 'Vêtement'),
        ('tenue', 'Tenue'),
        ('utilisateur', 'Utilisateur'),
    ]
    
    STATUTS = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de traitement'),
        ('resolu', 'Résolu'),
        ('rejete', 'Rejeté'),
    ]
    
    ACTIONS = [
        ('aucune', 'Aucune action'),
        ('avertissement', 'Avertissement'),
        ('suppression', 'Suppression du contenu'),
        ('suspension', 'Suspension temporaire'),
        ('bannissement', 'Bannissement permanent'),
    ]
    
    # Informations du signalement
    rapporteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports_envoyes', verbose_name="Rapporteur")
    type_contenu = models.CharField(max_length=20, choices=TYPES_CONTENU, verbose_name="Type de contenu")
    objet_id = models.IntegerField(verbose_name="ID de l'objet signalé")
    utilisateur_concerne = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports_recus', verbose_name="Utilisateur concerné")
    
    # Détails du rapport
    motif = models.TextField(verbose_name="Motif du signalement")
    description = models.TextField(blank=True, verbose_name="Description détaillée")
    date_rapport = models.DateTimeField(auto_now_add=True, verbose_name="Date du rapport")
    
    # Traitement
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente', verbose_name="Statut")
    moderateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderations_traitees', verbose_name="Modérateur")
    action_prise = models.CharField(max_length=20, choices=ACTIONS, default='aucune', verbose_name="Action prise")
    commentaire_moderateur = models.TextField(blank=True, verbose_name="Commentaire du modérateur")
    date_traitement = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    
    class Meta:
        verbose_name = "Rapport de modération"
        verbose_name_plural = "Rapports de modération"
        ordering = ['-date_rapport']
    
    def __str__(self):
        return f"Rapport {self.type_contenu} - {self.utilisateur_concerne.username} ({self.get_statut_display()})"


class ActionModeration(models.Model):
    """Historique des actions de modération"""
    
    TYPES_ACTION = [
        ('avertissement', 'Avertissement'),
        ('suppression_contenu', 'Suppression de contenu'),
        ('suspension', 'Suspension temporaire'),
        ('bannissement', 'Bannissement permanent'),
        ('levee_sanction', 'Levée de sanction'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_moderation', verbose_name="Utilisateur")
    moderateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_effectuees', verbose_name="Modérateur")
    type_action = models.CharField(max_length=30, choices=TYPES_ACTION, verbose_name="Type d'action")
    motif = models.TextField(verbose_name="Motif")
    date_action = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'action")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin (pour suspensions)")
    rapport_lie = models.ForeignKey(RapportModeration, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Rapport lié")
    
    class Meta:
        verbose_name = "Action de modération"
        verbose_name_plural = "Actions de modération"
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.get_type_action_display()} - {self.utilisateur.username} ({self.date_action.strftime('%d/%m/%Y')})"


class EvenementTenue(models.Model):
    """Événement avec tenue planifiée dans le calendrier"""

    TYPE_EVENEMENT_CHOICES = [
        ('travail', 'Travail'),
        ('reunion', 'Réunion'),
        ('sortie', 'Sortie'),
        ('rendez_vous', 'Rendez-vous'),
        ('ceremonie', 'Cérémonie'),
        ('sport', 'Sport'),
        ('voyage', 'Voyage'),
        ('autre', 'Autre'),
    ]

    # Propriétaire
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evenements', verbose_name="Propriétaire")

    # Informations de l'événement
    titre = models.CharField(max_length=200, verbose_name="Titre", help_text="Ex: Réunion client, Dîner restaurant")
    description = models.TextField(blank=True, verbose_name="Description")
    type_evenement = models.CharField(max_length=20, choices=TYPE_EVENEMENT_CHOICES, default='autre', verbose_name="Type d'événement")

    # Date et heure
    date = models.DateField(verbose_name="Date")
    heure_debut = models.TimeField(null=True, blank=True, verbose_name="Heure de début")
    heure_fin = models.TimeField(null=True, blank=True, verbose_name="Heure de fin")
    toute_journee = models.BooleanField(default=False, verbose_name="Événement toute la journée")

    # Tenue planifiée
    tenue = models.ForeignKey(Tenue, on_delete=models.SET_NULL, null=True, blank=True, related_name='evenements', verbose_name="Tenue prévue")

    # Lieu
    lieu = models.CharField(max_length=200, blank=True, verbose_name="Lieu")

    # Rappel
    rappel = models.BooleanField(default=False, verbose_name="Activer un rappel")
    rappel_minutes_avant = models.IntegerField(default=60, validators=[MinValueValidator(0)], verbose_name="Rappel (minutes avant)", help_text="Nombre de minutes avant l'événement")

    # Météo prévue (optionnel)
    meteo_prevue = models.CharField(max_length=100, blank=True, verbose_name="Météo prévue", help_text="Ex: Ensoleillé, Pluvieux")

    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")

    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['date', 'heure_debut']

    def __str__(self):
        return f"{self.titre} - {self.date.strftime('%d/%m/%Y')}"

    @property
    def est_passe(self):
        """Vérifie si l'événement est passé"""
        from datetime import date
        return self.date < date.today()

    @property
    def est_aujourdhui(self):
        """Vérifie si l'événement est aujourd'hui"""
        from datetime import date
        return self.date == date.today()

    @property
    def est_a_venir(self):
        """Vérifie si l'événement est à venir"""
        from datetime import date
        return self.date > date.today()
