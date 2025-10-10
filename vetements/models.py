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
    vetements = models.ManyToManyField(Vetement, related_name='valises', verbose_name="Vêtements emportés")
    tenues = models.ManyToManyField(Tenue, related_name='valises', blank=True, verbose_name="Tenues prévues")

    # Statut et organisation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='preparation', verbose_name="Statut")
    liste_articles_supplementaires = models.TextField(blank=True, verbose_name="Autres articles", help_text="Articles non-vêtements: trousse de toilette, médicaments, chargeurs, etc.")

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
        """Compte le nombre de vêtements dans la valise"""
        return self.vetements.count()

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
