from django import forms
from django.core.exceptions import ValidationError
from .models import Valise, Vetement, Tenue, Categorie, Couleur, Taille, EvenementTenue
from datetime import date


class ValiseForm(forms.ModelForm):
    """Formulaire pour créer/modifier une valise"""
    
    class Meta:
        model = Valise
        fields = [
            'nom', 'destination', 'type_voyage', 'date_depart', 'date_retour',
            'meteo_prevue', 'climat', 'liste_articles_supplementaires', 'notes'
        ]
        
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Ex: Barcelone Juillet 2025, Weekend Normandie',
                'class': 'form-control'
            }),
            'destination': forms.TextInput(attrs={
                'placeholder': 'Ex: Paris, Londres, Barcelone',
                'class': 'form-control'
            }),
            'type_voyage': forms.Select(attrs={'class': 'form-control'}),
            'date_depart': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'date_retour': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'meteo_prevue': forms.TextInput(attrs={
                'placeholder': 'Ex: Ensoleillé 25°C, Pluvieux 15°C',
                'class': 'form-control'
            }),
            'climat': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Sélectionnez le climat'),
                ('chaud', 'Chaud'),
                ('tempere', 'Tempéré'),
                ('froid', 'Froid'),
                ('tropical', 'Tropical'),
                ('montagne', 'Montagne'),
                ('plage', 'Plage')
            ]),
            'liste_articles_supplementaires': forms.Textarea(attrs={
                'placeholder': 'Ex: Trousse de toilette, chargeurs, médicaments, livre...',
                'rows': 4,
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Ex: Activités prévues, contraintes, rappels...',
                'rows': 3,
                'class': 'form-control'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_depart = cleaned_data.get('date_depart')
        date_retour = cleaned_data.get('date_retour')
        
        if date_depart and date_retour:
            if date_retour <= date_depart:
                raise ValidationError("La date de retour doit être postérieure à la date de départ.")
            
            if date_depart < date.today():
                raise ValidationError("La date de départ ne peut pas être dans le passé.")
                
        return cleaned_data


class ValiseVetementsForm(forms.Form):
    """Formulaire pour sélectionner les vêtements d'une valise"""
    
    def __init__(self, user, valise=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Récupérer les vêtements de l'utilisateur
        vetements = Vetement.objects.filter(proprietaire=user).order_by('categorie__nom', 'nom')
        
        # Organiser par catégorie
        categories = {}
        for vetement in vetements:
            cat_nom = vetement.categorie.nom
            if cat_nom not in categories:
                categories[cat_nom] = []
            categories[cat_nom].append(vetement)
        
        # Créer des champs pour chaque catégorie
        for categorie, vets in categories.items():
            choices = [(v.id, f"{v.nom} ({v.marque or 'Sans marque'})") for v in vets]

            initial_values = []
            if valise:
                # Utiliser le nouveau système ItemValise
                initial_values = [item.vetement.id for item in valise.items.filter(vetement__categorie__nom=categorie)]

            self.fields[f'vetements_{categorie.lower().replace(" ", "_")}'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'vetement-checkbox'}),
                required=False,
                label=f"{categorie}s",
                initial=initial_values
            )
        
        # Champ pour les tenues
        tenues = Tenue.objects.filter(proprietaire=user).order_by('nom')
        if tenues.exists():
            initial_tenues = []
            if valise:
                initial_tenues = valise.tenues.values_list('id', flat=True)
                
            self.fields['tenues'] = forms.ModelMultipleChoiceField(
                queryset=tenues,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'tenue-checkbox'}),
                required=False,
                label="Tenues complètes",
                initial=initial_tenues
            )


