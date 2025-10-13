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
from .models import (Vetement, Categorie, Tenue, Valise, ItemValise, Message, Amitie, AnnonceVente,
                      FavoriAnnonce, TransactionVente, EvaluationVendeur, Couleur, Taille, EvenementTenue)
from django.http import JsonResponse
import json
from .forms import ValiseForm, ValiseVetementsForm, ValiseStatutForm, VetementForm, EvenementForm
import calendar
from datetime import datetime, timedelta

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
        # Rediriger selon le type d'utilisateur
        if request.user.is_superuser:
            return redirect('/admin/')
        else:
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
                # Rediriger les superutilisateurs vers l'admin
                if user.is_superuser:
                    return redirect('/admin/')
                else:
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
    from datetime import datetime, timedelta
    from collections import defaultdict

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

    # ========================================
    # NOUVELLES STATISTIQUES AVANCÉES
    # ========================================

    # 1. Coût par portage par catégorie
    cout_par_categorie = []
    for cat in par_categorie:
        cat_nom = cat['categorie__nom']
        vetements_cat = vetements.filter(categorie__nom=cat_nom).exclude(prix_achat__isnull=True).exclude(nombre_portage=0)
        if vetements_cat.exists():
            couts_cat = [v.cout_par_portage for v in vetements_cat if v.cout_par_portage]
            if couts_cat:
                cout_par_categorie.append({
                    'categorie': cat_nom,
                    'cout_moyen': sum(couts_cat) / len(couts_cat),
                    'count': len(couts_cat)
                })
    cout_par_categorie = sorted(cout_par_categorie, key=lambda x: x['cout_moyen'])[:10]

    # 2. Top 10 vêtements les plus rentables (coût par portage le plus bas)
    plus_rentables = []
    for v in vetements_avec_prix:
        if v.cout_par_portage and v.nombre_portage >= 5:  # Au moins 5 portages pour être considéré
            plus_rentables.append(v)
    plus_rentables = sorted(plus_rentables, key=lambda x: x.cout_par_portage)[:10]

    # 3. Utilisation par mois (12 derniers mois)
    today = timezone.now().date()
    utilisation_mensuelle = []
    labels_mois = []

    for i in range(11, -1, -1):  # 12 derniers mois
        mois_debut = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        if mois_debut.month == 12:
            mois_fin = mois_debut.replace(year=mois_debut.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            mois_fin = mois_debut.replace(month=mois_debut.month + 1, day=1) - timedelta(days=1)

        # Compter les vêtements portés ce mois (dernière utilisation dans ce mois)
        portages_mois = vetements.filter(
            derniere_utilisation__gte=mois_debut,
            derniere_utilisation__lte=mois_fin
        ).count()

        utilisation_mensuelle.append(portages_mois)
        labels_mois.append(mois_debut.strftime('%b %Y'))

    # 4. Alertes intelligentes - Vêtements jamais portés ou pas portés depuis longtemps
    alertes = []
    vetements_jamais_portes = vetements.filter(nombre_portage=0)
    if vetements_jamais_portes.exists():
        alertes.append({
            'type': 'warning',
            'titre': 'Vêtements jamais portés',
            'message': f'{vetements_jamais_portes.count()} vêtement(s) n\'ont jamais été portés',
            'count': vetements_jamais_portes.count(),
            'icon': 'new_releases'
        })

    # Vêtements pas portés depuis plus de 6 mois
    six_mois_ago = today - timedelta(days=180)
    vetements_anciens = vetements.filter(
        derniere_utilisation__lt=six_mois_ago
    ).exclude(nombre_portage=0)
    if vetements_anciens.exists():
        alertes.append({
            'type': 'info',
            'titre': 'Pas portés depuis 6+ mois',
            'message': f'{vetements_anciens.count()} vêtement(s) n\'ont pas été portés depuis plus de 6 mois',
            'count': vetements_anciens.count(),
            'icon': 'schedule'
        })

    # 5. Palette de couleurs dominante (top 5)
    couleurs_dominantes = vetements.exclude(couleur__isnull=True).values(
        'couleur__nom', 'couleur__code_hex'
    ).annotate(count=Count('id')).order_by('-count')[:5]

    # 6. Statistiques de valeur
    valeur_portee = sum([v.prix_achat for v in vetements.filter(nombre_portage__gt=0) if v.prix_achat])
    valeur_non_portee = sum([v.prix_achat for v in vetements.filter(nombre_portage=0) if v.prix_achat])

    # 7. Taux de rotation (vêtements portés dans les 30 derniers jours)
    trente_jours_ago = today - timedelta(days=30)
    vetements_recents = vetements.filter(derniere_utilisation__gte=trente_jours_ago).count()
    taux_rotation = (vetements_recents / total_vetements * 100) if total_vetements > 0 else 0

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
        # Nouvelles statistiques
        'cout_par_categorie': cout_par_categorie,
        'plus_rentables': plus_rentables,
        'utilisation_mensuelle': utilisation_mensuelle,
        'labels_mois': labels_mois,
        'alertes': alertes,
        'couleurs_dominantes': couleurs_dominantes,
        'valeur_portee': valeur_portee,
        'valeur_non_portee': valeur_non_portee,
        'taux_rotation': taux_rotation,
        'vetements_recents': vetements_recents,
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
    
    # Récupérer les filtres depuis l'URL
    source_filter = request.GET.get('source', 'tous')  # tous, mes_vetements, amis, vente
    type_filter = request.GET.get('type', 'tous')      # tous, hauts, bas, chaussures
    
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

    # Récupérer les vêtements selon le filtre de source
    if source_filter == 'mes_vetements':
        # Seulement mes vêtements
        tous_vetements = Vetement.objects.filter(proprietaire=request.user)
    elif source_filter == 'amis':
        # Seulement les vêtements des amis
        tous_vetements = Vetement.objects.filter(proprietaire__id__in=amis_ids)
    elif source_filter == 'vente':
        # Seulement les vêtements en vente
        annonces_disponibles = AnnonceVente.objects.filter(statut='en_vente')
        tous_vetements = Vetement.objects.filter(
            id__in=annonces_disponibles.values_list('vetement_id', flat=True)
        ).exclude(proprietaire=request.user)  # Exclure mes propres vêtements en vente
    else:
        # Tous les vêtements (default)
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

    # Filtrer par catégorie selon le filtre de type
    if type_filter == 'hauts':
        hauts = tous_vetements.filter(
            categorie__nom__iregex=r'^(t-shirt|chemise|pull|sweat|veste|manteau|top|chemisier|polo|débardeur|gilet|cardigan|blouson)$'
        ).order_by('-date_ajout')
        bas = Vetement.objects.none()
        chaussures = Vetement.objects.none()
    elif type_filter == 'bas':
        hauts = Vetement.objects.none()
        bas = tous_vetements.filter(
            categorie__nom__iregex=r'^(pantalon|jean|short|jupe|legging|jogging|bermuda)$'
        ).order_by('-date_ajout')
        chaussures = Vetement.objects.none()
    elif type_filter == 'chaussures':
        hauts = Vetement.objects.none()
        bas = Vetement.objects.none()
        chaussures = tous_vetements.filter(
            categorie__nom__iregex=r'^(chaussure|basket|botte|sandale|escarpin|mocassin|sneaker|tong|ballerine|derby|chaussures)$'
        ).order_by('-date_ajout')
    else:
        # Tous les types (default)
        hauts = tous_vetements.filter(
            categorie__nom__iregex=r'^(t-shirt|chemise|pull|sweat|veste|manteau|top|chemisier|polo|débardeur|gilet|cardigan|blouson)$'
        ).order_by('-date_ajout')

        bas = tous_vetements.filter(
            categorie__nom__iregex=r'^(pantalon|jean|short|jupe|legging|jogging|bermuda)$'
        ).order_by('-date_ajout')

        chaussures = tous_vetements.filter(
            categorie__nom__iregex=r'^(chaussure|basket|botte|sandale|escarpin|mocassin|sneaker|tong|ballerine|derby|chaussures)$'
        ).order_by('-date_ajout')

    context = {
        'hauts': hauts,
        'bas': bas,
        'chaussures': chaussures,
        'user': request.user,
        'source_filter': source_filter,
        'type_filter': type_filter,
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
    ).select_related('vetement__categorie', 'vetement__couleur', 'vetement__taille', 'vendeur').order_by('-date_publication')

    # Filtrage par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        annonces = annonces.filter(vetement__categorie_id=categorie_id)

    # Filtrage par couleur
    couleur_id = request.GET.get('couleur')
    if couleur_id:
        annonces = annonces.filter(vetement__couleur_id=couleur_id)

    # Filtrage par taille
    taille_id = request.GET.get('taille')
    if taille_id:
        annonces = annonces.filter(vetement__taille_id=taille_id)

    # Filtrage par état
    etat = request.GET.get('etat')
    if etat:
        annonces = annonces.filter(vetement__etat=etat)

    # Filtrage par prix
    prix_min = request.GET.get('prix_min')
    if prix_min:
        try:
            annonces = annonces.filter(prix_vente__gte=float(prix_min))
        except ValueError:
            pass

    prix_max = request.GET.get('prix_max')
    if prix_max:
        try:
            annonces = annonces.filter(prix_vente__lte=float(prix_max))
        except ValueError:
            pass

    # Filtrage négociable/livraison
    if request.GET.get('negociable'):
        annonces = annonces.filter(negociable=True)
    if request.GET.get('livraison'):
        annonces = annonces.filter(livraison_possible=True)

    # Recherche
    recherche = request.GET.get('q')
    if recherche:
        annonces = annonces.filter(
            Q(vetement__nom__icontains=recherche) |
            Q(description_vente__icontains=recherche) |
            Q(vetement__marque__icontains=recherche)
        )

    # Récupérer les favoris de l'utilisateur
    favoris_ids = FavoriAnnonce.objects.filter(
        utilisateur=request.user
    ).values_list('annonce_id', flat=True)

    # Ajouter une annotation pour savoir si c'est un favori
    for annonce in annonces:
        annonce.est_favori = annonce.id in favoris_ids

    context = {
        'annonces': annonces,
        'categories': Categorie.objects.all(),
        'couleurs': Couleur.objects.all(),
        'tailles': Taille.objects.all().order_by('ordre'),
        'etats': Vetement.ETAT_CHOICES,
        'mes_favoris_count': len(favoris_ids),
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


# Gestion des favoris
@login_required
def marketplace_toggle_favori(request, annonce_id):
    """Ajouter/retirer une annonce des favoris"""
    annonce = get_object_or_404(AnnonceVente, pk=annonce_id, statut='en_vente')
    
    favori, created = FavoriAnnonce.objects.get_or_create(
        utilisateur=request.user,
        annonce=annonce
    )
    
    if not created:
        favori.delete()
        messages.success(request, "Annonce retirée des favoris.")
    else:
        messages.success(request, "Annonce ajoutée aux favoris!")
    
    return redirect('vetements:marketplace_liste')


@login_required
def marketplace_mes_favoris(request):
    """Liste des annonces favorites de l'utilisateur"""
    favoris = FavoriAnnonce.objects.filter(
        utilisateur=request.user
    ).select_related('annonce__vetement__categorie', 'annonce__vendeur').order_by('-date_ajout')
    
    # Filtrer uniquement les annonces toujours en vente
    favoris = [f for f in favoris if f.annonce.statut == 'en_vente']
    
    context = {
        'favoris': favoris,
    }
    return render(request, 'vetements/marketplace_mes_favoris.html', context)


# Gestion des transactions
@login_required
def marketplace_mes_transactions(request):
    """Historique des transactions (achats et ventes)"""
    # Mes achats
    mes_achats = TransactionVente.objects.filter(
        acheteur=request.user
    ).select_related('annonce__vetement', 'vendeur').order_by('-date_creation')
    
    # Mes ventes
    mes_ventes = TransactionVente.objects.filter(
        vendeur=request.user
    ).select_related('annonce__vetement', 'acheteur').order_by('-date_creation')
    
    context = {
        'mes_achats': mes_achats,
        'mes_ventes': mes_ventes,
    }
    return render(request, 'vetements/marketplace_mes_transactions.html', context)


@login_required
def marketplace_contacter_vendeur(request, annonce_id):
    """Contacter le vendeur via la messagerie"""
    annonce = get_object_or_404(AnnonceVente, pk=annonce_id)
    
    if annonce.vendeur == request.user:
        messages.error(request, "Vous ne pouvez pas vous contacter vous-même.")
        return redirect('vetements:marketplace_annonce_detail', annonce_id=annonce_id)
    
    # Rediriger vers la composition de message avec le vendeur prérempli
    return redirect('vetements:message_compose_to', destinataire_id=annonce.vendeur.id)


# ========================================
# GESTION DES VALISES POUR UTILISATEURS
# ========================================

@login_required
def valise_create(request):
    """Créer une nouvelle valise"""
    if request.method == 'POST':
        form = ValiseForm(request.POST)
        if form.is_valid():
            valise = form.save(commit=False)
            valise.proprietaire = request.user
            valise.save()
            messages.success(request, f"Valise '{valise.nom}' créée avec succès!")
            return redirect('vetements:valise_edit_content', pk=valise.pk)
    else:
        form = ValiseForm()
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle valise',
        'submit_text': 'Créer la valise'
    }
    return render(request, 'vetements/valise_form.html', context)


@login_required 
def valise_edit(request, pk):
    """Modifier les informations d'une valise"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)
    
    if request.method == 'POST':
        form = ValiseForm(request.POST, instance=valise)
        if form.is_valid():
            form.save()
            messages.success(request, f"Valise '{valise.nom}' modifiée avec succès!")
            return redirect('vetements:valise_detail', pk=valise.pk)
    else:
        form = ValiseForm(instance=valise)
    
    context = {
        'form': form,
        'valise': valise,
        'title': f'Modifier "{valise.nom}"',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'vetements/valise_form.html', context)


@login_required
def valise_edit_content(request, pk):
    """Modifier le contenu (vêtements) d'une valise"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        form = ValiseVetementsForm(request.user, valise, request.POST)
        if form.is_valid():
            # Vider d'abord les items de la valise (nouveau système)
            valise.items.all().delete()
            valise.tenues.clear()

            # Ajouter les vêtements sélectionnés en créant des ItemValise
            for field_name, vetement_ids in form.cleaned_data.items():
                if field_name.startswith('vetements_') and vetement_ids:
                    # Extraire la catégorie du nom du champ (ex: 'vetements_hauts' -> 'hauts')
                    categorie_prefix = field_name.replace('vetements_', '')

                    # Mapper les catégories aux catégories de valise
                    categorie_map = {
                        'hauts': 'vetements',
                        'bas': 'vetements',
                        'chaussures': 'chaussures',
                        'accessoires': 'accessoires',
                        'sous_vetements': 'sous_vetements',
                    }
                    categorie_valise = categorie_map.get(categorie_prefix, 'vetements')

                    for vetement_id in vetement_ids:
                        vetement = Vetement.objects.get(id=vetement_id, proprietaire=request.user)
                        # Créer un ItemValise pour chaque vêtement
                        ItemValise.objects.create(
                            valise=valise,
                            vetement=vetement,
                            emballe=False,
                            categorie_valise=categorie_valise,
                            poids_estime=200  # Poids par défaut en grammes
                        )
                elif field_name == 'tenues' and vetement_ids:
                    for tenue in vetement_ids:
                        valise.tenues.add(tenue)

            messages.success(request, f"Contenu de la valise '{valise.nom}' mis à jour!")
            return redirect('vetements:valise_detail', pk=valise.pk)
    else:
        form = ValiseVetementsForm(request.user, valise)

    context = {
        'form': form,
        'valise': valise,
        'title': f'Contenu de "{valise.nom}"'
    }
    return render(request, 'vetements/valise_content_form.html', context)


@login_required
def valise_delete(request, pk):
    """Supprimer une valise"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)
    
    if request.method == 'POST':
        nom_valise = valise.nom
        valise.delete()
        messages.success(request, f"Valise '{nom_valise}' supprimée avec succès!")
        return redirect('vetements:valises_list')
    
    context = {
        'valise': valise
    }
    return render(request, 'vetements/valise_confirm_delete.html', context)


@login_required
def valise_update_status(request, pk):
    """Mettre à jour le statut d'une valise"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)
    
    if request.method == 'POST':
        form = ValiseStatutForm(request.POST, instance=valise)
        if form.is_valid():
            form.save()
            messages.success(request, f"Statut de la valise '{valise.nom}' mis à jour!")
            return redirect('vetements:valise_detail', pk=valise.pk)
    
    return redirect('vetements:valise_detail', pk=valise.pk)


@login_required
def valise_copy(request, pk):
    """Copier une valise existante pour un nouveau voyage"""
    valise_source = get_object_or_404(Valise, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        form = ValiseForm(request.POST)
        if form.is_valid():
            # Créer la nouvelle valise
            nouvelle_valise = form.save(commit=False)
            nouvelle_valise.proprietaire = request.user
            nouvelle_valise.save()

            # Copier les items de la valise source (nouveau système)
            for item_source in valise_source.items.all():
                ItemValise.objects.create(
                    valise=nouvelle_valise,
                    vetement=item_source.vetement,
                    emballe=False,  # Réinitialiser l'état emballé
                    categorie_valise=item_source.categorie_valise,
                    poids_estime=item_source.poids_estime,
                    ordre=item_source.ordre,
                    note=item_source.note
                )

            # Copier les tenues
            nouvelle_valise.tenues.set(valise_source.tenues.all())

            messages.success(request, f"Valise copiée! Nouvelle valise '{nouvelle_valise.nom}' créée.")
            return redirect('vetements:valise_detail', pk=nouvelle_valise.pk)
    else:
        # Préremplir le formulaire avec quelques données de base
        form = ValiseForm(initial={
            'type_voyage': valise_source.type_voyage,
            'climat': valise_source.climat,
            'liste_articles_supplementaires': valise_source.liste_articles_supplementaires
        })

    context = {
        'form': form,
        'valise_source': valise_source,
        'title': f'Copier "{valise_source.nom}"',
        'submit_text': 'Créer la copie'
    }
    return render(request, 'vetements/valise_copy_form.html', context)


# ========================================
# CHECKLIST INTERACTIVE POUR VALISES
# ========================================

@login_required
def valise_checklist(request, pk):
    """Vue de la checklist interactive pour préparer sa valise"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)

    # Grouper les items par catégorie
    items_par_categorie = {}
    for item in valise.items.all().order_by('ordre', 'vetement__nom'):
        categorie = item.categorie_valise
        if categorie not in items_par_categorie:
            items_par_categorie[categorie] = []
        items_par_categorie[categorie].append(item)

    context = {
        'valise': valise,
        'items_par_categorie': items_par_categorie,
    }
    return render(request, 'vetements/valise_checklist.html', context)


@login_required
def valise_toggle_item(request, pk, item_id):
    """Basculer l'état emballé d'un item (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)
    item = get_object_or_404(ItemValise, pk=item_id, valise=valise)

    try:
        # Récupérer le nouvel état depuis le corps de la requête
        data = json.loads(request.body)
        item.emballe = data.get('emballe', not item.emballe)
        item.save()

        # Retourner les statistiques mises à jour
        stats = {
            'total': valise.items.count(),
            'emballe': valise.nombre_emballe,
            'pourcentage': valise.pourcentage_completion,
            'poids_kg': float(valise.poids_total_kg),
        }

        return JsonResponse({
            'success': True,
            'emballe': item.emballe,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def valise_add_items(request, pk):
    """Ajouter des vêtements à la valise depuis la checklist"""
    valise = get_object_or_404(Valise, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        vetements_ids = request.POST.getlist('vetements')
        categorie = request.POST.get('categorie', 'vetements')

        for vetement_id in vetements_ids:
            vetement = get_object_or_404(Vetement, pk=vetement_id, proprietaire=request.user)
            # Vérifier que le vêtement n'est pas déjà dans la valise
            if not valise.items.filter(vetement=vetement).exists():
                ItemValise.objects.create(
                    valise=valise,
                    vetement=vetement,
                    emballe=False,
                    categorie_valise=categorie,
                    poids_estime=200
                )

        messages.success(request, f"{len(vetements_ids)} vêtement(s) ajouté(s) à la valise!")
        return redirect('vetements:valise_checklist', pk=valise.pk)

    # GET: afficher le formulaire
    # Vêtements déjà dans la valise
    vetements_dans_valise = valise.items.values_list('vetement_id', flat=True)

    # Vêtements disponibles (pas encore dans la valise)
    vetements_disponibles = Vetement.objects.filter(
        proprietaire=request.user
    ).exclude(
        id__in=vetements_dans_valise
    ).order_by('categorie__nom', 'nom')

    context = {
        'valise': valise,
        'vetements_disponibles': vetements_disponibles,
    }
    return render(request, 'vetements/valise_add_items.html', context)


# ========================================
# GESTION DES VÊTEMENTS POUR UTILISATEURS
# ========================================

@login_required
def vetement_create(request):
    """Créer un nouveau vêtement"""
    if request.method == 'POST':
        form = VetementForm(request.POST, request.FILES)
        if form.is_valid():
            vetement = form.save(commit=False)
            vetement.proprietaire = request.user
            vetement.save()
            messages.success(request, f"Vêtement '{vetement.nom}' ajouté avec succès!")
            return redirect('vetements:detail_vetement', pk=vetement.pk)
    else:
        form = VetementForm()

    context = {
        'form': form,
        'title': 'Ajouter un nouveau vêtement',
        'submit_text': 'Ajouter le vêtement'
    }
    return render(request, 'vetements/vetement_form.html', context)


@login_required
def vetement_edit(request, pk):
    """Modifier un vêtement existant"""
    vetement = get_object_or_404(Vetement, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        form = VetementForm(request.POST, request.FILES, instance=vetement)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vêtement '{vetement.nom}' modifié avec succès!")
            return redirect('vetements:detail_vetement', pk=vetement.pk)
    else:
        form = VetementForm(instance=vetement)

    context = {
        'form': form,
        'vetement': vetement,
        'title': f'Modifier "{vetement.nom}"',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'vetements/vetement_form.html', context)


@login_required
def vetement_delete(request, pk):
    """Supprimer un vêtement"""
    vetement = get_object_or_404(Vetement, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        nom_vetement = vetement.nom
        vetement.delete()
        messages.success(request, f"Vêtement '{nom_vetement}' supprimé avec succès!")
        return redirect('vetements:liste_vetements')

    context = {
        'vetement': vetement
    }
    return render(request, 'vetements/vetement_confirm_delete.html', context)


# ========================================
# GESTION DU CALENDRIER
# ========================================

@login_required
def calendrier_mensuel(request):
    """Vue mensuelle du calendrier avec événements et tenues planifiées"""
    # Récupérer le mois et l'année depuis les paramètres URL
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Gérer la navigation précédent/suivant
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Créer le calendrier du mois
    cal = calendar.monthcalendar(year, month)

    # Récupérer les événements du mois
    mois_debut = date(year, month, 1)
    if month == 12:
        mois_fin = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        mois_fin = date(year, month + 1, 1) - timedelta(days=1)

    evenements = EvenementTenue.objects.filter(
        proprietaire=request.user,
        date__gte=mois_debut,
        date__lte=mois_fin
    ).select_related('tenue').order_by('date', 'heure_debut')

    # Organiser les événements par date
    evenements_par_jour = {}
    for evenement in evenements:
        jour = evenement.date.day
        if jour not in evenements_par_jour:
            evenements_par_jour[jour] = []
        evenements_par_jour[jour].append(evenement)

    # Calculer les mois précédent et suivant
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'evenements_par_jour': evenements_par_jour,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'vetements/calendrier_mensuel.html', context)


@login_required
def evenement_create(request):
    """Créer un nouvel événement"""
    # Récupérer la date depuis les paramètres URL (si fournie)
    date_param = request.GET.get('date')
    initial_date = None
    if date_param:
        try:
            initial_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            pass

    if request.method == 'POST':
        form = EvenementForm(user=request.user, data=request.POST)
        if form.is_valid():
            evenement = form.save(commit=False)
            evenement.proprietaire = request.user
            evenement.save()
            messages.success(request, f"Événement '{evenement.titre}' créé avec succès!")
            return redirect('vetements:calendrier_mensuel')
    else:
        initial = {}
        if initial_date:
            initial['date'] = initial_date
        form = EvenementForm(user=request.user, initial=initial)

    context = {
        'form': form,
        'title': 'Créer un nouvel événement',
        'submit_text': 'Créer l\'événement'
    }
    return render(request, 'vetements/evenement_form.html', context)


@login_required
def evenement_edit(request, pk):
    """Modifier un événement existant"""
    evenement = get_object_or_404(EvenementTenue, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        form = EvenementForm(user=request.user, data=request.POST, instance=evenement)
        if form.is_valid():
            form.save()
            messages.success(request, f"Événement '{evenement.titre}' modifié avec succès!")
            return redirect('vetements:calendrier_mensuel')
    else:
        form = EvenementForm(user=request.user, instance=evenement)

    context = {
        'form': form,
        'evenement': evenement,
        'title': f'Modifier "{evenement.titre}"',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'vetements/evenement_form.html', context)


@login_required
def evenement_delete(request, pk):
    """Supprimer un événement"""
    evenement = get_object_or_404(EvenementTenue, pk=pk, proprietaire=request.user)

    if request.method == 'POST':
        titre_evenement = evenement.titre
        evenement.delete()
        messages.success(request, f"Événement '{titre_evenement}' supprimé avec succès!")
        return redirect('vetements:calendrier_mensuel')

    context = {
        'evenement': evenement
    }
    return render(request, 'vetements/evenement_confirm_delete.html', context)
