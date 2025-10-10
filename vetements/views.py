from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Sum, Count, Q
from datetime import date
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Vetement, Categorie, Tenue, Valise, Message, Amitie, AnnonceVente

# Create your views here.

# Authentication views
def register(request):
    """Inscription d'un nouvel utilisateur"""
    if request.user.is_authenticated:
        return redirect('vetements:accueil')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}! Votre compte a été créé avec succès.")
            return redirect('vetements:accueil')
    else:
        form = UserCreationForm()

    return render(request, 'vetements/register.html', {'form': form})


def login_view(request):
    """Connexion d'un utilisateur"""
    if request.user.is_authenticated:
        return redirect('vetements:accueil')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {username}!")
                return redirect('vetements:accueil')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, 'vetements/login.html', {'form': form})


def logout_view(request):
    """Déconnexion d'un utilisateur"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('vetements:login')


@login_required
def user_profile(request):
    """Profil et paramètres de l'utilisateur"""
    if request.method == 'POST':
        # Mettre à jour le profil
        username = request.POST.get('username')
        email = request.POST.get('email')

        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            else:
                request.user.username = username
                request.user.save()
                messages.success(request, "Nom d'utilisateur mis à jour.")

        if email is not None:
            request.user.email = email
            request.user.save()
            messages.success(request, "Email mis à jour.")

        return redirect('vetements:user_profile')

    # Statistiques personnelles
    nb_vetements = Vetement.objects.filter(proprietaire=request.user).count()
    nb_tenues = Tenue.objects.filter(proprietaire=request.user).count()
    nb_valises = Valise.objects.filter(proprietaire=request.user).count()
    nb_messages_recus = Message.objects.filter(destinataire=request.user).count()
    nb_messages_envoyes = Message.objects.filter(expediteur=request.user).count()

    context = {
        'nb_vetements': nb_vetements,
        'nb_tenues': nb_tenues,
        'nb_valises': nb_valises,
        'nb_messages_recus': nb_messages_recus,
        'nb_messages_envoyes': nb_messages_envoyes,
    }
    return render(request, 'vetements/user_profile.html', context)

@login_required
def accueil(request):
    """Page d'accueil avec statistiques de la garde-robe"""
    # Filtrer par utilisateur connecté
    vetements = Vetement.objects.filter(proprietaire=request.user)
    total_vetements = vetements.count()
    favoris = vetements.filter(favori=True).count()
    a_laver = vetements.filter(a_laver=True).count()
    peu_portes = len([v for v in vetements if v.peu_porte])

    # Statistiques sur les prix
    total_depense = vetements.aggregate(total=Sum('prix_achat'))['total'] or 0

    # Vêtements par catégorie
    par_categorie = vetements.values('categorie__nom').annotate(count=Count('id')).order_by('-count')[:5]

    # Statistiques de portage
    total_portages = vetements.aggregate(total=Sum('nombre_portage'))['total'] or 0

    context = {
        'total_vetements': total_vetements,
        'favoris': favoris,
        'a_laver': a_laver,
        'peu_portes': peu_portes,
        'total_depense': total_depense,
        'par_categorie': par_categorie,
        'total_portages': total_portages,
        'derniers_vetements': vetements.order_by('-date_ajout')[:6],
        'total_tenues': Tenue.objects.filter(proprietaire=request.user).count(),
    }
    return render(request, 'vetements/accueil.html', context)


