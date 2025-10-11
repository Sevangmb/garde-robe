from django import forms
from django.core.exceptions import ValidationError
from .models import Valise, Vetement, Tenue
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
                initial_values = valise.vetements.filter(categorie__nom=categorie).values_list('id', flat=True)
            
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