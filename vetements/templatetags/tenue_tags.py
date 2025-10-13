from django import template

register = template.Library()


@register.filter
def get_vetement_by_type(vetements, type_name):
    """
    Récupère le premier vêtement d'un certain type dans la tenue.

    Types possibles:
    - haut: t-shirt, chemise, pull, sweat, veste, manteau, top, chemisier, polo, débardeur
    - bas: pantalon, jean, short, jupe, legging, jogging
    - chaussures: chaussure, basket, botte, sandale, escarpin, mocassin, sneaker
    """

    type_mapping = {
        'haut': ['t-shirt', 'chemise', 'pull', 'sweat', 'veste', 'manteau', 'top',
                 'chemisier', 'polo', 'débardeur', 'gilet', 'cardigan', 'blouson'],
        'bas': ['pantalon', 'jean', 'short', 'jupe', 'legging', 'jogging', 'bermuda'],
        'chaussures': ['chaussure', 'basket', 'botte', 'sandale', 'escarpin',
                       'mocassin', 'sneaker', 'tong', 'ballerine', 'derby']
    }

    categories = type_mapping.get(type_name.lower(), [])

    for vetement in vetements:
        if vetement.categorie and vetement.categorie.nom.lower() in categories:
            return vetement

    return None


@register.simple_tag
def split_outfit(tenue):
    """
    Sépare une tenue en haut, bas et chaussures.
    Retourne un dictionnaire avec les trois catégories.
    """
    vetements = tenue.vetements.all()

    result = {
        'haut': get_vetement_by_type(vetements, 'haut'),
        'bas': get_vetement_by_type(vetements, 'bas'),
        'chaussures': get_vetement_by_type(vetements, 'chaussures'),
    }

    return result


@register.filter
def get_item(dictionary, key):
    """
    Récupère un élément d'un dictionnaire par sa clé.
    Utilisé pour accéder aux événements par jour dans le calendrier.
    """
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