class VetementListView(ListView):
    """Liste de tous les vêtements de la garde-robe"""
    model = Vetement
    template_name = 'vetements/liste_vetements.html'
    context_object_name = 'vetements'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('vetements:login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filtrer par utilisateur connecté
        queryset = Vetement.objects.filter(proprietaire=self.request.user)

        # Filtrage par catégorie
        categorie_id = self.request.GET.get('categorie')
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)

        # Filtrage par genre
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)

        # Filtrage par saison
        saison = self.request.GET.get('saison')
        if saison:
            queryset = queryset.filter(saison=saison)

        # Filtrage par état
        etat = self.request.GET.get('etat')
        if etat:
            queryset = queryset.filter(etat=etat)

        # Filtrage favoris
        if self.request.GET.get('favori'):
            queryset = queryset.filter(favori=True)

        # Filtrage à laver
        if self.request.GET.get('a_laver'):
            queryset = queryset.filter(a_laver=True)

        # Recherche
        recherche = self.request.GET.get('q')
        if recherche:
            queryset = queryset.filter(nom__icontains=recherche) | queryset.filter(description__icontains=recherche) | queryset.filter(marque__icontains=recherche)

        return queryset.order_by('-date_ajout')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        return context


class VetementDetailView(DetailView):
    """Détails d'un vêtement"""
    model = Vetement
    template_name = 'vetements/detail_vetement.html'
    context_object_name = 'vetement'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('vetements:login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Filtrer par utilisateur connecté
        return Vetement.objects.filter(proprietaire=self.request.user)


@login_required
def vetements_par_categorie(request, categorie_id):
    """Liste des vêtements par catégorie"""
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    vetements = Vetement.objects.filter(categorie=categorie, proprietaire=request.user).order_by('-date_ajout')

    context = {
        'categorie': categorie,
        'vetements': vetements,
    }
    return render(request, 'vetements/categorie.html', context)


@login_required
def entretien(request):
    """Liste des vêtements nécessitant un entretien"""
    vetements = Vetement.objects.filter(proprietaire=request.user)
    a_laver = vetements.filter(a_laver=True)
    a_repasser = vetements.filter(a_repasser=True)
    a_reparer = vetements.filter(etat='reparer')
    pretes = vetements.filter(prete=True)

    context = {
        'a_laver': a_laver,
        'a_repasser': a_repasser,
        'a_reparer': a_reparer,
        'pretes': pretes,
    }
    return render(request, 'vetements/entretien.html', context)


@login_required
def tenues_list(request):
    """Liste des tenues"""
    tenues = Tenue.objects.filter(proprietaire=request.user).order_by('-date_creation')

    # Filtrage par occasion
    occasion = request.GET.get('occasion')
    if occasion:
        tenues = tenues.filter(occasion=occasion)

    # Filtrage favoris
    if request.GET.get('favori'):
        tenues = tenues.filter(favori=True)

    context = {
        'tenues': tenues,
    }
    return render(request, 'vetements/tenues_list.html', context)


@login_required
def tenue_detail(request, pk):
    """Détail d'une tenue"""
    tenue = get_object_or_404(Tenue, pk=pk, proprietaire=request.user)

    context = {
        'tenue': tenue,
    }
    return render(request, 'vetements/tenue_detail.html', context)


@login_required
def statistiques(request):
    """Page de statistiques détaillées"""
    vetements = Vetement.objects.filter(proprietaire=request.user)

    # Statistiques générales
    total_vetements = vetements.count()
    total_depense = vetements.aggregate(total=Sum('prix_achat'))['total'] or 0

    # Par catégorie
    par_categorie = vetements.values('categorie__nom').annotate(count=Count('id')).order_by('-count')

    # Par couleur
    par_couleur = vetements.values('couleur__nom').annotate(count=Count('id')).order_by('-count')[:10]

    # Par saison
    par_saison = vetements.values('saison').annotate(count=Count('id')).order_by('-count')

    # Statistiques de portage
    total_portages = vetements.aggregate(total=Sum('nombre_portage'))['total'] or 0
    vetements_avec_prix = vetements.exclude(prix_achat__isnull=True).exclude(nombre_portage=0)
    cout_moyen_portage = None
    if vetements_avec_prix.exists():
        couts = [v.cout_par_portage for v in vetements_avec_prix if v.cout_par_portage]
        if couts:
            cout_moyen_portage = sum(couts) / len(couts)

    # Les plus portés
    plus_portes = vetements.filter(nombre_portage__gt=0).order_by('-nombre_portage')[:10]

    # Les moins portés
    peu_portes = [v for v in vetements if v.peu_porte]

    context = {
        'total_vetements': total_vetements,
        'total_depense': total_depense,
        'par_categorie': par_categorie,
        'par_couleur': par_couleur,
        'par_saison': par_saison,
        'total_portages': total_portages,
        'cout_moyen_portage': cout_moyen_portage,
        'plus_portes': plus_portes,
        'peu_portes': peu_portes,
    }
    return render(request, 'vetements/statistiques.html', context)


# Vues pour les valises
@login_required
def valises_list(request):
    """Liste des valises pour les voyages"""
    today = date.today()
    valises = Valise.objects.filter(proprietaire=request.user)

    # Filtrer par statut
    statut_filter = request.GET.get('statut')
    if statut_filter:
        valises = valises.filter(statut=statut_filter)

    # Séparer par période
    valises_futures = valises.filter(date_depart__gt=today).order_by('date_depart')
    valises_en_cours = valises.filter(date_depart__lte=today, date_retour__gte=today).order_by('date_depart')
    valises_passees = valises.filter(date_retour__lt=today).order_by('-date_depart')[:10]  # Derniers 10 voyages

    context = {
        'valises_futures': valises_futures,
        'valises_en_cours': valises_en_cours,
        'valises_passees': valises_passees,
    }
    return render(request, 'vetements/valises_list.html', context)


@login_required
def valise_detail(request, pk):
    """Détail d'une valise de voyage"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)

    context = {
        'valise': valise,
    }
    return render(request, 'vetements/valise_detail.html', context)


# Messaging views
@login_required
def messages_inbox(request):
    """Boîte de réception des messages"""
    messages_recus = Message.objects.filter(
        destinataire=request.user,
        archive_destinataire=False
    ).order_by('-date_envoi')

    non_lus = messages_recus.filter(lu=False).count()

    # Gérer la sélection d'un message via paramètre URL
    selected_message = None
    msg_id = request.GET.get('msg')
    if msg_id:
        try:
            selected_message = Message.objects.get(
                pk=msg_id,
                destinataire=request.user,
                archive_destinataire=False
            )
            # Marquer comme lu si non lu
            if not selected_message.lu:
                selected_message.lu = True
                selected_message.date_lecture = timezone.now()
                selected_message.save()
        except Message.DoesNotExist:
            pass

    context = {
        'messages': messages_recus,
        'non_lus': non_lus,
        'selected_message': selected_message,
    }
    return render(request, 'vetements/messages_inbox.html', context)


@login_required
def messages_sent(request):
    """Messages envoyés"""
    messages_envoyes = Message.objects.filter(
        expediteur=request.user,
        archive_expediteur=False
    ).order_by('-date_envoi')

    # Gérer la sélection d'un message via paramètre URL
    selected_message = None
    msg_id = request.GET.get('msg')
    if msg_id:
        try:
            selected_message = Message.objects.get(
                pk=msg_id,
                expediteur=request.user,
                archive_expediteur=False
            )
        except Message.DoesNotExist:
            pass

    context = {
        'messages': messages_envoyes,
        'selected_message': selected_message,
    }
    return render(request, 'vetements/messages_sent.html', context)


@login_required
def message_detail(request, pk):
    """Détail d'un message"""
    message = get_object_or_404(Message, pk=pk)

    # Vérifier que l'utilisateur est autorisé à voir ce message
    if message.destinataire != request.user and message.expediteur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à voir ce message.")
        return redirect('vetements:messages_inbox')

    # Marquer comme lu si c'est le destinataire qui le lit
    if message.destinataire == request.user and not message.lu:
        message.marquer_comme_lu()

    context = {
        'message': message,
    }
    return render(request, 'vetements/message_detail.html', context)


@login_required
def message_compose(request, destinataire_id=None, repondre_a=None):
    """Composer un nouveau message"""
    destinataire = None
    message_original = None

    if destinataire_id:
        destinataire = get_object_or_404(User, pk=destinataire_id)

    if repondre_a:
        message_original = get_object_or_404(Message, pk=repondre_a)
        if message_original.expediteur == request.user:
            destinataire = message_original.destinataire
        else:
            destinataire = message_original.expediteur

    if request.method == 'POST':
        dest_id = request.POST.get('destinataire')
        sujet = request.POST.get('sujet')
        contenu = request.POST.get('contenu')

        if dest_id and sujet and contenu:
            dest_user = get_object_or_404(User, pk=dest_id)
            nouveau_message = Message.objects.create(
                expediteur=request.user,
                destinataire=dest_user,
                sujet=sujet,
                contenu=contenu,
                en_reponse_a=message_original if repondre_a else None
            )
            messages.success(request, f"Message envoyé à {dest_user.username}!")
            return redirect('vetements:message_detail', pk=nouveau_message.pk)
        else:
            messages.error(request, "Veuillez remplir tous les champs.")

    # Liste des utilisateurs pour le destinataire
    utilisateurs = User.objects.exclude(pk=request.user.pk).order_by('username')

    context = {
        'utilisateurs': utilisateurs,
        'destinataire': destinataire,
        'message_original': message_original,
    }
    return render(request, 'vetements/message_compose.html', context)


@login_required
def message_delete(request, pk):
    """Supprimer/archiver un message"""
    message = get_object_or_404(Message, pk=pk)

    if message.expediteur == request.user:
        message.archive_expediteur = True
        message.save()
    elif message.destinataire == request.user:
        message.archive_destinataire = True
        message.save()
    else:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce message.")
        return redirect('vetements:messages_inbox')

    messages.success(request, "Message archivé.")
    return redirect('vetements:messages_inbox')


# Widget Fring - Création rapide de tenues
@login_required
def fring_widget(request):
    """Widget Fring pour créer rapidement des tenues"""
    if request.method == 'POST':
        # Récupérer les IDs des vêtements sélectionnés
        haut_id = request.POST.get('haut')
        bas_id = request.POST.get('bas')
        chaussures_id = request.POST.get('chaussures')
        nom_tenue = request.POST.get('nom_tenue', 'Ma tenue')

        # Vérifier qu'au moins les 3 éléments sont sélectionnés
        if haut_id and bas_id and chaussures_id:
            try:
                # Récupérer les vêtements (peut être de l'utilisateur, d'un ami ou en vente)
                haut = Vetement.objects.get(pk=haut_id)
                bas = Vetement.objects.get(pk=bas_id)
                chaussures = Vetement.objects.get(pk=chaussures_id)

                # Créer la tenue avec uniquement les vêtements de l'utilisateur
                # Pour les vêtements d'amis ou en vente, on les note dans la description
                tenue = Tenue.objects.create(
                    nom=nom_tenue,
                    proprietaire=request.user,
                    occasion='decontracte',
                    saison='toutes'
                )

                # Ajouter seulement les vêtements qui appartiennent à l'utilisateur
                if haut.proprietaire == request.user:
                    tenue.vetements.add(haut)
                if bas.proprietaire == request.user:
                    tenue.vetements.add(bas)
                if chaussures.proprietaire == request.user:
                    tenue.vetements.add(chaussures)

                tenue.save()

                messages.success(request, f"Tenue '{nom_tenue}' créée avec succès!")
                return redirect('vetements:tenue_detail', pk=tenue.pk)

            except Vetement.DoesNotExist:
                messages.error(request, "Un ou plusieurs vêtements n'existent pas.")
        else:
            messages.error(request, "Veuillez sélectionner au moins un haut, un bas et une paire de chaussures.")

    # Récupérer les IDs des amis acceptés
    amities_acceptees = Amitie.objects.filter(
        Q(demandeur=request.user, statut='acceptee') |
        Q(destinataire=request.user, statut='acceptee')
    )

    amis_ids = set()
    for amitie in amities_acceptees:
        if amitie.demandeur == request.user:
            amis_ids.add(amitie.destinataire.id)
        else:
            amis_ids.add(amitie.demandeur.id)

    # Récupérer tous les vêtements : propres + amis + en vente
    # 1. Mes propres vêtements
    mes_vetements = Vetement.objects.filter(proprietaire=request.user)

    # 2. Vêtements des amis
    vetements_amis = Vetement.objects.filter(proprietaire__id__in=amis_ids)

    # 3. Vêtements en vente
    annonces_disponibles = AnnonceVente.objects.filter(statut='en_vente')
    vetements_en_vente = Vetement.objects.filter(
        id__in=annonces_disponibles.values_list('vetement_id', flat=True)
    ).exclude(proprietaire=request.user)  # Exclure mes propres vêtements en vente

    # Combiner tous les vêtements
    tous_vetements = mes_vetements | vetements_amis | vetements_en_vente
    tous_vetements = tous_vetements.distinct()

    # Filtrer par catégorie (insensible à la casse)
    # Hauts
    hauts = tous_vetements.filter(
        categorie__nom__iregex=r'^(t-shirt|chemise|pull|sweat|veste|manteau|top|chemisier|polo|débardeur|gilet|cardigan|blouson)$'
    ).order_by('-date_ajout')

    # Bas
    bas = tous_vetements.filter(
        categorie__nom__iregex=r'^(pantalon|jean|short|jupe|legging|jogging|bermuda)$'
    ).order_by('-date_ajout')

    # Chaussures
    chaussures = tous_vetements.filter(
        categorie__nom__iregex=r'^(chaussure|basket|botte|sandale|escarpin|mocassin|sneaker|tong|ballerine|derby|chaussures)$'
    ).order_by('-date_ajout')

    context = {
        'hauts': hauts,
        'bas': bas,
        'chaussures': chaussures,
        'user': request.user,
    }
    return render(request, 'vetements/fring_widget.html', context)


# Gestion des amis
@login_required
def amis_list(request):
    """Liste des amis et demandes d'amitié"""
    # Récupérer les amis acceptés
    amities_acceptees = Amitie.objects.filter(
        Q(demandeur=request.user, statut='acceptee') |
        Q(destinataire=request.user, statut='acceptee')
    )

    amis = []
    for amitie in amities_acceptees:
        if amitie.demandeur == request.user:
            amis.append({
                'user': amitie.destinataire,
                'depuis': amitie.date_reponse,
                'amitie_id': amitie.id
            })
        else:
            amis.append({
                'user': amitie.demandeur,
                'depuis': amitie.date_reponse,
                'amitie_id': amitie.id
            })

    # Demandes d'amitié reçues (en attente)
    demandes_recues = Amitie.objects.filter(
        destinataire=request.user,
        statut='en_attente'
    ).order_by('-date_demande')

    # Demandes d'amitié envoyées (en attente)
    demandes_envoyees = Amitie.objects.filter(
        demandeur=request.user,
        statut='en_attente'
    ).order_by('-date_demande')

    # Tous les utilisateurs pour rechercher des amis
    tous_utilisateurs = User.objects.exclude(pk=request.user.pk).order_by('username')

    # Exclure les utilisateurs déjà amis ou avec demande en cours
    amis_ids = [ami['user'].id for ami in amis]
    demandes_ids = list(demandes_recues.values_list('demandeur_id', flat=True)) + \
                   list(demandes_envoyees.values_list('destinataire_id', flat=True))

    utilisateurs_disponibles = tous_utilisateurs.exclude(
        Q(id__in=amis_ids) | Q(id__in=demandes_ids)
    )

    context = {
        'amis': amis,
        'demandes_recues': demandes_recues,
        'demandes_envoyees': demandes_envoyees,
        'utilisateurs_disponibles': utilisateurs_disponibles,
    }
    return render(request, 'vetements/amis_list.html', context)


@login_required
def amitie_demander(request, user_id):
    """Envoyer une demande d'amitié"""
    destinataire = get_object_or_404(User, pk=user_id)

    if destinataire == request.user:
        messages.error(request, "Vous ne pouvez pas vous ajouter vous-même.")
        return redirect('vetements:amis_list')

    # Vérifier qu'il n'y a pas déjà une relation
    relation_existante = Amitie.objects.filter(
        Q(demandeur=request.user, destinataire=destinataire) |
        Q(demandeur=destinataire, destinataire=request.user)
    ).first()

    if relation_existante:
        if relation_existante.statut == 'en_attente':
            messages.warning(request, "Une demande d'amitié est déjà en cours.")
        elif relation_existante.statut == 'acceptee':
            messages.info(request, f"Vous êtes déjà ami avec {destinataire.username}.")
        else:
            messages.error(request, "Une relation existe déjà.")
    else:
        # Créer la demande d'amitié
        Amitie.objects.create(
            demandeur=request.user,
            destinataire=destinataire,
            statut='en_attente'
        )
        messages.success(request, f"Demande d'amitié envoyée à {destinataire.username}!")

    return redirect('vetements:amis_list')


@login_required
def amitie_accepter(request, amitie_id):
    """Accepter une demande d'amitié"""
    amitie = get_object_or_404(Amitie, pk=amitie_id, destinataire=request.user, statut='en_attente')

    amitie.statut = 'acceptee'
    amitie.date_reponse = timezone.now()
    amitie.save()

    messages.success(request, f"Vous êtes maintenant ami avec {amitie.demandeur.username}!")
    return redirect('vetements:amis_list')


@login_required
def amitie_refuser(request, amitie_id):
    """Refuser une demande d'amitié"""
    amitie = get_object_or_404(Amitie, pk=amitie_id, destinataire=request.user, statut='en_attente')

    amitie.statut = 'refusee'
    amitie.date_reponse = timezone.now()
    amitie.save()

    messages.info(request, f"Demande d'amitié de {amitie.demandeur.username} refusée.")
    return redirect('vetements:amis_list')


@login_required
def amitie_supprimer(request, amitie_id):
    """Supprimer une amitié ou annuler une demande"""
    amitie = get_object_or_404(
        Amitie,
        Q(pk=amitie_id),
        Q(demandeur=request.user) | Q(destinataire=request.user)
    )

    if amitie.demandeur == request.user:
        autre_user = amitie.destinataire
    else:
        autre_user = amitie.demandeur

    amitie.delete()
    messages.success(request, f"Relation avec {autre_user.username} supprimée.")
    return redirect('vetements:amis_list')


# Marketplace
@login_required
def marketplace_liste(request):
    """Liste des vêtements en vente sur le marketplace"""
    # Vêtements en vente (sauf les miens)
    annonces = AnnonceVente.objects.filter(
        statut='en_vente'
    ).exclude(
        vendeur=request.user
    ).select_related('vetement', 'vendeur').order_by('-date_publication')

    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        annonces = annonces.filter(vetement__categorie_id=categorie_id)

    # Filtrage par prix
    prix_max = request.GET.get('prix_max')
    if prix_max:
        try:
            annonces = annonces.filter(prix_vente__lte=float(prix_max))
        except ValueError:
            pass

    # Recherche
    recherche = request.GET.get('q')
    if recherche:
        annonces = annonces.filter(
            Q(vetement__nom__icontains=recherche) |
            Q(description_vente__icontains=recherche) |
            Q(vetement__marque__icontains=recherche)
        )

    context = {
        'annonces': annonces,
        'categories': Categorie.objects.all(),
    }
    return render(request, 'vetements/marketplace_liste.html', context)


@login_required
def marketplace_mes_annonces(request):
    """Mes annonces de vente"""
    mes_annonces = AnnonceVente.objects.filter(
        vendeur=request.user
    ).select_related('vetement', 'acheteur').order_by('-date_publication')

    context = {
        'annonces': mes_annonces,
    }
    return render(request, 'vetements/marketplace_mes_annonces.html', context)


@login_required
def marketplace_annonce_detail(request, annonce_id):
    """Détail d'une annonce de vente"""
    annonce = get_object_or_404(
        AnnonceVente.objects.select_related('vetement', 'vendeur', 'acheteur'),
        pk=annonce_id
    )

    context = {
        'annonce': annonce,
    }
    return render(request, 'vetements/marketplace_annonce_detail.html', context)


@login_required
def marketplace_creer_annonce(request, vetement_id):
    """Créer une annonce de vente pour un vêtement"""
    vetement = get_object_or_404(Vetement, pk=vetement_id, proprietaire=request.user)

    # Vérifier qu'il n'y a pas déjà une annonce
    if hasattr(vetement, 'annonce_vente'):
        messages.warning(request, "Ce vêtement est déjà en vente.")
        return redirect('vetements:marketplace_mes_annonces')

    if request.method == 'POST':
        prix = request.POST.get('prix_vente')
        description = request.POST.get('description_vente', '')
        negociable = request.POST.get('negociable') == 'on'
        livraison = request.POST.get('livraison_possible') == 'on'

        if prix:
            try:
                prix_decimal = float(prix)
                if prix_decimal <= 0:
                    messages.error(request, "Le prix doit être supérieur à 0.")
                else:
                    AnnonceVente.objects.create(
                        vetement=vetement,
                        vendeur=request.user,
                        prix_vente=prix_decimal,
                        description_vente=description,
                        negociable=negociable,
                        livraison_possible=livraison,
                        statut='en_vente'
                    )
                    messages.success(request, f"Annonce créée pour {vetement.nom}!")
                    return redirect('vetements:marketplace_mes_annonces')
            except ValueError:
                messages.error(request, "Prix invalide.")
        else:
            messages.error(request, "Le prix est obligatoire.")

    context = {
        'vetement': vetement,
    }
    return render(request, 'vetements/marketplace_creer_annonce.html', context)


@login_required
def marketplace_modifier_annonce(request, annonce_id):
    """Modifier une annonce de vente"""
    annonce = get_object_or_404(AnnonceVente, pk=annonce_id, vendeur=request.user)

    if request.method == 'POST':
        prix = request.POST.get('prix_vente')
        description = request.POST.get('description_vente', '')
        negociable = request.POST.get('negociable') == 'on'
        livraison = request.POST.get('livraison_possible') == 'on'
        statut = request.POST.get('statut')

        if prix:
            try:
                prix_decimal = float(prix)
                if prix_decimal <= 0:
                    messages.error(request, "Le prix doit être supérieur à 0.")
                else:
                    annonce.prix_vente = prix_decimal
                    annonce.description_vente = description
                    annonce.negociable = negociable
                    annonce.livraison_possible = livraison
                    if statut in ['en_vente', 'retiree']:
                        annonce.statut = statut
                    annonce.save()
                    messages.success(request, "Annonce modifiée!")
                    return redirect('vetements:marketplace_mes_annonces')
            except ValueError:
                messages.error(request, "Prix invalide.")
        else:
            messages.error(request, "Le prix est obligatoire.")

    context = {
        'annonce': annonce,
    }
    return render(request, 'vetements/marketplace_modifier_annonce.html', context)


@login_required
def marketplace_supprimer_annonce(request, annonce_id):
    """Supprimer une annonce de vente"""
    annonce = get_object_or_404(AnnonceVente, pk=annonce_id, vendeur=request.user)

    vetement_nom = annonce.vetement.nom
    annonce.delete()

    messages.success(request, f"Annonce pour {vetement_nom} supprimée.")
    return redirect('vetements:marketplace_mes_annonces')
