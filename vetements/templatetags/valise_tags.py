"""
Template tags personnalisés pour le système de valises
"""
from django import template

register = template.Library()


@register.filter(name='category_icon')
def category_icon(category_key):
    """Retourne l'icône correspondant à une catégorie de valise"""
    icons = {
        'vetements': '👕',
        'chaussures': '👟',
        'sous_vetements': '🩲',
        'accessoires': '🎩',
        'toilette': '🧴',
        'electronique': '📱',
        'documents': '📄',
        'sante': '💊',
        'autre': '📦',
    }
    return icons.get(category_key, '📦')


@register.filter(name='category_name')
def category_name(category_key):
    """Retourne le nom lisible d'une catégorie"""
    names = {
        'vetements': 'Vêtements',
        'chaussures': 'Chaussures',
        'sous_vetements': 'Sous-vêtements',
        'accessoires': 'Accessoires',
        'toilette': 'Trousse de toilette',
        'electronique': 'Électronique',
        'documents': 'Documents',
        'sante': 'Santé & Médicaments',
        'autre': 'Autres',
    }
    return names.get(category_key, 'Autres')


@register.filter(name='packed_count')
def packed_count(items):
    """Compte le nombre d'items emballés dans une liste"""
    if not items:
        return 0
    return sum(1 for item in items if item.emballe)
