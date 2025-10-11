from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal

from .models import Categorie, Couleur, Taille, Vetement, Tenue, Valise


class VetementModelTestCase(TestCase):
    """Tests du modèle Vetement"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.categorie = Categorie.objects.create(nom='T-shirt')
        self.couleur = Couleur.objects.create(nom='Noir', code_hex='#000000')
        self.taille = Taille.objects.create(nom='M', type_taille='standard', ordre=3)

    def test_vetement_creation(self):
        """Test création d'un vêtement"""
        vetement = Vetement.objects.create(
            proprietaire=self.user,
            nom='T-shirt noir',
            categorie=self.categorie,
            couleur=self.couleur,
            taille=self.taille,
            genre='homme',
            saison='toute_saison',
            prix_achat=Decimal('19.99'),
            nombre_portage=5
        )
        self.assertEqual(vetement.nom, 'T-shirt noir')
        self.assertEqual(str(vetement), 'T-shirt noir')

    def test_cout_par_portage(self):
        """Test du calcul du coût par portage"""
        vetement = Vetement.objects.create(
            proprietaire=self.user,
            nom='Jean',
            categorie=self.categorie,
            couleur=self.couleur,
            taille=self.taille,
            genre='homme',
            saison='toute_saison',
            prix_achat=Decimal('50.00'),
            nombre_portage=10
        )
        self.assertEqual(vetement.cout_par_portage, Decimal('5.00'))

    def test_peu_porte_property(self):
        """Test de la propriété peu_porte"""
        vetement = Vetement.objects.create(
            proprietaire=self.user,
            nom='Veste',
            categorie=self.categorie,
            couleur=self.couleur,
            taille=self.taille,
            genre='homme',
            saison='hiver',
            nombre_portage=2
        )
        self.assertTrue(vetement.peu_porte)


class ValiseModelTestCase(TestCase):
    """Tests du modèle Valise"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_valise_creation(self):
        """Test création d'une valise"""
        today = date.today()
        valise = Valise.objects.create(
            proprietaire=self.user,
            nom='Voyage Paris',
            destination='Paris',
            type_voyage='weekend',
            date_depart=today + timedelta(days=7),
            date_retour=today + timedelta(days=9),
            statut='preparation'
        )
        self.assertEqual(valise.duree_sejour, 3)
        self.assertTrue(valise.est_a_venir)
        self.assertFalse(valise.est_passee)


class ViewsTestCase(TestCase):
    """Tests des vues"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_required(self):
        """Test que les vues nécessitent une authentification"""
        response = self.client.get(reverse('vetements:accueil'))
        self.assertEqual(response.status_code, 302)  # Redirection

    def test_accueil_authenticated(self):
        """Test de la page d'accueil authentifié"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('vetements:accueil'))
        self.assertEqual(response.status_code, 200)