class ValiseStatutForm(forms.ModelForm):
    """Formulaire pour modifier le statut et la checklist d'une valise"""

    class Meta:
        model = Valise
        fields = ['statut', 'checklist_faite']

        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'checklist_faite': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class VetementForm(forms.ModelForm):
    """Formulaire pour créer/modifier un vêtement"""

    class Meta:
        model = Vetement
        fields = [
            'nom', 'description', 'categorie', 'genre', 'saison',
            'couleur', 'taille', 'marque', 'matiere',
            'prix_achat', 'date_achat', 'lieu_achat',
            'etat', 'favori', 'emplacement', 'notes', 'image'
        ]

        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Ex: T-shirt bleu marine',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Description détaillée du vêtement...',
                'rows': 3,
                'class': 'form-control'
            }),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'saison': forms.Select(attrs={'class': 'form-control'}),
            'couleur': forms.Select(attrs={'class': 'form-control'}),
            'taille': forms.Select(attrs={'class': 'form-control'}),
            'marque': forms.TextInput(attrs={
                'placeholder': 'Ex: Zara, H&M, Nike...',
                'class': 'form-control'
            }),
            'matiere': forms.TextInput(attrs={
                'placeholder': 'Ex: 100% coton, polyester...',
                'class': 'form-control'
            }),
            'prix_achat': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'form-control',
                'step': '0.01'
            }),
            'date_achat': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'lieu_achat': forms.TextInput(attrs={
                'placeholder': 'Ex: Zara Centre-ville, Amazon...',
                'class': 'form-control'
            }),
            'etat': forms.Select(attrs={'class': 'form-control'}),
            'favori': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emplacement': forms.TextInput(attrs={
                'placeholder': 'Ex: Placard chambre, Dressing...',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Notes personnelles...',
                'rows': 2,
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre certains champs optionnels
        self.fields['description'].required = False
        self.fields['couleur'].required = False
        self.fields['taille'].required = False
        self.fields['marque'].required = False
        self.fields['matiere'].required = False
        self.fields['prix_achat'].required = False
        self.fields['date_achat'].required = False
        self.fields['lieu_achat'].required = False
        self.fields['emplacement'].required = False
        self.fields['notes'].required = False
        self.fields['image'].required = False


class EvenementForm(forms.ModelForm):
    """Formulaire pour créer/modifier un événement avec tenue planifiée"""

    class Meta:
        model = EvenementTenue
        fields = [
            'titre', 'description', 'type_evenement', 'date',
            'heure_debut', 'heure_fin', 'toute_journee',
            'tenue', 'lieu', 'meteo_prevue',
            'rappel', 'rappel_minutes_avant', 'notes'
        ]

        widgets = {
            'titre': forms.TextInput(attrs={
                'placeholder': 'Ex: Réunion importante, Dîner chez Pierre...',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Description de l\'événement...',
                'rows': 3,
                'class': 'form-control'
            }),
            'type_evenement': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'toute_journee': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tenue': forms.Select(attrs={'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={
                'placeholder': 'Ex: Bureau, Restaurant Le Gourmet...',
                'class': 'form-control'
            }),
            'meteo_prevue': forms.TextInput(attrs={
                'placeholder': 'Ex: Ensoleillé 22°C, Pluvieux...',
                'class': 'form-control'
            }),
            'rappel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rappel_minutes_avant': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '15'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Notes supplémentaires...',
                'rows': 2,
                'class': 'form-control'
            })
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrer les tenues de l'utilisateur
        if user:
            self.fields['tenue'].queryset = Tenue.objects.filter(proprietaire=user)

        # Rendre certains champs optionnels
        self.fields['description'].required = False
        self.fields['heure_debut'].required = False
        self.fields['heure_fin'].required = False
        self.fields['tenue'].required = False
        self.fields['lieu'].required = False
        self.fields['meteo_prevue'].required = False
        self.fields['notes'].required = False

    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        toute_journee = cleaned_data.get('toute_journee')

        # Si c'est un événement toute la journée, les heures ne sont pas nécessaires
        if not toute_journee:
            if heure_debut and heure_fin:
                if heure_fin <= heure_debut:
                    raise ValidationError("L'heure de fin doit être postérieure à l'heure de début.")

        return cleaned_data